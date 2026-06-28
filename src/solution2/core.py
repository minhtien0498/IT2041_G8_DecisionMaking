"""Hàm thuần dùng chung trong nội bộ Solution 2.

Viết lại độc lập (không import Solution 1) nhưng dùng CÙNG công thức toán
để member-4 so sánh hai solution công bằng.
"""

import math


def haversine_m(lat1, lon1, lat2, lon2):
    """Khoảng cách (mét) giữa hai điểm lat/lon theo công thức Haversine."""
    R = 6371000  # bán kính Trái Đất (m)
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def normalize_score(value, vmin, vmax, direction):
    """Chuẩn hóa min-max về [0, 1].

    direction = 'lower_better': giá trị càng nhỏ điểm càng cao.
    direction = 'higher_better': giá trị càng lớn điểm càng cao.
    """
    if vmax == vmin:
        return 0.0
    if direction == "lower_better":
        return max(0.0, min(1.0, (vmax - value) / (vmax - vmin)))
    if direction == "higher_better":
        return max(0.0, min(1.0, (value - vmin) / (vmax - vmin)))
    return 0.0
