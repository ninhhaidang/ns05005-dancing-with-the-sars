---
title: Thuật ngữ
description: Định nghĩa dễ hiểu cho các thuật ngữ radar, viễn thám và học máy dùng trên trang này.
sidebar:
  order: 5
---

Định nghĩa ngắn cho các thuật ngữ kỹ thuật dùng trong dự án, kèm ghi chú về cách mỗi khái niệm áp dụng ở đây.

## Thuật ngữ radar và NISAR

**SAR (Synthetic Aperture Radar, radar khẩu độ tổng hợp)**
Radar tạo ảnh đặt trên vệ tinh hoặc máy bay. Nó phát xung vi ba rồi ghi lại tín hiệu phản hồi; bằng cách kết hợp các phản hồi dọc đường bay, nó "tổng hợp" một ăng-ten dài hơn nhiều và đạt độ phân giải cao. SAR tự chiếu sáng nên hoạt động cả ngày lẫn đêm và xuyên qua mây. Trong dự án, SAR là đầu vào duy nhất của mô hình vì mây đã che khoảng 68% diện tích tỉnh trước vệ tinh quang học.

**NISAR**
Sứ mệnh radar khẩu độ tổng hợp chung của NASA và ISRO, vệ tinh đầu tiên mang cả radar băng L (của NASA) lẫn radar băng S (của ISRO). Dự án dùng dữ liệu băng L.

**Băng L**
Bước sóng radar khoảng 24 cm. Bước sóng dài xuyên sâu hơn vào tán cây và ít nhạy với lá nhỏ hơn bước sóng ngắn (băng C, khoảng 5,6 cm, của Sentinel-1), nên băng L "nhìn thấy" thân, cành và mặt đất bên dưới cây trồng.

**Tần số A / tần số B**
Sản phẩm NISAR có thể chứa hai dải con. Tần số A là dải chính; dự án chỉ dùng tần số A (20 m ở track bay xuống, 10 m ở track bay lên). Tần số B thô hơn ở vùng này (khoảng 80 m) và không được dùng.

**GCOV (Geocoded polarimetric COVariance)**
Sản phẩm mức 2 của NISAR: tán xạ ngược radar đã được nắn về lưới bản đồ (ở đây là UTM 48N) và hiệu chỉnh bức xạ theo địa hình. Nó lưu các thành phần hiệp phương sai phân cực; các thành phần đường chéo `HHHH` và `HVHV` là công suất tán xạ HH và HV. Xem [Dữ liệu NISAR](/vi/data/nisar/).

**VALIDATED / PROVISIONAL**
Các mức hoàn thiện của sản phẩm NISAR. Sản phẩm VALIDATED (ở đây là phiên bản xử lý CRID P05036, có từ 21/10/2026) đã qua hiệu chuẩn và kiểm định; sản phẩm PROVISIONAL trước đó không được dùng trong dự án.

**CRID**
Composite Release ID: phiên bản xử lý của một sản phẩm NISAR (ở đây là P05036).

**Track, bay lên, bay xuống**
Track là một đường quỹ đạo lặp lại. Lượt bay xuống (descending) đi từ bắc xuống nam, lượt bay lên (ascending) từ nam lên bắc, nên radar nhìn mặt đất từ hai phía đối diện. Trong dự án, 22/10 và 3/11 thuộc track 148 (bay xuống), 27/10 thuộc track 054 (bay lên).

**Tán xạ ngược (backscatter)**
Phần năng lượng radar quay về cảm biến. Vùng sáng phản hồi nhiều (nhà cửa), vùng tối phản hồi ít (mặt nước lặng).

**σ⁰ (sigma-naught) và γ⁰ (gamma-naught)**
Các đại lượng chuẩn hóa của tán xạ ngược. σ⁰ chuẩn hóa theo diện tích mặt đất; γ⁰ chuẩn hóa theo diện tích nhìn vuông góc với chùm tia radar và là quy ước của các sản phẩm hiệu chỉnh địa hình (RTC). GCOV cung cấp γ⁰ cùng một lớp (`rtcGammaToSigmaFactor`) để đổi sang σ⁰. Dự án dùng nguyên γ⁰ như được cung cấp.

**RTC (Radiometric Terrain Correction, hiệu chỉnh bức xạ địa hình)**
Hiệu chỉnh độ sáng tán xạ theo ảnh hưởng của sườn dốc quay về phía hoặc quay đi khỏi radar. Hưng Yên gần như bằng phẳng nên ảnh hưởng này nhỏ.

**Phân cực: HH và HV**
Hướng dao động điện trường của sóng radar. HH = phát ngang, thu ngang (đồng phân cực); HV = phát ngang, thu đứng (phân cực chéo). HV sinh ra chủ yếu do tán xạ nhiều lần trong thực vật, nên là chỉ báo tốt cho thực vật. HV là phân cực hữu ích nhất trong bộ phân loại của dự án.

**dB (decibel)**
Thang logarit cho tán xạ ngược: dB = 10·log10(công suất tuyến tính). Giảm 6 dB nghĩa là công suất phản hồi chỉ còn khoảng một phần tư. Giá trị điển hình ở đây: mặt nước lặng dưới khoảng −15 dB ở HH; HH trung vị trên AOI khoảng −8 dB.

**Speckle (nhiễu đốm)**
Nhiễu dạng hạt, trông ngẫu nhiên, có trong mọi ảnh radar, sinh ra do giao thoa phản hồi từ nhiều vật tán xạ trong một pixel. Đây không phải nhiễu cảm biến và không tự triệt tiêu trong một pixel; muốn giảm phải lấy trung bình nhiều look hoặc nhiều pixel lân cận.

**Look / số look**
Các mẫu độc lập được lấy trung bình vào một pixel. Càng nhiều look thì speckle càng ít. GCOV cho biết số look của từng pixel (trung vị khoảng 8,95 look mỗi pixel 20 m ở các ngày bay xuống, khoảng 4,64 look mỗi pixel 10 m ở ngày 27/10).

**ENL (Equivalent Number of Looks, số look tương đương)**
Số look độc lập sẽ tạo ra đúng mức speckle quan sát được. Khi các pixel lân cận tương quan với nhau, ENL của một cửa sổ nhỏ hơn tổng số look đơn thuần; phát hiện thay đổi của dự án hiệu chỉnh điều này bằng hệ số f ≈ 1,6–1,7.

**Phản xạ gương (specular reflection)**
Phản xạ như gương từ bề mặt phẳng, ví dụ mặt nước lặng: tín hiệu radar bật đi xa khỏi vệ tinh, nên bề mặt trông rất tối. Vì vậy mặt nước mới xuất hiện cho thấy cả HH và HV giảm mạnh.

**Tán xạ hai lần (double-bounce)**
Tín hiệu bật từ mặt đất rồi từ tường thẳng đứng (hoặc ngược lại) và quay thẳng về radar, như một gương góc. Nó làm nhà cửa rất sáng ở HH và phụ thuộc hướng của nhà so với hướng nhìn. Thực vật bị ngập nước cũng có thể gây tán xạ hai lần.

**Tán xạ khối (volume scattering)**
Tán xạ nhiều lần bên trong một khối như tán cây trồng hay tán cây gỗ. Nó tạo tín hiệu HV tương đối mạnh và là đặc trưng của thực vật.

**Phát hiện thay đổi bằng log tỷ số**
So sánh hai ảnh radar qua logarit tỷ số cường độ, r = ln(I₂/I₁). Log tỷ số biến speckle dạng nhân thành một thành phần cộng có thống kê đã biết, nhờ đó làm được kiểm định thống kê. Xem [Phát hiện thay đổi](/vi/methods/change-detection/).

**Hàm trigamma ψ₁**
Đạo hàm bậc hai của logarit hàm gamma. Với cường độ có phân bố Gamma L look, phương sai của ln(cường độ) là ψ₁(L); từ đó biết độ phân tán kỳ vọng của log tỷ số khi không có gì thay đổi.

**Điểm z (z-score)**
Một chênh lệch chia cho độ lệch chuẩn kỳ vọng của nó. Trong phép kiểm định thay đổi của dự án, yêu cầu |z| > 5 ở cả HH và HV.

## Thuật ngữ quang học và không gian địa lý

**Sentinel-2**
Vệ tinh quang học của ESA (10–20 m). Ở đây chỉ dùng làm ảnh để vẽ nhãn. Xem [Sentinel-2](/vi/data/sentinel2/).

**Cloud Score+**
Điểm chất lượng mây và bóng mây theo từng pixel của Google cho Sentinel-2 (`cs_cdf`, 0–1). Dự án giữ pixel có cs_cdf ≥ 0,789.

**Ảnh tổng hợp trung vị**
Ảnh mà mỗi pixel là trung vị của mọi lần quan sát sạch trong một khoảng thời gian, ở đây là 22/10–3/11/2026.

**Dynamic World**
Sản phẩm lớp phủ 10 m gần thời gian thực của Google, tạo từ Sentinel-2. Nó chỉ phủ 6,2% AOI trong khoảng nghiên cứu nên không được dùng.

**AOI (Area of Interest, vùng nghiên cứu)**
Khu vực nghiên cứu: tỉnh Hưng Yên sau sáp nhập, 2.571,7 km² (diện tích hình học). Xem [Vùng nghiên cứu](/vi/data/aoi/).

**UTM 48N / EPSG:32648**
Phép chiếu bản đồ dùng cho mọi raster (đơn vị mét, Universal Transverse Mercator múi 48 Bắc).

**Ô thuần**
Ô 20 m có ít nhất 80% diện tích thuộc một lớp nhãn. Chỉ ô thuần được dùng làm mẫu huấn luyện và kiểm tra.

## Thuật ngữ học máy và độ chính xác

**Random Forest (rừng ngẫu nhiên)**
Tập hợp nhiều cây quyết định, mỗi cây học trên một tập con ngẫu nhiên của dữ liệu và đặc trưng; các cây bỏ phiếu. Mô hình chính của dự án dùng 300 cây và trọng số lớp cân bằng theo tần suất lớp.

**Độ chính xác tổng thể (OA)**
Tỷ lệ mẫu kiểm tra được phân loại đúng. Bị thổi phồng khi một lớp chiếm đa số (Nước chiếm 51% số mẫu của dự án).

**Độ chính xác cân bằng lớp (BA)**
Trung bình recall của từng lớp; mỗi lớp được tính ngang nhau. Đây là chỉ số chính của dự án. Luôn đoán lớp đông nhất chỉ đạt BA 25% với bốn lớp.

**Recall, precision, F1**
Recall (độ chính xác người sản xuất): tỷ lệ phần tử thật của một lớp được tìm ra. Precision (độ chính xác người dùng): tỷ lệ dự đoán của một lớp là đúng. F1: trung bình điều hòa của hai đại lượng trên. F1 macro là trung bình F1 qua các lớp.

**Hệ số kappa Cohen**
Mức thống nhất giữa dự đoán và tham chiếu sau khi trừ phần trùng hợp ngẫu nhiên (0 = ngẫu nhiên, 1 = hoàn hảo).

**Ma trận nhầm lẫn**
Bảng lớp thật (hàng) so với lớp dự đoán (cột). Nhầm lẫn chính của dự án là Thực vật ↔ Đất trống.

**Kiểm tra chéo (cross-validation, CV)**
Chia mẫu nhiều lần thành phần huấn luyện và phần kiểm tra (fold) để mỗi mẫu được kiểm tra đúng một lần bởi một mô hình chưa từng thấy nó.

**Kiểm tra chéo theo khối không gian**
Kiểm tra chéo trong đó mẫu được nhóm theo các khối địa lý (ở đây là 5 km × 5 km) và mỗi khối thuộc trọn một fold. Cách này ngăn ô kiểm tra nằm sát cạnh ô huấn luyện. Xem [Kiểm chứng](/vi/methods/validation/).

**Rò rỉ không gian (spatial leakage)**
Độ chính xác lạc quan quá mức do mẫu kiểm tra nằm rất gần, nên rất giống, mẫu huấn luyện. Chia ngẫu nhiên theo ô làm BA của dự án cao hơn thực tế khoảng 3 điểm.

**Vùng đệm (buffer)**
Bỏ các mẫu huấn luyện nằm trong một khoảng cách nhất định quanh mẫu kiểm tra (250 m hoặc 1 km trong các thử nghiệm của dự án), để giảm rò rỉ thêm nữa.

**Bootstrap theo khối**
Ước lượng khoảng tin cậy bằng cách lấy lại nguyên các khối không gian có hoàn lại (ở đây 2.000 lần) rồi tính lại chỉ số.

**Kiểm định McNemar**
Kiểm định xem hai bộ phân loại có mắc lỗi khác nhau trên cùng các mẫu hay không. Giá trị p của nó lạc quan khi mẫu tương quan không gian.

**Độ quan trọng hoán vị (permutation importance)**
Mức giảm độ chính xác khi giá trị của một đặc trưng bị xáo trộn ngẫu nhiên; giảm nhiều nghĩa là mô hình dựa nhiều vào đặc trưng đó.

**Loại bỏ đặc trưng (ablation)**
Bỏ từng nhóm đặc trưng để xem mỗi nhóm đóng góp bao nhiêu độ chính xác.

**Đường học (learning curve)**
Độ chính xác theo lượng dữ liệu huấn luyện (ở đây là số polygon). Đường học của dự án gần bão hòa sau khoảng 300 polygon.

**Kiểm tra chéo lồng (nested cross-validation)**
Tinh chỉnh siêu tham số trong một vòng kiểm tra chéo bên trong, còn vòng bên ngoài đo mô hình đã tinh chỉnh trên dữ liệu chưa động tới. Tinh chỉnh chỉ cải thiện BA tối đa 0,5 điểm.

**Vùng áp dụng được (area of applicability, AOA)**
Phần bản đồ mà đặc trưng đầu vào đủ giống dữ liệu huấn luyện để độ chính xác kiểm tra chéo của mô hình còn có ý nghĩa (Meyer & Pebesma, 2021). 8,3% AOI của dự án nằm ngoài vùng này.

**Chỉ số khác biệt (dissimilarity index, DI)**
Khoảng cách từ một ô tới mẫu huấn luyện gần nhất trong không gian đặc trưng đã chuẩn hóa và nhân trọng số độ quan trọng, chia cho khoảng cách trung bình giữa các mẫu huấn luyện. Ô có DI trên 0,105 nằm ngoài vùng áp dụng được.

**Mức đồng thuận mô hình**
Số mô hình (trên 10) dự đoán cùng lớp với lớp đa số. Cả 10 mô hình đồng ý trên 65,9% AOI của dự án.

**Bộ lọc đa số (modal filter)**
Bộ lọc hậu xử lý thay lớp của mỗi ô bằng lớp xuất hiện nhiều nhất trong vùng lân cận, xóa các pixel lẻ loi kiểu "hạt tiêu". Chỉ dùng để hiển thị; ảnh hưởng tới độ chính xác chưa được đo.

**Tập kiểm tra mù**
Các mẫu tham chiếu chọn ngẫu nhiên và gán nhãn mà không nhìn dự đoán. Tập của dự án (250 ô) đã chuẩn bị nhưng chưa bao giờ được chấm.

**Ước lượng diện tích dựa trên thiết kế mẫu**
Ước lượng diện tích các lớp kèm khoảng tin cậy từ một mẫu xác suất có nhãn tham chiếu (Olofsson và cộng sự, 2014). Không làm được ở đây khi chưa có tập kiểm tra mù đã chấm, nên tỷ lệ diện tích của dự án chỉ là đếm pixel chưa kiểm chứng.
