---
title: Vùng nghiên cứu (AOI)
description: Ranh giới tỉnh Hưng Yên sau sáp nhập dùng để cắt mọi dữ liệu, diện tích của nó và cách xử lý.
sidebar:
  order: 2
---

Vùng nghiên cứu (AOI) của dự án là toàn bộ **tỉnh Hưng Yên sau đợt sáp nhập hành chính năm 2025**: tỉnh Hưng Yên cũ cộng tỉnh Thái Bình cũ, hợp nhất dưới tên Hưng Yên.

## File ranh giới AOI

- **File:** `data/ref/aoi.geojson` (do nhóm cung cấp; được coi là ranh giới chuẩn và không bao giờ sửa).
- **Cấu trúc:** một feature GeoJSON, hình học là **MultiPolygon gồm 8 mảnh**, tọa độ địa lý (EPSG:4326).
- **Thuộc tính trong file:** tên tỉnh Hưng Yên, sáp nhập từ "Hưng Yên, Thái Bình", mã tỉnh 33, dân số 3.567.943, diện tích hành chính 2.514,81 km², 104 đơn vị hành chính (11 phường, 93 xã), trụ sở tại Phố Hiến.
- **Bản đã chiếu:** `scripts/clip_gee_s2.py` ghi thêm `data/ref/aoi_32648.geojson`, cùng ranh giới ở UTM 48N, để mở tiện trong QGIS.
- **Khung bao (xấp xỉ):** 105,89°E đến 106,66°E, 20,25°N đến 21,01°N.

## Diện tích AOI: 2.571,7 km² và 2.514,81 km²

- **Diện tích hình học của ranh giới:** 2.571,7 km² khi chiếu polygon sang UTM 48N (2.572,6 km² nếu đo trên elipsoid). Trên lưới phân tích 20 m, đó là 6.429.330 ô × 400 m² = **2.571,7 km²**. Mọi tỷ lệ phần trăm AOI trên trang này đều dùng con số này.
- **Thuộc tính diện tích hành chính:** file ranh giới ghi 2.514,81 km². Số liệu thống kê chính thức này lệch khoảng 2% so với diện tích hình học của polygon. Chênh lệch chưa được đối chiếu; có thể do khác cơ sở đo đạc hoặc do ranh giới đã được khái quát hóa.

## AOI được dùng thế nào trong xử lý

- **Cắt ảnh NISAR:** `scripts/crop_gcov.py` chiếu polygon AOI sang UTM 48N (EPSG:32648) trước khi cắt, rồi gán nodata cho mọi pixel ngoài polygon. Vì việc chiếu được làm ngay lúc cắt, việc file gốc ở EPSG:4326 không ảnh hưởng gì tới kết quả.
- **Kiểm tra:** vùng dữ liệu hợp lệ của cả ba ngày NISAR trùng khít với AOI rasterize trên lưới UTM.
- **Cắt ảnh Sentinel-2:** `scripts/clip_gee_s2.py` cắt ảnh tổng hợp Sentinel-2 10 m bằng cùng polygon (pixel ngoài AOI = 0).
- **Bẫy đã tránh:** một phiên bản code trước từng chỉ đọc feature đầu tiên của file GeoJSON nhiều feature và âm thầm làm mất một phần ranh giới. File hiện tại có đúng một feature (đã kiểm tra), nên đọc feature đầu là đọc trọn ranh giới.

## Cảnh quan trong AOI

Hưng Yên nằm ở vùng thấp, bằng phẳng của đồng bằng sông Hồng. Cảnh quan là một bức khảm chi tiết gồm ruộng lúa, ruộng màu và cây ăn quả, ao nuôi cá và tôm, làng xóm có vườn cây bao quanh, thị trấn và khu công nghiệp, sông, kênh mương và đê. Nước trong ruộng và ao được người dân chủ động điều tiết (cho vào và tháo ra), và đó chính là điều mà [phát hiện thay đổi](/vi/methods/change-detection/) tìm kiếm. Địa hình gần như phẳng nên ảnh hưởng địa hình lên radar nhỏ.

Xem ranh giới trên [bản đồ tương tác](/vi/?view=overview).
