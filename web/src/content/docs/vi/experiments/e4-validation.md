---
title: "E4: Cách kiểm chứng và rò rỉ không gian"
description: Cùng một mô hình được chấm theo 12 cách chia train/test, cho thấy chia ngẫu nhiên thổi phồng độ chính xác, độ chính xác giảm theo khoảng cách tới nhãn, và vì sao 93% không phải độ chính xác bản đồ.
sidebar:
  order: 4
---

**Câu hỏi.** Cách chia dữ liệu huấn luyện và kiểm tra làm thay đổi độ chính xác báo cáo bao nhiêu, và mô hình lớp phủ đáng tin ở khoảng cách bao xa so với vùng có nhãn?

**Trả lời ngắn.** Chia ngẫu nhiên theo ô thổi phồng độ chính xác cân bằng lớp (BA) khoảng 3 điểm (95,9% so với 93,1% với Random Forest). Khối không gian lớn hơn làm BA giảm chậm (91,4% với khối 20 km). Chia tỉnh làm đôi làm BA tụt còn 83–87%, một phần do nhãn phân bố lệch. 44% AOI cách mọi nhãn trên 2 km, nơi BA trên ô thuần khoảng 90%.

## Thiết lập E4

- **Dữ liệu và đặc trưng:** cùng 3.918 mẫu thuần và 12 đặc trưng SAR như [E1](/vi/experiments/e1-models/).
- **Mô hình:** Random Forest (mô hình chính), LightGBM, SVM (RBF), hồi quy logistic.
- **Các cách chia:** ngẫu nhiên theo ô, theo polygon, khối không gian 1, 2, 5, 10 và 20 km, khối 5 km kèm vùng đệm 250 m hoặc 1 km, và ba cách chia vùng (Tây/Đông, Bắc/Nam, 4 góc phần tư).
- **Vùng đệm:** bỏ các ô huấn luyện cách ô kiểm tra gần nhất dưới khoảng đệm. Việc này chặn rò rỉ qua cửa sổ làm trơn 3×3 (60 m) và kết cấu 7×7 (140 m) ở ranh giới khối.
- **Khoảng cách:** với mỗi ô kiểm tra, khoảng cách tới ô huấn luyện gần nhất; bảng ghi trung vị.

## Kết quả E4 theo cách kiểm chứng

![E4: độ chính xác cân bằng lớp theo từng cách kiểm chứng](/figures/vi/E4_validation_schemes.png)

| Cách chia train/test | Khoảng cách test → train (trung vị) | Random Forest | LightGBM | SVM | Hồi quy logistic |
|---|---|---|---|---|---|
| Ngẫu nhiên theo ô (rò rỉ) | 20 m | 95,9 | 96,8 | 96,2 | 94,5 |
| Theo polygon | 300 m | 94,1 | 94,4 | 94,4 | 93,5 |
| Khối 1 km | 501 m | 94,2 | 94,6 | 94,4 | 93,6 |
| Khối 2 km | 800 m | 93,4 | 93,6 | 93,9 | 93,3 |
| **Khối 5 km (chính)** | 1.686 m | **93,1** | 92,9 | 93,6 | 93,3 |
| Khối 5 km + vùng đệm 250 m | 1.920 m | 93,1 | 93,2 | 93,6 | 93,4 |
| Khối 5 km + vùng đệm 1 km | 2.500 m | 92,8 | 93,0 | 93,4 | 92,8 |
| Khối 10 km | 2.925 m | 92,3 | 92,4 | 93,4 | 91,5 |
| Khối 20 km | 4.099 m | 91,4 | 92,3 | 93,2 | 91,4 |
| Chia Tây / Đông | 18,7 km | 87,0 | 86,2 | 83,0 | 86,1 |
| Chia Bắc / Nam | 17,9 km | 83,8 | 82,9 | 85,7 | 86,5 |
| 4 góc phần tư | 15,0 km | 90,4 | 91,3 | 92,4 | 90,5 |

Mọi giá trị là BA (%).

## E4: rò rỉ không gian

- **Chia ngẫu nhiên theo ô cho kết quả lạc quan.** Ô kiểm tra chỉ cách ô huấn luyện cùng polygon 20 m, nên mô hình thực chất được kiểm tra trên gần như bản sao của dữ liệu học. BA cao hơn khoảng 3 điểm so với khối 5 km.
- **Chia theo polygon vẫn lạc quan khoảng 1 điểm,** vì polygon cùng lớp được vẽ thành cụm (trung vị 102 m tới polygon cùng lớp gần nhất, xem [E0 ở trang tổng quan](/vi/experiments/#e0-kiểm-tra-phân-bố-không-gian-của-nhãn)).
- **Đặc trưng làm trơn không gây rò rỉ đáng kể qua ranh giới khối:** thêm vùng đệm 250 m, lớn hơn cửa sổ kết cấu 140 m, BA không đổi (93,1%).

## E4: độ chính xác theo kích thước khối và cách chia vùng

- **BA giảm chậm theo kích thước khối**, từ 93,1% (5 km) xuống 91,4% (20 km) với Random Forest. SVM ổn định nhất (93,2% ở khối 20 km).
- **Chia vùng tụt còn 83–87%,** nhưng con số này lẫn với việc nhãn phân bố lệch:

| Lớp | Số mẫu Tây / Đông | Số mẫu Bắc / Nam |
|---|---|---|
| Nước | 1.011 / 1.000 | 655 / 1.356 |
| Thực vật | 209 / 413 | 284 / 338 |
| Đất trống | 308 / 352 | 402 / 258 |
| Đô thị | 431 / 194 | **618 / 7** |

Với chỉ 7 mẫu Đô thị ở nửa nam, mô hình học bằng nửa nam gần như không học được Đô thị. Kết quả chia vùng vì vậy đo cả việc "thiếu một lớp ở một vùng", không thuần là khả năng chuyển giữa các vùng.

## E4: độ chính xác theo khoảng cách tới nhãn gần nhất

BA của Random Forest theo khoảng cách từ mỗi ô kiểm tra tới ô huấn luyện gần nhất:

| Cách chia | < 500 m | 500 m – 2 km | 2 – 5 km | > 5 km |
|---|---|---|---|---|
| Khối 5 km | 98–100% (n = 495) | 93,7% (n = 1.715) | 90,7% (n = 1.629) | 96,7% (n = 79) |
| Khối 20 km | 96,7% (n = 161) | 94,1% (n = 846) | 89,7% (n = 1.222) | 90,9% (n = 1.675) |

Nhóm > 5 km của khối 5 km chỉ có 79 mẫu nên không đáng tin.

![E4: độ chính xác cân bằng lớp theo khoảng cách tới mẫu huấn luyện gần nhất](/figures/vi/E4_accuracy_by_distance.png)

**Phần còn lại của tỉnh cách nhãn bao xa?** Khoảng cách từ mọi ô AOI tới mẫu huấn luyện gần nhất (tính riêng, ngoài `experiments.py`):

| Khoảng cách | < 500 m | 0,5 – 2 km | 2 – 5 km | 5 – 10 km |
|---|---|---|---|---|
| Tỷ lệ ô AOI | 12% | 44% | 32% | 12% |

Vậy **44% AOI cách mọi nhãn trên 2 km.** Ở khoảng cách đó, BA đo trên ô thuần khoảng 90% (89,7–90,9%), thấp hơn con số 93% của toàn bộ kiểm tra chéo.

## Kết luận E4

- **Phải kiểm chứng theo khối không gian.** Chia ngẫu nhiên hay theo polygon đánh giá quá cao độ chính xác khi nhãn tụ cụm.
- **93% không phải độ chính xác bản đồ.** Con số này đo trên ô thuần gần vùng có nhãn; gần một nửa tỉnh ở xa hơn, và ô lẫn lớp (làng có cây, ao nhỏ) hoàn toàn chưa được kiểm tra.
- **Nhãn đa dạng hơn, nhất là Đô thị ở phía nam, sẽ giúp nhiều hơn nhãn cùng kiểu** (xem [E5](/vi/experiments/e5-learning-curve/)). Bản đồ web cho thấy nơi mô hình ngoại suy qua [lớp vùng áp dụng được E8](/vi/experiments/e8-applicability/).
