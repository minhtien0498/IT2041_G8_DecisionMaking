"""Chọn nguồn enrichment (mapbox/geoapify/overpass) qua 1 biến môi trường duy nhất.

Đổi nguồn enrichment CHỈ cần đổi `SOLUTION1_ENRICHMENT_PROVIDER` (mapbox/geoapify/
overpass, mặc định "mapbox") — không cần sửa code. Biến này quyết định đồng thời
2 việc, luôn đồng bộ với nhau:

1. File JSON nào được nạp vào Postgres (`run_solution1.py` gọi `get_properties_file`).
2. Client thật nào được `ToolExecutor` (`tools.py`) dùng cho `fetch_nearby_custom`/
   `get_distance_to_place` khi LLM gọi tool (`get_client`).

Nhờ vậy DB luôn được nạp từ CÙNG provider mà tool tra cứu động đang gọi — tránh tình
huống DB enrich bằng 1 API nhưng tool lại tra cứu bằng API khác.

Cả 3 client (`mapbox_client`, `geoapify_client`, `overpass_client`) cùng chung 1
interface (`geocode_address`, `fetch_nearby_one`, `get_distance_m`) nên `tools.py`
không cần biết đang chạy provider nào — output/schema của tool giữ nguyên không đổi.
"""

import os

from . import geoapify_client, mapbox_client, overpass_client

VALID_PROVIDERS = ("mapbox", "geoapify", "overpass")
DEFAULT_PROVIDER = "mapbox"

# property_id giống hệt nhau giữa 3 file (cùng sinh ra từ data/go_vap_tan_binh_100.json),
# chỉ khác phần dữ liệu enrichment POI (khoảng cách/tên/số lượng tiện ích).
_PROPERTIES_FILE_REL_PARTS = {
    "mapbox": ("data", "mapbox", "go_vap_tan_binh_100_enriched_mapbox_api.json"),
    "geoapify": ("data", "geoapify", "go_vap_tan_binh_100_enriched_geoapify_api.json"),
    "overpass": ("data", "overpass", "go_vap_tan_binh_100_enriched_overpass_api.json"),
}

_CLIENTS = {
    "mapbox": mapbox_client,
    "geoapify": geoapify_client,
    "overpass": overpass_client,
}


def get_provider():
    """Đọc + validate `SOLUTION1_ENRICHMENT_PROVIDER` từ env (mặc định "mapbox")."""
    provider = os.environ.get("SOLUTION1_ENRICHMENT_PROVIDER", DEFAULT_PROVIDER).strip().lower()
    if provider not in VALID_PROVIDERS:
        raise ValueError(
            f"SOLUTION1_ENRICHMENT_PROVIDER={provider!r} không hợp lệ. "
            f"Phải là một trong {VALID_PROVIDERS}."
        )
    return provider


def get_properties_file(root_dir):
    """Đường dẫn file JSON properties tương ứng provider đang chọn, để nạp vào Postgres."""
    return os.path.join(root_dir, *_PROPERTIES_FILE_REL_PARTS[get_provider()])


def get_client():
    """Module client thật tương ứng provider đang chọn, dùng cho `fetch_nearby_custom`/
    `get_distance_to_place` trong `tools.py`."""
    return _CLIENTS[get_provider()]
