---
title: Bản đồ lớp phủ chỉ từ SAR
description: Bản đồ lớp phủ 4 lớp của Hưng Yên ở độ phân giải 20 m làm chỉ từ ba ngày ảnh NISAR, kèm tỷ lệ diện tích, lớp độ tin cậy và các lưu ý cần biết khi đọc.
sidebar:
  order: 2
---

Trang này trình bày bản đồ lớp phủ tỉnh Hưng Yên (ranh giới sau sáp nhập 2025, 2.571,7 km²) làm **chỉ từ SAR NISAR**, không dùng dữ liệu quang học nào. Vì SAR nhìn xuyên mây, bản đồ phủ toàn tỉnh, kể cả khoảng 69% diện tích không có ảnh Sentinel-2 sạch nào trong giai đoạn 22/10–3/11/2026. Xem trên [bản đồ tương tác, chế độ lớp phủ](/vi/?view=landcover).

:::caution[Độ chính xác và diện tích chưa được kiểm chứng]
Con số **khoảng 93% là độ chính xác cân bằng lớp trên ô 20 m thuần, kiểm tra chéo theo khối không gian 5 km, không phải độ chính xác của bản đồ này.** Chưa có tập kiểm tra độc lập (tập mù 250 ô đã chuẩn bị nhưng chưa chấm). **Tỷ lệ diện tích dưới đây là đếm pixel, chưa kiểm chứng và chưa hiệu chỉnh.**
:::

## Các lớp lớp phủ

| Lớp | Ý nghĩa trong dự án | Tín hiệu L-band điển hình |
|---|---|---|
| 1 Nước | Sông, ao, khu nuôi trồng thủy sản, ruộng ngập | Rất tối ở HH và HV (bề mặt phẳng, phản xạ gương) |
| 2 Thực vật | Cây trồng, cây xanh, vườn, cỏ | HV tương đối sáng (tán xạ khối) |
| 3 Đất trống | Ruộng đã gặt hoặc đã cày, đất trống | HH trung bình, HV tối hơn |
| 4 Đô thị | Nhà cửa dày đặc, thị trấn, làng | HH rất sáng (tán xạ hai lần giữa tường và mặt đất) |

Nhãn được vẽ thành hình chữ nhật trên ảnh tổng hợp Sentinel-2 (xem [Nhãn](/vi/data/labels/)); nhãn "Đô thị" là các khối nhà dày đặc.

## Bản đồ lớp phủ được làm thế nào

- **Đầu vào:** 12 đặc trưng trên mỗi ô 20 m từ NISAR GCOV (VALIDATED) ngày 22/10, 27/10 và 3/11/2026: HH và HV từng ngày, giá trị trung bình, HV − HH, độ lệch chuẩn theo thời gian và kết cấu. Xem [Phương pháp phân loại](/vi/methods/classification/).
- **Mô hình:** Random Forest (300 cây, `min_samples_leaf=2`, trọng số lớp cân bằng) huấn luyện trên toàn bộ 3.918 mẫu ô thuần từ 864 polygon nhãn.
- **Vì sao chọn Random Forest:** [so sánh mô hình E1](/vi/experiments/e1-models/) cho thấy 11 mô hình chênh nhau dưới 1 điểm; Random Forest bền, nhanh và được giữ lại.

## Tỷ lệ diện tích các lớp (chưa kiểm chứng)

| Lớp | Bản đồ Random Forest, km² | Bản đồ Random Forest, % AOI | Đồng thuận 10 mô hình, % AOI |
|---|---|---|---|
| Nước | 130,5 | 5,1% | 5,6% |
| Thực vật | 646,3 | 25,1% | 26,8% |
| Đất trống | 1.174,5 | 45,7% | 43,6% |
| Đô thị | 620,4 | 24,1% | 24,0% |

Diện tích là số ô 20 m (mỗi ô 400 m²) trên bản đồ Random Forest gốc; cột đồng thuận là lớp đa số của 10 mô hình trong [E7](/vi/experiments/e7-map-agreement/). Giữa 10 mô hình đó, tỷ lệ dao động: Nước 5,0–6,3%, Thực vật 22,6–33,2%, Đất trống 38,7–46,5%, Đô thị 15,7–25,9%.

**Cách đọc các con số này.** Tỷ lệ ổn định giữa các mô hình, nhưng mọi mô hình học từ cùng một bộ nhãn. Tỷ lệ Đô thị gần 24% có vẻ cao với một tỉnh đồng bằng nông nghiệp. Một lý giải hợp lý nhưng chưa kiểm tra là làng có cây và vườn bị xếp vào Đô thị. Tỷ lệ Đất trống lớn phù hợp với việc nhiều ruộng lúa đã gặt trước 22/10 (xem [Thu hoạch lúa](/vi/results/rice-harvest/)), nhưng điều này cũng chưa được kiểm chứng.

![Bản đồ lớp phủ chỉ từ SAR (kết quả Random Forest gốc)](/figures/common/landcover_sar.png)

## Bộ phân loại lớp phủ chính xác đến đâu?

Những gì *đã* đo được, chỉ trên ô thuần:

- **Độ chính xác cân bằng lớp khoảng 93%** (Random Forest 93,1%), độ chính xác tổng khoảng 95%, kappa khoảng 0,93 với CV khối không gian 5 km ([E1](/vi/experiments/e1-models/)).
- **F1 từng lớp (Random Forest):** Nước 99,5%, Thực vật 88,1%, Đất trống 89,6%, Đô thị 95,1%. Nhầm lẫn chính là Thực vật ↔ Đất trống (6–9% mỗi chiều).
- **Độ chính xác giảm theo khoảng cách tới nhãn:** khoảng 90% ở 2–5 km, và 44% diện tích tỉnh cách mọi nhãn trên 2 km ([E4](/vi/experiments/e4-validation/)).
- **Chưa đo:** ô lẫn lớp (làng có cây, ao nhỏ, ruộng xen nhà), vốn chiếm phần lớn cảnh quan thật; độ chính xác ở đó chắc chắn thấp hơn.

## Các lớp độ tin cậy trên bản đồ web

Hai lớp cho biết nơi bản đồ lớp phủ đáng tin hơn hay kém hơn ([mở chế độ độ tin cậy](/vi/?view=confidence)):

- **Mức đồng thuận mô hình ([E7](/vi/experiments/e7-map-agreement/)):** số mô hình trong 10 mô hình khác nhau dự đoán lớp đa số. Cả 10 đồng ý ở 65,9% AOI; từ 5 trở xuống ở 3,0%.
- **Vùng áp dụng được ([E8](/vi/experiments/e8-applicability/)):** ô có tín hiệu SAR khác xa mọi mẫu huấn luyện (chỉ số khác biệt > 0,105). 8,3% AOI nằm ngoài, như nhau ở vùng sạch mây và vùng mây.

## Đô thị là lớp kém tin cậy nhất

- **23,5% số ô dự đoán là Đô thị nằm ngoài vùng áp dụng được**, so với 0,7% ở Thực vật và 4,5–4,9% ở Nước và Đất trống ([E8](/vi/experiments/e8-applicability/)).
- **Nhãn Đô thị gần như chỉ có ở phía bắc:** 618 trong 625 mẫu Đô thị nằm ở nửa bắc, 7 mẫu ở nửa nam ([E4](/vi/experiments/e4-validation/)).
- **Đô thị có độ chênh giữa các mô hình lớn nhất** (15,7–25,9% AOI).
- Các ô Đô thị nằm ngoài vùng áp dụng tập trung ở phía bắc và **chưa được đối chiếu với bản đồ nền.**

## Hậu xử lý trên bản đồ web

Bản đồ web hiển thị bản đồ Random Forest sau **lọc đa số 3×3**: mỗi ô nhận lớp xuất hiện nhiều nhất trong chính nó và 8 ô lân cận. Việc này giảm nhiễu hạt tiêu thường gặp khi phân loại từng pixel. **Ảnh hưởng của bước lọc lên độ chính xác chưa được đo**, và tỷ lệ diện tích của bản đồ đã lọc có thể hơi khác bảng trên (tính trên bản đồ gốc).

## Tóm tắt giới hạn của bản đồ lớp phủ

Chưa có kiểm chứng độc lập; độ chính xác chỉ đo trên ô thuần; nhãn tụ cụm và lệch vùng; tỷ lệ diện tích chưa hiệu chỉnh; định nghĩa Đô thị có thể khác nhau giữa nhãn và bản đồ; nhãn vẽ trên ảnh median 12 ngày trong khi mặt đất đang thay đổi (mùa gặt). Danh sách đầy đủ: [Giới hạn](/vi/limitations/).
