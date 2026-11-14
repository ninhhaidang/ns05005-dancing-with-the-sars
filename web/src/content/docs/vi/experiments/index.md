---
title: Tổng quan thí nghiệm
description: Chuỗi thí nghiệm E0–E8 kiểm tra bộ phân loại lớp phủ chỉ dùng SAR hoạt động tốt đến đâu, nên kiểm chứng thế nào, và bản đồ cuối cùng đáng tin đến mức nào.
sidebar:
  order: 0
---

Bản đồ lớp phủ của dự án được làm **chỉ từ SAR NISAR**. Trước khi tin vào nó, chúng tôi chạy 9 thí nghiệm (E0–E8) trên cùng bộ nhãn và đặc trưng, để trả lời 4 câu hỏi:

1. Chọn mô hình học máy nào có quan trọng không? (E1, E6)
2. Đặc trưng SAR nào mang thông tin? (E2, E3)
3. Mỗi cách kiểm chứng lạc quan đến đâu, và mô hình đáng tin ở khoảng cách bao xa so với vùng có nhãn? (E0, E4, E5)
4. *Bản đồ* (chứ không chỉ các mẫu) đáng tin đến đâu? (E7, E8)

Mọi con số lấy từ `scripts/experiments.py` (chạy ngày 14/11/2026). Hình vẽ bằng `scripts/plot_experiments.py`. Phương pháp được mô tả ở [Phân loại](/vi/methods/classification/) và [Kiểm chứng](/vi/methods/validation/).

:::caution[Cách đọc mọi con số trong mục này]
Mọi chỉ số độ chính xác là **kiểm tra chéo trên ô 20 m thuần** (ô nằm ≥80% trong một polygon nhãn). **Chưa có tập kiểm tra độc lập**: tập kiểm tra mù 250 ô ngẫu nhiên đã được chuẩn bị nhưng chưa chấm nhãn. Con số "khoảng 93%" là **độ chính xác cân bằng lớp trên ô thuần, kiểm tra chéo theo khối không gian 5 km, không phải độ chính xác của toàn bộ bản đồ.**
:::

## Thiết lập chung của E0–E8

**Bài toán.** Phân loại mỗi ô 20 m của tỉnh Hưng Yên (6,43 triệu ô, 2.571,7 km²) vào 4 lớp: Nước, Thực vật, Đất trống, Đô thị (đô thị/làng).

**Dữ liệu vào.** NISAR L2 GCOV, VALIDATED (CRID P05036), tần số A, phân cực HH và HV, ba ngày: 22/10/2026 (track 148 quỹ đạo xuống, 20 m), 27/10/2026 (track 054 quỹ đạo lên, 10 m, lấy trung bình về 20 m), 3/11/2026 (track 148 quỹ đạo xuống, 20 m). Xem [Dữ liệu NISAR](/vi/data/nisar/).

**Nhãn.** 1.347 polygon hình chữ nhật vẽ trên ảnh tổng hợp Sentinel-2 đã lọc mây: Nước 190, Thực vật 485, Đất trống 444, Đô thị 228. Xem [Nhãn](/vi/data/labels/).

**Mẫu.** Một ô 20 m trở thành mẫu nếu ≥80% diện tích thuộc một lớp (siêu lấy mẫu 8×8), tối đa 20 ô mỗi polygon. Kết quả: **3.918 mẫu từ 864 polygon** (Nước 2.011, Thực vật 622, Đất trống 660, Đô thị 625). 483 polygon (36%) không cho mẫu nào vì nhỏ hơn một ô 20 m trọn vẹn.

**Đặc trưng (12 trên mỗi ô).** HH và HV (dB, làm trơn 3×3) của từng ngày trong 3 ngày, HH trung bình, HV trung bình, HV − HH, độ lệch chuẩn HH và HV qua 3 ngày, và kết cấu 7×7 (độ lệch chuẩn cục bộ của HH trung bình).

**Chỉ số chính.** Độ chính xác cân bằng lớp (BA, trung bình recall của 4 lớp), chốt trước khi chạy. Nước chiếm 51% số mẫu nên độ chính xác tổng sẽ bị kéo lên.

**Cách kiểm chứng chính.** Kiểm tra chéo 5 fold theo **khối không gian 5×5 km** (`StratifiedGroupKFold`), lặp 5 lần với cách phân khối khác nhau; khoảng tin cậy 95% bằng bootstrap theo khối (2.000 lần). Mọi mô hình dùng chung các fold.

## E0: kiểm tra phân bố không gian của nhãn

E0 là bước kiểm tra dữ liệu, chạy trước các thí nghiệm mô hình, và giải thích vì sao phải kiểm chứng theo khối không gian.

- **Nhãn tụ thành cụm cùng lớp.** Khoảng cách từ một polygon đến polygon *cùng lớp* gần nhất có trung vị **102 m**; đến polygon *khác lớp* gần nhất là **509 m**. Chỉ 1,8% polygon có láng giềng khác lớp trong vòng 100 m. Không polygon nào chạm nhau.
- **Mẫu tập trung.** Mẫu nằm trên **88 khối** 5×5 km (trung vị 21 mẫu/khối, khối lớn nhất 348), nhưng **10 khối đông nhất chứa 48%** số mẫu.
- **Mỗi lớp chỉ có mặt ở 33–45 khối:** Nước 33, Thực vật 38, Đất trống 34, Đô thị 45.
- **Các fold cân bằng:** trong CV khối 5 km, mỗi fold kiểm tra có khoảng 400 mẫu Nước, 99–182 Thực vật, 130–133 Đất trống và 124–126 Đô thị.

Hệ quả: chia ngẫu nhiên theo ô hay theo polygon sẽ đặt ô kiểm tra ngay cạnh ô huấn luyện cùng lớp, và độ đa dạng thật của tập nhãn thấp hơn nhiều so với con số "3.918 mẫu". Điều này được đo trực tiếp ở [E4](/vi/experiments/e4-validation/).

## Tóm tắt kết quả

| Thí nghiệm | Câu hỏi | Kết quả chính |
|---|---|---|
| [E1 Mô hình](/vi/experiments/e1-models/) | Mô hình nào tốt nhất trong 14 mô hình? | 11/14 mô hình đạt BA 93,0–93,6%; chênh lệch nằm trong độ bất định. SVM 93,6%, Random Forest 93,1%, mốc đoán lớp đông nhất 25%. |
| [E2 Đặc trưng](/vi/experiments/e2-features/) | Nhóm đặc trưng nào quan trọng? | 3 ngày đạt 93,1%, một ngày chỉ 83,4–85,6%. Cần cả HH lẫn HV (mỗi cái khoảng 4 điểm). Kết cấu thêm 0,2 điểm. |
| [E3 Độ quan trọng](/vi/experiments/e3-importance/) | Đặc trưng riêng lẻ nào quan trọng? | HV ngày 27/10 (ngày quỹ đạo lên duy nhất) quan trọng nhất (BA giảm 6,7 điểm khi xáo trộn), tiếp theo là độ lệch chuẩn HH (−3,9). |
| [E4 Kiểm chứng](/vi/experiments/e4-validation/) | Cách kiểm chứng làm điểm số thay đổi bao nhiêu? | Chia ngẫu nhiên theo ô thổi phồng BA khoảng 3 điểm (95,9%). Chia nửa tỉnh còn 83–87%. 44% AOI cách nhãn trên 2 km, nơi BA trên ô thuần khoảng 90%. |
| [E5 Đường học](/vi/experiments/e5-learning-curve/) | Thêm nhãn có giúp không? | BA gần bão hòa sau khoảng 300 polygon (92,2% ở 40% số polygon, 93,2% ở 100%). |
| [E6 Tinh chỉnh](/vi/experiments/e6-tuning/) | Tinh chỉnh siêu tham số có giúp không? | Tối đa +0,5 điểm (SVM 93,6 → 94,1%); RF không đổi. |
| [E7 Đồng thuận bản đồ](/vi/experiments/e7-map-agreement/) | Các mô hình có cho cùng bản đồ không? | Cả 10 mô hình đồng ý ở 65,9% AOI. Tỷ lệ diện tích ổn định giữa các mô hình nhưng chưa kiểm chứng: Đô thị khoảng 24%, Đất trống khoảng 44%. |
| [E8 Vùng áp dụng](/vi/experiments/e8-applicability/) | Mô hình đang ngoại suy ở đâu? | 8,3% AOI nằm ngoài vùng áp dụng, như nhau ở vùng sạch mây và vùng mây. 23,5% ô dự đoán Đô thị nằm ngoài vùng này. |

## Kết luận chung từ các thí nghiệm

- **Phân loại 4 lớp chỉ từ SAR khả thi** với NISAR L-band đa thời gian: BA khoảng 93% trên ô thuần với kiểm chứng theo khối không gian, bền với lựa chọn mô hình, tinh chỉnh và vùng đệm.
- **Dữ liệu, không phải độ phức tạp mô hình, mới là yếu tố quyết định:** 3 ngày và 2 phân cực mang lại 7–10 điểm; đổi mô hình mang lại chưa tới 1 điểm.
- **Độ tin cậy không đều trên bản đồ:** độ chính xác giảm khi xa vùng có nhãn, và lớp Đô thị kém tin cậy nhất. Vì vậy bản đồ web có các lớp độ tin cậy ([mở chế độ độ tin cậy](/vi/map/?view=confidence)).

## Chạy lại các thí nghiệm

```bash
python -I scripts/experiments.py               # toàn bộ E0–E8, khoảng 35 phút trên máy 8 nhân
python -I scripts/experiments.py --only E1,E4  # chạy riêng một phần
python -I scripts/plot_experiments.py vi       # hình tiếng Việt
```

Hạt giống ngẫu nhiên cố định (0); chạy lại có thể lệch rất nhỏ do Random Forest chạy song song. Hướng dẫn đầy đủ: [Tái tạo kết quả](/vi/reproduce/).
