---
title: "E6: Tinh chỉnh siêu tham số bằng CV lồng"
description: Kiểm tra chéo không gian lồng nhau cho thấy tinh chỉnh Random Forest, SVM và LightGBM chỉ thay đổi độ chính xác cân bằng lớp tối đa nửa điểm.
sidebar:
  order: 6
---

**Câu hỏi.** Tinh chỉnh siêu tham số có làm các bộ phân loại lớp phủ SAR tốt hơn đáng kể không?

**Trả lời ngắn.** Không. Mức tăng lớn nhất là +0,5 điểm (SVM 93,6% → 94,1% độ chính xác cân bằng lớp); Random Forest không cải thiện (92,9% → 92,8%).

## Thiết lập E6

- **Kiểm tra chéo lồng nhau**, để bước tinh chỉnh không bao giờ nhìn thấy khối kiểm tra:
  - **Vòng ngoài:** CV khối không gian 5 km (lần lặp đầu trong các fold của [E1](/vi/experiments/e1-models/)).
  - **Vòng trong:** `GroupKFold` 3 fold theo khối 5 km bên trong mỗi tập huấn luyện vòng ngoài; chọn tham số theo độ chính xác cân bằng lớp (BA).
- Cột "mặc định" là mô hình với thiết lập mặc định trên cùng các fold vòng ngoài, nên hai cột so sánh trực tiếp được.

## Kết quả E6

![E6: độ chính xác cân bằng lớp với tham số mặc định và sau tinh chỉnh](/figures/vi/E6_nested_tuning.png)

| Mô hình | BA mặc định (%) | BA sau tinh chỉnh (%) | Lưới tìm kiếm |
|---|---|---|---|
| Random Forest | 92,9 | 92,8 | `max_features` ∈ {√p, 0,5, 1}, `min_samples_leaf` ∈ {1, 2, 5} |
| SVM (RBF) | 93,6 | 94,1 | C ∈ {1, 10, 100}, γ ∈ {scale, 0,03, 0,3} |
| LightGBM | 92,9 | 93,1 | `num_leaves` ∈ {15, 31, 63}, `learning_rate` ∈ {0,03, 0,1} |

Giá trị mặc định của Random Forest ở đây (92,9%) khác con số 93,1% ở E1 vì E6 chỉ dùng lần lặp CV đầu tiên, còn E1 lấy trung bình 5 lần lặp.

## E6: tham số được chọn ở từng fold vòng ngoài

| Mô hình | Fold 1 | Fold 2 | Fold 3 | Fold 4 | Fold 5 |
|---|---|---|---|---|---|
| Random Forest | √p, lá 5 | √p, lá 1 | 0,5, lá 5 | √p, lá 2 | √p, lá 5 |
| SVM (RBF) | C 1, γ scale | C 1, γ 0,03 | C 1, γ 0,3 | C 1, γ scale | C 1, γ 0,3 |
| LightGBM | lr 0,1, 31 lá | lr 0,1, 31 lá | lr 0,03, 15 lá | lr 0,1, 15 lá | lr 0,1, 63 lá |

## E6: diễn giải

- **Tinh chỉnh gần như không giúp** (tối đa 0,5 điểm), nằm gọn trong độ bất định của phép so sánh E1.
- **SVM chọn C = 1 ở cả 5 fold,** tức biên quyết định trơn hơn, ít phức tạp hơn mặc định (C = 10) lại tổng quát hóa qua không gian tốt hơn chút ít.
- **Random Forest và LightGBM chọn tham số khác nhau ở mỗi fold** mà không có lợi ích gì, dấu hiệu bề mặt độ chính xác rất phẳng.
- Vì vậy bản đồ chính giữ Random Forest mặc định (300 cây, `min_samples_leaf=2`, trọng số lớp cân bằng).
