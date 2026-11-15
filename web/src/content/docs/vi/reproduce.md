---
title: Cách tái tạo kết quả
description: Hướng dẫn từng bước dựng lại mọi bộ dữ liệu, bản đồ, thí nghiệm và hình của dự án từ dữ liệu NISAR công khai.
sidebar:
  order: 3
---

Mọi thứ trong dự án đều dựng lại được từ dữ liệu công khai bằng các script trong repo. Thư mục `data/` (khoảng 1 GB) **không** nằm trong git; code, nhãn (`labeling/*.gpkg`), bảng kết quả và hình (`outputs/`) thì có.

:::note[File ranh giới AOI]
Ranh giới tỉnh `data/ref/aoi.geojson` (Hưng Yên sau sáp nhập, một feature MultiPolygon ở EPSG:4326) do nhóm cung cấp và nằm trong thư mục `data/` vốn bị gitignore. Đặt file vào đó trước khi chạy bất kỳ script nào. Xem [Vùng nghiên cứu](/vi/data/aoi/).
:::

## Yêu cầu để tái tạo

- **Môi trường Python:** môi trường conda tên `dwts` từ conda-forge (Python 3.12). `environment.yml` liệt kê các gói cơ bản (rasterio, numpy, h5py, scipy, scikit-learn, matplotlib, pyproj, requests, earthengine-api). Phần phân loại và thí nghiệm cần thêm **pandas, geopandas, pyogrio, shapely, statsmodels, seaborn, xgboost, lightgbm và catboost** từ conda-forge. Phiên bản đã dùng: scikit-learn 1.9.1, numpy 2.5.4, XGBoost 3.4.2, LightGBM 4.7.0, CatBoost 1.2.10 (CatBoost 1.2.5 lỗi với numpy 2.5).
- **Môi trường không có pip:** cài thêm gói bằng `conda install -c conda-forge <gói>`.
- **Tài khoản Earthdata Login** (miễn phí, của NASA) để tải NISAR từ ASF.
- **Tùy chọn:** tài khoản Google Earth Engine nếu muốn dựng lại ảnh tổng hợp Sentinel-2 dùng để vẽ nhãn.

```bash
conda env create -f environment.yml
conda activate dwts
conda install -c conda-forge pandas geopandas pyogrio shapely statsmodels seaborn xgboost lightgbm catboost
```

## Quy ước khi chạy

- **Luôn chạy Python với cờ `-I`** (chế độ cô lập), từ thư mục gốc của repo, ví dụ `python -I scripts/change_detection.py`. Chế độ cô lập bỏ qua site-packages của người dùng và thư mục hiện tại; các script tự thêm thư mục của mình vào `sys.path` để import được `sar_dataset.py`.
- **Không chạy Python từ bên trong các thư mục dữ liệu.**
- **Seed ngẫu nhiên cố định (0)**; kết quả giữa các lần chạy có thể lệch rất ít vì Random Forest chạy song song (ví dụ 1 ô trên 6,4 triệu ô của bản đồ chính).

## Bước 1: tải NISAR GCOV từ ASF

1. Tạo token Earthdata Login và lưu vào file `.earthdata_token` ở thư mục gốc của repo. **File này nằm trong gitignore; không bao giờ commit, in ra hay chia sẻ token.**
2. Tải ba granule ghi trong `data/manifest.json` (trường `url`; các sản phẩm VALIDATED ngày 22/10, 27/10 và 3/11/2026, CRID P05036) vào `data/tmp/`, gửi kèm header `Authorization: Bearer <token>`:

```bash
mkdir -p data/tmp
curl -L -H "Authorization: Bearer $(cat .earthdata_token)" -o data/tmp/<granule>.h5 "<url trong manifest.json>"
```

3. Có thể kiểm tra SHA-256 của từng file so với `raw_sha256` trong manifest.

Chỉ dùng khoảng 22/10–3/11/2026 và sản phẩm VALIDATED. Không cần granule ngày 29/10 (track 076), vì chỉ phủ 4% AOI.

## Bước 2: cắt theo AOI

```bash
python -I scripts/crop_gcov.py data/tmp/*.h5
```

Script đọc tần số A của từng file HDF5, cắt theo `data/ref/aoi.geojson` (đã chiếu sang UTM 48N), ghi 6 lớp GeoTIFF mỗi ngày vào `data/nisar/gcov/` và ghi lại `data/manifest.json`. Sau đó có thể xóa file HDF5. Xem [Tiền xử lý](/vi/methods/preprocessing/).

## Bước 3: ảnh xem nhanh và phát hiện thay đổi

```bash
python -I scripts/quicklook.py          # outputs/quicklook.png, outputs/change_22oct_3nov.png
python -I scripts/change_detection.py   # data/derived/change_class_22oct_3nov.tif, outputs/change_patches.csv
```

`change_detection.py` in ra hệ số tương quan speckle f của HH và HV, diện tích từng lớp thay đổi và các mảng lớn nhất. Xem [Phát hiện thay đổi](/vi/methods/change-detection/). `scripts/sar_analysis.py` là phân tích thăm dò ban đầu (hotspot và ngưỡng thô), không cần cho kết quả cuối.

## Bước 4: nhãn (chỉ khi vẽ lại)

File nhãn đã gộp `labeling/labels_polygon.gpkg` có sẵn trong git, nên bước này là tùy chọn.

```bash
python -I scripts/merge_label_polygons.py "<thư mục chứa water.shp, vegetation.shp, bareland.shp, building.shp>"
```

Ảnh nền Sentinel-2 để vẽ nhãn lấy từ `scripts/gee_s2_composite.js` (chạy trong Earth Engine Code Editor, xuất ra Drive), đặt vào `data/s2/gee_10m/` rồi cắt bằng `python -I scripts/clip_gee_s2.py`. Các ô kiểm tra mù tạo bằng `python -I scripts/make_blind_test.py` (script từ chối ghi đè file đã có).

## Bước 5: huấn luyện bộ phân loại lớp phủ

```bash
python -I scripts/train_classifier.py
```

Script dựng 12 đặc trưng và các mẫu ô thuần, in kết quả kiểm tra chéo (theo khối 5 km và theo polygon), rồi ghi `data/derived/landcover_sar_20m.tif`, `data/derived/samples_polygon_20m.csv` và `outputs/landcover_sar.png`. Xem [Phân loại](/vi/methods/classification/).

## Bước 6: chạy thí nghiệm và vẽ hình

```bash
python -I scripts/experiments.py            # E0–E8, khoảng 35 phút trên máy 8 nhân
python -I scripts/experiments.py --only E1,E4   # chỉ chạy một phần
python -I scripts/plot_experiments.py       # mọi hình ở vi/ và en/, bảng tiếng Anh ở en/tables/ (khoảng 1 phút)
```

Đầu ra: bảng CSV và `log.txt` trong `outputs/experiments/`, hình và báo cáo trong `outputs/experiments/vi/` và `outputs/experiments/en/`, cùng `data/derived/landcover_model_mode.tif`, `landcover_model_agreement.tif` và `aoa_dissimilarity.tif`. E8 cần ảnh tổng hợp Sentinel-2 trong `data/s2/gee_10m/` (để chia vùng sạch và vùng mây).

## Bước 7 (tùy chọn): đánh giá trên tập kiểm tra mù

Sau khi điền cột `label` của `labeling/blind_test_cells.gpkg` (1 Nước, 2 Thực vật, 3 Đất trống, 4 Đô thị, 0 lẫn/không rõ):

```bash
python -I scripts/eval_blind.py
```

Dự án **chưa** làm bước này; xem [Kiểm chứng](/vi/methods/validation/).

## Danh sách script

| Nhóm | Script | Chức năng |
|---|---|---|
| SAR | `crop_gcov.py` | Cắt tần số A của GCOV HDF5 theo AOI, ghi các lớp GeoTIFF và manifest |
| SAR | `quicklook.py` | Ảnh xem nhanh đơn vị dB và chênh lệch thô 22/10 → 3/11 |
| SAR | `sar_analysis.py` | Phân tích thăm dò ban đầu (hotspot, ngưỡng thô) |
| SAR | `change_detection.py` | Phát hiện thay đổi thống kê 22/10 → 3/11 |
| Sentinel-2 | `gee_s2_composite.js` | Ảnh tổng hợp trung vị trên Earth Engine với Cloud Score+ |
| Sentinel-2 | `check_gee_s2.py`, `clip_gee_s2.py` | Kiểm tra và cắt ảnh tổng hợp Earth Engine |
| Sentinel-2 | `s2_scl_coverage.py`, `s2_composite.py` | Kiểm tra độ phủ và ảnh tổng hợp kiểu cũ từ AWS (đã thay thế) |
| Nhãn | `merge_label_polygons.py` | Gộp bốn shapefile theo lớp thành một GeoPackage |
| Nhãn | `make_blind_test.py`, `eval_blind.py` | Tạo và đánh giá tập kiểm tra mù |
| Phân loại | `sar_dataset.py` | Module dùng chung: đặc trưng và mẫu |
| Phân loại | `train_classifier.py` | Mô hình Random Forest chính và bản đồ |
| Phân loại | `experiments.py` | Thí nghiệm E0–E8 (chỉ tính bảng) |
| Phân loại | `plot_experiments.py` | Hình song ngữ và bảng tiếng Anh |
