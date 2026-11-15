---
title: Nhãn huấn luyện
description: 1.347 polygon nhãn vẽ tay cho Nước, Thực vật, Đất trống và Đô thị, cách chuyển thành mẫu huấn luyện, các thiên lệch, và tập kiểm tra mù chưa chấm.
sidebar:
  order: 4
---

Bộ phân loại lớp phủ học từ **1.347 polygon nhãn hình chữ nhật** do nhóm vẽ. Mỗi polygon đánh dấu một vùng rõ ràng thuộc một trong bốn lớp. Nhãn được vẽ bằng mắt trên [ảnh tổng hợp Sentinel-2](/vi/data/sentinel2/) 10 m, nên chỉ có ở nơi ảnh đó không bị mây (khoảng 32% AOI).

## Các lớp nhãn và số polygon

| Mã lớp | Lớp (tên trên bản đồ) | Shapefile nguồn | Số polygon | Diện tích polygon trung vị | Tổng diện tích |
|---|---|---|---|---|---|
| 1 | Nước | `water.shp` | 190 | 5.829 m² | 2,66 km² |
| 2 | Thực vật | `vegetation.shp` | 485 | 568 m² | 0,54 km² |
| 3 | Đất trống | `bareland.shp` | 444 | 997 m² | 0,57 km² |
| 4 | Đô thị (nhãn gốc là "building") | `building.shp` | 228 | 1.669 m² | 0,48 km² |
| | **Tổng** | | **1.347** | | **4,25 km²** |

- **Ý nghĩa dự kiến của các lớp:** Nước = mặt nước hở (sông, ao, ruộng ngập). Thực vật = ruộng và cây có lớp phủ xanh. Đất trống = đất không có lớp phủ xanh, kể cả ruộng mới gặt hoặc mới cày. Đô thị = nhà cửa dày đặc (thị trấn, làng); lớp nguồn tên là "building".
- **Độ phủ của nhãn:** tất cả polygon cộng lại chỉ 4,25 km², khoảng 0,17% trong 2.571,7 km² của AOI.

## File nhãn và cách tạo

- **Vẽ:** các thành viên vẽ hình chữ nhật trong ArcGIS Pro trên nền ảnh màu thật Sentinel-2, mỗi lớp một shapefile.
- **Gộp:** `scripts/merge_label_polygons.py <thư mục shapefile>` gộp bốn shapefile thành `labeling/labels_polygon.gpkg`. Script bỏ chiều Z (PolygonZ → Polygon), sửa hình học không hợp lệ, ép tất cả về MultiPolygon và gán EPSG:32648 (file .prj của ArcGIS là WKT không có mã EPSG). Shapefile gốc không bị sửa.
- **Các cột:** `poly_id` (mã duy nhất, dùng để nhóm khi kiểm tra chéo), `class_id` (1–4), `class_name`, `source` (shapefile gốc), `area_m2`.
- **Lịch sử:** các vòng nhãn điểm trước đây (file CSV) đã được thay bằng polygon và xóa khỏi repo.

## Từ polygon nhãn đến mẫu huấn luyện (ô 20 m thuần)

Mô hình làm việc trên lưới NISAR 20 m, nên mỗi polygon được chuyển thành các ô huấn luyện 20 m (code: `scripts/sar_dataset.py`, hàm `samples`):

1. **Tỷ lệ phủ:** mỗi ô 20 m được chia thành 8 × 8 ô con (2,5 m) để tính phần diện tích thuộc mỗi lớp. (Nếu chia 4 × 4 thì ngưỡng 80% thực chất bị làm tròn thành 100%, nên bắt buộc dùng 8 × 8.)
2. **Ngưỡng thuần:** một ô chỉ thành mẫu nếu **≥ 80%** diện tích thuộc một lớp ("ô thuần").
3. **Giới hạn mỗi polygon:** giữ tối đa **20 ô mỗi polygon** (chọn ngẫu nhiên, seed 0), để các polygon nước lớn không lấn át.
4. **Kết quả:** **3.918 mẫu từ 864 polygon**: Nước 2.011, Thực vật 622, Đất trống 660, Đô thị 625.
5. **Polygon không dùng được:** **483 polygon (36%)** không cho mẫu nào vì quá nhỏ, không chứa trọn một ô 400 m². Phần lớn là polygon thực vật (diện tích polygon thực vật trung vị chỉ 568 m²).

## Phân bố cụm và mất cân bằng của nhãn

- **Vẽ thành cụm:** polygon được vẽ thành cụm cùng lớp. Khoảng cách trung vị từ một polygon tới polygon *cùng lớp* gần nhất là 102 m, tới polygon *khác lớp* gần nhất là 509 m. Không có polygon nào chạm nhau.
- **Ít địa điểm độc lập:** mẫu rơi vào 88 khối 5 × 5 km, nhưng 10 khối dày nhất chứa 48% số mẫu; mỗi lớp chỉ có mặt ở 33–45 khối.
- **Lệch vùng:** lớp Đô thị có 618 mẫu ở nửa bắc tỉnh và chỉ 7 mẫu ở nửa nam. Thực vật có 209 mẫu ở nửa tây và 413 ở nửa đông.
- **Hệ quả:** kiểm tra chéo phải chia theo khối không gian, không chia theo ô hay theo polygon (xem [Kiểm chứng](/vi/methods/validation/)), và độ đa dạng thực sự của bộ nhãn thấp hơn nhiều so với con số 3.918 ô.

## Tập kiểm tra mù (đã chuẩn bị, chưa chấm)

- **File:** `labeling/blind_test_cells.gpkg`, layer `cells`, tạo bằng `scripts/make_blind_test.py` (seed ngẫu nhiên 20261114).
- **Thiết kế:** **250 ô 20 m × 20 m** chọn ngẫu nhiên đơn giản trong các ô nằm trong AOI, sạch mây hoàn toàn trên Sentinel-2 (cả bốn pixel 10 m đều sạch), cách mọi polygon huấn luyện ít nhất 200 m và cách nhau ít nhất 200 m. Ô được chọn mà không nhìn bản đồ dự đoán, và file không chứa dự đoán, nên việc chấm sẽ là "mù".
- **Mã nhãn:** 1 Nước, 2 Thực vật, 3 Đất trống, 4 Đô thị, 0 = lẫn lớp hoặc không rõ, −1 = chưa chấm.
- **Trạng thái:** cả 250 ô vẫn mang nhãn −1. **Nhóm đã quyết định không chấm tập này**, nên **không có ước lượng độ chính xác độc lập** cho bản đồ. Script đánh giá `scripts/eval_blind.py` (độ chính xác kèm khoảng tin cậy Wilson 95%, ma trận nhầm, tỷ lệ ô lẫn) đã sẵn sàng nhưng chưa bao giờ chạy trên nhãn thật.

## Xem nhãn và dự đoán cùng nhau

[Chế độ xem lớp phủ của bản đồ tương tác](/vi/?view=landcover) hiển thị dự đoán chỉ từ SAR; [chế độ xem độ tin cậy](/vi/?view=confidence) cho thấy bao nhiêu mô hình đồng ý và những nơi đặc trưng SAR khác hẳn mọi thứ trong bộ nhãn này (ngoài vùng áp dụng được).
