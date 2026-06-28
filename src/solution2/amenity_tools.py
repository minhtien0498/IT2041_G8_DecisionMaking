"""Mock 'Search Map API' trên database tiện ích cục bộ (Gò Vấp).

`search_amenities` có cùng chữ ký với một lệnh gọi OSM/Overpass thật,
nên về sau chỉ cần thay phần thân hàm là chuyển sang API thật được.
"""

from .core import haversine_m

# Tọa độ thực tế quanh Gò Vấp cho từng loại tiện ích.
# Các loại có sẵn trong form (school/park/hospital/supermarket/boulevard)
# được giữ để dedup; các loại mở rộng (market/cafe/kindergarten/pharmacy/gym)
# phục vụ nhu cầu free-text.
AMENITY_DATABASE = {
    "school": [
        {"name": "Trường THCS Nguyễn Du", "lat": 10.8405, "lon": 106.6550},
        {"name": "Trường THPT Trần Hưng Đạo", "lat": 10.8370, "lon": 106.6635},
        {"name": "Trường TH Lương Thế Vinh", "lat": 10.8480, "lon": 106.6520},
        {"name": "Trường THCS Gò Vấp", "lat": 10.8330, "lon": 106.6450},
        {"name": "Trường THPT Nguyễn Công Trứ", "lat": 10.8450, "lon": 106.6700},
    ],
    "park": [
        {"name": "Công viên Gia Định", "lat": 10.8190, "lon": 106.6770},
        {"name": "Công viên Phần mềm Quang Trung", "lat": 10.8460, "lon": 106.6330},
        {"name": "Công viên phường 12", "lat": 10.8350, "lon": 106.6400},
        {"name": "Công viên Làng Hoa", "lat": 10.8430, "lon": 106.6580},
    ],
    "hospital": [
        {"name": "Bệnh viện Quận Gò Vấp", "lat": 10.8380, "lon": 106.6500},
        {"name": "Bệnh viện 175", "lat": 10.8570, "lon": 106.6640},
        {"name": "Phòng khám Đa khoa Sài Gòn", "lat": 10.8450, "lon": 106.6620},
    ],
    "supermarket": [
        {"name": "Emart Gò Vấp", "lat": 10.8345, "lon": 106.6575},
        {"name": "Co.opmart Quang Trung", "lat": 10.8400, "lon": 106.6470},
        {"name": "VinMart Thống Nhất", "lat": 10.8430, "lon": 106.6650},
        {"name": "Mega Market Quang Trung", "lat": 10.8310, "lon": 106.6390},
    ],
    "boulevard": [
        {"name": "Quang Trung (trục chính)", "lat": 10.8380, "lon": 106.6450},
        {"name": "Nguyễn Oanh", "lat": 10.8420, "lon": 106.6700},
        {"name": "Phạm Văn Đồng", "lat": 10.8200, "lon": 106.6830},
        {"name": "Lê Đức Thọ", "lat": 10.8530, "lon": 106.6580},
    ],
    "market": [
        {"name": "Chợ Gò Vấp", "lat": 10.8378, "lon": 106.6668},
        {"name": "Chợ Xóm Mới", "lat": 10.8512, "lon": 106.6500},
        {"name": "Chợ Hạnh Thông Tây", "lat": 10.8430, "lon": 106.6560},
        {"name": "Chợ Tân Sơn Nhất", "lat": 10.8290, "lon": 106.6480},
        {"name": "Chợ Căn Cứ 26", "lat": 10.8485, "lon": 106.6385},
        {"name": "Chợ An Nhơn", "lat": 10.8460, "lon": 106.6720},
    ],
    "cafe": [
        {"name": "Highlands Quang Trung", "lat": 10.8388, "lon": 106.6535},
        {"name": "The Coffee House Nguyễn Oanh", "lat": 10.8412, "lon": 106.6695},
        {"name": "Phúc Long Phan Văn Trị", "lat": 10.8265, "lon": 106.6845},
        {"name": "Cafe Cộng Lê Đức Thọ", "lat": 10.8540, "lon": 106.6575},
        {"name": "Katinat Phạm Văn Đồng", "lat": 10.8225, "lon": 106.6810},
        {"name": "Trung Nguyên Lê Văn Thọ", "lat": 10.8470, "lon": 106.6620},
        {"name": "Cafe Sỏi Đá", "lat": 10.8360, "lon": 106.6490},
    ],
    "kindergarten": [
        {"name": "Trường Mầm non Sơn Ca", "lat": 10.8380, "lon": 106.6480},
        {"name": "Mầm non Hoa Mai", "lat": 10.8455, "lon": 106.6595},
        {"name": "Mầm non Tuổi Thơ", "lat": 10.8320, "lon": 106.6520},
        {"name": "Mầm non Họa Mi", "lat": 10.8500, "lon": 106.6440},
    ],
    "pharmacy": [
        {"name": "Pharmacity Quang Trung", "lat": 10.8395, "lon": 106.6510},
        {"name": "Long Châu Nguyễn Oanh", "lat": 10.8425, "lon": 106.6685},
        {"name": "An Khang Lê Đức Thọ", "lat": 10.8525, "lon": 106.6585},
        {"name": "Pharmacity Phan Văn Trị", "lat": 10.8270, "lon": 106.6800},
    ],
    "gym": [
        {"name": "California Fitness Gò Vấp", "lat": 10.8400, "lon": 106.6560},
        {"name": "Citigym Emart", "lat": 10.8348, "lon": 106.6578},
        {"name": "Phòng tập Diamond", "lat": 10.8480, "lon": 106.6630},
    ],
}


def geocode(prop):
    """Mock tool 'lat,long từ địa chỉ': lấy từ field có sẵn của BĐS."""
    return prop["latitude"], prop["longitude"]


def search_amenities(lat, lon, amenity_name, radius_m):
    """Trả về số tiện ích trong bán kính và khoảng cách tới cái gần nhất.

    Cùng chữ ký một lệnh gọi OSM/Overpass thật:
    {amenity_name, lat, lon, radius} -> {count, nearest_distance_m}.
    """
    pois = AMENITY_DATABASE.get(amenity_name)
    if not pois:
        return {"count": 0, "nearest_distance_m": None}

    distances = [haversine_m(lat, lon, p["lat"], p["lon"]) for p in pois]
    count = sum(1 for d in distances if d <= radius_m)
    return {
        "count": count,
        "nearest_distance_m": round(min(distances)),
    }


def known_amenities():
    """Danh sách amenity_name mà tool hiện hỗ trợ (cho capability-aware reasoning)."""
    return set(AMENITY_DATABASE.keys())
