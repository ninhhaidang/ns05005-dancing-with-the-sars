# Kịch bản nói cho bộ 7 slide (tiếng Việt)

Slide (tiếng Anh): https://claude.ai/artifact/2ESVM21L4uTuY4z2NQjwME (chế độ riêng tư cho đến khi chủ sở hữu bấm Share).
Thời lượng khoảng 6 phút, phù hợp phần trình bày 5-7 phút trong tổng 15 phút trước Ban giám khảo.

## Slide 1. Tên dự án, đội thi, thử thách

Xin chào ban giám khảo. Chúng em là đội 2936-ThanhNoi, mã đội NS05005, từ Việt Nam. Bài của chúng em có tên NISAR L-band Change Detection and Land Cover Mapping, thuộc thử thách Dancing with the SARs. Chúng em dùng ba ảnh radar NISAR băng L, chụp từ ngày 22 tháng 10 đến ngày 3 tháng 11 năm 2026, trên tỉnh Hưng Yên (sau sáp nhập năm 2025 gồm cả Thái Bình), để làm hai việc: phát hiện thay đổi có kiểm định thống kê và vẽ bản đồ lớp phủ chỉ từ dữ liệu radar. Sản phẩm là một bản đồ web tương tác, chạy công khai tại dwts.ninhhaidang.com.

## Slide 2. Vấn đề cần giải quyết

Hưng Yên là vùng đồng bằng với ruộng lúa, ao nuôi và đê bao, nơi nước được điều tiết liên tục nên mặt đất có thể đổi trong vài ngày. Muốn theo dõi thì cần ảnh thường xuyên, nhưng mây là trở ngại lớn: trong khoảng từ 22 tháng 10 đến 3 tháng 11, chỉ khoảng 32 phần trăm diện tích tỉnh có ảnh Sentinel-2 không mây. Radar xuyên được mây, nhưng dữ liệu băng L thô, tính bằng đề-xi-ben, rất khó đọc với người không chuyên. Vấn đề của chúng em là biến ba ảnh radar thành thông tin dễ dùng: bản đồ thay đổi có kiểm định thống kê và bản đồ lớp phủ, kèm cảnh báo chỗ nào chưa đáng tin.

## Slide 3. Giải pháp của đội

Giải pháp của chúng em là một quy trình chỉ dùng dữ liệu radar, cho ra hai sản phẩm. Thứ nhất là phát hiện thay đổi có kiểm định thống kê: chúng em so sánh hai ảnh cùng quỹ đạo ngày 22 tháng 10 và 3 tháng 11 bằng tỷ số logarit, hiệu chỉnh nhiễu speckle, và chỉ giữ các mảng có z lớn hơn 5 và diện tích từ 0,05 ki-lô-mét vuông. Thứ hai là bản đồ lớp phủ bốn lớp gồm nước, thực vật, đất trống và đô thị, dùng Random Forest trên 12 đặc trưng HH và HV của ba ngày, huấn luyện từ 1.347 polygon nhãn do đội vẽ. Cả hai được đưa lên một bản đồ web tương tác, có thanh trượt so sánh ba ngày, công cụ tra giá trị từng điểm, tài liệu song ngữ và trợ lý AI.

## Slide 4. Dữ liệu NASA đã sử dụng và cách xử lý

Dữ liệu NASA chúng em dùng là sản phẩm NISAR L2 GCOV mức VALIDATED, mã CRID P05036, tải từ ASF DAAC bằng tài khoản Earthdata. Có ba ngày: 22 tháng 10 và 3 tháng 11 cùng quỹ đạo 148 hướng xuống, độ phân giải 20 mét; ngày 27 tháng 10 quỹ đạo 054 hướng lên, độ phân giải 10 mét. Ảnh ngày 29 tháng 10 bị loại vì chỉ phủ 4 phần trăm vùng nghiên cứu. Quy trình xử lý gồm năm bước: tải file HDF5, cắt theo ranh giới tỉnh ở hệ tọa độ UTM 48N, đổi công suất tuyến tính sang đề-xi-ben, kiểm định thay đổi trên cặp ảnh cùng hình học, và tạo 12 đặc trưng từ ba ngày cho bộ phân loại. Ảnh Sentinel-2 chỉ dùng để vẽ nhãn, không đưa vào mô hình.

## Slide 5. Kết quả

Đây là kết quả chính. Về thay đổi, 99,89 phần trăm diện tích tỉnh không đổi đáng kể. Điểm nổi bật duy nhất là một cụm nước mới khoảng 1,6 ki-lô-mét vuông ở tọa độ 106,484 độ Đông, 20,463 độ Bắc, nơi tín hiệu HH giảm từ âm 10 xuống âm 16 đề-xi-ben, hình khối chữ nhật cạnh một khúc sông. Nguyên nhân chưa được kiểm chứng; giả thuyết của chúng em là ao, ruộng hoặc đê bao được cho nước vào, nhưng mây che nên chưa có ảnh quang học xác nhận. Về lớp phủ, bộ phân loại chỉ dùng radar đạt khoảng 93 phần trăm độ chính xác cân bằng trên các ô thuần, kiểm tra chéo theo khối 5 ki-lô-mét. Chúng em nói rõ đây không phải độ chính xác của cả bản đồ, vì chưa có tập kiểm tra độc lập. Trên web, lớp đồng thuận giữa các mô hình và vùng áp dụng cho thấy chỗ nào kém tin cậy, nhất là lớp đô thị.

## Slide 6. Tác động và hướng phát triển

Tác động của dự án: một quy trình mở, tái lập được cho bất kỳ vùng nào có dữ liệu NISAR GCOV; hoạt động được khi có mây, lúc ảnh quang học thất bại; và quan trọng là bản đồ tự cho biết độ tin cậy của mình, qua lớp đồng thuận giữa các mô hình và vùng áp dụng. Công cụ web công khai phục vụ cán bộ quản lý nước, chính quyền địa phương và giáo viên. Bước tiếp theo: kiểm chứng cụm nước mới bằng ảnh quang học hoặc ảnh độ phân giải cao; kiểm chứng bản đồ bằng một tập kiểm tra độc lập; thêm chuỗi ảnh GCOV dài hơn để thấy thu hoạch lúa và mùa lũ; và mở rộng sang các tỉnh khác. Chúng em cũng nêu rõ giới hạn: 93 phần trăm đo trên ô thuần, lớp đô thị kém tin cậy nhất, và nguyên nhân cụm nước chưa kiểm chứng.

## Slide 7. Thành viên và nguồn tham khảo

Đội chúng em gồm ba thành viên: Ninh Hải Đăng, đội trưởng, Phạm Minh Quang và Lê Toàn Thắng. Nguồn dữ liệu chính là sản phẩm NISAR L2 GCOV của NASA và ISRO qua ASF DAAC và NASA Earthdata; ảnh Sentinel-2 của ESA chỉ dùng để vẽ nhãn. Phần mềm gồm Python với scikit-learn, rasterio, h5py, và MapLibre, Astro Starlight cho web. Về trí tuệ nhân tạo, chúng em dùng Claude của Anthropic qua Claude Code để viết mã, tài liệu và dịch Anh Việt, và một mô hình Gemini chạy trợ lý hỏi đáp trên web; các quyết định phân tích và nhãn là của đội. Bản đồ web ở dwts.ninhhaidang.com và mã nguồn mở theo giấy phép Apache 2.0 trên GitHub. Xin cảm ơn ban giám khảo, chúng em sẵn sàng trả lời câu hỏi.

## Gợi ý trả lời câu hỏi thường gặp

- **93% có phải độ chính xác bản đồ không?** Không. Đó là độ chính xác cân bằng trên ô thuần 20 m, kiểm tra chéo theo khối 5 km. Chưa có tập kiểm tra độc lập; chia ngẫu nhiên theo ô thổi phồng khoảng 3 điểm, và chia theo nửa tỉnh chỉ còn 84-87%.
- **Cụm nước mới là gì?** Chưa biết. Giả thuyết là ao, ruộng hoặc đê bao được cho nước vào; mây che nên chưa kiểm chứng.
- **Vì sao không dùng Sentinel-2 làm đầu vào?** Chỉ khoảng 32% tỉnh có ảnh sạch trong khoảng ngày, nên mô hình chỉ dùng SAR để phủ toàn tỉnh.
- **Lớp nào kém tin cậy nhất?** Đô thị: 23,5% ô dự đoán là đô thị nằm ngoài vùng áp dụng.
