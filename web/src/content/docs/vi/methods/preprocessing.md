---
title: Tiền xử lý
description: Cách tải file NISAR GCOV HDF5, cắt theo AOI, đổi sang dB, đưa về chung lưới 20 m và làm trơn.
sidebar:
  order: 1
---

Tiền xử lý biến ba file NISAR GCOV HDF5 dung lượng lớn thành các lớp GeoTIFF nhỏ, khớp nhau trên cùng một lưới 20 m phủ đúng AOI Hưng Yên. Các bước được giữ ở mức tối thiểu: không hiệu chuẩn thêm, không lọc speckle nào ngoài lấy trung bình đơn giản, không dùng dữ liệu quang học.

## Bước 1: tải NISAR GCOV từ ASF

- **Nguồn:** Alaska Satellite Facility (ASF) DAAC, `https://nisar.asf.earthdatacloud.nasa.gov/NISAR/NISAR_L2_GCOV_V1/<granule>/<granule>.h5`.
- **Xác thực:** token Earthdata Login gửi qua header HTTP `Authorization: Bearer <token>`. Token lưu ở máy trong file `.earthdata_token`, file này nằm trong gitignore, không bao giờ commit hay in ra.
- **Sản phẩm:** ba granule VALIDATED (CRID P05036): 22/10, 27/10 và 3/11/2026. URL chính xác và mã SHA-256 nằm trong `data/manifest.json`. Xem [Dữ liệu NISAR](/vi/data/nisar/).

## Bước 2: cắt tần số A theo AOI (`scripts/crop_gcov.py`)

Cách chạy: `python -I scripts/crop_gcov.py data/tmp/*.h5`

1. **Chiếu AOI:** polygon AOI (EPSG:4326) được chuyển sang UTM 48N (EPSG:32648), phép chiếu của lưới GCOV (script kiểm tra phép chiếu trong HDF5 đúng là 32648).
2. **Cửa sổ:** từ các mảng tọa độ trong HDF5 (`xCoordinates`, `yCoordinates`, khoảng cách pixel), script tính cửa sổ pixel bao khung AOI, nên chỉ đọc phần cửa sổ đó.
3. **Che phần ngoài AOI:** pixel ngoài polygon gán nodata (NaN với lớp số thực, 255 với `mask`, 65535 với `inputDataExceptionMask`).
4. **Ghi GeoTIFF:** mỗi ngày 6 lớp lấy từ `science/LSAR/GCOV/grids/frequencyA`: `HHHH`, `HVHV`, `numberOfLooks`, `rtcGammaToSigmaFactor`, `mask`, `inputDataExceptionMask`. File được chia tile, nén deflate, gắn tag granule nguồn, tên lớp, ngày, mức hoàn thiện VALIDATED và CRID P05036.
5. **Manifest:** `data/manifest.json` ghi cho từng lớp: đường dẫn file ra, URL nguồn, SHA-256 của HDF5 gốc, ngày, sản phẩm, mức hoàn thiện và kích thước pixel.

- **Thư mục ra:** `data/nisar/gcov/` (khoảng 391 MB cho ba ngày).
- **File HDF5 gốc** không bị script xóa; trong dự án này chúng được xóa thủ công sau đó để tiết kiệm dung lượng và có thể tải lại.

## Bước 3: đổi tán xạ NISAR sang decibel

- GCOV lưu tán xạ ngược dưới dạng **công suất tuyến tính** (γ⁰ đã hiệu chỉnh địa hình). Dự án đổi sang decibel bằng **dB = 10 · log10(công suất)**, trước đó gán NaN cho giá trị ≤ 0.
- Hệ số đổi γ⁰ → σ⁰ (`rtcGammaToSigmaFactor`) **không** được áp dụng; mọi phân tích dùng nguyên γ⁰ như được cung cấp.
- **Chỗ lấy trung bình theo công suất tuyến tính:** việc đưa 10 m về 20 m và các cửa sổ của phát hiện thay đổi đều lấy trung bình công suất tuyến tính (lấy trung bình giá trị dB sẽ làm trung bình bị lệch xuống). Riêng bước làm trơn 3 × 3 các đặc trưng phân loại (Bước 5) thì làm trên giá trị dB.

## Bước 4: đưa mọi ngày về một lưới 20 m

- **Lưới chuẩn:** lớp HH ngày 22/10: 4.001 × 4.174 pixel 20 m, UTM 48N.
- **22/10 và 3/11** đã nằm sẵn trên lưới này (cùng track, cùng lưới), không cần nội suy.
- **27/10 (10 m, bay lên)** được đưa về lưới chuẩn bằng `rasterio.warp.reproject` với phép nội suy **average** trên công suất tuyến tính, nên mỗi ô 20 m là trung bình của bốn pixel 10 m.
- **Mặt nạ AOI:** các ô có giá trị HH ngày 22/10 hữu hạn xác định AOI (6.429.330 ô = 2.571,7 km²).

## Bước 5: giảm speckle bằng làm trơn

- **Cho đặc trưng lớp phủ** (`scripts/sar_dataset.py`): mỗi lớp dB được làm trơn bằng **bộ lọc trung bình 3 × 3** (60 m × 60 m). Trước khi lọc, các ô NaN tạm được điền bằng trung vị của ảnh để bộ lọc không lan NaN vào mép AOI; các ô ngoài AOI sau đó bị loại bằng mặt nạ AOI.
- **Cho phát hiện thay đổi** (`scripts/change_detection.py`): công suất tuyến tính được lấy trung bình trong **cửa sổ 5 × 5** (100 m × 100 m), chỉ tính ô hợp lệ, đồng thời theo dõi số look để mô hình hóa thống kê phần speckle còn lại (xem [Phát hiện thay đổi](/vi/methods/change-detection/)).
- **Không dùng bộ lọc speckle nâng cao** (Lee, Refined Lee, v.v.). Lấy trung bình đơn giản giúp thống kê speckle vẫn tính được cho phép kiểm định thay đổi (biết số look trong cửa sổ). Chưa so sánh với các bộ lọc nâng cao.

## Bước 6: dữ liệu quang học chỉ để vẽ nhãn

Sentinel-2 được xử lý riêng (ảnh tổng hợp trung vị trên Earth Engine, cắt bằng `scripts/clip_gee_s2.py`) và chỉ dùng làm ảnh nền khi vẽ nhãn. Nó không bao giờ đi vào mô hình. Xem [Sentinel-2](/vi/data/sentinel2/).

## Lưu ý thực tế khi chạy tiền xử lý

- Chạy Python trong môi trường conda `dwts` với cờ `-I` (chế độ cô lập); các script trong `scripts/` tự thêm thư mục của mình vào `sys.path` vì `-I` bỏ thư mục đó đi.
- Không chạy Python từ bên trong các thư mục dữ liệu.
- `data/` không nằm trong git. Các lớp NISAR và mọi raster dẫn xuất đều tạo lại được từ dữ liệu công khai; riêng ranh giới AOI `data/ref/aoi.geojson` là file do nhóm cung cấp, cũng nằm trong `data/`, phải lấy riêng. Xem [Tái tạo kết quả](/vi/reproduce/).
