# Dancing with the SARs

NASA Space Apps 2026, thử thách "Dancing with the SARs". Đội **2936-ThanhNoi**, mã đội **NS05005**: Ninh Hải Đăng (trưởng nhóm), Phạm Minh Quang, Lê Toàn Thắng. Web: https://dwts.ninhhaidang.com. Dùng GCOV VALIDATED của NISAR (CRID P05036, từ 21/10/2026) cho tỉnh Hưng Yên (sau sáp nhập 2025 = Hưng Yên cũ + Thái Bình).

**Session mới: đọc `HANDOFF.md` trước** (trạng thái, kết quả, việc tiếp theo, các bẫy đã gặp).

## Quy tắc làm việc

- Trả lời tiếng Việt. Luôn làm việc và commit thẳng trên `main`, không tạo branch mới. Chỉ commit/push khi người dùng yêu cầu.
- Không xóa/cắt dữ liệu khi chưa được yêu cầu. Không tự sửa `data/ref/aoi.geojson` (ranh giới chuẩn do người dùng cung cấp).
- Báo kết quả trung thực: nói rõ điều chưa kiểm chứng, đừng khẳng định suy đoán (đã từng báo sai NDVI do lỗi hiệu chuẩn, xem HANDOFF).
- Shell: dùng `/bin/ls` (ls bị alias), quote glob trong `grep --include`. Python: `/Users/ninhhaidang/miniconda3/envs/dwts/bin/python -I script.py` (conda env `dwts`, không `cd` vào thư mục chứa dữ liệu khi chạy Python).

## Phạm vi

- Chỉ dùng dữ liệu trong khoảng **22/10 đến 3/11/2026** (3 ngày GCOV VALIDATED). Không mở thêm ngày: không dùng PROVISIONAL hay dữ liệu cũ.
- Được bổ sung dữ liệu khác nếu không vượt khoảng ngày trên (Sentinel-2/-1, DEM, lớp phủ tĩnh, OSM).
- Hướng đề tài: phát hiện thay đổi do điều tiết nước (ruộng, ao nuôi, đê bao) + bản đồ lớp phủ 4 lớp chỉ từ SAR.

## Dịch vụ ngoài

- Token Earthdata nằm ở `.earthdata_token` (gitignore, không in ra, không commit). Tải ASF: header `Authorization: Bearer <token>`.
- Earth Engine: project `earthengine-dang`, `ee.Initialize(project='earthengine-dang')`. Chưa xác minh được cuộc thi có cho phép Earth Engine hay không.

## Dữ liệu (`data/`, không commit; `labeling/*.html` cũng không)

- `data/ref/aoi.geojson`: AOI chuẩn (1 feature, MultiPolygon 8 mảnh, 2.514,81 km²).
- `data/nisar/gcov/`: GCOV tần số A đã cắt theo AOI, EPSG:32648. 22/10 và 3/11 (track 148 xuống) ở **20 m**, 27/10 (track 054 lên) ở **10 m**. Ngày 29/10 không dùng (chỉ phủ 4% AOI). Manifest: `data/manifest.json`.
- `data/s2/composite_20m.tif`: tổ hợp Sentinel-2 pixel sạch trên lưới SAR 20 m (int16, phản xạ×1e4; băng 6 = chỉ số ngày nguồn). `composite_20m_uint16_sai.tif` là bản SAI, bỏ.
- `data/s2/gee_10m/`: chỗ người dùng bỏ ảnh S2 10 m tải từ Earth Engine (xem HANDOFF).
- `data/derived/`: `change_class_22oct_3nov.tif`, `landcover_sar_20m.tif`.
- `data/_legacy/`: PROVISIONAL, Sentinel-2 cũ, aoi cũ. Không dùng.
