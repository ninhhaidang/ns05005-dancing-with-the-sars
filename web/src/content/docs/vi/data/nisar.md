---
title: Dữ liệu NISAR GCOV
description: Ba lần chụp NISAR băng L GCOV VALIDATED trên Hưng Yên mà dự án dùng, các lớp dữ liệu, lưới pixel và những điểm cần lưu ý.
sidebar:
  order: 1
---

Đầu vào duy nhất của mô hình là tán xạ ngược radar từ **NISAR**, sứ mệnh radar khẩu độ tổng hợp chung của NASA và ISRO. Dự án dùng sản phẩm mức 2 **GCOV** (Geocoded polarimetric COVariance) ở mức hoàn thiện **VALIDATED**, phiên bản xử lý (CRID) **P05036**, **tần số A** của radar băng L. Sản phẩm GCOV VALIDATED có từ ngày 21/10/2026.

## Các lần chụp được dùng

| Ngày (2026) | Track quỹ đạo | Hướng bay | Kích thước pixel | Độ phủ AOI | Dùng? |
|---|---|---|---|---|---|
| 22/10 | 148 | Xuống (descending) | 20 m | 100% | Có |
| 27/10 | 054 | Lên (ascending) | 10 m | 100% | Có |
| 3/11 | 148 | Xuống | 20 m | 100% | Có |
| 29/10 | 076 | Xuống | — | 4% | Không (phủ quá ít) |

- **Cặp cùng track cho phát hiện thay đổi:** 22/10 và 3/11 cùng track 148 hướng xuống, cách nhau 12 ngày. Cùng hình học chụp nên chênh lệch tán xạ phản ánh thay đổi trên mặt đất chứ không phải do đổi góc nhìn. Hai ngày này dùng cho [phát hiện thay đổi](/vi/methods/change-detection/).
- **Ngày 27/10 nhìn từ phía khác:** ảnh 27/10 chụp ở lượt bay lên (track 054), radar nhìn mặt đất từ phía đối diện. Ảnh này bổ sung thông tin cho [phân loại](/vi/methods/classification/) (nhà cửa tán xạ khác nhau tùy hướng nhìn) nhưng không dùng trong phép kiểm định thay đổi 22/10 → 3/11.
- **Quy tắc khoảng thời gian:** dự án chỉ dùng dữ liệu từ 22/10 đến 3/11/2026. Không dùng sản phẩm PROVISIONAL, không dùng dữ liệu cũ hơn.

Mã sản phẩm đầy đủ (ví dụ ngày 22/10): `NISAR_L2_PR_GCOV_033_148_D_078_2005_DHDH_A_20261022T112852_20261022T112927_P05036_N_F_J_001`. Sản phẩm 27/10 là `..._034_054_A_012_4005_DHDH_A_20261027T222209_...`, sản phẩm 3/11 là `..._034_148_D_078_2005_DHDH_A_20261103T112853_...`. Các lượt bay xuống chụp khoảng 11:29 UTC (khoảng 18:29 giờ Việt Nam), lượt bay lên khoảng 22:22 UTC (khoảng 05:22 sáng hôm sau giờ Việt Nam). URL nguồn và mã băm SHA-256 của file HDF5 gốc được ghi trong `data/manifest.json`.

## Các lớp trong mỗi file NISAR GCOV

Với mỗi ngày, tần số A của file GCOV HDF5 được cắt theo AOI và ghi thành 6 lớp GeoTIFF (xem [Tiền xử lý](/vi/methods/preprocessing/)):

| Lớp | Ý nghĩa | Kiểu dữ liệu, nodata |
|---|---|---|
| `HHHH` | Công suất tán xạ ngược HH (phát ngang, thu ngang), thang tuyến tính | float32, NaN |
| `HVHV` | Công suất tán xạ ngược HV (phát ngang, thu đứng; phân cực chéo), thang tuyến tính | float32, NaN |
| `numberOfLooks` | Số look được lấy trung bình trong mỗi pixel (quyết định mức speckle) | float32, NaN |
| `rtcGammaToSigmaFactor` | Hệ số đổi giá trị γ⁰ (gamma-naught) đã hiệu chỉnh địa hình sang σ⁰ (sigma-naught) | float32, NaN |
| `mask` | Mặt nạ hợp lệ; trong AOI mọi pixel bằng 1, ngoài AOI bằng 255 | uint8, 255 |
| `inputDataExceptionMask` | Cờ báo lỗi của dữ liệu đầu vào | uint16, 65535 |

- **Đơn vị:** giá trị là công suất tuyến tính. Đổi sang decibel bằng dB = 10·log10(giá trị). Mọi ngưỡng trong dự án (ví dụ −15 dB) đều tính bằng dB.
- **Quy ước tán xạ:** dự án dùng nguyên giá trị HHHH và HVHV lưu trong GCOV (γ⁰ đã hiệu chỉnh địa hình). Lớp `rtcGammaToSigmaFactor` được giữ lại nhưng không áp dụng; trên vùng đồng bằng phẳng này trung vị của nó khoảng −1,07 dB ở track xuống và −1,17 dB ở track lên.
- **Giá trị điển hình trên AOI (phân vị 5 / 50 / 95, dB):** HH ngày 22/10: −15,2 / −8,2 / 0,0; HV ngày 22/10: −22,1 / −15,1 / −8,5. Hai ngày còn lại chênh không quá khoảng 1 dB.
- **Số look:** trung vị khoảng 8,95 look mỗi pixel 20 m ở hai ngày bay xuống, khoảng 4,64 look mỗi pixel 10 m ở ngày 27/10.
- **Tần số B** (thô hơn, khoảng 80 m ở vùng này) có trong file nhưng không dùng.

## Lưới pixel và độ phủ của ảnh NISAR

- **Hệ tọa độ:** UTM múi 48N (EPSG:32648), là phép chiếu gốc của lưới GCOV trên Hưng Yên; khi cắt không phải nội suy lại.
- **Hai ngày 20 m (22/10, 3/11):** 4.001 × 4.174 pixel, phạm vi x 592.920–672.940 m, y 2.239.820–2.323.300 m. Trong AOI có 6.429.330 pixel hợp lệ (2.571,7 km²).
- **Ngày 10 m (27/10):** 8.002 × 8.346 pixel trên cùng phạm vi. Khi phân loại, ảnh này được lấy trung bình về lưới 20 m (mỗi ô 20 m = trung bình 2 × 2 pixel theo công suất tuyến tính).
- **Vùng dữ liệu hợp lệ:** vùng hợp lệ của cả ba ngày trùng khít với AOI rasterize trên lưới UTM. Pixel ngoài ranh giới tỉnh là nodata.

## Lưu ý chất lượng dữ liệu NISAR GCOV

- **VALIDATED không có nghĩa là hoàn hảo:** VALIDATED nghĩa là sản phẩm đã qua giai đoạn hiệu chuẩn và kiểm định của sứ mệnh, nhưng NISAR vẫn công bố các lỗi đã biết (known issues) cho sản phẩm giai đoạn đầu. Dự án không áp dụng thêm hiệu chỉnh bức xạ nào.
- **Speckle:** mỗi pixel đều nhiễu do speckle (giao thoa ngẫu nhiên của các sóng phản hồi). Dự án giảm speckle bằng cách lấy trung bình (làm trơn 3 × 3 khi phân loại; cửa sổ 5 × 5 kèm mô hình thống kê khi phát hiện thay đổi).
- **File HDF5 gốc đã xóa** sau khi cắt để tiết kiệm dung lượng. Có thể tải lại từ các URL trong `data/manifest.json` (xem [Tái tạo kết quả](/vi/reproduce/)).

## Xem ảnh NISAR

[Chế độ xem SAR của bản đồ tương tác](/vi/?view=sar) hiển thị mỗi ngày dưới dạng ảnh màu giả. Đổi ngày bằng thanh trượt, ví dụ [22/10](/vi/?view=sar&date=2026-10-22), [27/10](/vi/?view=sar&date=2026-10-27), [3/11](/vi/?view=sar&date=2026-11-03).

![Ảnh xem nhanh HH và HV (dB) của ba ngày](/figures/common/quicklook.png)
