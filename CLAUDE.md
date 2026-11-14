# Dancing with the SARs

NASA Space Apps 2026. Dùng GCOV VALIDATED của NISAR (CRID P05036, từ 21/10/2026) cho tỉnh Hưng Yên (sau sáp nhập 2025).

## Git

- Luôn làm việc và commit thẳng trên `main`. Không tạo branch mới.

## Phạm vi

- Chỉ dùng dữ liệu trong khoảng 22/10 đến 3/11/2026 (3 ngày GCOV VALIDATED). Không mở thêm ngày: không dùng PROVISIONAL hay dữ liệu cũ.
- Được bổ sung dữ liệu khác (Sentinel-2/Sentinel-1 trong cùng khoảng ngày, DEM, lớp phủ tĩnh, OSM) nếu không vượt khoảng ngày trên.
- Hướng đề tài: phát hiện và phân loại thay đổi do điều tiết nước (ruộng, ao nuôi, đê bao).

- Earth Engine: project `earthengine-dang` (`ee.Initialize(project='earthengine-dang')`), nhãn lớp phủ dùng Dynamic World V1 (`GOOGLE/DYNAMICWORLD/V1`).

## Dữ liệu (`data/`, không commit)

- `data/ref/aoi.geojson`: ranh giới chuẩn do người dùng cung cấp. Không tự sửa.
- `data/nisar/gcov/`: GeoTIFF tần số A đã cắt theo AOI (EPSG:32648). 22/10 và 3/11 ở 20 m, 27/10 ở 10 m.
- `data/_legacy/`: dữ liệu PROVISIONAL và Sentinel-2 cũ. Không dùng.
- `.earthdata_token`: token tải dữ liệu, không commit, không in ra.
- Môi trường: conda `dwts` (`environment.yml`). Cắt dữ liệu: `scripts/crop_gcov.py`.
