---
title: "E3: Độ quan trọng hoán vị của đặc trưng"
description: Xáo trộn từng đặc trưng SAR trên fold kiểm tra cho thấy HV ngày 27/10 và độ lệch chuẩn HH theo thời gian mang nhiều thông tin nhất.
sidebar:
  order: 3
---

**Câu hỏi.** Mô hình lớp phủ Random Forest dựa vào những đặc trưng SAR riêng lẻ nào?

**Trả lời ngắn.** HV ngày 27/10 (lần chụp quỹ đạo lên duy nhất) quan trọng nhất: xáo trộn nó làm độ chính xác cân bằng lớp (BA) giảm 6,7 điểm. Tiếp theo là độ lệch chuẩn HH qua các ngày (−3,9), HV ngày 3/11 (−3,2) và HV trung bình (−2,3). Mọi đặc trưng còn lại dưới 0,5 điểm.

## Thiết lập E3

- **Mô hình và kiểm chứng:** Random Forest, CV khối không gian 5 km (như [E1](/vi/experiments/e1-models/)).
- **Cách làm:** độ quan trọng hoán vị tính **trên các fold kiểm tra** của lần lặp CV đầu tiên: ở mỗi fold trong 5 fold, huấn luyện Random Forest trên các khối train, xáo trộn một đặc trưng trong các khối test (10 lần), dự đoán lại và đo mức giảm BA. Giá trị là trung bình ± độ lệch chuẩn qua 5 fold.

## Kết quả E3

![E3: mức giảm độ chính xác cân bằng lớp khi xáo trộn từng đặc trưng](/figures/vi/E3_permutation_importance.png)

| Đặc trưng | BA giảm (điểm) |
|---|---|
| HV, 27/10 (quỹ đạo lên) | 6,71 ± 3,32 |
| Độ lệch chuẩn HH qua 3 ngày | 3,89 ± 2,35 |
| HV, 3/11 | 3,23 ± 1,18 |
| HV trung bình | 2,34 ± 1,53 |
| HH, 22/10 | 0,47 ± 0,52 |
| HV, 22/10 | 0,41 ± 1,15 |
| Kết cấu (độ lệch chuẩn 7×7 của HH trung bình) | 0,22 ± 0,31 |
| Độ lệch chuẩn HV qua 3 ngày | 0,21 ± 0,34 |
| HV − HH | 0,06 ± 0,20 |
| HH, 27/10 | −0,04 ± 0,69 |
| HH trung bình | −0,06 ± 0,69 |
| HH, 3/11 | −0,14 ± 0,62 |

## E3: diễn giải

- **HV chiếm ưu thế.** 3 trong 4 đặc trưng đứng đầu là HV, khớp với [E2](/vi/experiments/e2-features/), nơi chỉ dùng HV tốt hơn chỉ dùng HH.
- **Lần chụp quỹ đạo lên có vai trò đặc biệt.** HV ngày 27/10 là đặc trưng duy nhất từ quỹ đạo lên (track 054), nhìn mặt đất từ phía ngược lại. Backscatter của nhà cửa phụ thuộc mạnh vào hướng nhìn, nên chênh lệch hướng nhìn có thể mang thông tin vật lý về vùng đô thị. **Giả thuyết này chưa được kiểm chứng.**
- **Độ lệch chuẩn HH** đứng thứ hai. Vì 27/10 là quỹ đạo lên, đặc trưng này lẫn khác biệt hướng nhìn với thay đổi thật trên mặt đất, nên không được hiểu thuần là "thay đổi theo thời gian".
- **Đặc trưng tương quan chia nhau độ quan trọng.** HH từng ngày, HH trung bình và độ lệch chuẩn HH tương quan mạnh; xáo trộn một cái thì các cái kia vẫn còn, nên độ quan trọng riêng lẻ nhỏ hoặc hơi âm. Phải đọc bảng này cùng thí nghiệm loại bỏ nhóm ở [E2](/vi/experiments/e2-features/), nơi bỏ *toàn bộ* đặc trưng HH làm mất khoảng 4 điểm.

## Kết quả E3 được dùng ở đâu

Độ quan trọng hoán vị được dùng làm **trọng số đặc trưng** trong phân tích vùng áp dụng được ([E8](/vi/experiments/e8-applicability/)).
