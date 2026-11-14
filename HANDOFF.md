# HANDOFF — trạng thái dự án (cập nhật 14/11/2026)

## Tóm tắt một dòng
Đã có 3 ảnh NISAR GCOV VALIDATED cắt theo AOI Hưng Yên mới, phát hiện thay đổi có kiểm định thống kê, nhãn tự chấm 2 vòng, bộ phân loại 4 lớp chỉ dùng SAR (~80% trên nhãn mù). **Đang chờ người dùng tải ảnh Sentinel-2 10 m từ Earth Engine** để chấm nhãn tiếp trong QGIS.

## Dữ liệu NISAR (tất cả VALIDATED, P05036, tần số A)
| Ngày | Track | Pixel | Ghi chú |
|---|---|---|---|
| 22/10 | 148 xuống | 20 m | phủ 100% AOI |
| 27/10 | 054 lên | 10 m | phủ 100% AOI, góc nhìn khác |
| 3/11 | 148 xuống | 20 m | phủ 100% AOI |
| 29/10 | 076 xuống | | chỉ phủ 4% AOI, bỏ |

Mỗi ngày có 6 lớp GeoTIFF: HHHH, HVHV, mask, numberOfLooks, rtcGammaToSigmaFactor, inputDataExceptionMask. Giá trị là công suất tuyến tính (đổi dB: 10·log10). File HDF5 gốc đã xóa (tải lại từ URL trong manifest nếu cần). Bỏ tần số B (80 m).

## Kết quả chính
1. **Phát hiện thay đổi** (`scripts/change_detection.py`, cặp 22/10 và 3/11, kiểm định z>5, ≥0,05 km², hiệu chỉnh tương quan speckle f≈1,6-1,7): 99,89% AOI không đổi. Điểm duy nhất đáng kể: **cụm nước mới ~1,6 km² quanh 106,484°E, 20,463°N** (HH −10→−16 dB, HV −17→−23 dB, giảm dần qua cả 27/10; khối chữ nhật cạnh khúc sông). **Nguyên nhân chưa biết** (giả thuyết: ao/ruộng/đê bao được cho nước vào), **chưa kiểm chứng**: mây che gần như luôn (chỉ ~9% diện tích có một ngày S2 sạch). Danh sách mảng: `outputs/change_patches.csv`.
2. **Thu hoạch lúa**: không thấy tín hiệu trong 12 ngày; đa số ruộng có vẻ đã gặt trước 22/10 (NDVI trung vị ~0,31). Đề tài lúa yếu.
3. **Dynamic World** trong khoảng ngày chỉ có nhãn cho 6,2% AOI, lệch ven biển, 0% trên cụm nước → **không dùng**. Đã chuyển sang tự chấm nhãn.
4. **Nhãn** (4 lớp: 1 Nước, 2 Thực vật, 3 Đất trống, 4 Đô thị/làng): vòng 1 `labeling/labels.csv` 265 nhãn nhưng 97,7% trùng gợi ý của quy tắc (hiệu ứng neo, gần như không độc lập); vòng 2 `labeling/labels_r2.csv` 70 nhãn **mù** (bỏ qua 70/140). Quy tắc S2 (NDVI/MNDWI/NDBI/HH) khớp nhãn mù 74,3%; quy tắc bỏ sót đô thị (8/30 mẫu "đất trống" thật là đô thị). Mẫu NDVI 0,3-0,5 không có mẫu nào là thực vật → thực vật thật sự ít.
5. **Bộ phân loại SAR-only** (`scripts/train_classifier.py`, RandomForest, 12 đặc trưng): 80,0% trên 70 nhãn mù (mốc 30%), 80,0% CV khối 5 km (n=335). Nhầm chính: thực vật↔đất trống. Bản đồ: `data/derived/landcover_sar_20m.tif`, `outputs/landcover_sar.png`. **Cảnh báo:** n nhỏ (sai số ~±10 điểm), tập mù thiên về mẫu dễ (bỏ qua một nửa), chưa kiểm ở vùng mây, tỷ lệ diện tích dự đoán chưa đáng tin (Đô thị 18,5% có vẻ cao do lấy mẫu cân bằng), bản đồ còn nhiễu hạt tiêu.

## Các bẫy đã gặp (đừng lặp lại)
- **Sentinel-2 từ Earth Search/GEE harmonized: phản xạ = DN × 1e-4, KHÔNG trừ 0,1.** STAC ghi `raster:bands.offset=-0.1` nhưng `earthsearch:boa_offset_applied=True` (đã áp offset). Trừ thêm → phản xạ âm, NDVI sai (từng báo NDVI 0,69 sai). Đã sửa trong `scripts/s2_composite.py`.
- Đọc COG qua mạng: dùng cửa sổ + overview + đa luồng + env GDAL (`GDAL_HTTP_MULTIPLEX` v.v., xem `s2_composite.py`); đọc tuần tự từng đoạn nhỏ gần như đứng. Tải 175 file S2 AWS thì chậm và hay lỗi "Read failed" → đã hủy.
- Ranh giới: aoi cũ có 2 feature + 5 lỗ rỗng; aoi hiện tại do người dùng cung cấp (8 mảnh là đảo/bãi bồi, giữ nguyên).
- Mây S2: không ngày nào đủ sạch (cao nhất 24% AOI); gộp mọi ngày được ~51,7% AOI.
- Đã từng nhầm khi chỉ đọc feature đầu của geojson nhiều feature.
- Không có Node trên máy; QGIS có MCP (`mcp__qgis__*`) nếu cần.

## Script (`scripts/`)
`crop_gcov.py` (cắt HDF5→GeoTIFF+manifest), `quicklook.py`, `sar_analysis.py`, `change_detection.py`, `s2_scl_coverage.py`, `s2_composite.py` (tổ hợp 20 m), `make_label_tool.py [--round 2]` (công cụ chấm nhãn HTML), `train_classifier.py`, `gee_s2_composite.js` (dán vào GEE Code Editor, xuất 1 ảnh median 10 m, 6 băng B2,B3,B4,B8,B11,n_clear, EPSG:32648), `download_s2.py` (tải S2 AWS, đã bỏ, không dùng).

## Trạng thái hiện tại / đang chờ
- Người dùng **tự chạy `gee_s2_composite.js` trên Earth Engine** và sẽ bỏ ảnh vào **`data/s2/gee_10m/S2_composite_10m_20261022_20261103.tif`** (nếu xuất từng ngày: `S2_10m_<yyyymmdd>.tif`). Khi có file: kiểm tra số băng, CRS, độ phủ sạch, đối chiếu phản xạ với `composite_20m.tif`.
- Người dùng định **chấm lại nhãn trong QGIS ở 10 m** (nhãn là cho ô 20 m = 40×40 m, đừng chấm theo 1 pixel 10 m). Ưu tiên mẫu vòng 1 không chắc.
- Git: `main` trước `origin/main` 2 commit (chưa push). Chưa commit: `scripts/download_s2.py`, `scripts/gee_s2_composite.js`, `CLAUDE.md` mới, `HANDOFF.md`.

## Việc tiếp theo (gợi ý, theo thứ tự)
1. Kiểm tra ảnh GEE khi có; dựng đặc trưng/nhãn 10 m nếu cần.
2. Chấm thêm nhãn mù trong QGIS (cân nhắc thêm lớp "Nước nhỏ/ao/ruộng ngập" thành 5 lớp — người dùng đã chọn giữ 4 lớp), huấn luyện lại; làm mịn bản đồ (lọc đa số); hiệu chỉnh tỷ lệ lớp.
3. Kiểm chứng cụm nước mới bằng ảnh quang học/ảnh độ phân giải cao nếu có (S2 trong khoảng ngày gần như không giúp được).
4. Sản phẩm nộp: bản đồ web tương tác (thanh trượt 22/10, 27/10, 3/11; lớp phủ; mảng thay đổi), kể chuyện + giả thuyết vật lý (mặt nước phẳng phản xạ gương → HH, HV cùng giảm) + nêu rõ giới hạn (chỉ 3 ngày/12 ngày, 20 m, dữ liệu VALIDATED còn known issues).
5. Viết README hướng dẫn tái tạo (data/ không commit: tải lại từ ASF bằng token + `crop_gcov.py`).
6. Kiểm tra quy định cuộc thi về dùng Earth Engine/Dynamic World (trang rules/FAQ render bằng JS, tôi không đọc được).
7. Xóa `data/s2/composite_20m_uint16_sai.tif` khi người dùng đồng ý; push khi người dùng yêu cầu.
