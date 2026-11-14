---
title: "E5: Đường học"
description: Huấn luyện với tỷ lệ polygon nhãn tăng dần cho thấy độ chính xác cân bằng lớp gần bão hòa sau khoảng 300 polygon.
sidebar:
  order: 5
---

**Câu hỏi.** Vẽ thêm polygon nhãn có cải thiện bộ phân loại lớp phủ SAR không?

**Trả lời ngắn.** Không nhiều, nếu là nhãn cùng kiểu. Độ chính xác cân bằng lớp (BA) tăng nhanh tới khoảng 300 polygon rồi đi ngang: 92,2% với 40% số polygon, 93,2% với toàn bộ.

## Thiết lập E5

- **Mô hình:** Random Forest, CV khối không gian 5 km, 3 lần lặp × 5 fold.
- **Cách làm:** ở mỗi fold, giữ ngẫu nhiên một tỷ lệ (5% đến 100%) *polygon huấn luyện* (giữ mọi ô của polygon được chọn), huấn luyện, rồi chấm trên toàn bộ fold kiểm tra. Bỏ qua trường hợp tỷ lệ quá nhỏ khiến một lớp không còn mẫu nào.
- **Giá trị ±** là độ lệch chuẩn qua 15 lượt fold.

## Kết quả E5

![E5: đường học, độ chính xác cân bằng lớp theo số polygon huấn luyện](/figures/vi/E5_learning_curve.png)

| Tỷ lệ polygon huấn luyện | 5% | 10% | 20% | 40% | 60% | 80% | 100% |
|---|---|---|---|---|---|---|---|
| Số polygon (trung bình mỗi fold) | 35 | 69 | 139 | 277 | 416 | 555 | 694 |
| BA (%) | 86,4 ± 5,7 | 87,7 ± 5,1 | 91,0 ± 3,0 | 92,2 ± 1,6 | 92,5 ± 1,9 | 92,8 ± 1,6 | 93,2 ± 1,5 |

Ở mức 100%, một fold huấn luyện chứa khoảng 694 trong 864 polygon cho mẫu (số còn lại nằm ở fold kiểm tra).

## E5: diễn giải

- **Đường học gần bão hòa sau khoảng 300 polygon.** Từ 40% lên 100% số polygon chỉ thêm 1 điểm BA.
- **Độ dao động giảm khi có nhiều polygon hơn** (±5,7 ở 5%, ±1,5 ở 100%): tập nhãn nhỏ cho kết quả bấp bênh tùy polygon nào được chọn.
- **Thứ còn có thể giúp là độ đa dạng, không phải số lượng:** nhãn ở vùng thiếu (Đô thị ở phía nam chỉ có 7 mẫu, xem [E4](/vi/experiments/e4-validation/)) và nhãn ở ô khó như ô làng xen cây hay ruộng vừa gặt.
- Lưu ý ô kiểm tra là ô thuần gần vùng có nhãn; đường học không nói gì về ô lẫn lớp.
