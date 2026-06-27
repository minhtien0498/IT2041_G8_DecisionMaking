# Mẫu Validation Set

## 1. Hướng dẫn sử dụng
- Mỗi dòng là 1 test case.
- Cả Solution 1 và 2 đều chạy trên **cùng một tập case này** để đảm bảo so sánh công bằng.
- Input chung gồm 2 phần: **Form** (các tiêu chí cơ bản có thể định lượng) và **Nhu cầu thêm** (mô tả tự do, có thể để trống).
- Chỉ ghi kỳ vọng đầu ra ở mức định hướng, không cần chi tiết kỹ thuật.

## 2. Cấu trúc input chung
| Trường | Mô tả | Bắt buộc |
|---|---|---|
| Ngân sách (tỷ VND) | Giới hạn giá tối đa | Có |
| Số phòng ngủ | Số phòng ngủ mong muốn | Có |
| Khoảng cách tối đa đến trường học (m) | 0 nếu không quan tâm | Có |
| Khoảng cách tối đa đến công viên (m) | 0 nếu không quan tâm | Có |
| Khoảng cách tối đa đến trục giao thông (m) | 0 nếu không quan tâm | Có |
| Nhu cầu thêm (free-text) | Mô tả tự do các mong muốn bổ sung | Không |

## 3. Bảng case

| Case ID | Nhóm case | Form (ngân sách / phòng / trường / công viên / giao thông) | Nhu cầu thêm (free-text) | Hard constraints kỳ vọng | Soft priorities kỳ vọng | Tradeoff chấp nhận | Ghi chú review |
|---|---|---|---|---|---|---|---|
| C001 | Rõ ràng | 5 tỷ / 3 phòng / 500m / 0 / 0 |  | Giá ≤ 5 tỷ, đúng 3 phòng | Gần trường | Giá vs diện tích |  |
| C002 | Rõ ràng | 8 tỷ / 4 phòng / 0 / 1000m / 500m |  | Giá ≤ 8 tỷ, đúng 4 phòng | Gần công viên, gần giao thông | Giá vs vị trí |  |
| C003 | Mơ hồ | 10 tỷ / 3 phòng / 0 / 0 / 0 | "Muốn nơi ở tốt, yên tĩnh nhưng vẫn tiện lợi" | Giá ≤ 10 tỷ | Cân bằng yên tĩnh và tiện ích | Yên tĩnh vs tiện ích |  |
| C004 | Mơ hồ | 6 tỷ / 2 phòng / 0 / 0 / 0 | "Gần nhiều chợ và quán ăn" | Giá ≤ 6 tỷ | Nhiều tiện ích ăn uống xung quanh | Giá vs mật độ tiện ích |  |
| C005 | Mâu thuẫn | 3 tỷ / 4 phòng / 300m / 500m / 300m |  | Giá ≤ 3 tỷ, đúng 4 phòng | Gần đủ tiện ích | Không khả thi — cần nới lỏng |  |
| C006 | Mâu thuẫn | 15 tỷ / 2 phòng / 0 / 0 / 0 | "Muốn yên tĩnh nhưng gần trung tâm sầm uất" | Giá ≤ 15 tỷ | Yên tĩnh và sầm uất cùng lúc | Xung đột — LLM cần chỉ ra |  |
| C007 | Không hỗ trợ | 7 tỷ / 3 phòng / 0 / 0 / 0 | "Hàng xóm thân thiện, cộng đồng tốt" | Giá ≤ 7 tỷ | Không đo lường được | Nên bị gắn cờ unsupported |  |
| C008 | Không hỗ trợ | 9 tỷ / 3 phòng / 0 / 0 / 0 | "Phong thủy tốt, hướng nhà đẹp" | Giá ≤ 9 tỷ | Không đo lường được | Nên bị gắn cờ unsupported |  |

## 4. Mức coverage tối thiểu
- Nhu cầu rõ ràng (form đầy đủ, không mơ hồ): >= 10 case
- Nhu cầu mơ hồ (có free-text mơ hồ): >= 10 case
- Nhu cầu mâu thuẫn (form tự mâu thuẫn hoặc xung đột với free-text): >= 5 case
- Nhu cầu không hỗ trợ được (free-text không thể đo lường): >= 5 case

## 5. Review chéo
- Người tạo case:
- Người review 1:
- Người review 2:
- Ngày chốt:
