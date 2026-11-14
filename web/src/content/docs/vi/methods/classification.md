---
title: Phương pháp phân loại lớp phủ
description: Cách bộ phân loại Random Forest chỉ dùng SAR lập bản đồ Nước, Thực vật, Đất trống và Đô thị ở 20 m từ 12 đặc trưng NISAR.
sidebar:
  order: 3
---

Bản đồ lớp phủ gán mỗi ô 20 m trong AOI Hưng Yên vào một trong bốn lớp, **Nước, Thực vật, Đất trống, Đô thị**, chỉ dùng **đặc trưng radar NISAR** của ba ngày. Dữ liệu quang học chỉ dùng để vẽ nhãn huấn luyện. Mô hình chính là Random Forest. Code: `scripts/sar_dataset.py` (đặc trưng và mẫu), `scripts/train_classifier.py` (mô hình chính và bản đồ), `scripts/experiments.py` (các thí nghiệm so sánh).

## Các lớp của bản đồ lớp phủ SAR

| Mã | Lớp | Hành vi radar điển hình (băng L) |
|---|---|---|
| 1 | Nước | Rất tối ở cả HH và HV: mặt nước lặng phản xạ tín hiệu đi chỗ khác (phản xạ gương). |
| 2 | Thực vật | HH trung bình, HV tương đối cao: lá và thân cây tán xạ tín hiệu ra nhiều hướng (tán xạ khối), tạo ra phản hồi phân cực chéo (HV). |
| 3 | Đất trống | HV thấp hơn thực vật; HH phụ thuộc độ nhám và độ ẩm đất. |
| 4 | Đô thị | HH rất sáng: tường nhà và mặt đất tạo thành gương góc (tán xạ hai lần, double-bounce). Độ sáng phụ thuộc hướng của nhà so với hướng nhìn radar. |

Mã 0 trong raster bản đồ là ngoài AOI.

## 12 đặc trưng SAR cho mỗi ô 20 m

Mọi đặc trưng được tính trên lưới 20 m từ tán xạ HH và HV đơn vị dB, sau khi ảnh 10 m ngày 27/10 đã được lấy trung bình về 20 m. Mỗi lớp dB theo ngày được làm trơn bằng bộ lọc trung bình 3 × 3 (60 m) để giảm speckle. Xem [Tiền xử lý](/vi/methods/preprocessing/).

| # | Đặc trưng | Định nghĩa |
|---|---|---|
| 1–3 | HH_1022, HH_1027, HH_1103 | HH (dB, đã làm trơn) ngày 22/10, 27/10, 3/11 |
| 4–6 | HV_1022, HV_1027, HV_1103 | HV (dB, đã làm trơn) ba ngày tương ứng |
| 7 | HH trung bình | Trung bình ba giá trị HH (dB) |
| 8 | HV trung bình | Trung bình ba giá trị HV (dB) |
| 9 | HV − HH | Tỷ số phân cực chéo: HV trung bình trừ HH trung bình (dB) |
| 10 | Độ lệch chuẩn HH | Độ lệch chuẩn của HH qua ba ngày (dB) |
| 11 | Độ lệch chuẩn HV | Độ lệch chuẩn của HV qua ba ngày (dB) |
| 12 | Kết cấu | Độ lệch chuẩn cục bộ của HH trung bình trong cửa sổ 7 × 7 (140 m) |

- **Lưu ý về hướng nhìn:** 27/10 là ảnh bay lên còn hai ngày kia bay xuống. Vì vậy các đặc trưng "độ lệch chuẩn qua ba ngày" trộn lẫn thay đổi thật với khác biệt do hướng nhìn (ví dụ nhà cửa nhìn từ hai phía đối diện trông khác nhau).

## Mẫu huấn luyện cho bộ phân loại

- **Nguồn:** 1.347 [polygon nhãn](/vi/data/labels/).
- **Ô thuần:** một ô 20 m là mẫu nếu ≥ 80% diện tích (đo bằng siêu lấy mẫu 8 × 8) thuộc một lớp.
- **Giới hạn:** tối đa 20 ô mỗi polygon, chọn ngẫu nhiên (seed 0).
- **Kết quả:** **3.918 mẫu** từ 864 polygon: Nước 2.011, Thực vật 622, Đất trống 660, Đô thị 625. Mẫu có đặc trưng không hữu hạn bị loại.

## Mô hình Random Forest

- **Mô hình:** `RandomForestClassifier` của scikit-learn với **300 cây**, `min_samples_leaf = 2`, `class_weight = "balanced"` (để lớp Nước đông mẫu không lấn át), `random_state = 0`.
- **Vì sao chọn Random Forest:** bền và nhanh (khoảng 0,4 giây mỗi lần huấn luyện trên khoảng 3.100 mẫu). Khi so sánh mô hình, 11 trên 14 mô hình đạt độ chính xác cân bằng 93,0–93,6% với kiểm tra chéo theo khối không gian và không mô hình nào tốt hơn Random Forest (93,1%) một cách đáng kể; SVM cao nhất với 93,6%. Tinh chỉnh siêu tham số thay đổi kết quả dưới 0,5 điểm.
- **Bản đồ cuối:** mô hình được huấn luyện trên toàn bộ 3.918 mẫu rồi dự đoán cả 6,43 triệu ô AOI, mỗi lượt 1 triệu ô.
- **Đặc trưng hữu ích nhất (độ quan trọng hoán vị, thí nghiệm E3):** HV ngày 27/10 (độ chính xác cân bằng giảm 6,7 điểm khi bị xáo trộn), độ lệch chuẩn HH (3,9), HV ngày 3/11 (3,2) và HV trung bình (2,3); mọi đặc trưng khác dưới 0,5 điểm.

## Điều gì quyết định độ chính xác

- **Ba ngày là quan trọng nhất:** một ngày cho độ chính xác cân bằng 83–86%; đủ ba ngày cho 93%. Riêng hai ngày bay xuống chỉ đạt 87,0%, nên hướng nhìn khác của ngày 27/10 bổ sung thông tin thật.
- **Cần cả hai phân cực:** chỉ HV 89,4%, chỉ HH 88,9%, cả hai 93,1%.
- **Kết cấu gần như vô dụng:** bỏ đi chỉ mất 0,2 điểm.
- **Nhầm lẫn chính:** Thực vật ↔ Đất trống (khoảng 6–9% mỗi chiều), sau đó là Đô thị bị đoán thành Thực vật (3–5%). Nước gần như không bị nhầm (khoảng 99% đúng).

## Đầu ra lớp phủ

| File | Nội dung |
|---|---|
| `data/derived/landcover_sar_20m.tif` | Bản đồ Random Forest chính (uint8: 0 ngoài AOI, 1 Nước, 2 Thực vật, 3 Đất trống, 4 Đô thị) |
| `data/derived/landcover_model_mode.tif` | Bản đồ đồng thuận: lớp đa số của 10 mô hình khác nhau |
| `data/derived/landcover_model_agreement.tif` | Số mô hình (trên 10) đồng ý với lớp đa số (3–10) |
| `data/derived/aoa_dissimilarity.tif` | Chỉ số khác biệt cho vùng áp dụng được (ngưỡng 0,105) |
| `data/derived/samples_polygon_20m.csv` | Hàng, cột, lớp và mã polygon của từng mẫu huấn luyện |
| `outputs/landcover_sar.png` | Ảnh xem nhanh bản đồ chính |

## Diện tích lớp phủ dự đoán (chưa kiểm chứng)

Tỷ lệ AOI theo bản đồ Random Forest chính: Nước 5,1%, Thực vật 25,1%, Đất trống 45,7%, Đô thị 24,1%. Bản đồ đồng thuận 10 mô hình cho: Nước 5,6%, Thực vật 26,8%, Đất trống 43,6%, Đô thị 24,0%.

:::caution[Diện tích này chưa được kiểm chứng]
Tỷ lệ diện tích chỉ là đếm pixel, chưa phải ước lượng đã hiệu chỉnh sai lệch. Tỷ lệ Đô thị khoảng 24% có vẻ cao với một tỉnh nông nghiệp đồng bằng; một cách giải thích có thể là làng có nhiều cây bị xếp vào Đô thị trong khi nhãn chỉ đánh dấu khối nhà dày đặc. Điều này chưa được kiểm tra. Đô thị là lớp kém tin cậy nhất: 23,5% số ô dự đoán là Đô thị nằm ngoài vùng áp dụng được của mô hình.
:::

![Bản đồ lớp phủ chỉ từ SAR (Nước / Thực vật / Đất trống / Đô thị)](/figures/common/landcover_sar.png)

Xem [chế độ lớp phủ](/vi/?view=landcover) và [chế độ độ tin cậy](/vi/?view=confidence) trên bản đồ tương tác, và [Kiểm chứng](/vi/methods/validation/) để biết con số 93% được đo thế nào.

## Hậu xử lý bản đồ lớp phủ

Bản đồ Random Forest gốc dự đoán từng pixel riêng lẻ nên có nhiễu hạt tiêu. Bản đồ web dùng một phiên bản đã làm trơn bằng bộ lọc đa số (modal) để giảm các pixel lẻ loi. Việc làm trơn này chỉ để hiển thị: ảnh hưởng của nó tới độ chính xác chưa được đo.
