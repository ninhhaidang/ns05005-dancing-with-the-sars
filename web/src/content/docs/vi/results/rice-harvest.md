---
title: Thu hoạch lúa (kết quả âm tính)
description: Không tìm thấy tín hiệu thu hoạch lúa trong 12 ngày dữ liệu NISAR, nhiều khả năng vì vụ chính đã gặt xong trước 22/10/2026; Dynamic World bị mây che nên không dùng được.
sidebar:
  order: 3
---

Một ý tưởng ban đầu của dự án là lập bản đồ **thu hoạch lúa** ở Hưng Yên từ chuỗi ảnh NISAR. Trang này giải thích vì sao ý tưởng đó bị bỏ. Đây là kết quả âm tính, ghi lại cho đầy đủ.

## Thu hoạch lúa trông thế nào trên SAR L-band

Khi lúa đứng bị gặt, khối thân và lá biến mất. Ở L-band điều này thường thể hiện bằng **HV giảm** (phân cực chéo, do tán xạ khối chi phối), thường kèm thay đổi HH tùy độ ẩm đất và gốc rạ. Ruộng được cho nước vào sau gặt trở thành mặt nước phẳng và tối đi ở **cả** HH và HV.

## Kết quả trong 12 ngày dữ liệu

- **Không có tín hiệu gặt trên diện rộng.** Từ 22/10 đến 3/11/2026, phát hiện thay đổi có kiểm định cho thấy **99,89% diện tích tỉnh không đổi** ở mức ý nghĩa đã chọn (|z| > 5 ở HH và HV, mảng ≥ 0,05 km²). Không có mức giảm HV diện rộng như kỳ vọng khi gặt; không mảng "chỉ HV giảm" nào vượt ngưỡng ([Kết quả thay đổi](/vi/results/change/)).
- **Nhiều ruộng đã trông như đất trống.** Bản đồ lớp phủ chỉ từ SAR xếp khoảng 44–46% diện tích tỉnh vào Đất trống ([Kết quả lớp phủ](/vi/results/landcover/)), phù hợp với ruộng đã gặt hoặc đã cày.
- **Diễn giải (chưa kiểm chứng):** phần lớn ruộng lúa có lẽ đã **gặt xong trước 22/10**, nên 12 ngày dữ liệu rơi vào sau vụ gặt chính. Điều này khớp với lịch thời vụ thông thường của đồng bằng sông Hồng, nhưng chưa được đối chiếu với ngày gặt thực tế hay dữ liệu thực địa.

## Vì sao chủ đề lúa yếu với bộ dữ liệu này

- **Khoảng thời gian quá ngắn và quá muộn:** dự án chỉ dùng 12 ngày dữ liệu VALIDATED (22/10–3/11/2026), và chỉ có một cặp cùng hình học (22/10 và 3/11, track 148). Theo dõi mùa gặt cần ảnh trải suốt thời gian gặt.
- **Ngưỡng phát hiện thay đổi chặt:** thay đổi từ từ hoặc theo từng thửa dưới 0,05 km² được cố ý không báo.
- **Không có ảnh quang học để xác nhận:** mây che phần lớn tỉnh trong giai đoạn này (chỉ khoảng 32% AOI có ít nhất một quan sát Sentinel-2 sạch).

## Dynamic World không dùng làm tham chiếu được

Sản phẩm lớp phủ gần thời gian thực Dynamic World của Google từng được cân nhắc làm tham chiếu cho cây trồng và đất trống. Trong khoảng 22/10–3/11/2026, nó **chỉ phủ 6,2% AOI** (vì được tạo từ pixel Sentinel-2 không mây), nên **không được dùng** cho nhãn hay kiểm chứng.

## Dự án chuyển trọng tâm sang đâu

Dự án vì vậy tập trung vào (1) **thay đổi do điều tiết nước** (ruộng, ao, đê bao), với phát hiện chính là [cụm nước mới](/vi/results/change/), và (2) **bản đồ lớp phủ 4 lớp chỉ từ SAR** ([Kết quả lớp phủ](/vi/results/landcover/)).
