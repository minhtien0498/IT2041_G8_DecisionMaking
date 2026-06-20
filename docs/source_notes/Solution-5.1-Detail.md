# Chi tiết Solution 5.1

## Free-Text Query -> Fuzzy LLM Reasoning -> Iterative Search -> Top 5 + Tradeoff Explanation

Ý tưởng cốt lõi của solution 5.1 là **LLM sử dụng fuzzy reasoning để hiểu các nhu cầu mơ hồ, sau đó thực hiện tìm kiếm lặp lại từ các góc độ khác nhau**. Thay vì áp dụng một quy trình cố định (như rule-based), hệ thống **tích cực suy luận về các tradeoff** và **điều chỉnh chiến lược tìm kiếm dựa trên kết quả trung gian**. Theo cách này, LLM không chỉ là lớp giải thích, mà là **chính suy luận chủ đạo** của hệ thống.

Điểm khác biệt so với solution 5.2:
- Solution 5.2 dùng form cố định + LLM để mở rộng tiêu chí
- Solution 5.1 dùng LLM để **suy luận iterative** với cơ sở dữ liệu hybrid (vector DB + SQL DB)

### Bước 1. Người dùng nhập free-text query
Khác với solution 5.2 dùng form cố định, solution 5.1 chỉ cần người dùng mô tả nhu cầu bằng **tự do**:
- "Tôi muốn một căn hộ tốt, vị trí tốt, giá cả hợp lý nhưng không quá đắt"
- "Căn hộ đủ rộng cho gia đình, gần trường con, có nhiều tiện ích"
- "Tìm kiếm nơi ở yên tĩnh nhưng vẫn phải sống tiện lợi"

Các câu truy vấn này **có tính mơ hồ cao** (fuzzy): "tốt" có nhiều ý nghĩa, "hợp lý" không rõ ngưỡng, "không quá đắt" là so sánh tương đối.

### Bước 2. LLM phân tích và xác định các chiều mơ hồ (Fuzzy Dimensions)
LLM không cố gắng ép câu truy vấn vào một schema cố định. Thay vào đó, LLM **xác định các chiều mơ hồ**:

```
User query: "Tôi muốn căn hộ tốt, vị trí tốt, giá cả hợp lý"

LLM identifies fuzzy dimensions:
├─ "Căn hộ tốt" có thể là:
│  ├─ Interpretation A: hiện đại, well-maintained (chất lượng)
│  ├─ Interpretation B: vị trí sống động với cafe, quán ăn (vibrant)
│  └─ Interpretation C: yên tĩnh, xanh mát, an toàn (peaceful)
│
├─ "Vị trí tốt" có thể là:
│  ├─ Interpretation D: gần trường/công viên (family-focused)
│  ├─ Interpretation E: trung tâm, dễ di chuyển (accessibility)
│  └─ Interpretation F: yên tĩnh, ít ô nhiễm (quality of life)
│
└─ "Giá cả hợp lý" có thể là:
   ├─ Interpretation G: rẻ (giá dưới trung bình thị trường)
   └─ Interpretation H: trung bình (không quá cao, không quá thấp)
```

Từ mỗi chiều mơ hồ, LLM sẽ **tạo các query text khác nhau** để tìm kiếm theo từng diễn giải.

### Bước 3. Lập kế hoạch tìm kiếm lặp lại (Iterative Search Strategy)
LLM **lên kế hoạch** tìm kiếm theo các vòng (rounds), mỗi vòng tập trung vào một hoặc vài diễn giải:

```
Search Round 1: Test "Vibrant apartment + affordable"
  Query: "3-bed apartment, modern, vibrant neighborhood with cafes and amenities, affordable price"
  Tool: vector_search() → Returns 15 candidates
  Median price: 3.2-3.5B
  
  LLM: "Found vibrant options. But user said 'not too expensive'. 
       Let me test if there are quieter, cheaper options."

Search Round 2: Test "Quiet apartment + cheap"
  Query: "3-bed apartment, quiet area, peaceful, good value, lower price"
  Tool: vector_search() → Returns 12 candidates
  Median price: 2.8-3.1B
  
  LLM: "Now I see a clear tradeoff: vibrant areas are pricier (3.2-3.5B),
       quiet areas are cheaper (2.8-3.1B). Let me find the middle ground."

Search Round 3: Test "Balanced approach"
  Query: "3-bed apartment, balanced price, some amenities, moderate neighborhood"
  Tool: vector_search() → Returns 18 candidates
  Median price: 3.0-3.3B
  
  LLM: "Perfect. Now I have three clusters with clear tradeoff patterns."
```

Số vòng tìm kiếm không cố định — LLM quyết định dừng lại khi nó cảm thấy **đã khám phá đủ các góc độ** để đưa ra lời giải thích tốt về tradeoff.

### Bước 4. Phân tích kết quả và xác định các cluster (Tradeoff Analysis)
Sau khi tìm kiếm từ các góc độ khác nhau, LLM **phân nhóm các bất động sản** thành các cluster và **xác định tradeoff** cho mỗi nhóm:

```python
analysis_result = {
    "clusters": [
        {
            "cluster_name": "vibrant_neighborhood",
            "fuzzy_satisfaction": {
                "quality": 0.95,      # "Căn hộ tốt" → vibrant areas đạt 95%
                "price": 0.60,        # "Giá hợp lý" → cao hơn ngân sách, chỉ 60% thỏa mãn
                "location": 0.85      # "Vị trí tốt" → tốt nhưng có thể xa trường
            },
            "overall_fuzzy_score": 0.80,
            "properties": ["A", "B", "C"],
            "price_range": "3.2-3.5B",
            "tradeoff": "Cực kỳ sống động, tiện ích tốt, nhưng giá cao hơn"
        },
        {
            "cluster_name": "quiet_neighborhood",
            "fuzzy_satisfaction": {
                "quality": 0.70,      # Chất lượng ổn nhưng không vibrant
                "price": 0.95,        # Giá rất phù hợp
                "location": 0.75      # Vị trí bình thường
            },
            "overall_fuzzy_score": 0.80,
            "properties": ["D", "E", "F"],
            "price_range": "2.8-3.1B",
            "tradeoff": "Rất tiết kiệm, yên tĩnh, nhưng ít tiện ích"
        },
        {
            "cluster_name": "balanced_option",
            "fuzzy_satisfaction": {
                "quality": 0.82,      # Tốt, tuy không xuất sắc
                "price": 0.82,        # Phù hợp, không cao không thấp
                "location": 0.80      # Vị trí ổn
            },
            "overall_fuzzy_score": 0.81,
            "properties": ["G", "H", "I"],
            "price_range": "3.0-3.3B",
            "tradeoff": "Cân bằng: không phải cực đoan ở chiều nào"
        }
    ]
}
```

**Fuzzy satisfaction** là độ đo mức độ thỏa mãn một yêu cầu mơ hồ, từ 0 (hoàn toàn không) đến 1 (hoàn toàn).

### Bước 5. SQL filtering cho hard constraints (nếu có)
Nếu user đề cập bất kỳ constraint cứng nào (ví dụ "3 phòng", "dưới 3.5B"), LLM có thể:
1. Gọi `sql_filter()` để loại bỏ những bất động sản không thỏa mãn
2. Giới hạn các cluster chỉ chứa ứng viên hợp lệ

```sql
-- Nếu user nói "3 phòng và dưới 3.5B"
SELECT * FROM properties 
WHERE bedrooms = 3 
  AND price <= 3500000000
```

Sau bước này, từng cluster sẽ chỉ chứa những bất động sản **đáp ứng hard constraints**.

### Bước 6. Ranking trong mỗi cluster (Ranking by Fuzzy Score)
Trong mỗi cluster, LLM sắp xếp các bất động sản theo **fuzzy_satisfaction_score tương ứng với cluster đó**:

```
Cluster "vibrant_neighborhood":
  1. Property A: fuzzy_quality=0.97, fuzzy_price=0.55 → weighted_score = 0.82
  2. Property B: fuzzy_quality=0.94, fuzzy_price=0.62 → weighted_score = 0.81
  3. Property C: fuzzy_quality=0.92, fuzzy_price=0.64 → weighted_score = 0.80

Cluster "balanced_option":
  1. Property G: fuzzy_quality=0.85, fuzzy_price=0.88 → weighted_score = 0.86
  2. Property H: fuzzy_quality=0.80, fuzzy_price=0.80 → weighted_score = 0.80
  3. Property I: fuzzy_quality=0.78, fuzzy_price=0.75 → weighted_score = 0.76

Cluster "quiet_neighborhood":
  1. Property D: fuzzy_quality=0.72, fuzzy_price=0.98 → weighted_score = 0.83
  2. Property E: fuzzy_quality=0.70, fuzzy_price=0.93 → weighted_score = 0.81
  3. Property F: fuzzy_quality=0.68, fuzzy_price=0.89 → weighted_score = 0.77
```

### Bước 7. Chọn Top 5 với cân bằng cluster
LLM **chọn Top 5 bằng cách cân bằng giữa các cluster** để cung cấp **diversity** và cho phép người dùng nhìn thấy các lựa chọn khác nhau:

```
Recommendation:
  1. G (balanced, best overall fit)
  2. H (balanced, alternative)
  3. A (vibrant, best in class for vibrant)
  4. D (quiet, best in class for quiet)
  5. B (vibrant, alternative to A)

Hoặc:
  1. G (balanced, best overall fit)
  2. D (quiet, offers cheapest option)
  3. A (vibrant, best quality)
  4. H (balanced, alternative)
  5. E (quiet, alternative)
```

Cách chọn phụ thuộc vào **tín hiệu từ user query**. Nếu user nhấn mạnh "hợp lý", có thể ưu tiên quiet options. Nếu user nhấn mạnh "tốt", ưu tiên vibrant options.

### Bước 8. LLM sinh lời giải thích đầy đủ về tradeoff
LLM **giải thích chi tiết** tại sao mỗi property được chọn và các tradeoff liên quan:

```
Final Output:

"Tôi tìm thấy ba nhóm bất động sản với các tradeoff khác nhau:

1. **Property G & H (Balanced Options)**
   - Giá: 3.0-3.3B (phù hợp yêu cầu 'không quá đắt')
   - Chất lượng: Tốt, tuy không xuất sắc
   - Vị trí: Có tiện ích, cân bằng giữa sống động và yên tĩnh
   → Khuyến khích nếu bạn muốn không cực đoan ở chiều nào

2. **Property A & B (Vibrant Options)**
   - Giá: 3.2-3.5B (cao hơn một chút so với 'hợp lý')
   - Chất lượng: Xuất sắc, modern, lively
   - Vị trí: Rất nhiều cafe, quán ăn, tiện ích gần
   → Thích hợp nếu bạn ưu tiên 'căn hộ tốt' và 'vị trí tốt' hơn giá

3. **Property D & E (Quiet Options)**
   - Giá: 2.8-3.1B (rất tiết kiệm)
   - Chất lượng: Ổn, không lâu lâu cải tạo
   - Vị trí: Yên tĩnh, xanh mát
   → Phù hợp nếu bạn muốn 'giá hợp lý' là ưu tiên hàng đầu

Gợi ý của tôi: **Bắt đầu với G hoặc H** vì chúng cân bằng tất cả yếu tố. 
Nếu bạn cảm thấy chúng thiếu năng lượng, xem A hoặc B. 
Nếu bạn lo về ngân sách, xem D hoặc E."
```

### Bước 9. Hỗ trợ iterative refinement
Nếu user không hài lòng, LLM có thể:
1. Hỏi: "Bạn muốn ưu tiên điều gì hơn: giá hay chất lượng?"
2. Thực hiện tìm kiếm mới với ưu tiên đó
3. Cập nhật lại Top 5 và tradeoff explanation

### Cấu trúc output gợi ý

```python
bds_recommendation = [
    {
        "rank": 1,
        "name": "Apartment G",
        "cluster": "balanced_option",
        "overall_fuzzy_score": 0.86,
        "fuzzy_dimensions": {
            "quality": {
                "score": 0.85,
                "interpretation": "Modern, well-maintained"
            },
            "price_affordability": {
                "score": 0.88,
                "interpretation": "3.2B - reasonable, not too expensive"
            },
            "vibrant_amenities": {
                "score": 0.75,
                "interpretation": "Some cafes and parks nearby"
            }
        },
        "why_recommended": "Cân bằng tốt giữa chất lượng, giá và vị trí. Phù hợp nếu bạn muốn tránh các lựa chọn cực đoan.",
        "tradeoff": "Không phải tốt nhất ở chiều nào, nhưng ổn ở mọi chiều",
        "cluster_info": {
            "cluster_name": "balanced_option",
            "rationale": "Các bất động sản trong nhóm này cung cấp sự cân bằng giữa chất lượng, giá và vị trí",
            "properties_in_cluster": ["G", "H", "I"]
        }
    },
    {
        "rank": 2,
        "name": "Apartment A",
        "cluster": "vibrant_neighborhood",
        "overall_fuzzy_score": 0.82,
        "fuzzy_dimensions": {
            "quality": {
                "score": 0.97,
                "interpretation": "Xuất sắc, modern, lively"
            },
            "price_affordability": {
                "score": 0.55,
                "interpretation": "3.4B - cao hơn, nhưng đáng để trải nghiệm"
            },
            "vibrant_amenities": {
                "score": 0.95,
                "interpretation": "Rất nhiều cafe, quán ăn, tiện ích"
            }
        },
        "why_recommended": "Nếu 'căn hộ tốt' và 'vị trí tốt' là ưu tiên, đây là lựa chọn tốt nhất.",
        "tradeoff": "Giá cao hơn yêu cầu 'hợp lý', nhưng đổi lấy chất lượng and tiện ích tốt",
        "cluster_info": {
            "cluster_name": "vibrant_neighborhood",
            "rationale": "Nhóm này tập trung vào chất lượng cao và vị trí sống động",
            "properties_in_cluster": ["A", "B", "C"]
        }
    }
]
```

### Pipeline đề xuất

`Free-Text Query → LLM Fuzzy Analysis → Multi-Round Vector Search → Result Clustering → Tradeoff Analysis → SQL Filtering (if any) → Cluster Ranking → Top 5 Selection → LLM Explanation with Tradeoff`

### Ưu điểm của solution 5.1

1. **Xử lý mơ hồ tự nhiên**: Người dùng không cần form cố định, có thể mô tả bằng tự do
2. **Iterative reasoning**: LLM tích cực suy luận và tìm kiếm từ nhiều góc độ
3. **Tradeoff transparency**: Rõ ràng giải thích các tradeoff thay vì ép vào công thức điểm cứng
4. **Fuzzy satisfaction**: Sử dụng độ đo mức độ thỏa mãn (0-1) thay vì nhị phân
5. **Diversity**: Top 5 bao gồm nhiều lựa chọn từ các cluster khác nhau
6. **Interpretable**: Mỗi quyết định đều giải thích rõ bằng chain-of-thought
7. **Modern AI**: Sử dụng LLM reasoning và vector search — đó là xu hướng hiện tại

So với solution 5.2, solution 5.1 là một phương pháp **hoàn toàn khác**: thay vì form + enrichment, ta dùng free-text + iterative fuzzy reasoning.