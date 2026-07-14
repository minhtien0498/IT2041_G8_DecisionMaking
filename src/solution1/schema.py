"""Single source of truth cho schema DB `properties` của Solution 1.

Dùng để:
(a) sinh DDL Postgres (`db.py`)
(b) sinh đoạn mô tả "database schema" trong system prompt của LLM #1 (`reasoner.py`)
(c) validate whitelist `conditions` của tool `sql_filter` (`tools.py`)
(d) map field định lượng có trong form -> cột DB cho hard filter, generic/schema-driven
    (không hardcode cứng chỉ 2 field, dễ mở rộng nếu form thêm field sau này)
"""

TABLE_NAME = "properties"

# ── Định nghĩa cột DB (tên, kiểu SQL, đơn vị, mô tả) ──
# Khớp đúng field của data/go_vap_tan_binh_100_enriched.json.
COLUMNS = [
    {"name": "property_id", "sql_type": "TEXT PRIMARY KEY", "unit": None,
     "description": "Mã định danh duy nhất của BĐS, vd 'GV_001', 'TB_012'."},
    {"name": "title", "sql_type": "TEXT", "unit": None,
     "description": "Tiêu đề tin đăng."},
    {"name": "district", "sql_type": "TEXT", "unit": None,
     "description": "Quận, vd 'Gò Vấp', 'Tân Bình'."},
    {"name": "ward", "sql_type": "TEXT", "unit": None,
     "description": "Phường."},
    {"name": "location_raw", "sql_type": "TEXT", "unit": None,
     "description": "Địa chỉ thô chưa chuẩn hóa."},
    {"name": "price_million_vnd", "sql_type": "DOUBLE PRECISION", "unit": "triệu VND",
     "description": "Giá bán, đơn vị triệu VND."},
    {"name": "price_billion_vnd", "sql_type": "DOUBLE PRECISION", "unit": "tỷ VND",
     "description": "Giá bán, đơn vị tỷ VND (= price_million_vnd / 1000)."},
    {"name": "area_m2", "sql_type": "DOUBLE PRECISION", "unit": "m2",
     "description": "Diện tích."},
    {"name": "price_per_m2_million", "sql_type": "DOUBLE PRECISION", "unit": "triệu VND/m2",
     "description": "Đơn giá trên mỗi m2."},
    {"name": "bedrooms", "sql_type": "INTEGER", "unit": "phòng",
     "description": "Số phòng ngủ."},
    {"name": "bathrooms", "sql_type": "INTEGER", "unit": "phòng",
     "description": "Số phòng tắm."},
    {"name": "floors", "sql_type": "INTEGER", "unit": "tầng",
     "description": "Số tầng (có thể NULL)."},
    {"name": "direction", "sql_type": "TEXT", "unit": None,
     "description": "Hướng nhà (có thể NULL, dữ liệu thưa)."},
    {"name": "position", "sql_type": "TEXT", "unit": None,
     "description": "Vị trí, vd 'Trong hẻm', 'Mặt tiền' (có thể NULL)."},
    {"name": "latitude", "sql_type": "DOUBLE PRECISION", "unit": "độ",
     "description": "Vĩ độ."},
    {"name": "longitude", "sql_type": "DOUBLE PRECISION", "unit": "độ",
     "description": "Kinh độ."},
    {"name": "description_snippet", "sql_type": "TEXT", "unit": None,
     "description": "Mô tả ngắn từ tin đăng (có thể NULL)."},
    {"name": "distance_to_nearest_school_m", "sql_type": "DOUBLE PRECISION", "unit": "m",
     "description": "Khoảng cách tới trường học gần nhất."},
    {"name": "distance_to_nearest_park_m", "sql_type": "DOUBLE PRECISION", "unit": "m",
     "description": "Khoảng cách tới công viên gần nhất."},
    {"name": "distance_to_nearest_hospital_m", "sql_type": "DOUBLE PRECISION", "unit": "m",
     "description": "Khoảng cách tới bệnh viện/phòng khám gần nhất."},
    {"name": "distance_to_nearest_supermarket_m", "sql_type": "DOUBLE PRECISION", "unit": "m",
     "description": "Khoảng cách tới siêu thị gần nhất."},
    {"name": "distance_to_nearest_boulevard_m", "sql_type": "DOUBLE PRECISION", "unit": "m",
     "description": "Khoảng cách tới trục đường lớn gần nhất."},
    {"name": "nearest_school_name", "sql_type": "TEXT", "unit": None,
     "description": "Tên trường học gần nhất."},
    {"name": "near_school_count_1km", "sql_type": "INTEGER", "unit": "số lượng",
     "description": "Số trường học trong bán kính 1km."},
    {"name": "nearest_park_name", "sql_type": "TEXT", "unit": None,
     "description": "Tên công viên gần nhất."},
    {"name": "near_park_count_1km", "sql_type": "INTEGER", "unit": "số lượng",
     "description": "Số công viên trong bán kính 1km."},
    {"name": "nearest_hospital_name", "sql_type": "TEXT", "unit": None,
     "description": "Tên bệnh viện/phòng khám gần nhất."},
    {"name": "near_hospital_count_1km", "sql_type": "INTEGER", "unit": "số lượng",
     "description": "Số bệnh viện/phòng khám trong bán kính 1km."},
    {"name": "nearest_supermarket_name", "sql_type": "TEXT", "unit": None,
     "description": "Tên siêu thị gần nhất."},
    {"name": "near_supermarket_count_1km", "sql_type": "INTEGER", "unit": "số lượng",
     "description": "Số siêu thị trong bán kính 1km."},
    {"name": "nearest_boulevard_name", "sql_type": "TEXT", "unit": None,
     "description": "Tên trục đường lớn gần nhất."},
    {"name": "near_boulevard_count_1km", "sql_type": "INTEGER", "unit": "số lượng",
     "description": "Số trục đường lớn trong bán kính 1km."},
]

COLUMN_NAMES = [c["name"] for c in COLUMNS]
_NUMERIC_TYPES = {"DOUBLE PRECISION", "INTEGER"}
NUMERIC_COLUMNS = {c["name"] for c in COLUMNS if c["sql_type"] in _NUMERIC_TYPES}
TEXT_COLUMNS = {c["name"] for c in COLUMNS if c["sql_type"] not in _NUMERIC_TYPES}

# ── Toán tử hợp lệ cho sql_filter (whitelist, chống injection) ──
NUMERIC_OPS = {">=", "<=", ">", "<", "=", "!="}
TEXT_OPS = {"=", "!=", "ilike"}

# ── Mapping generic: field định lượng trong FORM -> (cột DB, toán tử) ──
# Sinh hard filter bắt buộc từ CÁC FIELD CÓ TRONG FORM. Thêm field mới ở đây
# khi form mở rộng thêm field định lượng, không cần sửa logic reasoner.
FORM_HARD_FILTER_MAP = {
    "budget_max_million": {"column": "price_million_vnd", "op": "<="},
    "min_bedrooms": {"column": "bedrooms", "op": ">="},
}


def build_hard_conditions(form):
    """Sinh list điều kiện lọc cứng bắt buộc từ form, generic theo FORM_HARD_FILTER_MAP.

    Trả về list [{"column", "op", "value"}], bỏ qua field không có trong form
    hoặc giá trị None.
    """
    conditions = []
    form = form or {}
    for field_name, mapping in FORM_HARD_FILTER_MAP.items():
        value = form.get(field_name)
        if value is None:
            continue
        conditions.append({"column": mapping["column"], "op": mapping["op"], "value": value})
    return conditions


def validate_condition(condition):
    """Validate 1 condition {"column", "op", "value"} theo whitelist.

    Raise ValueError nếu không hợp lệ. Không bao giờ cho phép string-concat
    trực tiếp giá trị LLM vào SQL — chỉ trả về sau khi qua whitelist này.
    """
    if not isinstance(condition, dict):
        raise ValueError(f"condition phải là object, nhận: {type(condition)}")
    column = condition.get("column")
    op = condition.get("op")
    value = condition.get("value")

    if column not in COLUMN_NAMES:
        raise ValueError(f"Cột không hợp lệ: {column!r}")
    if column in NUMERIC_COLUMNS:
        if op not in NUMERIC_OPS:
            raise ValueError(f"Toán tử không hợp lệ cho cột số {column!r}: {op!r}")
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"Giá trị phải là số cho cột {column!r}, nhận: {value!r}")
    else:
        if op not in TEXT_OPS:
            raise ValueError(f"Toán tử không hợp lệ cho cột text {column!r}: {op!r}")
        if not isinstance(value, str):
            raise ValueError(f"Giá trị phải là chuỗi cho cột {column!r}, nhận: {value!r}")
    return column, op, value


def to_ddl():
    """Sinh câu lệnh DDL `CREATE TABLE IF NOT EXISTS properties (...)`."""
    lines = [f"CREATE TABLE IF NOT EXISTS {TABLE_NAME} ("]
    col_defs = [f"    {c['name']} {c['sql_type']}" for c in COLUMNS]
    lines.append(",\n".join(col_defs))
    lines.append(");")
    return "\n".join(lines)


def schema_prompt_block():
    """Sinh đoạn mô tả schema DB dùng trong system prompt của LLM #1."""
    lines = [f"Bảng `{TABLE_NAME}` có các cột sau:"]
    for c in COLUMNS:
        unit = f" (đơn vị: {c['unit']})" if c["unit"] else ""
        lines.append(f"- {c['name']}{unit}: {c['description']}")
    return "\n".join(lines)
