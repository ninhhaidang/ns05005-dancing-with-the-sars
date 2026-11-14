---
title: Phương pháp phát hiện thay đổi
description: Phép kiểm định log tỷ số có hiệu chỉnh tương quan speckle dùng để tìm các thay đổi tán xạ có ý nghĩa giữa 22/10 và 3/11/2026.
sidebar:
  order: 2
---

Phát hiện thay đổi so sánh hai ảnh NISAR chụp từ **cùng một track quỹ đạo** (track 148, bay xuống): **22/10/2026** và **3/11/2026**, cách nhau 12 ngày. Cùng track nghĩa là cùng hình học chụp, nên chênh lệch tán xạ phản ánh điều gì đó đã thay đổi trên mặt đất. Mục tiêu là tìm các thay đổi do điều tiết nước (ruộng, ao hay khu đê bao được cho nước vào hoặc tháo ra) trong khi giữ báo động giả do speckle radar ở mức cực hiếm. Code: `scripts/change_detection.py`.

## Ý tưởng: kiểm định z trên log tỷ số của hai ảnh radar

Cường độ radar bị nhiễu do **speckle**: kể cả khi không có gì thay đổi, hai ảnh của cùng một thửa ruộng vẫn khác nhau ngẫu nhiên. Lấy trung bình *L* look độc lập sẽ giảm nhiễu này. Theo mô hình chuẩn, cường độ đa look tuân theo **phân bố Gamma với L look**, và logarit của tỷ số hai ảnh độc lập có phương sai đã biết:

- log tỷ số: **r = ln(Ī₂ / Ī₁)**, trong đó Ī₁ và Ī₂ là cường độ trung bình trong cửa sổ ngày 22/10 và 3/11 (công suất tuyến tính).
- độ lệch chuẩn lý thuyết: **σ = √( ψ₁(L₁) + ψ₁(L₂) )**, trong đó ψ₁ là hàm trigamma, L₁ và L₂ là số look hiệu dụng của hai cửa sổ.
- thống kê kiểm định: **z = r / (f · σ)**, với f là hệ số hiệu chỉnh tương quan speckle (xem dưới).

z âm lớn nghĩa là tán xạ giảm có ý nghĩa; z dương lớn nghĩa là tán xạ tăng. Mức thay đổi tính bằng dB, dùng để diễn giải, là 10·log10(Ī₂/Ī₁).

## Từng bước: cửa sổ, số look hiệu dụng, hệ số hiệu chỉnh

1. **Ô hợp lệ:** một ô 20 m chỉ được dùng nếu HH hữu hạn ở cả hai ngày và `numberOfLooks` > 0 ở cả hai ngày.
2. **Lấy trung bình trong cửa sổ:** với mỗi ô, cường độ được lấy trung bình trong **cửa sổ 5 × 5** (100 m × 100 m), chỉ tính ô hợp lệ. Làm riêng cho HH và HV, riêng cho từng ngày, trên công suất tuyến tính.
3. **Số look hiệu dụng:** L của mỗi ngày là **tổng `numberOfLooks` của các ô hợp lệ trong cửa sổ** (khoảng 25 × 8,95 ≈ 224 look với cửa sổ đầy đủ). Cách tính này giả định look của các pixel lân cận độc lập, điều không hoàn toàn đúng.
4. **Hệ số hiệu chỉnh tương quan speckle f:** vì các pixel lân cận tương quan với nhau, độ phân tán thực của r lớn hơn σ dự đoán. Script đo nó một cách bền vững trên toàn AOI: **f = 1,4826 · MAD(r) / trung vị(σ)**, trong đó MAD là độ lệch tuyệt đối trung vị (1,4826·MAD ước lượng độ lệch chuẩn khi phần lớn ô không thay đổi). Giá trị thu được là **f ≈ 1,6–1,7** (f = 1 nghĩa là các pixel độc lập). Chia cho f·σ giúp z ở vùng không đổi có dạng gần biến chuẩn tắc.
5. **Ngưỡng:** một phân cực thay đổi có ý nghĩa khi **|z| > 5**. Với biến chuẩn tắc, |z| > 5 xảy ra ngẫu nhiên khoảng một lần trong 1,7 triệu ô, nên speckle ngẫu nhiên gần như không bao giờ vượt ngưỡng.

## Các lớp thay đổi và quy tắc phân lớp

Mỗi ô hợp lệ được gán một lớp, dựa trên z của HH (z_HH) và HV (z_HV):

| Lớp | Tên | Quy tắc |
|---|---|---|
| 1 | Không đổi đáng kể | không thỏa quy tắc nào bên dưới |
| 2 | **Nước mới / bề mặt phẳng hóa** | z_HH < −5 và z_HV < −5, và HH ngày 3/11 < −15 dB |
| 3 | Giảm cả HH và HV (khác) | z_HH < −5 và z_HV < −5, và HH ngày 3/11 ≥ −15 dB |
| 4 | Tăng cả HH và HV | z_HH > 5 và z_HV > 5 |
| 5 | Chỉ HV giảm | \|z_HV\| > 5, z_HV < 0, và \|z_HH\| ≤ 5 |
| 6 | Chỉ HV tăng | \|z_HV\| > 5, z_HV > 0, và \|z_HH\| ≤ 5 |

- **Hai phân cực phải đồng thuận** với lớp 2–4, giúp giảm thêm báo động giả.
- **Quy tắc −15 dB cho lớp 2:** mặt nước lặng phản xạ tín hiệu radar đi chỗ khác như gương (phản xạ gương), nên rất tối ở HH, thường dưới −15 dB. Một lần giảm có ý nghĩa mà kết thúc dưới −15 dB vì vậy được gán "nước mới / phẳng hóa". Ngưỡng này là quy tắc kinh nghiệm, chưa hiệu chuẩn trên dữ liệu thay đổi có nhãn.
- **Diện tích mảng tối thiểu:** các mảng liền nhau của lớp 2–6 nhỏ hơn **125 ô (0,05 km² = 5 ha)** được đưa về lớp 1. Do đó các ao đơn lẻ nhỏ không được báo.

## Đầu ra của phát hiện thay đổi

- **Raster:** `data/derived/change_class_22oct_3nov.tif` (uint8, 20 m, 0 = ngoài AOI, 1–6 = các lớp trên).
- **Bảng mảng:** `outputs/change_patches.csv`, mỗi dòng một mảng: lớp, diện tích (km²), kinh độ/vĩ độ tâm, HH trung bình ngày 22/10 và 3/11 (dB).
- **Hình:** `outputs/change_detection.png`.

## Kết quả phát hiện thay đổi bằng số

| Lớp | Diện tích | Tỷ lệ AOI | Số mảng |
|---|---|---|---|
| 1 Không đổi đáng kể | 2.569,0 km² | 99,89% | — |
| 2 Nước mới / phẳng hóa | 1,58 km² | 0,061% | 5 |
| 3 Giảm HH và HV (khác) | 0,38 km² | 0,015% | 5 |
| 4 Tăng HH và HV | 0,58 km² | 0,023% | 7 |
| 5 Chỉ HV giảm | 0 km² | 0% | 0 |
| 6 Chỉ HV tăng | 0,16 km² | 0,006% | 2 |

- **Phát hiện chính:** cả 5 mảng "nước mới" (tổng 1,58 km²; hai mảng lớn nhất 0,71 km² và 0,62 km²) nằm chung một cụm quanh **106,47–106,49°E, 20,46–20,48°N**, cạnh một khúc sông ở phía đông nam tỉnh. Bốn trong năm mảng lớp 3 cũng nằm trong cụm này. Ở cụm này HH giảm từ khoảng −10 xuống −16 dB và HV từ khoảng −17 xuống −23 dB, và đã bắt đầu giảm từ ngày 27/10 (thấy trên ảnh bay lên). Khu này có dạng khối chữ nhật.
- **Diễn giải (giả thuyết):** một khu ruộng, ao hoặc đê bao được cho nước vào giữa 22/10 và 3/11. **Chưa được kiểm chứng**: không có ảnh quang học sạch nào để xác nhận.
- **Các mảng tăng (lớp 4)** nhỏ (0,05–0,13 km²) và rải rác, phần lớn ở phía tây bắc tỉnh (khoảng 106,05–106,10°E, 20,73–20,85°N) và gần 106,30°E, 20,56°N. Nguyên nhân chưa được tìm hiểu.
- **Không có tín hiệu thu hoạch lúa:** không thấy kiểu thay đổi diện rộng nào khớp với việc gặt trong 12 ngày này; phần lớn lúa có vẻ đã gặt trước 22/10.

![Các thay đổi có ý nghĩa 22/10 → 3/11](/figures/common/change_detection.png)

![Chênh lệch HH và HV, 3/11 trừ 22/10, đơn vị dB](/figures/common/change_22oct_3nov.png)

Xem [chế độ xem thay đổi trên bản đồ tương tác](/vi/?view=change) và [Kết quả thay đổi](/vi/results/change/).

## Hạn chế của phát hiện thay đổi

- **Chỉ hai ngày, cách nhau 12 ngày:** thay đổi trước 22/10 hoặc sau 3/11 không thấy được.
- **Không dùng 27/10 trong phép kiểm định:** ảnh này từ quỹ đạo và hướng nhìn khác nên tán xạ không so sánh trực tiếp được; nó chỉ dùng làm bằng chứng bổ trợ.
- **Ngưỡng nghiêm ngặt:** |z| > 5, yêu cầu HH và HV đồng thuận, và diện tích tối thiểu 5 ha giúp rất ít báo động giả nhưng bỏ sót thay đổi nhỏ hoặc yếu.
- **Hệ số hiệu chỉnh toàn cục:** f được ước lượng một lần cho cả AOI; khác biệt cục bộ về tương quan speckle không được mô hình hóa.
- **Ngưỡng nước là quy tắc kinh nghiệm:** mặt nước gợn sóng do gió có thể sáng hơn −15 dB, còn bề mặt rất phẳng (ví dụ đất trống ẩm) có thể tối hơn.
- **Nguyên nhân vật lý chưa được kiểm chứng** ở mọi mảng phát hiện được.
