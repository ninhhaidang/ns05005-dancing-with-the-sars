---
title: "E2: Nhóm đặc trưng nào quan trọng"
description: Thí nghiệm loại bỏ đặc trưng với Random Forest cho thấy ba ngày ảnh và cả hai phân cực HH, HV quyết định độ chính xác, còn kết cấu gần như không đóng góp.
sidebar:
  order: 2
---

**Câu hỏi.** Bộ phân loại lớp phủ thật sự cần những nhóm đặc trưng SAR nào?

**Trả lời ngắn.** Đa thời gian quan trọng nhất: 3 ngày cho độ chính xác cân bằng lớp (BA) 93,1%, một ngày chỉ 83,4–85,6%. Cần cả hai phân cực (bỏ HH hay HV đều mất khoảng 4 điểm). Kết cấu chỉ đóng góp 0,2 điểm.

## Thiết lập E2

- **Mô hình:** Random Forest (300 cây, `min_samples_leaf=2`, trọng số lớp cân bằng), cũng là mô hình làm bản đồ chính.
- **Kiểm chứng:** CV khối không gian 5 km, 5 lần lặp (cùng fold với [E1](/vi/experiments/e1-models/)).
- **Cách làm:** huấn luyện lại với một tập con của 12 đặc trưng và so BA. Giá trị ± là độ lệch chuẩn qua 5 lần lặp.

## Kết quả E2

![E2: độ chính xác cân bằng lớp của từng bộ đặc trưng](/figures/vi/E2_ablation.png)

| Bộ đặc trưng | Số đặc trưng | BA (%) | F1 Nước | F1 Thực vật | F1 Đất trống | F1 Đô thị |
|---|---|---|---|---|---|---|
| Đủ 12 đặc trưng | 12 | **93,1 ± 0,1** | 99,5 | 88,1 | 89,6 | 95,1 |
| Bỏ kết cấu | 11 | 92,9 ± 0,1 | 99,3 | 88,3 | 88,7 | 95,1 |
| Bỏ độ lệch chuẩn thời gian | 10 | 92,0 ± 0,2 | 99,4 | 86,1 | 87,3 | 94,8 |
| Chỉ HV (3 ngày + HV trung bình + độ lệch chuẩn HV) | 5 | 89,4 ± 0,1 | 99,4 | 80,9 | 88,3 | 88,6 |
| Chỉ HH (3 ngày + HH trung bình + độ lệch chuẩn HH + kết cấu) | 6 | 88,9 ± 0,1 | 97,8 | 82,9 | 81,0 | 93,0 |
| Hai ngày quỹ đạo xuống (22/10, 3/11) | 4 | 87,0 ± 0,1 | 98,2 | 78,0 | 81,9 | 89,1 |
| Chỉ trung bình (HH tb, HV tb, HV − HH) | 3 | 86,9 ± 0,2 | 97,8 | 77,1 | 78,9 | 91,8 |
| Một ngày 22/10 (HH, HV, HV − HH) | 3 | 85,6 ± 0,1 | 97,4 | 76,2 | 78,7 | 88,5 |
| Một ngày 27/10, quỹ đạo lên | 3 | 85,6 ± 0,1 | 97,7 | 75,5 | 78,6 | 88,9 |
| Một ngày 3/11 | 3 | 83,4 ± 0,1 | 95,9 | 75,5 | 73,5 | 85,7 |

## E2: diễn giải

- **Đa thời gian quan trọng nhất.** 3 ngày hơn 1 ngày 7–10 điểm BA. Một phần lợi ích đơn giản là có nhiều quan sát hơn (speckle được trung bình hóa); phần khác đến từ **hướng nhìn thứ hai**: hai ngày quỹ đạo xuống gộp lại chỉ đạt 87,0%, thêm ngày 27/10 quỹ đạo lên mới đạt đủ 93,1%.
- **Cần cả hai phân cực.** Chỉ HV (89,4%) hay chỉ HH (88,9%) đều mất khoảng 4 điểm. HV (phân cực chéo, nhạy với tán xạ khối của thực vật) tách Thực vật và Đất trống tốt hơn; HH (nhạy với tán xạ bề mặt và tán xạ hai lần) giúp nhiều nhất cho lớp Đô thị.
- **Biến động theo thời gian giúp một chút** (−1,1 điểm khi bỏ các đặc trưng độ lệch chuẩn), nhưng lưu ý đặc trưng này lẫn thay đổi thật với khác biệt hướng nhìn, vì 27/10 là quỹ đạo lên còn hai ngày kia là quỹ đạo xuống.
- **Kết cấu gần như vô dụng** (−0,2 điểm) ở độ phân giải 20 m với bộ nhãn này, có thể bỏ.
- **Nước dễ ở mọi cấu hình** (F1 ≥ 95,9%); khác biệt giữa các bộ đặc trưng đến từ Thực vật, Đất trống và Đô thị.

## Kết luận E2

Điều làm phân loại chỉ từ SAR hoạt động được ở đây là **chuỗi ảnh lặp của NISAR từ nhiều hình học chụp, ở cả HH và HV**, chứ không phải mô hình phức tạp ([E1](/vi/experiments/e1-models/)) hay kết cấu. Đây là lập luận cho việc khai thác tần suất chụp dày của NISAR để lập bản đồ lớp phủ dưới mây. Độ quan trọng của từng đặc trưng riêng lẻ được xét ở [E3](/vi/experiments/e3-importance/).
