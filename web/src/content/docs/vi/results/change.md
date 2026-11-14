---
title: Kết quả phát hiện thay đổi
description: Từ 22/10 đến 3/11/2026, 99,89% diện tích Hưng Yên không có thay đổi SAR đáng kể; ngoại lệ chính là một cụm nước mới khoảng 1,6 km² chưa rõ nguyên nhân.
sidebar:
  order: 1
---

Trang này trình bày kết quả phát hiện thay đổi có kiểm định thống kê giữa hai ảnh NISAR cùng hình học chụp, **22/10/2026 và 3/11/2026** (track 148, quỹ đạo xuống, 20 m). Phương pháp (kiểm định log tỷ số với mô hình speckle Gamma, |z| > 5 ở cả HH và HV, mảng tối thiểu 0,05 km²) được mô tả ở [Phương pháp phát hiện thay đổi](/vi/methods/change-detection/). Xem trên [bản đồ tương tác, chế độ thay đổi](/vi/map/?view=change).

:::caution[Chưa kiểm chứng thực địa]
Chưa mảng thay đổi nào được xác nhận bằng ảnh quang học hay dữ liệu thực địa, vì mây che gần như liên tục trong giai đoạn này. Mọi diễn giải dưới đây là **giả thuyết dựa trên vật lý SAR.**
:::

## Tóm tắt phát hiện thay đổi: 99,89% không đổi

| Lớp | Quy tắc | Diện tích (km²) | Tỷ lệ AOI | Số mảng |
|---|---|---|---|---|
| 1 Không đổi đáng kể | — | 2.569,03 | 99,895% | — |
| 2 Nước mới / bề mặt phẳng hóa | HH và HV cùng giảm (z < −5) và HH ngày 3/11 < −15 dB | **1,579** | 0,061% | 5 |
| 3 HH và HV giảm (khác) | cùng giảm, HH ngày 3/11 ≥ −15 dB | 0,381 | 0,015% | 5 |
| 4 HH và HV tăng | cùng tăng (z > 5) | 0,583 | 0,023% | 7 |
| 5 Chỉ HV giảm | chỉ HV có ý nghĩa, âm | 0 | 0% | 0 |
| 6 Chỉ HV tăng | chỉ HV có ý nghĩa, dương | 0,158 | 0,006% | 2 |

Tổng diện tích phân tích: 2.571,73 km² (6,43 triệu ô 20 m). Mảng nhỏ hơn 0,05 km² (125 ô) được gán lại về lớp 1, nên các thay đổi nhỏ như từng thửa ruộng riêng lẻ được cố ý bỏ qua. Tổng cộng **19 mảng** vượt ngưỡng kiểm định.

![Các lớp thay đổi giữa 22/10 và 3/11/2026](/figures/common/change_detection.png)

## Cụm nước mới gần 106,484°E, 20,463°N

Thay đổi đáng kể duy nhất trong tỉnh là một cụm mảng tối cạnh một khúc sông ở phía đông nam tỉnh, tâm gần **106,484°E, 20,463°N**.

- **Kích thước:** cả 5 mảng lớp 2 (tổng 1,58 km²) nằm trong bán kính khoảng 3 km quanh điểm này; hai mảng lớn nhất 0,71 km² và 0,62 km². Tính cả các mảng lớp 3 liền kề (0,32 km² trong cùng khu vực), cụm rộng khoảng 1,6–1,9 km² tùy cách tính. Cụm có dạng gần chữ nhật, giống các khoảnh ruộng.
- **Mức giảm backscatter** (trung bình công suất tuyến tính trên mọi ô lớp 2, đổi ra dB):

| Ngày | HH (dB) | HV (dB) |
|---|---|---|
| 22/10 (quỹ đạo xuống) | −10,3 | −17,5 |
| 27/10 (quỹ đạo lên) | −12,0 | −19,9 |
| 3/11 (quỹ đạo xuống) | −16,4 | −23,1 |

- **Mức giảm diễn ra dần:** ảnh trung gian ngày 27/10 đã nằm giữa hai mức. Vì 27/10 chụp từ hướng ngược lại (quỹ đạo lên), giá trị trung gian này chỉ mang tính tham khảo.
- Để so sánh, phần không đổi của tỉnh có trung bình khoảng −3 dB ở HH và −12,5 dB ở HV ở mọi ngày.

![Hiệu HH và HV giữa 3/11 và 22/10 (dB) trên toàn tỉnh; vệt đỏ đậm phía đông nam trung tâm là cụm nước mới](/figures/common/change_22oct_3nov.png)

Ô bên phải của hình dưới đây là HH quanh cụm ngày 22/10, 27/10 và 3/11 (trái sang phải): khối ruộng cạnh khúc sông tối dần. Hai ô bên trái của hình khám phá ban đầu này (phân loại theo ngưỡng và HH − HV) đã được thay thế bởi [kết quả lớp phủ](/vi/results/landcover/).

![Phân tích SAR khám phá; ô phải: HH quanh cụm nước mới ngày 22/10, 27/10 và 3/11](/figures/common/sar_analysis.png)

### Diễn giải vật lý cụm nước mới (giả thuyết)

HH và HV **cùng** giảm khoảng 6 dB xuống mức điển hình của mặt nước (HH dưới −15 dB) là điều SAR L-band ghi nhận khi một bề mặt nhám (lúa, gốc rạ, đất ẩm) trở thành **mặt nước phẳng**: xung radar bị phản xạ đi xa khỏi vệ tinh như gương (phản xạ gương), nên rất ít năng lượng quay về ở cả hai phân cực.

Các nguyên nhân khả dĩ, phù hợp chủ đề điều tiết nước của dự án:
- cho nước vào một hoặc một nhóm ruộng (ví dụ sau gặt, hoặc để chuẩn bị ao nuôi);
- tích nước ao cá/tôm hoặc một khu có đê bao cạnh sông;
- ngập tạm thời phía sau đê.

**Nguyên nhân chưa biết và chưa kiểm chứng.** Chưa đối chiếu với ảnh quang học (vì mây), ảnh độ phân giải cao hay thông tin địa phương.

## Các mảng thay đổi khác

| Lớp | Diện tích (km²) | Kinh độ | Vĩ độ | HH 22/10 (dB) | HH 3/11 (dB) |
|---|---|---|---|---|---|
| 2 Nước mới | 0,713 | 106,4820 | 20,4667 | −11,4 | −16,7 |
| 2 Nước mới | 0,624 | 106,4848 | 20,4610 | −9,7 | −16,3 |
| 4 Tăng | 0,127 | 106,0756 | 20,7290 | −10,2 | −5,2 |
| 3 Giảm (khác) | 0,118 | 106,4830 | 20,4561 | −8,6 | −13,7 |
| 4 Tăng | 0,102 | 106,3051 | 20,5620 | −11,4 | −6,5 |
| 2 Nước mới | 0,092 | 106,4883 | 20,4576 | −9,9 | −15,8 |
| 6 Chỉ HV tăng | 0,090 | 106,4685 | 20,3502 | −3,8 | −2,4 |
| 4 Tăng | 0,086 | 106,0649 | 20,8508 | −11,5 | −6,0 |
| 3 Giảm (khác) | 0,082 | 106,4944 | 20,4641 | −8,4 | −13,2 |
| 4 Tăng | 0,082 | 106,1040 | 20,7303 | −12,5 | −6,3 |
| 2 Nước mới | 0,080 | 106,4907 | 20,4697 | −11,6 | −16,1 |
| 4 Tăng | 0,072 | 106,1948 | 20,5219 | −8,8 | +6,8 |
| 2 Nước mới | 0,070 | 106,4739 | 20,4834 | −9,2 | −15,6 |
| 6 Chỉ HV tăng | 0,067 | 106,4924 | 20,3138 | −10,9 | −8,6 |
| 3 Giảm (khác) | 0,063 | 106,4871 | 20,4680 | −9,0 | −14,1 |
| 3 Giảm (khác) | 0,062 | 106,4067 | 20,4621 | −3,4 | −10,0 |
| 4 Tăng | 0,060 | 106,0545 | 20,8531 | −8,7 | +1,5 |
| 3 Giảm (khác) | 0,056 | 106,4877 | 20,4593 | −9,0 | −14,0 |
| 4 Tăng | 0,054 | 106,3048 | 20,5660 | −11,3 | −6,3 |

Tọa độ là tâm mảng (WGS84); giá trị dB là HH trung bình trên mảng.

- **Tăng (lớp 4, 0,58 km², 7 mảng)** tập trung ở phía tây bắc (khoảng 106,05–106,10°E, 20,73–20,85°N), thêm hai mảng gần 106,30°E, 20,56°N và một mảng ở 106,19°E, 20,52°N. Trung bình trên mọi ô lớp 4, HH đi từ −10,2 qua −9,1 lên **+0,8 dB**, HV từ −18,2 qua −17,1 lên −11,6 dB: phần lớn mức tăng xảy ra giữa 27/10 và 3/11. Nguyên nhân khả dĩ gồm công trình hay vật liệu mới, thay đổi độ ẩm hay độ nhám của đất, hoặc tán xạ hai lần giữa mặt nước và thực vật/công trình. **Chưa kiểm chứng.**
- **Chỉ HV tăng (lớp 6, 0,16 km², 2 mảng)** nằm ở phía đông nam (khoảng 106,47–106,49°E, 20,31–20,35°N). HV tăng riêng lẻ thường gợi ý tán xạ khối tăng (cấu trúc thực vật). **Chưa kiểm chứng.**
- **Không có mảng "chỉ HV giảm"** (lớp 5) nào vượt ngưỡng.

## Kết quả thay đổi nói gì về thu hoạch lúa

Không phát hiện mức giảm HV trên diện rộng, vốn là dấu hiệu khi lúa bị gặt. Xem [Thu hoạch lúa](/vi/results/rice-harvest/).

## Giới hạn của kết quả thay đổi

- **Chỉ có một cặp cùng hình học** (22/10 → 3/11, 12 ngày). Ảnh 27/10 có hình học khác và chỉ dùng làm mốc trung gian định tính.
- **Ngưỡng chặt** (|z| > 5 ở cả hai phân cực, ≥ 0,05 km²) ưu tiên ít báo động giả hơn là độ nhạy; thay đổi nhỏ hoặc từ từ bị bỏ sót.
- **Không có dữ liệu thực địa:** mọi diễn giải là giả thuyết.
- Danh sách mảng cũng có trong trợ lý AI và trên [bản đồ](/vi/map/?view=change).
