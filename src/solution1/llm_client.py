"""OpenRouterLLMClient: client LLM thật qua OpenRouter (OpenAI-compatible API).

2 tầng fallback:
1. Model pool theo stage ("reasoning" | "explanation") — model mặc định của stage thử
   trước, lỗi thì chuyển sang model kế tiếp trong pool chung.
2. API key rotation — mỗi model được thử với TỪNG key trong danh sách (bắt đầu từ key
   đang "tốt" gần nhất) khi lỗi có dấu hiệu rate-limit/hết quota/auth (401/402/403/429).
   Lỗi khác (model không tồn tại, network...) không rotate key vì không giải quyết được
   gì — chuyển thẳng sang model kế tiếp.

Ghi lại model + key nào đã phục vụ mỗi lần gọi (`last_model_used`, `last_key_label_used`)
để so sánh hiệu quả sau và debug khi cần.

Lazy-import `openai` (chỉ cần khi thực sự gọi LLM).
"""

import os

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# nvidia/nemotron-3-ultra-550b-a55b:free (550B tham số, 55B active - MoE) được chọn làm
# mặc định cho stage "reasoning": model nhiều tham số nhất trong pool free, kỳ vọng suy
# luận/chấm điểm chính xác hơn. openai/gpt-oss-120b:free (nhỏ hơn) dùng cho stage
# "explanation" — đủ tốt cho việc diễn giải, không cần model lớn nhất.
DEFAULT_MODEL_REASONING = "nvidia/nemotron-3-ultra-550b-a55b:free"
DEFAULT_MODEL_EXPLANATION = "openai/gpt-oss-120b:free"
DEFAULT_MODEL_POOL = (
    "nvidia/nemotron-3-ultra-550b-a55b:free,nvidia/nemotron-3-super-120b-a12b:free,"
    "openai/gpt-oss-120b:free,qwen/qwen3-coder:free,openai/gpt-oss-20b:free"
)

# Status code cho thấy lỗi gắn với 1 key cụ thể (hết quota/rate-limit/auth) — đáng thử
# lại bằng key khác thay vì bỏ cuộc luôn.
_RETRYABLE_KEY_STATUS_CODES = {401, 402, 403, 429}


def _dedupe_keep_order(items):
    seen = set()
    out = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _load_api_keys():
    """Đọc danh sách API key theo thứ tự ưu tiên rotation.

    `OPENROUTER_API_KEYS` (phân tách dấu phẩy, vd "key_cu,key_moi") được ưu tiên; nếu
    không có thì dùng `OPENROUTER_API_KEY` đơn lẻ (tương thích ngược).
    """
    keys_env = os.environ.get("OPENROUTER_API_KEYS")
    if keys_env:
        keys = [k.strip() for k in keys_env.split(",") if k.strip()]
    else:
        single = os.environ.get("OPENROUTER_API_KEY")
        keys = [single] if single else []
    if not keys:
        raise RuntimeError("Thiếu OPENROUTER_API_KEY(S) trong biến môi trường.")
    return keys


def _is_retryable_with_other_key(exc):
    """True nếu lỗi có khả năng do rate-limit/hết quota/auth của MỘT key cụ thể."""
    return getattr(exc, "status_code", None) in _RETRYABLE_KEY_STATUS_CODES


class OpenRouterLLMClient:
    """Client gọi OpenRouter, tự fallback qua model pool VÀ key pool khi lỗi."""

    def __init__(self, stage):
        """stage: "reasoning" hoặc "explanation" — chọn model mặc định tương ứng."""
        from openai import OpenAI  # lazy import

        api_keys = _load_api_keys()

        self.stage = stage
        default_model = (
            os.environ.get("SOLUTION1_LLM_MODEL_REASONING", DEFAULT_MODEL_REASONING)
            if stage == "reasoning"
            else os.environ.get("SOLUTION1_LLM_MODEL_EXPLANATION", DEFAULT_MODEL_EXPLANATION)
        )
        pool = os.environ.get("SOLUTION1_LLM_MODEL_POOL", DEFAULT_MODEL_POOL)
        pool_models = [m.strip() for m in pool.split(",") if m.strip()]

        # Model mặc định của stage thử trước, sau đó fallback qua các model còn lại
        # trong pool chung (dùng chung giữa 2 stage để fallback lẫn nhau).
        self.models = _dedupe_keep_order([default_model] + pool_models)
        self.last_model_used = None
        self.last_key_label_used = None

        self._clients = [OpenAI(base_url=OPENROUTER_BASE_URL, api_key=k) for k in api_keys]
        self._key_labels = [f"key{i + 1}" for i in range(len(api_keys))]
        # Key "đang tốt" gần nhất — mỗi lần gọi mới bắt đầu thử từ đây trước, tránh lãng
        # phí request vào key đã biết là hết quota trong cùng 1 lần chạy pipeline.
        self._current_key_index = 0

    def chat(self, messages, tools=None, tool_choice=None, max_tokens=2000, temperature=0.3,
             reasoning_effort="low"):
        """Gọi chat completion, tự fallback qua model pool + key pool khi lỗi.

        `reasoning_effort`: giới hạn tỉ lệ token dành cho reasoning nội bộ của model
        (OpenRouter unified `reasoning` param) — free model kiểu gpt-oss/nemotron dễ
        tiêu hết max_tokens vào reasoning khiến content rỗng/None. "low" (~20%
        max_tokens) để dành đủ ngân sách cho content thật, đồng thời giảm độ trễ. Set
        None để tắt.

        Trả về (response, model_used, key_label_used). Raise lỗi cuối cùng nếu mọi
        model/key đều lỗi.
        """
        kwargs = {
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if tools is not None:
            kwargs["tools"] = tools
        if tool_choice is not None:
            kwargs["tool_choice"] = tool_choice
        if reasoning_effort is not None:
            kwargs["extra_body"] = {"reasoning": {"effort": reasoning_effort, "exclude": True}}

        last_error = None
        n_keys = len(self._clients)

        for model in self.models:
            for offset in range(n_keys):
                key_idx = (self._current_key_index + offset) % n_keys
                client = self._clients[key_idx]
                is_last_key_attempt = offset == n_keys - 1
                try:
                    response = client.chat.completions.create(model=model, **kwargs)
                    if not response.choices:
                        # Một số lỗi (hết quota/rate-limit) trả về HTTP 200 với body dạng
                        # lỗi thiếu `choices` thay vì raise exception — SDK không tự phát
                        # hiện được thành exception. Coi như lỗi retryable-theo-key (giống
                        # 429) để rotate key ngay, tránh crash 'NoneType' ở nơi gọi.
                        last_error = RuntimeError(
                            f"Response rỗng/không hợp lệ từ {model} ({self._key_labels[key_idx]}): "
                            f"{getattr(response, 'error', response)}"
                        )
                        if not is_last_key_attempt:
                            continue
                        break
                    self.last_model_used = model
                    self.last_key_label_used = self._key_labels[key_idx]
                    self._current_key_index = key_idx  # nhớ key vừa thành công cho lần gọi sau
                    return response, model, self._key_labels[key_idx]
                except Exception as e:  # noqa: BLE001 — fallback rộng cho mọi lỗi API/network
                    last_error = e
                    if _is_retryable_with_other_key(e) and not is_last_key_attempt:
                        continue  # thử key kế tiếp cho CÙNG model
                    break  # lỗi khác (hoặc đã hết key) -> chuyển model kế tiếp

        raise RuntimeError(
            f"Tất cả model/key trong pool đều lỗi (stage={self.stage}): models={self.models}"
        ) from last_error

