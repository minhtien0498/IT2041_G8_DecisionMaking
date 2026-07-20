"""Tool definitions (JSON schema OpenAI tool-calling) + `ToolExecutor` thực thi thật.

3 tool cho LLM #1 (`reasoner.py`):
- `sql_filter` — bắt buộc turn 1, lọc cứng qua Postgres (`db.py`).
- `fetch_nearby_custom` — tùy chọn, tiện ích + bán kính tùy chỉnh qua client thật
  (mapbox/geoapify/overpass, chọn qua `SOLUTION1_ENRICHMENT_PROVIDER`).
- `get_distance_to_place` — tùy chọn, khoảng cách tới 1 địa điểm cụ thể (geocode qua
  cùng client thật ở trên).

Cả 2 tool enrichment đều batched theo `candidate_ids` (tiết kiệm turn budget) và chỉ
tra cứu trong candidate set đã có từ `sql_filter` (không tự ý mở rộng ra ngoài). Xem
`enrichment_provider.py` để biết cách chọn provider — đổi 1 biến môi trường là tool
chuyển hẳn sang API thật tương ứng, output/schema của tool không đổi.
"""

from . import db, enrichment_provider, schema

# 9 loại tiện ích "generic" mà fetch_nearby_custom hỗ trợ — không đổi theo provider,
# vì cả 3 client (mapbox_client/geoapify_client/overpass_client) đều implement cùng
# 1 tập amenity này (xem enrichment_provider.py). Đổi provider chỉ đổi API thật đứng
# sau, không đổi danh sách amenity mà LLM được phép hỏi.
AMENITY_TYPES = [
    "cafe", "gym", "hospital", "kindergarten", "market",
    "park", "pharmacy", "school", "supermarket",
]

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "sql_filter",
            "description": (
                "Lọc bất động sản trong CSDL theo danh sách điều kiện (kết hợp AND). "
                "LUÔN LÀ tool gọi đầu tiên. Điều kiện hard-filter bắt buộc từ form đã "
                "được liệt kê sẵn trong system prompt — phải đưa vào conditions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "conditions": {
                        "type": "array",
                        "description": "Danh sách điều kiện lọc, kết hợp AND.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "column": {"type": "string", "description": "Tên cột trong bảng properties."},
                                "op": {"type": "string", "enum": [">=", "<=", ">", "<", "=", "!=", "ilike"]},
                                "value": {"description": "Số hoặc chuỗi tùy loại cột."},
                            },
                            "required": ["column", "op", "value"],
                        },
                    }
                },
                "required": ["conditions"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_nearby_custom",
            "description": (
                "Tìm tiện ích quanh MỖI candidate trong bán kính radius_m tùy chỉnh, dùng "
                "API bản đồ thật (mapbox/geoapify/overpass tùy cấu hình). Chỉ dùng khi "
                "free_text yêu cầu bán kính khác mặc định 1km, hoặc loại tiện ích không "
                "có sẵn trong cột dữ liệu."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "candidate_ids": {
                        "type": "array", "items": {"type": "string"},
                        "description": "Danh sách property_id lấy từ kết quả sql_filter.",
                    },
                    "amenity": {"type": "string", "enum": AMENITY_TYPES},
                    "radius_m": {"type": "integer", "description": "Bán kính tìm kiếm, đơn vị mét."},
                },
                "required": ["candidate_ids", "amenity", "radius_m"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_distance_to_place",
            "description": (
                "Tính khoảng cách từ MỖI candidate tới 1 địa điểm/địa chỉ cụ thể (vd 'chỗ "
                "làm ở 123 Nguyễn Oanh', 'Chung cư Landmark 81'), dùng geocoding + haversine "
                "thật (mapbox/geoapify/overpass tùy cấu hình). Chỉ dùng khi free_text nhắc "
                "địa điểm cụ thể, không phải loại tiện ích chung."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "candidate_ids": {
                        "type": "array", "items": {"type": "string"},
                        "description": "Danh sách property_id lấy từ kết quả sql_filter.",
                    },
                    "place_query_or_address": {"type": "string"},
                },
                "required": ["candidate_ids", "place_query_or_address"],
            },
        },
    },
]


class ToolExecutor:
    """Thực thi tool call thật cho 1 lần chạy pipeline (1 case).

    Giữ state `candidates_by_id` sau lần `sql_filter` đầu tiên để 2 tool enrichment
    tra cứu lat/lon mà không cần query lại DB — đúng tinh thần "batched theo candidate list".
    """

    def __init__(self, conn, required_conditions=None):
        self.conn = conn
        # Hard filter bắt buộc từ form (schema.build_hard_conditions) — LUÔN được AND vào
        # bất kể LLM truyền conditions gì, để đảm bảo không bao giờ vi phạm ràng buộc cứng
        # kể cả khi free model tính sai/bỏ sót lúc dịch form -> điều kiện SQL.
        self.required_conditions = required_conditions or []
        self.candidates_by_id = {}
        # Client enrichment thật (mapbox/geoapify/overpass) theo
        # SOLUTION1_ENRICHMENT_PROVIDER — luôn cùng nguồn với dataset đã nạp vào DB.
        self.client = enrichment_provider.get_client()

    def sql_filter(self, conditions):
        merged = list(self.required_conditions) + list(conditions or [])
        rows = db.query_properties(self.conn, merged)
        self.candidates_by_id = {r["property_id"]: r for r in rows}
        # Trả về property_id + các field CẦN THIẾT để LLM chấm điểm theo rubric (giá,
        # diện tích, và toàn bộ cột khoảng cách/số lượng tiện ích) — bỏ các field văn
        # bản dài (title, description_snippet, location_raw, nearest_*_name) để tiết
        # kiệm token vì không cần cho việc chấm điểm định lượng. Property đầy đủ (kể cả
        # các field văn bản) vẫn giữ nguyên trong self.candidates_by_id cho
        # guardrail/explainer dùng sau.
        scoring_columns = [
            "property_id", "price_million_vnd", "area_m2", "price_per_m2_million",
            "bedrooms", "bathrooms", "district", "ward",
            "distance_to_nearest_school_m", "distance_to_nearest_park_m",
            "distance_to_nearest_hospital_m", "distance_to_nearest_supermarket_m",
            "distance_to_nearest_boulevard_m",
            "near_school_count_1km", "near_park_count_1km", "near_hospital_count_1km",
            "near_supermarket_count_1km", "near_boulevard_count_1km",
        ]
        return [{col: r.get(col) for col in scoring_columns} for r in rows]

    def fetch_nearby_custom(self, candidate_ids, amenity, radius_m):
        results = []
        for pid in candidate_ids:
            prop = self.candidates_by_id.get(pid)
            if not prop:
                continue
            r = self.client.fetch_nearby_one(prop["latitude"], prop["longitude"], amenity, radius_m)
            results.append({"property_id": pid, **r})
        return results

    def get_distance_to_place(self, candidate_ids, place_query_or_address):
        geo = self.client.geocode_address(place_query_or_address)
        if not geo:
            return {"error": "Không tìm thấy địa điểm.", "results": []}
        results = []
        for pid in candidate_ids:
            prop = self.candidates_by_id.get(pid)
            if not prop:
                continue
            d = self.client.get_distance_m(prop["latitude"], prop["longitude"], geo["lat"], geo["lon"])
            results.append({"property_id": pid, "distance_m": round(d)})
        return {"place_name": geo["place_name"], "results": results}

    def dispatch(self, name, arguments):
        """Gọi tool theo tên (dùng khi xử lý tool_calls trả về từ LLM)."""
        if name == "sql_filter":
            return self.sql_filter(arguments.get("conditions", []))
        if name == "fetch_nearby_custom":
            return self.fetch_nearby_custom(
                arguments["candidate_ids"], arguments["amenity"], arguments["radius_m"]
            )
        if name == "get_distance_to_place":
            return self.get_distance_to_place(
                arguments["candidate_ids"], arguments["place_query_or_address"]
            )
        raise ValueError(f"Tool không hợp lệ: {name}")
