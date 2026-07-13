"""Kết nối Postgres, loader idempotent, và query builder parameterized.

Không bao giờ string-concat giá trị/điều kiện của LLM vào SQL — mọi điều
kiện phải qua `schema.validate_condition` trước khi build query (whitelist
cột + toán tử), và giá trị luôn bind bằng placeholder `%s` (psycopg).
"""

import json
import os

import psycopg
from psycopg.rows import dict_row

from . import schema

DEFAULT_DSN = "postgresql://solution1:solution1@localhost:5433/solution1"


def get_dsn():
    return os.environ.get("SOLUTION1_DB_DSN", DEFAULT_DSN)


def get_connection(dsn=None):
    """Mở kết nối Postgres mới. Dùng `with get_connection() as conn:` để tự đóng."""
    return psycopg.connect(dsn or get_dsn(), row_factory=dict_row)


def init_schema(conn):
    """Tạo bảng `properties` nếu chưa có (idempotent)."""
    with conn.cursor() as cur:
        cur.execute(schema.to_ddl())
    conn.commit()


def load_properties(conn, json_path):
    """Đọc JSON danh sách BĐS, upsert vào bảng `properties` (idempotent).

    Chạy lại nhiều lần an toàn: dùng ON CONFLICT (property_id) DO UPDATE.
    Trả về số dòng đã upsert.
    """
    with open(json_path, encoding="utf-8") as f:
        properties = json.load(f)

    cols = schema.COLUMN_NAMES
    col_list = ", ".join(cols)
    placeholders = ", ".join(["%s"] * len(cols))
    update_set = ", ".join(f"{c} = EXCLUDED.{c}" for c in cols if c != "property_id")
    stmt = (
        f"INSERT INTO {schema.TABLE_NAME} ({col_list}) VALUES ({placeholders}) "
        f"ON CONFLICT (property_id) DO UPDATE SET {update_set}"
    )

    with conn.cursor() as cur:
        for prop in properties:
            values = [prop.get(c) for c in cols]
            cur.execute(stmt, values)
    conn.commit()
    return len(properties)


def _build_where(conditions):
    """Build mệnh đề WHERE parameterized từ list condition đã validate.

    conditions: list [{"column", "op", "value"}]. Trả về (sql_str, params).
    Mỗi condition được validate qua `schema.validate_condition` (whitelist
    cột + toán tử) trước khi ghép vào SQL — chỉ tên cột/toán tử (đã whitelist)
    được nội suy vào chuỗi SQL, giá trị luôn bind qua placeholder.
    """
    if not conditions:
        return "", []

    clauses = []
    params = []
    for cond in conditions:
        column, op, value = schema.validate_condition(cond)
        if op == "ilike":
            clauses.append(f"{column} ILIKE %s")
            params.append(f"%{value}%")
        else:
            clauses.append(f"{column} {op} %s")
            params.append(value)

    return " WHERE " + " AND ".join(clauses), params


def query_properties(conn, conditions=None):
    """Query bảng `properties` theo danh sách điều kiện (AND), trả về list dict."""
    where_sql, params = _build_where(conditions or [])
    sql = f"SELECT * FROM {schema.TABLE_NAME}{where_sql} ORDER BY property_id"
    with conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    return rows
