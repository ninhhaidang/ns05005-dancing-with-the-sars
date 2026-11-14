---
title: "E7: Các mô hình có cho cùng một bản đồ không?"
description: Mười mô hình huấn luyện trên toàn bộ mẫu và áp dụng cho cả tỉnh đồng ý ở 65,9% diện tích; tỷ lệ diện tích tương tự nhau nhưng chưa được kiểm chứng.
sidebar:
  order: 7
---

**Câu hỏi.** Các mô hình có điểm số như nhau trên mẫu kiểm tra ([E1](/vi/experiments/e1-models/)) vẫn có thể vẽ ra bản đồ khác nhau. Bản đồ lớp phủ của các mô hình trùng nhau đến đâu, và tỷ lệ diện tích ổn định đến đâu?

**Trả lời ngắn.** Cả 10 mô hình cho cùng một lớp ở **65,9%** AOI; chỉ 3,0% số ô có từ 5 mô hình trở xuống đồng ý với lớp đa số. Tỷ lệ diện tích khá ổn định (Đô thị 22–26%, Đất trống 39–47%, không tính LDA), nhưng **ổn định không có nghĩa là đúng**: mọi mô hình học từ cùng một bộ nhãn.

## Thiết lập E7

- **Mô hình (10):** Random Forest, Extra Trees, HistGradientBoosting, XGBoost, LightGBM, CatBoost, MLP (64-32), hồi quy logistic, LDA, Maximum Likelihood (QDA).
- **Huấn luyện:** mỗi mô hình học trên toàn bộ 3.918 mẫu rồi dự đoán toàn bộ 6,43 triệu ô 20 m của AOI (2.571,7 km²).
- **Đầu ra:** tỷ lệ diện tích của từng mô hình, ma trận trùng khớp từng cặp, **bản đồ đồng thuận** (lớp đa số trong 10 mô hình) và **mức đồng thuận** (số mô hình bầu cho lớp đa số, từ 3 đến 10).

## E7: tỷ lệ diện tích theo mô hình

![E7: tỷ lệ diện tích dự đoán của từng lớp theo mô hình](/figures/vi/E7_area_by_model.png)

| Mô hình | Nước | Thực vật | Đất trống | Đô thị |
|---|---|---|---|---|
| Random Forest | 5,1 | 25,1 | 45,7 | 24,1 |
| Extra Trees | 5,0 | 27,8 | 44,8 | 22,4 |
| HistGradientBoosting | 5,9 | 26,0 | 42,4 | 25,7 |
| XGBoost | 5,5 | 26,3 | 43,2 | 25,0 |
| LightGBM | 5,8 | 25,9 | 43,3 | 25,0 |
| CatBoost | 5,2 | 25,1 | 44,4 | 25,3 |
| MLP (64-32) | 6,2 | 22,6 | 46,5 | 24,8 |
| Hồi quy logistic | 5,1 | 27,5 | 44,4 | 23,0 |
| LDA | 6,3 | 33,2 | 44,8 | 15,7 |
| Maximum Likelihood (QDA) | 6,2 | 29,1 | 38,7 | 25,9 |
| **Đồng thuận (lớp đa số)** | **5,6** | **26,8** | **43,6** | **24,0** |

Các số là % diện tích AOI theo dự đoán (đếm pixel), **chưa hiệu chỉnh và chưa kiểm chứng**. Khoảng dao động giữa 10 mô hình: Nước 5,0–6,3%, Thực vật 22,6–33,2%, Đất trống 38,7–46,5%, Đô thị 15,7–25,9%.

## E7: mức đồng thuận giữa các mô hình

![E7: bản đồ số mô hình đồng ý với lớp đa số](/figures/vi/E7_agreement_map.png)

| Số mô hình đồng ý với lớp đa số | 10 | 9 | 8 | 7 | 6 | 5 | 4 | 3 |
|---|---|---|---|---|---|---|---|---|
| Tỷ lệ AOI | 65,86% | 15,45% | 6,63% | 4,73% | 4,36% | 2,71% | 0,26% | < 0,01% |

![E7: mức trùng khớp từng cặp mô hình](/figures/vi/E7_pairwise_agreement.png)

- **Các mô hình cây và boosting trùng nhau ở 88,7–96,8% số ô** (cao nhất: XGBoost–LightGBM 96,8%, Random Forest–Extra Trees 95,3%).
- **LDA và QDA lệch khỏi nhóm:** chỉ trùng với các mô hình khác ở 78,8–85,6% (LDA) và 83,5–85,0% (QDA) số ô, và trùng nhau ở 75,5%.

## E7: diễn giải

- **Bản đồ vững ở nơi các mô hình đồng ý.** Hai phần ba diện tích tỉnh nhận cùng một lớp từ mọi mô hình.
- **Tỷ lệ diện tích ổn định nhưng chưa kiểm chứng.** Tỷ lệ Đô thị khoảng 24% có vẻ cao với một tỉnh đồng bằng nông nghiệp. Một lý giải khả dĩ là định nghĩa lớp không khớp: nhãn Đô thị là khối nhà dày đặc, còn lớp Đô thị trên bản đồ có thể gồm cả làng có cây. Điều này chưa được đối chiếu với dữ liệu độc lập.
- **Mức đồng thuận đo sự nhất trí giữa các mô hình, không đo độ đúng:** mọi mô hình mang cùng thiên lệch của bộ nhãn.

## Kết quả E7 dùng trên bản đồ web

- `landcover_model_mode.tif`: bản đồ lớp phủ đồng thuận (đa số của 10 mô hình).
- `landcover_model_agreement.tif`: số mô hình đồng ý, hiển thị làm **lớp độ tin cậy** trên [bản đồ tương tác](/vi/map/?view=confidence).

Bản thân lớp lớp phủ chính là bản đồ Random Forest (xem [Kết quả lớp phủ](/vi/results/landcover/)).
