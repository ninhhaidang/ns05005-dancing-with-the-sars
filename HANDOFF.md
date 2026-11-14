# HANDOFF: trạng thái dự án (cập nhật 15/11/2026)

## Tóm tắt một dòng
Có 3 ảnh NISAR GCOV VALIDATED đã cắt theo AOI, phát hiện thay đổi có kiểm định thống kê, nhãn polygon 4 lớp (1.347 polygon), bộ phân loại chỉ dùng SAR đạt **BA khoảng 93% trên ô thuần** (CV khối 5 km), 8 thí nghiệm so sánh và báo cáo song ngữ `outputs/experiments/vi/BAO_CAO.md` / `outputs/experiments/en/REPORT.md`. **Chưa có tập kiểm tra độc lập, và người dùng không chấm thêm nhãn nữa.** Việc tiếp theo là làm sản phẩm nộp.

## Dữ liệu NISAR (tất cả VALIDATED, P05036, tần số A)
| Ngày | Track | Pixel | Ghi chú |
|---|---|---|---|
| 22/10 | 148 xuống | 20 m | phủ 100% AOI |
| 27/10 | 054 lên | 10 m | phủ 100% AOI, góc nhìn khác |
| 3/11 | 148 xuống | 20 m | phủ 100% AOI |
| 29/10 | 076 xuống | | chỉ phủ 4% AOI, bỏ |

- **Định dạng:** mỗi ngày có 6 lớp GeoTIFF: HHHH, HVHV, mask, numberOfLooks, rtcGammaToSigmaFactor, inputDataExceptionMask. Giá trị là công suất tuyến tính, đổi sang dB bằng 10·log10.
- **Bản gốc:** file HDF5 gốc đã xóa; tải lại từ URL trong `data/manifest.json` nếu cần. Không dùng tần số B (80 m).
- **Vùng hợp lệ:** đã kiểm, vùng dữ liệu hợp lệ của cả 3 ảnh trùng khít với AOI rasterize sang UTM. AOI gốc ở EPSG:4326 không ảnh hưởng gì, vì `crop_gcov.py` chiếu sang UTM ngay lúc cắt.

## Sentinel-2 (chỉ dùng để vẽ nhãn, không đưa vào mô hình)
- **`data/s2/gee_10m/S2_composite_10m_aoi.tif`:** ảnh GEE median 22/10-3/11, Cloud Score+ ngưỡng **0,789**, đã cắt theo AOI. 6 băng: B2, B3, B4, B8, B11, `n_clear`. Nén deflate, có overview, nodata = 0. Hiển thị màu thật: R = băng 3, G = băng 2, B = băng 1. File gốc chưa cắt vẫn còn bên cạnh.
- **Độ phủ sạch:** chỉ **khoảng 32% AOI** có `n_clear` > 0. Bản AWS cũ `composite_20m.tif` (lọc SCL 4/5/6) phủ 51,7%, nhưng phần chỉ AWS coi là sạch có dấu hiệu nhiễm mây mỏng: B2 trung vị 1129 so với 900 ở vùng cả hai nguồn sạch. Vì vậy ưu tiên ảnh GEE.
- **Mã:** `scripts/check_gee_s2.py` (kiểm tra và đối chiếu), `scripts/clip_gee_s2.py` (cắt theo AOI, có tạo thêm `data/ref/aoi_32648.geojson`).

## Kết quả chính
1. **Phát hiện thay đổi** (`scripts/change_detection.py`, cặp 22/10 và 3/11, kiểm định z > 5, mảng ≥ 0,05 km², hiệu chỉnh tương quan speckle f ≈ 1,6-1,7):
   - 99,89% AOI không đổi.
   - Điểm duy nhất đáng kể: **cụm nước mới khoảng 1,6 km² quanh 106,484°E, 20,463°N**. HH giảm từ −10 xuống −16 dB, HV từ −17 xuống −23 dB, giảm dần qua cả 27/10. Đây là một khối chữ nhật cạnh khúc sông.
   - **Nguyên nhân chưa biết.** Giả thuyết: ao, ruộng hoặc đê bao được cho nước vào. **Chưa kiểm chứng** vì mây che gần như liên tục. Danh sách mảng thay đổi: `outputs/change_patches.csv`.
2. **Thu hoạch lúa:** không thấy tín hiệu trong 12 ngày. Đa số ruộng có vẻ đã gặt trước 22/10. Đề tài lúa yếu.
3. **Dynamic World:** chỉ phủ 6,2% AOI trong khoảng ngày, nên không dùng.
4. **Nhãn polygon** (`labeling/labels_polygon.gpkg`, tạo từ shapefile ArcGIS Pro của đồng đội bằng `scripts/merge_label_polygons.py`):
   - 1.347 hình chữ nhật: Nước 190, Thực vật 485, Đất trống 444, Công trình (= Đô thị/làng) 228. EPSG:32648, các cột `poly_id`, `class_id`, `class_name`, `source`, `area_m2`.
   - Nhãn điểm cũ (vòng 1-2, các file CSV) đã bị người dùng xóa ở commit 67d5eae.
5. **Bộ phân loại chỉ dùng SAR** (`scripts/train_classifier.py`, Random Forest, 12 đặc trưng; đặc trưng và mẫu dựng trong `scripts/sar_dataset.py`):
   - Mẫu là ô 20 m thuần ≥ 80%, tối đa 20 ô mỗi polygon: 3.918 ô từ 864 polygon.
   - **BA 93% trên ô thuần, kiểm tra chéo theo khối 5 km.**
   - Bản đồ: `data/derived/landcover_sar_20m.tif`, ảnh xem nhanh `outputs/landcover_sar.png`. Bản đồ cũ từ nhãn điểm được sao lưu thành `*_nhan_diem_cu.*`.
6. **Thí nghiệm** (`scripts/experiments.py`, chạy khoảng 35 phút). Bảng CSV gốc (nhãn tiếng Việt) và `log.txt` ở `outputs/experiments/`; hình và báo cáo song ngữ ở `outputs/experiments/vi/` và `outputs/experiments/en/` (kèm `en/tables/`: bảng CSV đã dịch), tạo bằng `scripts/plot_experiments.py`:
   - **E1 mô hình:** 14 mô hình, 11 mô hình đứng đầu đạt BA 93,0-93,6% và chênh nhau không đáng kể. SVM cao nhất, Random Forest 93,1%.
   - **E2 đặc trưng:** dùng 1 ngày chỉ đạt BA 83-86%, 3 ngày đạt 93%. Cần cả HH lẫn HV. Kết cấu gần như vô dụng.
   - **E4 cách kiểm chứng:** chia ngẫu nhiên theo ô thổi phồng khoảng 3 điểm. Chia theo nửa tỉnh chỉ còn 84-87%, một phần do nhãn lệch vùng (Đô thị có 618 mẫu ở phía bắc, 7 mẫu ở phía nam). Độ chính xác giảm theo khoảng cách tới nhãn, và 44% AOI cách nhãn trên 2 km.
   - **E5 đường học:** gần bão hòa sau khoảng 300 polygon.
   - **E6 tinh chỉnh lồng:** cải thiện dưới 0,5 điểm.
   - **E7 mức bản đồ:** 10 mô hình cùng một lớp ở 65,9% AOI. Diện tích: Đô thị khoảng 24%, Đất trống khoảng 44%, **chưa kiểm chứng**.
   - **E8 vùng áp dụng được:** 8,3% AOI ngoài vùng áp dụng, như nhau ở vùng sạch và vùng mây. Nhưng 23,5% số ô dự đoán là Đô thị nằm ngoài vùng áp dụng, nên lớp Đô thị kém tin cậy nhất.
   - **Lớp phụ cho bản đồ web:** `data/derived/landcover_model_{mode,agreement}.tif` (lớp đa số và mức đồng thuận giữa mô hình), `data/derived/aoa_dissimilarity.tif` (chỉ số khác biệt DI).
7. **Tập kiểm tra mù** `labeling/blind_test_cells.gpkg`: 250 ô ngẫu nhiên trong vùng S2 sạch, cột `label` = −1 (chưa chấm). Script đánh giá: `scripts/eval_blind.py`. **Người dùng đã quyết định không chấm**, nên đừng đề nghị chấm lại. Mọi báo cáo phải ghi rõ: con số 93% đo trên ô thuần, không phải độ chính xác bản đồ.

## Các bẫy đã gặp (đừng lặp lại)
**Sentinel-2**
- **Phản xạ = DN × 1e-4, KHÔNG trừ 0,1.** Áp dụng cho Earth Search và GEE harmonized. STAC ghi `offset = -0.1` nhưng offset đã được áp. Trừ thêm sẽ ra phản xạ âm; từng báo sai NDVI vì lỗi này.
- **Mây:** không ngày nào đủ sạch. Ngày tốt nhất phủ 24% AOI; GEE gộp được 32%, AWS 51,7% (có nhiễm).
- **Đọc COG qua mạng:** dùng cửa sổ, overview, đa luồng và env GDAL (xem `s2_composite.py`). Đọc tuần tự gần như đứng.

**Ranh giới AOI**
- `aoi.geojson` có 1 feature MultiPolygon gồm 8 mảnh; giữ nguyên, không sửa. Diện tích hình học thật là **2.571,7 km²** (2.572,6 km² trên elipsoid). Con số 2.514,81 km² trong CLAUDE.md không khớp và chưa được sửa.
- Đã từng nhầm khi chỉ đọc feature đầu của GeoJSON nhiều feature.

**Nhãn và mẫu**
- Polygon là hình chữ nhật. Siêu lấy mẫu 4×4 làm ngưỡng thuần 80% thành 100%, nên phải dùng 8×8.
- 36% polygon quá nhỏ (dưới một ô 20 m thuần) nên không cho mẫu.
- Nhãn vẽ thành cụm cùng lớp (cùng lớp cách nhau trung vị 102 m, khác lớp 509 m). Kiểm tra chéo phải chia theo khối không gian, không chia theo ô hay theo polygon.

**Python và thư viện**
- **`python -I` bỏ thư mục script khỏi `sys.path`:** các script trong `scripts/` dùng `sys.path.insert(0, ...)` để import `sar_dataset`.
- **pyogrio không ghi được cột số nguyên rỗng,** và module `sqlite3` không `UPDATE` được bảng GPKG vì trigger cần hàm không gian. Dùng giá trị −1 làm "trống".
- **Env `dwts` không có pip.** Cài gói bằng conda-forge.
- **CatBoost 1.2.5 lỗi với numpy 2.5;** đã nâng lên 1.2.10. Thư mục `catboost_info/` do CatBoost tự tạo, đã gitignore.

**Công cụ**
- **QGIS chậm khi zoom:** file ảnh không phải nguyên nhân, vì đọc qua overview mất dưới 0,1 giây. Nghi ngờ hệ tọa độ project là EPSG:4326 nên QGIS phải chiếu lại raster; đặt project CRS = EPSG:32648.
- **`sed` trên macOS** lỗi với chuỗi tiếng Việt trong lệnh thay thế; dùng công cụ Edit hoặc Python.
- Không có Node trên máy. QGIS có MCP (`mcp__qgis__*`) nhưng kết nối hay mất.

## Script (`scripts/`)
| Nhóm | Script |
|---|---|
| SAR | `crop_gcov.py` (HDF5 → GeoTIFF + manifest), `quicklook.py`, `sar_analysis.py`, `change_detection.py` |
| Sentinel-2 | `s2_scl_coverage.py`, `s2_composite.py` (bản AWS 20 m), `gee_s2_composite.js` (dán vào GEE Code Editor), `check_gee_s2.py`, `clip_gee_s2.py`. `download_s2.py` đã bỏ, không dùng. |
| Nhãn | `merge_label_polygons.py <thư mục shapefile>`, `make_blind_test.py`, `eval_blind.py`. `make_label_tool.py` là công cụ cũ cho nhãn điểm. |
| Phân loại | `sar_dataset.py` (module dùng chung), `train_classifier.py`, `experiments.py [--only E1,E4]` (chỉ tính, ghi CSV), `plot_experiments.py [vi|en]` (vẽ hình song ngữ bằng seaborn, xuất bảng CSV tiếng Anh; thêm nhãn mới vào từ điển `TR` khi CSV có chuỗi tiếng Việt mới) |

## Trạng thái git
`main` trùng với `origin/main` sau mỗi lần push theo yêu cầu. Untracked: `outputs/landcover_sar_nhan_diem_cu.png`, bản sao lưu bản đồ cũ, cố ý không commit vì bản gốc đã có trong lịch sử git.

## Việc tiếp theo (gợi ý, theo thứ tự)
1. **Hậu xử lý bản đồ:** lọc đa số để giảm nhiễu hạt tiêu.
2. **Sản phẩm nộp:** bản đồ web tương tác gồm
   - thanh trượt 22/10, 27/10, 3/11;
   - lớp phủ, kèm lớp độ tin cậy (mức đồng thuận E7, vùng áp dụng E8);
   - mảng thay đổi.

   Kèm phần kể chuyện, giả thuyết vật lý (mặt nước phẳng phản xạ gương nên HH và HV cùng giảm), và nêu rõ giới hạn: chỉ 3 ngày trong 12 ngày, ô 20 m, dữ liệu VALIDATED còn known issues, chỉ đo trên ô thuần, diện tích chưa kiểm chứng.
3. **Kiểm chứng cụm nước mới** bằng ảnh quang học hoặc ảnh độ phân giải cao, nếu có.
4. **README** hướng dẫn tái tạo. `data/` không commit; tải lại từ ASF bằng token rồi chạy `crop_gcov.py`.
5. **Quy định cuộc thi:** kiểm tra việc dùng Earth Engine và Dynamic World có được phép không. Trang rules/FAQ render bằng JS nên chưa đọc được.
6. **Dọn dẹp:** xóa `data/s2/composite_20m_uint16_sai.tif` khi người dùng đồng ý. Cân nhắc sửa diện tích AOI trong CLAUDE.md thành 2.571,7 km².
