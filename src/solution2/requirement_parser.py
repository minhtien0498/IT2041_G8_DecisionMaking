"""Requirement parsing cho phần free-text (deterministic, capability-aware).

Tách `user_need_text` thành: hard / soft (đo lường được) / unsupported,
đồng thời dedup với các tiêu chí đã có trong form.

Interface ổn định (`parse(form, free_text)`) để sau này thay bằng LLM thật.
"""

import re
import unicodedata
from dataclasses import dataclass, field

from .amenity_tools import known_amenities


def _norm(text):
    """Chuẩn hóa để so khớp: lowercase + bỏ dấu tiếng Việt.

    Validation set dùng chung của nhóm nhập free-text KHÔNG dấu
    ("Nha phai co cho trong vong 1km"), trong khi lexicon viết CÓ dấu.
    Bỏ dấu hai phía trước khi so khớp giúp parser hoạt động với cả hai kiểu nhập.
    """
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text.replace("đ", "d")

# ── Lexicon: cụm từ tiếng Việt -> amenity_name mà tool hiểu ──
AMENITY_LEXICON = {
    "market": ["chợ"],
    "cafe": ["cafe", "cà phê", "ca phe", "quán cà phê", "coffee"],
    "kindergarten": ["mầm non", "mẫu giáo", "nhà trẻ"],
    "school": ["trường học", "trường cấp", "trường tiểu học", "gần trường"],
    "supermarket": ["siêu thị"],
    "park": ["công viên"],
    "hospital": ["bệnh viện", "phòng khám"],
    "pharmacy": ["nhà thuốc", "hiệu thuốc"],
    "gym": ["gym", "phòng tập", "phòng gym"],
    "boulevard": ["trục đường", "đường lớn", "đường chính", "mặt tiền lớn"],
}

# amenity đã được form xử lý -> field tương ứng trong soft_preferences
FORM_AMENITY_FIELDS = {
    "school": "distance_to_nearest_school_m",
    "park": "distance_to_nearest_park_m",
    "supermarket": "distance_to_nearest_supermarket_m",
    "boulevard": "distance_to_nearest_boulevard_m",
    "hospital": "distance_to_nearest_hospital_m",
}

# Từ khóa nhu cầu chủ quan / không đo được bằng tool hiện có
SUBJECTIVE_KEYWORDS = [
    "yên tĩnh", "yen tinh", "vibe", "hàng xóm", "an ninh", "sang trọng",
    "phong thủy", "phong thuy", "view đẹp", "thoáng mát", "đông dân",
    "khu dân cư", "dân trí", "thân thiện", "sầm uất",
]

# Dấu hiệu đây là một nhu cầu (để không gắn cờ những mệnh đề rác)
NEED_MARKERS = ["muốn", "ưu tiên", "uu tien", "cần", "thích", "gần", "nhiều",
                "càng", "trong vòng", "trong ban kinh", "trong bán kính", "có"]

# Dấu hiệu ràng buộc cứng
HARD_MARKERS = ["phải", "bắt buộc", "tối thiểu", "ít nhất", "không quá", "chỉ nhận"]

# Dấu hiệu muốn ĐẾM số lượng (higher_better) thay vì khoảng cách gần nhất
COUNT_MARKERS = ["nhiều", "càng nhiều", "số lượng", "mật độ", "nhiều tiện ích",
                 "bao quanh", "xung quanh"]


@dataclass
class ParsedRequirements:
    soft: list = field(default_factory=list)
    hard: list = field(default_factory=list)
    unsupported: list = field(default_factory=list)
    duplicates: list = field(default_factory=list)  # {raw_phrase, form_field}


# Lexicon đã bỏ dấu sẵn để so khớp (tính 1 lần)
_LEXICON_NORM = {a: [_norm(p) for p in ps] for a, ps in AMENITY_LEXICON.items()}
_SUBJECTIVE_NORM = [_norm(k) for k in SUBJECTIVE_KEYWORDS]
_NEED_NORM = [_norm(k) for k in NEED_MARKERS]
_HARD_NORM = [_norm(k) for k in HARD_MARKERS]
_COUNT_NORM = [_norm(k) for k in COUNT_MARKERS]


def _split_clauses(text):
    """Tách free-text thành các mệnh đề nhỏ (chấp nhận cả 'và' lẫn 'va')."""
    parts = re.split(r"[,.;\n]|(?:\s+v[àa]\s+)|(?:\s+&\s+)", text)
    return [p.strip() for p in parts if p and p.strip()]


# Bẫy đồng âm khi bỏ dấu: "chợ" -> "cho", trùng với giới từ "cho" và "chỗ".
# Chỉ áp dụng cho input KHÔNG dấu; input có dấu không cần vì "chợ" != "cho".
_FALSE_FRIENDS = {
    "market": re.compile(
        r"\bcho\s+(thue|con|phep|nen|biet|vay|toi|minh|gia|nguoi)\b"
        r"|\b(du|danh|dam\s+bao|khong)\s+cho\b"
    ),
}


def _has_diacritics(text):
    return _norm(text) != text.lower()


def _detect_amenity(clause):
    """Trả về amenity_name khớp trong mệnh đề, hoặc None.

    - Input CÓ dấu: so khớp trực tiếp (chính xác, không nhập nhằng).
    - Input KHÔNG dấu: so khớp bản bỏ dấu + loại các trường hợp đồng âm.
    Duyệt theo thứ tự AMENITY_LEXICON (cụ thể -> chung), nên `kindergarten`
    được xét trước `school`: "trường mầm non" ra kindergarten, không ra school.
    """
    accented = _has_diacritics(clause)
    lexicon = AMENITY_LEXICON if accented else _LEXICON_NORM
    text = clause.lower() if accented else _norm(clause)

    for amenity, phrases in lexicon.items():
        if not accented:
            trap = _FALSE_FRIENDS.get(amenity)
            if trap and trap.search(text):
                continue
        for ph in phrases:
            if re.search(rf"(?<!\w){re.escape(ph)}(?!\w)", text):
                return amenity
    return None


def _parse_radius_m(clause):
    """Trích bán kính (m) từ mệnh đề, mặc định 1000m nếu không nêu."""
    low = _norm(clause)
    m_km = re.search(r"(\d+(?:[.,]\d+)?)\s*km", low)
    if m_km:
        return int(float(m_km.group(1).replace(",", ".")) * 1000)
    m_m = re.search(r"(\d+)\s*m(?:et)?\b", low)
    if m_m:
        return int(m_m.group(1))
    return 1000


def parse(form, free_text):
    """Phân tích free_text dựa trên năng lực tool và các tiêu chí đã có trong form.

    form: dict input (gồm 'soft_preferences' nếu có).
    free_text: chuỗi nhu cầu tự do của người dùng.
    """
    result = ParsedRequirements()
    if not free_text or not free_text.strip():
        return result

    supported = known_amenities()
    form_prefs = (form or {}).get("soft_preferences", {}) or {}

    for clause in _split_clauses(free_text):
        low = _norm(clause)
        amenity = _detect_amenity(clause)

        # 1) Không map được sang amenity nào tool hiểu -> xét unsupported.
        #    (Ưu tiên nhận diện amenity trước: nếu mệnh đề vừa nêu tiện ích đo
        #    được vừa kèm tính từ chủ quan, vẫn giữ phần đo được.)
        if amenity is None:
            if any(k in low for k in _SUBJECTIVE_NORM) or any(k in low for k in _NEED_NORM):
                result.unsupported.append(clause)
            continue

        # 2) amenity không nằm trong năng lực tool
        if amenity not in supported:
            result.unsupported.append(clause)
            continue

        # 4) Dedup với form
        form_field = FORM_AMENITY_FIELDS.get(amenity)
        if form_field and form_field in form_prefs:
            result.duplicates.append({"raw_phrase": clause, "form_field": form_field})
            continue

        # 5) Sinh requirement đo lường được
        is_count = any(k in low for k in _COUNT_NORM)
        radius = _parse_radius_m(clause)
        weight = 1.5 if ("cang" in low or "rat" in low) else 1.0

        if is_count:
            req = {
                "raw_phrase": clause,
                "amenity_name": amenity,
                "agg": "count",
                "radius_m": radius,
                "derived_attribute": f"nearby_{amenity}_count_within_{radius}m",
                "direction": "higher_better",
                "weight": weight,
            }
        else:
            req = {
                "raw_phrase": clause,
                "amenity_name": amenity,
                "agg": "nearest_distance",
                "radius_m": radius,
                "derived_attribute": f"distance_to_nearest_{amenity}_m",
                "direction": "lower_better",
                "weight": weight,
            }

        if any(k in low for k in _HARD_NORM):
            result.hard.append(req)
        else:
            result.soft.append(req)

    return result
