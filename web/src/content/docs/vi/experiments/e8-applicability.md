---
title: "E8: Vùng áp dụng được của mô hình"
description: Chỉ số khác biệt trong không gian đặc trưng SAR đánh dấu 8,3% diện tích tỉnh nơi mô hình ngoại suy ra ngoài dữ liệu huấn luyện, gồm 23,5% số ô dự đoán là Đô thị.
sidebar:
  order: 8
---

**Câu hỏi.** Ở đâu mô hình lớp phủ gặp tín hiệu SAR không giống bất kỳ mẫu huấn luyện nào, tức là đang ngoại suy?

**Trả lời ngắn.** **8,3% AOI** nằm ngoài vùng áp dụng được (AOA). Tỷ lệ này như nhau ở vùng không mây và vùng mây, nên việc chỉ vẽ nhãn ở nơi Sentinel-2 sạch mây không làm mẫu kém đại diện trong không gian đặc trưng SAR. Nhưng **23,5% số ô dự đoán là Đô thị** nằm ngoài AOA, khiến Đô thị là lớp kém tin cậy nhất.

## Phương pháp E8: chỉ số khác biệt (Meyer & Pebesma, 2021)

1. Chuẩn hóa 12 đặc trưng SAR theo mẫu huấn luyện, nhân mỗi đặc trưng với độ quan trọng hoán vị từ [E3](/vi/experiments/e3-importance/) (độ quan trọng âm đặt bằng 0).
2. Với mỗi ô AOI, tính khoảng cách trong không gian đặc trưng có trọng số này tới **mẫu huấn luyện gần nhất**, chia cho khoảng cách trung bình giữa các mẫu huấn luyện. Đây là **chỉ số khác biệt (DI)**.
3. Tính DI cho các mẫu kiểm tra trong CV khối không gian 5 km (chỉ so với các fold huấn luyện). **Ngưỡng** là râu trên của boxplot (Q3 + 1,5 × IQR) = **0,105**.
4. Ô có DI > 0,105 nằm **ngoài vùng áp dụng được**.

## Kết quả E8

![E8: bản đồ vùng áp dụng được và chỉ số khác biệt](/figures/vi/E8_area_of_applicability.png)

| Chỉ số | Giá trị |
|---|---|
| Ngưỡng DI | 0,105 |
| AOI nằm ngoài AOA | **8,3%** |
| … ở vùng Sentinel-2 sạch mây (nơi vẽ nhãn) | 8,4% |
| … ở vùng mây | 8,3% |
| DI trung vị, vùng sạch so với vùng mây | 0,048 so với 0,048 |

Tỷ lệ ô ngoài AOA theo **lớp dự đoán** (bản đồ Random Forest):

| Nước | Thực vật | Đất trống | Đô thị |
|---|---|---|---|
| 4,5% | 0,7% | 4,9% | **23,5%** |

## E8: diễn giải

- **Vùng mây không kém hơn.** Khoảng 69% diện tích tỉnh không có ảnh quang học sạch trong giai đoạn này, và nhãn chỉ vẽ được ở 32% sạch mây. Phân tích AOA cho thấy tín hiệu SAR của vùng mây được dữ liệu huấn luyện bao phủ tốt như vùng sạch. Đây là tin tốt cho ý tưởng cốt lõi: lập bản đồ dưới mây bằng SAR.
- **Đô thị là lớp yếu.** Gần một phần tư số ô dự đoán Đô thị có tín hiệu SAR khác xa mọi mẫu huấn luyện. Các ô này tập trung ở phía bắc tỉnh. **Chưa được đối chiếu với bản đồ nền**, nên chưa biết đó là loại bề mặt gì.
- **Nước và Thực vật được bao phủ tốt** (4,5% và 0,7% nằm ngoài).

## E8: giới hạn của chỉ số khác biệt

DI đo **mức giống dữ liệu huấn luyện, không đo độ đúng.** Trong kiểm tra chéo, BA không giảm đều theo DI:

| Nhóm tứ phân vị DI (mẫu kiểm tra) | 0,01–0,03 | 0,03–0,04 | 0,04–0,06 | 0,06–1,01 |
|---|---|---|---|---|
| BA (%) | 86,7 | 94,2 | 91,1 | 83,6 |

Nhóm DI thấp nhất có độ chính xác thấp hơn các nhóm giữa. Một lý do khả dĩ là mẫu DI thấp rơi vào vùng chồng lấn dày đặc giữa Thực vật và Đất trống, nơi các lớp gần nhau trong không gian đặc trưng; **điều này chưa được kiểm tra.** Vì vậy nên đọc lớp AOA là "mô hình đang ngoại suy ở đây", không phải ước lượng sai số từng pixel.

## Kết quả E8 dùng trên bản đồ web

`aoa_dissimilarity.tif` lưu DI cho mọi ô (ngưỡng 0,105 ghi trong metadata). Trên [bản đồ tương tác](/vi/map/?view=confidence), ô ngoài AOA được đánh dấu cùng với lớp [mức đồng thuận mô hình E7](/vi/experiments/e7-map-agreement/).

**Tài liệu tham khảo.** Meyer, H. & Pebesma, E. (2021). Predicting into unknown space? Estimating the area of applicability of spatial prediction models. *Methods in Ecology and Evolution*, 12, 1620–1633.
