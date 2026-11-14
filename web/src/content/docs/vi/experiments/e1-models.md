---
title: "E1: So sánh 14 mô hình"
description: Mười bốn bộ phân loại được so sánh trên cùng đặc trưng SAR và cùng các fold khối không gian 5 km; 11 mô hình đứng đầu không khác nhau có ý nghĩa, quanh 93% độ chính xác cân bằng lớp.
sidebar:
  order: 1
---

**Câu hỏi.** Việc chọn mô hình học máy có ảnh hưởng tới phân loại lớp phủ chỉ từ SAR ở Hưng Yên không?

**Trả lời ngắn.** Không đáng kể. 11 trong 14 mô hình đạt độ chính xác cân bằng lớp (BA) 93,0–93,6% trên ô thuần, khoảng tin cậy chồng lên nhau. Hồi quy logistic đơn giản (93,3%) ngang các mô hình cây phức tạp. Chỉ LDA và cây quyết định độ sâu 4 kém rõ rệt.

## Thiết lập E1

- **Dữ liệu:** 3.918 mẫu ô 20 m thuần, 12 đặc trưng SAR (xem [Tổng quan thí nghiệm](/vi/experiments/)).
- **Kiểm chứng:** kiểm tra chéo 5 fold theo khối không gian 5×5 km, lặp 5 lần; mọi mô hình dùng đúng cùng các fold.
- **Siêu tham số:** giá trị mặc định hợp lý, không tinh chỉnh trên các fold đánh giá (tinh chỉnh được thử riêng ở [E6](/vi/experiments/e6-tuning/)).
- **Độ bất định:** khoảng tin cậy (CI) 95% bằng bootstrap theo khối (lấy lại 2.000 lần các khối 5 km) trên lần lặp đầu. Hiệu so với Random Forest (ΔBA) tính trên cùng các mẫu bootstrap.

## Bảng kết quả E1

![E1: độ chính xác cân bằng lớp của 14 mô hình với khoảng tin cậy 95%](/figures/vi/E1_models.png)

| Mô hình | BA (CI 95%) | OA | F1 macro | kappa | F1 Nước | F1 Thực vật | F1 Đất trống | F1 Đô thị |
|---|---|---|---|---|---|---|---|---|
| SVM (RBF) | **93,6** (91,4–95,8) | 95,6 | 93,5 | 0,933 | 99,5 | 88,4 | 91,4 | 94,7 |
| Extra Trees | 93,3 (91,1–95,6) | 95,3 | 93,2 | 0,929 | 99,4 | 88,6 | 89,5 | 95,3 |
| CatBoost | 93,3 (91,4–95,6) | 95,3 | 93,1 | 0,929 | 99,5 | 88,1 | 89,6 | 95,3 |
| Hồi quy logistic | 93,3 (91,2–95,4) | 95,3 | 93,2 | 0,929 | 99,3 | 89,1 | 89,8 | 94,8 |
| MLP (64-32) | 93,2 (91,8–95,4) | 95,5 | 93,4 | 0,931 | 99,4 | 89,0 | 90,2 | 94,7 |
| Random Forest | 93,1 (90,5–95,0) | 95,3 | 93,1 | 0,929 | 99,5 | 88,1 | 89,6 | 95,1 |
| Maximum Likelihood (QDA) | 93,1 (91,5–94,4) | 94,6 | 92,7 | 0,918 | 98,4 | 88,9 | 88,1 | 95,3 |
| k-NN (k=15) | 93,1 (91,0–94,8) | 95,3 | 93,3 | 0,929 | 99,2 | 88,8 | 90,1 | 95,1 |
| XGBoost | 93,1 (90,7–95,0) | 95,2 | 93,0 | 0,928 | 99,5 | 87,8 | 89,7 | 94,9 |
| LightGBM | 93,0 (90,5–95,0) | 95,2 | 92,9 | 0,927 | 99,6 | 87,5 | 89,6 | 95,0 |
| HistGradientBoosting | 93,0 (90,9–95,2) | 95,1 | 92,8 | 0,926 | 99,5 | 87,6 | 89,7 | 94,6 |
| LDA | 90,2 (87,4–93,1) | 93,5 | 90,7 | 0,900 | 98,6 | 85,6 | 85,2 | 93,3 |
| Cây quyết định (sâu 4) | 88,9 (84,9–90,8) | 92,0 | 88,7 | 0,879 | 98,4 | 83,3 | 83,3 | 89,9 |
| Mốc: luôn đoán lớp đông nhất | 25,0 | 51,3 | 17,0 | 0,000 | 67,8 | 0 | 0 | 0 |

BA, OA (độ chính xác tổng) và F1 tính bằng %; BA, OA, F1 và kappa là trung bình qua 5 lần lặp; CI từ bootstrap theo khối trên lần lặp đầu.

## E1: hiệu so với Random Forest

| Mô hình | ΔBA so với Random Forest (CI 95%) | McNemar p |
|---|---|---|
| SVM (RBF) | +0,7 (−0,1 đến +1,7) | 0,080 |
| Extra Trees | +0,5 (+0,0 đến +1,1) | 0,155 |
| CatBoost | +0,7 (+0,2 đến +1,3) | 0,009 |
| Hồi quy logistic | +0,4 (−0,7 đến +1,5) | 0,399 |
| MLP (64-32) | +0,8 (−0,4 đến +2,0) | 0,005 |
| Maximum Likelihood (QDA) | +0,1 (−1,3 đến +1,7) | 0,144 |
| k-NN (k=15) | +0,1 (−1,0 đến +1,2) | 0,589 |
| XGBoost | +0,1 (−0,4 đến +0,6) | 1 |
| LightGBM | −0,0 (−0,7 đến +0,7) | 1 |
| HistGradientBoosting | +0,3 (−0,3 đến +1,0) | 0,556 |
| LDA | −2,6 (−4,2 đến −1,0) | 1,6 × 10⁻⁶ |
| Cây quyết định (sâu 4) | −4,8 (−6,6 đến −3,1) | 5,7 × 10⁻²³ |

ΔBA tính trên lần lặp đầu, nên có thể hơi khác hiệu của trung bình 5 lần lặp ở bảng trên. Giá trị p của McNemar **lạc quan** vì các ô gần nhau tương quan không gian, không độc lập; khoảng tin cậy bootstrap theo khối là thước đo trung thực hơn.

## E1: các lớp hay bị nhầm

![E1: ma trận nhầm của 4 mô hình đứng đầu](/figures/vi/E1_confusion_top4.png)

- **Thực vật ↔ Đất trống** là nhầm lẫn chính ở mọi mô hình, khoảng 6–9% mỗi chiều. Cả hai đều là bề mặt nông nghiệp có backscatter L-band chồng lấn (ruộng vừa gặt, cây thưa, đất ẩm).
- **Đô thị bị đoán thành Thực vật** đứng thứ hai (3–5%), nhiều khả năng là làng có cây.
- **Nước gần như không bị nhầm** (F1 khoảng 99%): mặt nước lặng rất tối ở cả HH và HV.

## E1: chi phí huấn luyện

Mỗi lần huấn luyện trên khoảng 3.100 mẫu: từ 0,003 s (LDA) đến 6,5 s (HistGradientBoosting); Random Forest 0,4 s, SVM 0,05 s, XGBoost 2,0 s, LightGBM 4,4 s, CatBoost 1,6 s. Mô hình nào cũng rẻ; chi phí không phải lý do để chọn.

## Kết luận E1

- **Chọn mô hình không quan trọng lắm.** 11 mô hình đứng đầu chênh nhau dưới 1 điểm BA và khoảng tin cậy chồng nhau.
- **Dữ liệu gần như tách được tuyến tính** với 12 đặc trưng này: hồi quy logistic tốt ngang gradient boosting.
- **Random Forest được giữ lại** cho bản đồ chính ([Kết quả lớp phủ](/vi/results/landcover/)); SVM cũng là lựa chọn hợp lý như vậy.
- Mười mô hình được dùng lại ở [E7](/vi/experiments/e7-map-agreement/) để đo mức trùng khớp giữa các *bản đồ*.
