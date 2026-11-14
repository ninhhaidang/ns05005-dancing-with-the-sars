---
title: Thiết kế kiểm chứng
description: Cách đo độ chính xác của bộ phân loại lớp phủ chỉ dùng SAR, con số 93% có nghĩa là gì và không có nghĩa là gì.
sidebar:
  order: 4
---

Trang này giải thích cách đánh giá bộ phân loại lớp phủ: chỉ số, kiểm tra chéo theo không gian, ước lượng bất định, phân tích vùng áp dụng được, và giới hạn thật của tất cả những điều đó. Số liệu chi tiết của từng thí nghiệm nằm trong [mục Thí nghiệm](/vi/experiments/); code là `scripts/experiments.py`.

:::caution[Con số "93%" nghĩa là gì]
Con số chính, **độ chính xác cân bằng lớp ≈ 93%** (Random Forest 93,1%, SVM 93,6%), được đo bằng **kiểm tra chéo theo khối không gian 5 km trên ô 20 m thuần** nằm trong các polygon nhãn vẽ tay. Đây **không phải** độ chính xác của toàn bản đồ. Ô lẫn lớp và vùng xa nhãn chắc chắn kém chính xác hơn, và **độ chính xác ở mức bản đồ hiện chưa biết** vì tập kiểm tra mù độc lập chưa bao giờ được chấm.
:::

## Chỉ số chính: độ chính xác cân bằng lớp (BA)

- **Định nghĩa:** độ chính xác cân bằng lớp (balanced accuracy, BA) là trung bình recall (độ chính xác người sản xuất) của bốn lớp: BA = (recall_Nước + recall_ThựcVật + recall_ĐấtTrống + recall_ĐôThị) / 4.
- **Vì sao dùng BA thay cho độ chính xác tổng thể:** Nước chiếm 51% trong 3.918 mẫu, nên độ chính xác tổng thể (OA) bị thổi phồng bởi các ô nước dễ đoán. BA coi mọi lớp ngang nhau. Mô hình luôn đoán lớp đông nhất đạt OA 51,3% nhưng BA chỉ 25%.
- **Chốt trước:** BA theo kiểm tra chéo khối 5 km được chọn làm chỉ số chính trước khi chạy thí nghiệm, để tránh chọn con số đẹp nhất sau khi đã thấy kết quả.
- **Chỉ số phụ:** độ chính xác tổng thể, F1 macro, hệ số kappa Cohen, F1 từng lớp và ma trận nhầm lẫn.

## Kiểm tra chéo theo khối không gian (khối 5 km)

- **Vấn đề:** nhãn phân bố thành cụm (khoảng cách trung vị tới polygon cùng lớp gần nhất chỉ 102 m), và các ô 20 m cạnh nhau có đặc trưng gần như giống hệt, một phần vì đặc trưng được làm trơn trên 60–140 m. Chia ngẫu nhiên sẽ kiểm tra mô hình trên các ô sát cạnh ô huấn luyện, làm độ chính xác bị thổi phồng (**rò rỉ không gian**).
- **Giải pháp:** lưới AOI được chia thành **khối 5 km × 5 km** (250 × 250 ô). Mọi mẫu trong một khối thuộc cùng một fold, nên ô kiểm tra thường ở xa ô huấn luyện (khoảng cách trung vị 1.686 m).
- **Fold và số lần lặp:** 5 fold bằng `StratifiedGroupKFold` của scikit-learn (nhóm = khối, cân bằng tỷ lệ lớp giữa các fold), **lặp 5 lần** với cách gán khối vào fold ngẫu nhiên khác nhau. Mọi mô hình được đánh giá trên đúng cùng các fold.
- **Số khối:** 3.918 mẫu rơi vào 88 khối.

## Bất định: khoảng tin cậy bằng bootstrap theo khối

- **Khoảng tin cậy 95%** của BA được tính bằng **bootstrap theo khối**: lấy lại các khối 5 km có hoàn lại 2.000 lần và tính lại BA trên dự đoán ngoài fold mỗi lần. Lấy lại theo khối thay vì theo ô giúp tôn trọng tương quan không gian.
- **Chênh lệch giữa mô hình:** hiệu BA của mỗi mô hình so với Random Forest được tính trên cùng các mẫu bootstrap, cho ra khoảng tin cậy của hiệu.
- **Kiểm định McNemar** cũng được báo cáo, nhưng giá trị p của nó lạc quan vì các ô lân cận không độc lập.
- **Ví dụ:** Random Forest BA 93,1% (khoảng tin cậy 95%: 90,5–95,0%); SVM 93,6% (91,4–95,8%).

## Cách chia dữ liệu làm thay đổi kết quả

Thí nghiệm E4 so sánh nhiều cách chia tập huấn luyện và kiểm tra (BA của Random Forest):

| Cách chia | Khoảng cách trung vị kiểm tra → huấn luyện | BA |
|---|---|---|
| Ngẫu nhiên theo ô (rò rỉ) | 20 m | 95,9% |
| Theo polygon | 300 m | 94,1% |
| Khối 5 km (chính) | 1.686 m | 93,1% |
| Khối 5 km + vùng đệm 1 km | 2.500 m | 92,8% |
| Khối 20 km | 4.099 m | 91,4% |
| Hai nửa Tây / Đông | 18,7 km | 87,0% |
| Hai nửa Bắc / Nam | 17,9 km | 83,8% |

- **Rò rỉ là có thật:** chia ngẫu nhiên theo ô lạc quan khoảng 3 điểm; ngay cả chia theo polygon cũng lạc quan khoảng 1 điểm.
- **Vùng đệm gần như không ảnh hưởng:** bỏ các ô huấn luyện trong phạm vi 250 m hoặc 1 km quanh ô kiểm tra làm BA đổi tối đa 0,3 điểm, nên việc làm trơn đặc trưng không gây rò rỉ qua biên khối.
- **Chia theo vùng giảm mạnh (83–87%),** một phần vì các lớp phân bố không đều: Đô thị có 618 mẫu ở phía bắc và chỉ 7 ở phía nam, nên mô hình học từ phía nam gần như không biết Đô thị.

## Độ chính xác theo khoảng cách tới nhãn

- **Đo trên ô kiểm tra trong kiểm tra chéo (Random Forest, khối 5 km):** BA 98–100% với ô cách ô huấn luyện dưới 500 m, 93,7% ở 500 m–2 km, và 90,7% ở 2–5 km.
- **Khoảng cách của toàn AOI tới mẫu huấn luyện gần nhất:** 12% ô AOI trong phạm vi 500 m, 44% ở 0,5–2 km, 32% ở 2–5 km và 12% ở 5–10 km. Như vậy **khoảng 44% AOI cách mọi nhãn hơn 2 km**, nơi độ chính xác đo trên ô thuần chỉ khoảng 90%.

## Vùng áp dụng được (AOA) và chỉ số khác biệt (DI)

Vùng áp dụng được (area of applicability, Meyer & Pebesma, 2021) đánh dấu những nơi mô hình phải dự đoán cho giá trị đặc trưng SAR không giống bất kỳ mẫu huấn luyện nào.

1. **Không gian đặc trưng có trọng số:** mỗi đặc trưng trong 12 đặc trưng được chuẩn hóa (trung bình 0, độ lệch chuẩn 1 trên các mẫu huấn luyện) rồi nhân với độ quan trọng hoán vị của nó từ thí nghiệm E3.
2. **Chỉ số khác biệt:** với mỗi ô AOI, DI = (khoảng cách tới mẫu huấn luyện gần nhất trong không gian này) / (khoảng cách trung bình giữa các cặp mẫu huấn luyện, ước lượng trên 3.000 mẫu ngẫu nhiên).
3. **Ngưỡng:** DI cũng được tính cho mẫu kiểm tra trong kiểm tra chéo so với fold huấn luyện của chính nó (khối 5 km). Ngưỡng là râu trên của phân bố đó, Q3 + 1,5 × IQR = **0,105**. Ô có DI > 0,105 nằm **ngoài vùng áp dụng được**.
4. **Đầu ra:** `data/derived/aoa_dissimilarity.tif` (DI kiểu float32 cho từng ô; ngưỡng lưu ở tag).

**Kết quả vùng áp dụng được:**
- **8,3% AOI nằm ngoài vùng áp dụng được.** Tỷ lệ này như nhau ở nơi Sentinel-2 sạch (8,4%) và nơi bị mây (8,3%), và DI trung vị bằng nhau (0,048). Vậy việc chỉ vẽ nhãn ở vùng không mây không làm dữ liệu huấn luyện kém đại diện cho vùng mây trong không gian đặc trưng SAR.
- **Theo lớp dự đoán:** 23,5% số ô dự đoán là Đô thị nằm ngoài vùng áp dụng được, so với 4,5–4,9% ở Nước và Đất trống và 0,7% ở Thực vật. **Đô thị là lớp kém tin cậy nhất.**
- **Giới hạn:** DI đo mức giống dữ liệu huấn luyện, không đo độ đúng. Trong kiểm tra chéo, BA theo tứ phân vị DI (từ thấp đến cao) là 86,7%, 94,2%, 91,1%, 83,6%, nên độ chính xác không giảm đều theo DI.

## Mức đồng thuận giữa mô hình làm lớp độ tin cậy

Mười mô hình khác nhau (Random Forest, Extra Trees, các biến thể gradient boosting, MLP, hồi quy logistic, LDA, QDA) được huấn luyện trên toàn bộ mẫu và áp dụng cho cả AOI. Cả 10 mô hình đồng ý trên **65,9% AOI**; chỉ 3,0% số ô có từ 5 mô hình trở xuống đồng ý với lớp đa số. Số mô hình đồng thuận ở từng ô (`data/derived/landcover_model_agreement.tif`, giá trị 3–10) được hiển thị thành lớp độ tin cậy trên [bản đồ](/vi/map/?view=confidence). Đồng thuận cao không chứng minh là đúng: mọi mô hình học từ cùng một bộ nhãn và mang cùng thiên lệch.

## Tập kiểm tra mù: đã chuẩn bị nhưng không dùng

- **250 ô 20 m ngẫu nhiên** (`labeling/blind_test_cells.gpkg`) được chọn ngẫu nhiên đơn giản trong vùng không mây, cách polygon huấn luyện ít nhất 200 m và cách nhau ít nhất 200 m, không nhìn dự đoán. Xem [Nhãn](/vi/data/labels/).
- **Chưa chấm:** nhóm quyết định không chấm, nên `scripts/eval_blind.py` chưa chạy trên nhãn thật.
- **Hệ quả:** **không có ước lượng độ chính xác độc lập dựa trên thiết kế mẫu** và **không có ước lượng diện tích đã hiệu chỉnh sai lệch** (phương pháp thực hành tốt của Olofsson và cộng sự, 2014 cần đúng một mẫu xác suất như vậy).

## Tóm tắt điều đã và chưa được kiểm chứng

| Khẳng định | Trạng thái |
|---|---|
| BA ≈ 93% trên ô thuần, kiểm tra chéo khối 5 km | Đã đo |
| Chọn mô hình gần như không quan trọng; ba ngày và hai phân cực mới quan trọng | Đã đo (kiểm tra chéo) |
| Độ chính xác toàn bản đồ, kể cả ô lẫn lớp | **Chưa biết** |
| Tỷ lệ diện tích (Đô thị ≈ 24%, Đất trống ≈ 44%) | **Chưa kiểm chứng, chưa hiệu chỉnh sai lệch** |
| Độ tin cậy của lớp Đô thị | Lớp yếu nhất (23,5% ngoài vùng áp dụng được) |

**Tài liệu tham khảo:** Meyer, H. & Pebesma, E. (2021). Predicting into unknown space? Estimating the area of applicability of spatial prediction models. *Methods in Ecology and Evolution*, 12, 1620–1633. Olofsson, P. và cộng sự (2014). Good practices for estimating area and assessing accuracy of land change. *Remote Sensing of Environment*, 148, 42–57.
