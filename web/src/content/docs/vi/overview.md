---
title: Tổng quan dự án
description: Dự án Dancing with the SARs làm gì, ở đâu, dùng dữ liệu nào và tìm thấy gì.
sidebar:
  order: 1
---

**Dancing with the SARs** là bài dự thi của đội **2936-ThanhNoi** (mã đội **NS05005**: Ninh Hải Đăng, trưởng nhóm; Phạm Minh Quang; Lê Toàn Thắng) cho thử thách cùng tên tại NASA Space Apps Challenge 2026. Xem [Đội thi](/vi/team/). Nhóm dùng ảnh radar băng L của vệ tinh NISAR để trả lời hai câu hỏi về tỉnh Hưng Yên ở đồng bằng sông Hồng: *cuối tháng 10/2026, việc điều tiết nước đã làm bề mặt đất thay đổi ở đâu*, và *có lập được bản đồ lớp phủ chỉ từ radar khi vệ tinh quang học bị mây che không?*

:::tip[Xem kết quả]
Mở [bản đồ tương tác](/vi/map/?view=overview) để xem ảnh radar ba ngày, các vùng thay đổi và bản đồ lớp phủ kèm các lớp độ tin cậy. Bạn cũng có thể [hỏi trợ lý AI](/vi/chat/) bất kỳ câu nào về dự án.
:::

## Thử thách Dancing with the SARs

Thử thách *Dancing with the SARs* của Space Apps 2026 (chủ đề Khoa học Trái Đất, mức trung bình đến nâng cao) yêu cầu xây dựng một ứng dụng tương tác, mã nguồn mở, dùng dữ liệu radar của sứ mệnh NASA–ISRO **NISAR** để theo dõi và trực quan hóa thay đổi bề mặt Trái Đất, chẳng hạn hoạt động nông nghiệp, ngập lụt hay mất đất ngập nước. Mỗi đội tự chọn khu vực, tải dữ liệu NISAR miễn phí (có thể thêm ảnh quang học hoặc lớp GIS làm bối cảnh), trình bày kết quả dưới dạng số tương tác và đưa ra giả thuyết về nguyên nhân vật lý của những gì thấy, hoặc không thấy, trong dữ liệu SAR. SAR (radar khẩu độ tổng hợp) tự phát xung vi ba rồi đo tín hiệu phản hồi, nên chụp được cả ngày lẫn đêm và xuyên qua mây. SAR rất nhạy với độ nhám và độ ẩm bề mặt, nhờ đó mặt nước hiện lên rõ.

Dự án dùng sản phẩm **GCOV** của NISAR (mức 2, đã nắn hình học và hiệu chỉnh địa hình) ở mức hoàn thiện **VALIDATED** (phiên bản xử lý CRID P05036), có từ ngày 21/10/2026.

## Khu vực nghiên cứu: tỉnh Hưng Yên mới

- **Vị trí:** tỉnh Hưng Yên, miền Bắc Việt Nam, nằm giữa đồng bằng sông Hồng bằng phẳng, canh tác dày đặc.
- **"Mới" nghĩa là gì:** trong đợt sáp nhập hành chính năm 2025, tỉnh Hưng Yên cũ và tỉnh Thái Bình cũ hợp nhất thành một tỉnh mang tên Hưng Yên. Vùng nghiên cứu (AOI) là ranh giới của tỉnh sau sáp nhập.
- **Diện tích:** ranh giới AOI có diện tích hình học **2.571,7 km²** (6,43 triệu ô 20 m × 20 m trên lưới UTM 48N). File ranh giới còn ghi diện tích hành chính chính thức 2.514,81 km². Hai con số đến từ hai nguồn khác nhau và chưa được đối chiếu. Xem [Vùng nghiên cứu](/vi/data/aoi/).
- **Cảnh quan:** ruộng lúa, ruộng màu và cây ăn quả, ao nuôi cá và tôm, làng xóm dày đặc có cây xanh bao quanh, thị trấn, sông, kênh mương và đê. Mực nước trong ruộng và ao do người dân chủ động điều tiết.

## Vì sao dùng radar: mây che phủ đồng bằng

- **Mây trong khoảng thời gian nghiên cứu:** từ 22/10 đến 3/11/2026 không có ngày Sentinel-2 nào đủ sạch. Ngay cả ảnh tổng hợp trung vị 12 ngày đã lọc mây cũng chỉ có ít nhất một lần quan sát sạch trên **khoảng 32% AOI**. Xem [Sentinel-2](/vi/data/sentinel2/).
- **Dynamic World** (sản phẩm lớp phủ gần thời gian thực của Google, tạo từ Sentinel-2) chỉ phủ **6,2% AOI** trong cùng khoảng ngày, nên không dùng được.
- **Radar xuyên mây:** cả ba lần chụp NISAR đều phủ 100% AOI.

## Hai câu hỏi nghiên cứu

1. **Phát hiện thay đổi do điều tiết nước.** Giữa hai ảnh radar cùng quỹ đạo (22/10 và 3/11/2026), những chỗ nào thay đổi có ý nghĩa thống kê, và các thay đổi đó có giống ruộng, ao hay khu đê bao được cho nước vào hoặc tháo nước ra không? Phương pháp: kiểm định thống kê log tỷ số có tính đến nhiễu speckle của radar. Xem [Phương pháp phát hiện thay đổi](/vi/methods/change-detection/).
2. **Lớp phủ 4 lớp chỉ từ SAR.** Có phân loại được từng ô 20 m thành **Nước, Thực vật, Đất trống, Đô thị** chỉ bằng tán xạ ngược HH và HV của NISAR trong ba ngày không, để bản đồ phủ được cả khoảng 68% diện tích tỉnh bị mây che? Xem [Phương pháp phân loại](/vi/methods/classification/).

## Dữ liệu sử dụng (chỉ từ 22/10 đến 3/11/2026)

| Dữ liệu | Vai trò | Chi tiết |
|---|---|---|
| NISAR GCOV VALIDATED, tần số A | Đầu vào chính | 22/10 (track 148 xuống, 20 m), 27/10 (track 054 lên, 10 m), 3/11 (track 148 xuống, 20 m). Phân cực HH và HV. Xem [Dữ liệu NISAR](/vi/data/nisar/). |
| Ảnh tổng hợp phản xạ bề mặt Sentinel-2 | Chỉ để vẽ nhãn | Trung vị 10 m 22/10–3/11, lọc mây bằng Cloud Score+. **Không đưa vào mô hình.** |
| Polygon nhãn | Nhãn huấn luyện | 1.347 hình chữ nhật do nhóm vẽ: Nước 190, Thực vật 485, Đất trống 444, Đô thị 228. Xem [Nhãn](/vi/data/labels/). |
| Ranh giới AOI | Cắt dữ liệu | Tỉnh Hưng Yên sau sáp nhập, MultiPolygon 8 mảnh. |

Ảnh ngày 29/10 (track 076) bị loại vì chỉ phủ 4% AOI. Dự án không dùng sản phẩm PROVISIONAL và không dùng dữ liệu ngoài khoảng 22/10–3/11/2026.

## Kết quả chính và các lưu ý

### Kết quả phát hiện thay đổi (22/10 → 3/11/2026)

- **99,89% AOI không có thay đổi có ý nghĩa thống kê** trong 12 ngày này (ngưỡng |z| > 5 ở cả HH và HV, mảng ≥ 0,05 km²).
- **Tín hiệu đáng kể duy nhất là một cụm nước mới khoảng 1,6 km²** quanh 106,48°E, 20,46°N, cạnh một khúc sông ở phía đông nam tỉnh. Tán xạ HH giảm từ khoảng −10 xuống −16 dB, HV từ khoảng −17 xuống −23 dB, và đã giảm từ ngày 27/10. Khu này có dạng khối chữ nhật, điển hình của ruộng hoặc ao có bờ bao.
- **Nguyên nhân chưa kiểm chứng:** giả thuyết là ruộng, ao hoặc một khu đê bao được chủ động cho nước vào, nhưng mây che nên không có ảnh quang học nào để xác nhận. Xem [Kết quả thay đổi](/vi/results/change/) và [chế độ xem thay đổi trên bản đồ](/vi/map/?view=change).
- **Không thấy tín hiệu thu hoạch lúa** trong 12 ngày; phần lớn lúa có vẻ đã gặt trước 22/10.

### Kết quả lớp phủ (chỉ SAR, 4 lớp)

- **Độ chính xác cân bằng lớp (BA) khoảng 93%** với Random Forest (SVM 93,6%) khi kiểm tra chéo theo khối không gian 5 km. Mốc so sánh luôn đoán lớp đông nhất chỉ đạt 25%.
- **Lưu ý quan trọng:** con số 93% đo trên **ô 20 m thuần**, tức ô nằm trọn trong một hình chữ nhật nhãn. Đây **không phải** độ chính xác của toàn bản đồ, vốn còn gồm ô lẫn lớp và vùng xa nhãn. Độ chính xác ở mức bản đồ hiện chưa biết.
- **Không có tập kiểm tra độc lập:** đã chuẩn bị tập kiểm tra mù gồm 250 ô ngẫu nhiên (`labeling/blind_test_cells.gpkg`) nhưng chưa chấm nhãn, và nhóm đã quyết định không chấm.
- **Diện tích chưa kiểm chứng:** bản đồ đồng thuận xếp khoảng 24% AOI vào Đô thị và khoảng 44% vào Đất trống. Các tỷ lệ này chưa hiệu chỉnh sai lệch. Đô thị là lớp kém tin cậy nhất: 23,5% số ô dự đoán là Đô thị nằm ngoài vùng áp dụng được của mô hình.
- **Yếu tố quyết định:** dùng đủ ba ngày và cả hai phân cực. Chọn mô hình nào gần như không quan trọng (11 trên 14 mô hình chênh nhau dưới 1 điểm).
- Xem [Phương pháp phân loại](/vi/methods/classification/), [Kiểm chứng](/vi/methods/validation/), cùng các chế độ xem [lớp phủ](/vi/map/?view=landcover) và [độ tin cậy](/vi/map/?view=confidence) trên bản đồ.

## Đọc tiếp

- [Dữ liệu NISAR](/vi/data/nisar/), [Vùng nghiên cứu](/vi/data/aoi/), [Sentinel-2](/vi/data/sentinel2/), [Nhãn](/vi/data/labels/)
- [Tiền xử lý](/vi/methods/preprocessing/), [Phát hiện thay đổi](/vi/methods/change-detection/), [Phân loại](/vi/methods/classification/), [Kiểm chứng](/vi/methods/validation/)
- [Cách tái tạo kết quả](/vi/reproduce/), [Thuật ngữ](/vi/glossary/)
