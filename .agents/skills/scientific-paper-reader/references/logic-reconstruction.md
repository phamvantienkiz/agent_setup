# Tái dựng logic nghiên cứu và đọc cấu trúc bài báo

## Mục lục

1. Bảng tái dựng 7 thành phần (+ 4 trạng thái ghi nhận trung thực)
2. Đối tượng đề xuất vs căn cứ kiểm chứng
3. Gap - Unknown - Personal Knowledge Deficit
4. Giả thuyết - Giả định - Phương pháp đề xuất
5. Đọc theo chức năng lập luận (IMRAD và đặc thù AI/CS)
6. Đọc Tiêu đề
7. Đọc Abstract
8. Đọc Introduction (5 câu hỏi của Widom)

## 1. Bảng tái dựng 7 thành phần

| #   | Thành phần                                          | Câu hỏi dẫn                                                                                                                       |
| --- | --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Bối cảnh & Bài toán                                 | Giải quyết vấn đề gì, trong điều kiện ứng dụng nào, vì sao đáng quan tâm?                                                         |
| 2   | Khoảng trống & Điều chưa biết                       | Công trình trước chưa làm rõ/giải quyết thỏa đáng điều gì? Ảnh hưởng ra sao?                                                      |
| 3   | Câu hỏi nghiên cứu                                  | Trả lời câu hỏi cụ thể nào?                                                                                                       |
| 4   | Giả thuyết / Ý tưởng giải pháp / Mục tiêu phân tích | Dự đoán, cách giải thích, khẳng định nào cần đánh giá? (Nếu không có giả thuyết tường minh: ý tưởng giải pháp chính là gì?)       |
| 5   | Hệ thống giả định                                   | Phương pháp và lập luận dựa vào điều kiện tiên quyết nào (tường minh/ngầm định)?                                                  |
| 6   | Đối tượng đề xuất & Thiết kế kiểm tra               | Đề xuất gì (mô hình, thuật toán, kiến trúc, dữ liệu)? Tổ chức dữ liệu, thực nghiệm, phân tích, chứng minh thế nào để kiểm tra nó? |
| 7   | Kết quả & Phạm vi kết luận                          | Kết quả cụ thể là gì và cho phép kết luận gì _trong phạm vi điều kiện đã kiểm tra_?                                               |

Đây là công cụ tổ chức thông tin, **không phải biểu mẫu bắt buộc**. Cho phép bốn trạng thái ghi nhận trung thực: _Không áp dụng_ (vd. bài lý thuyết thuần túy, bài mô tả bộ dữ liệu) · _Tác giả không phát biểu tường minh_ · _Chưa xác định từ phần đã đọc ở lượt hiện tại_ · _Cần kiểm tra thêm ở phần kỹ thuật/phụ lục_. Không điền bừa để cho đủ 7 ô.

## 2. Đối tượng đề xuất vs căn cứ kiểm chứng

Sơ đồ kiến trúc hay lưu đồ thuật toán mới là _thứ tác giả đề xuất_, chưa phải căn cứ bảo vệ khẳng định về tốc độ, độ chính xác, khả năng mở rộng. Căn cứ là thực nghiệm, ablation, phân tích độ phức tạp, định lý/chứng minh.

## 3. Ba khái niệm dễ lẫn

- **Research Gap:** thiếu hụt hiểu biết/phương pháp/lý thuyết/bằng chứng trong tập công trình đã công bố của cộng đồng.
- **Unknown:** câu hỏi cụ thể chưa có câu trả lời rõ trong phạm vi tài liệu đang khảo sát.
- **Personal Knowledge Deficit:** điều người đọc chưa hiểu nhưng đã được giải quyết trong giáo trình/tài liệu nền.

Trước khi coi điểm chưa hiểu là cơ hội nghiên cứu, kiểm tra xem nó là gap của lĩnh vực hay kiến thức nền cần bổ sung. Với gap thật, ghi ba dòng riêng: (1) gap do tác giả tuyên bố; (2) căn cứ/tài liệu tác giả dẫn để xác lập; (3) mức người đọc đã tự đối chiếu. Không chuyển một câu nhận xét ở phần Mở đầu thành "toàn cộng đồng chưa từng nghiên cứu".

## 4. Giả thuyết - Giả định - Phương pháp

- **Giả thuyết:** dự đoán/cách giải thích cần được đánh giá bằng bằng chứng hoặc phân tích.
- **Giả định:** điều kiện đặt làm tiền đề để dựng phương pháp/suy luận/chứng minh.
- **Phương pháp đề xuất:** giải pháp kỹ thuật cụ thể (thuật toán, cách biểu diễn, kiến trúc).
  Khẳng định phải được phát biểu rõ và hỗ trợ bằng thực nghiệm _hoặc_ phân tích lý thuyết phù hợp (tinh thần hướng dẫn JMLR). Không áp khuôn "giả thuyết - thí nghiệm - dataset" lên bài lý thuyết, vốn dựa trên định nghĩa, bổ đề, định lý, chứng minh.

## 5. Đọc theo chức năng lập luận

Bài báo là cách tác giả tổ chức công trình để người đọc hiểu và kiểm tra, không nhất thiết là nhật ký trình tự thí nghiệm (Medawar 1963; Widom 2006). Related Work có thể đặt ngay sau Intro hoặc gần cuối. Hỏi: "Phần này làm chức năng gì trong việc làm rõ và bảo vệ khẳng định?" thay vì suy đoán lịch sử nghiên cứu từ thứ tự đề mục.

| Chức năng                   | Tìm gì trong bài AI/CS                                                              |
| --------------------------- | ----------------------------------------------------------------------------------- |
| 1. Đặt vấn đề               | Bối cảnh, động lực, phát biểu bài toán, câu hỏi, hạn chế của công trình trước       |
| 2. Đề xuất cách giải quyết  | Mô hình, thuật toán, cơ chế biểu diễn, thiết kế hệ thống, khung phân tích lý thuyết |
| 3. Cung cấp căn cứ          | Thiết kế thực nghiệm, dữ liệu, phép đo, đối sánh, ablation, định lý và chứng minh   |
| 4. Diễn giải & giới hạn     | Ý nghĩa kết quả, điều kiện áp dụng, trade-off, giới hạn còn lại                     |
| 5. Hỗ trợ kiểm tra chi tiết | Phụ lục, cấu hình tham số, mô tả dữ liệu, mã nguồn, tài liệu bổ sung                |

## 6. Đọc Tiêu đề

- **"X for Y":** X thường là phương pháp/mô hình/công cụ; Y là bài toán/phạm vi ứng dụng.
- **"X via/using Y":** X là mục tiêu/tác vụ; Y là cơ chế thực hiện (vd. _Rapid Object Detection Using a Boosted Cascade of Simple Features_).
- **"On X" / "Understanding X":** thường là phân tích lý thuyết hoặc khảo sát làm rõ bản chất.
- **Tên riêng + mô tả:** tách tên viết tắt của mô hình khỏi mô tả kỹ thuật để nhận diện đúng đóng góp tuyên bố.
  Cấu trúc tiêu đề chỉ là gợi ý. Bốn câu hỏi sau tiêu đề: (1) bài toán/đối tượng chính? (2) tác giả muốn cải thiện hay làm rõ khía cạnh nào? (3) cách tiếp cận gợi ý? (4) điều kiện/phạm vi nào nêu ngay trong tiêu đề?

## 7. Đọc Abstract

Abstract hiệu quả thường cô đọng: bài toán, cách tiếp cận, giải pháp, đóng góp chính. Đảo chiều khi đọc: công trình muốn giải quyết việc gì, đề xuất gì, báo cáo kết quả nào, có nêu điều kiện áp dụng không. Đánh dấu các khẳng định chính để kiểm tra căn cứ ở Methods/Results.

## 8. Đọc Introduction theo 5 câu hỏi (Widom 2006, Stanford InfoLab)

1. Bài toán là gì? 2. Vì sao thú vị và quan trọng? 3. Vì sao khó (vì sao cách đơn giản, trực quan không đủ)? 4. Vì sao các cách trước chưa thỏa đáng và cách mới khác ở đâu? 5. Thành phần chính của cách tiếp cận, kết quả và giới hạn?
   Đây là khung hướng dẫn hữu ích của một tác giả, không phải quy định bắt buộc. Gán nhãn chức năng cho từng đoạn: bối cảnh - tầm quan trọng - độ khó kỹ thuật - hạn chế trước đây - ý tưởng đề xuất - đóng góp & giới hạn. Mắt xích nào thiếu thì ghi nguyên nhân: bài chưa nêu tường minh / trình bày chưa rõ / người đọc thiếu nền.
