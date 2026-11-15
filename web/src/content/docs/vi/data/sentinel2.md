---
title: Ảnh quang học Sentinel-2
description: Cách tạo ảnh tổng hợp Sentinel-2 đã lọc mây, ảnh phủ được bao nhiêu AOI và vì sao chỉ dùng để vẽ nhãn.
sidebar:
  order: 3
---

Sentinel-2 (vệ tinh quang học của ESA, độ phân giải 10–20 m) trong dự án này **chỉ được dùng làm ảnh nền để vẽ nhãn huấn luyện**. Nó **không** phải đầu vào của mô hình lớp phủ hay của phát hiện thay đổi. Mọi thứ mô hình nhìn thấy đều đến từ radar NISAR, nên bản đồ áp dụng được cả ở vùng bị mây che, nơi Sentinel-2 không thấy gì.

## Ảnh tổng hợp Sentinel-2 dùng để vẽ nhãn (Google Earth Engine, 10 m)

- **File:** `data/s2/gee_10m/S2_composite_10m_aoi.tif` (đã cắt theo AOI; bản xuất chưa cắt vẫn để bên cạnh).
- **Tạo bằng:** `scripts/gee_s2_composite.js`, chạy trong Google Earth Engine Code Editor.
- **Bộ ảnh:** `COPERNICUS/S2_SR_HARMONIZED` (phản xạ bề mặt), từ 22/10 đến hết 3/11/2026.
- **Lọc mây:** Google Cloud Score+ (`GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED`), băng `cs_cdf`, giữ pixel khi cs_cdf ≥ **0,789** (càng cao càng nghiêm ngặt).
- **Tổng hợp:** lấy **trung vị** theo từng pixel của mọi lần quan sát sạch.
- **Băng (6):** B2 (lam), B3 (lục), B4 (đỏ), B8 (cận hồng ngoại), B11 (hồng ngoại sóng ngắn 1,6 µm) và `n_clear` (số lần quan sát sạch của mỗi pixel).
- **Lưới:** 10 m, UTM 48N (EPSG:32648), cùng phép chiếu với dữ liệu NISAR; 8.002 × 8.346 pixel sau khi cắt; int16; nodata = 0; nén deflate, có overview bên trong.
- **Hiển thị màu thật:** đỏ = băng 3 (B4), lục = băng 2 (B3), lam = băng 1 (B2).
- **Thang phản xạ:** phản xạ = DN × 0,0001. **Không** trừ thêm 0,1: bộ ảnh harmonized đã áp offset. Một lần trước đây trừ thêm offset đã cho phản xạ âm và báo sai NDVI.

## Độ phủ trời quang của Sentinel-2 trong khoảng nghiên cứu

- **Chỉ khoảng 32% AOI** có ít nhất một lần quan sát sạch (`n_clear` > 0) trong 22/10–3/11/2026. Khoảng 68% diện tích tỉnh hoàn toàn không có ảnh quang học dùng được trong khoảng này.
- **Không có ngày nào sạch:** ngày tốt nhất chỉ phủ khoảng 24% AOI.
- **Ảnh tổng hợp AWS cũ (không dùng):** một ảnh tổng hợp trước đó tạo từ Sentinel-2 L2A trên Earth Search (AWS), lọc theo lớp phân loại cảnh SCL (lớp 4, 5, 6 = thực vật, đất trống, nước), phủ 51,7% AOI (`data/s2/composite_20m.tif`, 20 m trên lưới SAR). Nhưng phần diện tích mà chỉ ảnh này coi là sạch có dấu hiệu nhiễm mây mỏng: trung vị phản xạ băng lam (B2) ở đó là 1129 (×10⁻⁴), so với 900 ở vùng cả hai nguồn đều coi là sạch. Vì vậy ưu tiên ảnh Earth Engine lọc bằng Cloud Score+.
- **Không dùng:** `data/s2/composite_20m_uint16_sai.tif` là file đã biết là sai (sai kiểu dữ liệu), bỏ qua.

## Vì sao Sentinel-2 không phải đầu vào mô hình

1. **Độ phủ:** chỉ khoảng 32% diện tích sạch, nên mô hình cần dữ liệu quang học chỉ lập được bản đồ cho tối đa một phần ba tỉnh.
2. **Tính độc lập:** không đưa dữ liệu quang học vào mô hình giúp kết quả đúng là phép thử xem riêng SAR làm được gì, đúng mục tiêu của thử thách.
3. **Đã kiểm tra tính đại diện:** dù nhãn chỉ vẽ được ở nơi Sentinel-2 sạch, [phân tích vùng áp dụng được](/vi/methods/validation/) cho thấy vùng mây và vùng sạch được đại diện như nhau trong không gian đặc trưng SAR (8,3% và 8,4% nằm ngoài vùng áp dụng được).

## Dynamic World (không dùng)

Sản phẩm lớp phủ Dynamic World của Google (tạo từ Sentinel-2) chỉ phủ **6,2% AOI** trong 22/10–3/11/2026, nên không dùng làm nhãn hay để so sánh.

## Các script liên quan tới Sentinel-2

| Script | Mục đích |
|---|---|
| `scripts/gee_s2_composite.js` | Script Earth Engine tạo và xuất ảnh tổng hợp 10 m |
| `scripts/check_gee_s2.py` | Kiểm tra file xuất và đối chiếu với ảnh tổng hợp AWS cũ |
| `scripts/clip_gee_s2.py` | Cắt ảnh theo AOI, tạo overview, ghi `aoi_32648.geojson` |
| `scripts/s2_scl_coverage.py`, `scripts/s2_composite.py` | Kiểm tra độ phủ và ảnh tổng hợp 20 m kiểu cũ từ AWS (Earth Search), đã thay thế |

Hình dưới là **ảnh tổng hợp AWS cũ** (đã thay thế; màu trắng = không có pixel sạch) và NDVI của nó. Hình cho thấy ngay cả khi gộp 12 ngày ảnh, phần lớn tỉnh vẫn bị mây che; ảnh Earth Engine thực sự dùng để vẽ nhãn phủ ít hơn (khoảng 32%) nhưng sạch hơn.

![Ảnh tổng hợp pixel sạch Sentinel-2 kiểu cũ từ AWS (trái) và NDVI (phải); vùng trắng không có quan sát sạch](/figures/common/s2_composite.png)
