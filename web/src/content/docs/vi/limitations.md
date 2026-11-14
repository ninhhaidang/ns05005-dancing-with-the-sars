---
title: Giới hạn
description: Danh sách rõ ràng những gì dự án chưa hoặc không thể kiểm chứng, về dữ liệu, nhãn, độ chính xác, phát hiện thay đổi và bản đồ web.
sidebar:
  order: 2
---

Dự án làm việc với dữ liệu NISAR hoàn toàn mới trên một tỉnh bị mây che gần như liên tục. Kết quả hữu ích, nhưng cần đọc kèm các giới hạn dưới đây. Chúng tôi muốn nói thẳng ra thay vì để người đọc tự đoán.

## Giới hạn về dữ liệu

- **Chỉ có ba ngày ảnh.** Dự án chủ ý chỉ dùng sản phẩm NISAR GCOV gắn nhãn **VALIDATED** (CRID P05036) trong khoảng **22/10–3/11/2026**: 22/10 và 3/11 (track 148, quỹ đạo xuống, 20 m) và 27/10 (track 054, quỹ đạo lên, 10 m). Lần chụp thứ tư (29/10, track 076) chỉ phủ 4% AOI nên bị bỏ. Không dùng sản phẩm PROVISIONAL cũ hơn.
- **Hình học chụp lẫn lộn.** 27/10 là quỹ đạo lên, hai ngày còn lại là quỹ đạo xuống. Điều này giúp phân loại ([E2](/vi/experiments/e2-features/)) nhưng nghĩa là chỉ có một cặp cùng hình học (22/10 → 3/11) để phát hiện thay đổi, và các đặc trưng "theo thời gian" lẫn khác biệt hướng nhìn với thay đổi thật.
- **Ô 20 m.** Mọi phân tích trên lưới 20 m (ảnh 10 m được lấy trung bình về 20 m). Đối tượng nhỏ hơn vài ô, như bờ đê hẹp, ao nhỏ hay từng ngôi nhà, không phân giải được.
- **VALIDATED không có nghĩa là hoàn hảo.** Sản phẩm VALIDATED vẫn còn các vấn đề đã biết do bên cung cấp dữ liệu liệt kê; ảnh hưởng có thể có của chúng tới kết quả này chưa được đánh giá.
- **Không dùng tần số B (80 m).**

## Giới hạn về nhãn

- **Nhãn lấy từ ảnh quang học cùng giai đoạn,** vẽ trên ảnh Sentinel-2 median 12 ngày. Chỉ khoảng 32% AOI có ít nhất một quan sát sạch, nên nhãn chỉ có ở đó.
- **Nhãn và ngày chụp không khớp hoàn toàn:** mặt đất thay đổi trong 12 ngày (gặt lúa, cho nước vào ruộng), nên một số nhãn có thể không đúng với bề mặt ở một ngày chụp SAR cụ thể.
- **Nhãn tụ cụm:** polygon cùng lớp được vẽ sát nhau (trung vị 102 m), và 10 khối 5 km đông nhất chứa 48% số mẫu ([E0](/vi/experiments/#e0-kiểm-tra-phân-bố-không-gian-của-nhãn)).
- **Phân bố theo vùng không đều:** 618 trong 625 mẫu Đô thị nằm ở nửa bắc tỉnh ([E4](/vi/experiments/e4-validation/)).
- **Polygon nhỏ bị bỏ:** 483 trong 1.347 polygon (36%), phần lớn là thực vật, quá nhỏ để chứa một ô 20 m thuần.
- **Định nghĩa lớp:** nhãn "Đô thị" là khối nhà dày đặc, nhưng lớp Đô thị trên bản đồ có thể gồm cả làng có cây.

## Giới hạn về các con số độ chính xác

- **Không có tập kiểm tra độc lập.** Mọi con số độ chính xác là kiểm tra chéo trên nhãn do cùng một nhóm vẽ. Một **tập kiểm tra mù 250 ô ngẫu nhiên** đã được chuẩn bị trong vùng sạch mây, nhưng **chưa được chấm nhãn**, nên không cho kết quả.
- **Chỉ đo trên ô thuần.** Độ chính xác đo trên ô 20 m nằm ≥80% trong một polygon một lớp. Ô lẫn lớp, chiếm phần lớn cảnh quan thật, chưa được kiểm tra; độ chính xác ở đó chắc chắn thấp hơn.
- **"Khoảng 93%" không phải độ chính xác bản đồ.** Đó là độ chính xác cân bằng lớp trên ô thuần với CV khối không gian 5 km. Độ chính xác giảm còn khoảng 90% ở 2–5 km từ nhãn, và 44% diện tích tỉnh cách nhãn trên 2 km ([E4](/vi/experiments/e4-validation/)).
- **Tỷ lệ diện tích chưa kiểm chứng và chưa hiệu chỉnh.** Ước lượng diện tích theo thiết kế mẫu (Olofsson et al., 2014) cần một tập tham chiếu lấy mẫu theo xác suất, chính là tập mù chưa chấm.
- **Đô thị là lớp kém tin cậy nhất:** 23,5% số ô dự đoán Đô thị nằm ngoài vùng áp dụng được của mô hình ([E8](/vi/experiments/e8-applicability/)).

## Giới hạn của phát hiện thay đổi

- **Một cặp ảnh, 12 ngày.** Thay đổi trước 22/10 hoặc sau 3/11 không thấy được.
- **Ngưỡng chặt:** |z| > 5 ở cả HH và HV, mảng ≥ 0,05 km². Thay đổi nhỏ hoặc từ từ không được báo.
- **Nguyên nhân chưa kiểm chứng.** Cụm nước mới gần 106,484°E, 20,463°N và 18 mảng khác chưa được xác nhận bằng ảnh quang học, ảnh độ phân giải cao hay dữ liệu thực địa ([Kết quả thay đổi](/vi/results/change/)).
- **Không nghiên cứu được thu hoạch lúa:** phần lớn ruộng có vẻ đã gặt trước khoảng thời gian dữ liệu ([Thu hoạch lúa](/vi/results/rice-harvest/)).

## Giới hạn của bản đồ web và trợ lý AI

- **Lớp lớp phủ hiển thị đã qua hậu xử lý** bằng lọc đa số 3×3; ảnh hưởng tới độ chính xác chưa được đo.
- **Lớp độ tin cậy là chỉ báo, không phải bản đồ sai số:** mức đồng thuận đo sự nhất trí giữa các mô hình học cùng bộ nhãn; chỉ số khác biệt đo mức giống dữ liệu huấn luyện, không đo độ đúng.
- **Trợ lý AI** trả lời dựa trên tài liệu này và dữ liệu dự án. Trợ lý vẫn có thể sai; hãy kiểm tra các thông tin quan trọng ở trang được trích dẫn.
