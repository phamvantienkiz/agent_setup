# Thẩm định: khẳng định - căn cứ, theo loại công trình

## Mục lục

1. Nguyên tắc cốt lõi
2. Thang chắc chắn của ngôn ngữ
3. Nhận định cân bằng (4 mục)
4. Không suy đoán động cơ
5. Câu hỏi thẩm định theo 4 loại bài
6. Đánh giá phép so sánh thực nghiệm
7. Câu hỏi Socratic và câu hỏi phân biệt
8. Chuỗi tương tác ngắn có điểm kiểm tra (chế độ D)

## 1. Nguyên tắc cốt lõi

Xem sự tương xứng giữa **khẳng định (claim)** và **căn cứ (evidence/proof)**. Theo tiêu chí TMLR, khẳng định phải được hỗ trợ bằng bằng chứng chính xác; khi có khoảng cách giữa khẳng định và bằng chứng, cách khắc phục không nhất thiết là làm thêm thí nghiệm mà có thể là _thu hẹp phát biểu_ cho vừa phạm vi bằng chứng. Một bài không cần đề xuất phương pháp hoàn toàn mới mới có giá trị, miễn cung cấp căn cứ trung thực và hiểu biết mới.

## 2. Thang chắc chắn

_chứng minh được_ (suy diễn toán học/logic chặt từ tập giả định) > _cung cấp bằng chứng hỗ trợ_ > _cho thấy trong điều kiện thử nghiệm đã báo cáo_ > _phù hợp với giả thuyết ban đầu_.
Kết quả thực nghiệm luôn gắn với dữ liệu, cấu hình, điều kiện đánh giá nên không dùng "chứng minh" như nhãn chung. Ví dụ: ablation cho bằng chứng về mức đóng góp của một mô-đun _trong điều kiện đã đánh giá_, không tự động chứng minh mô-đun đó tối ưu trong mọi bối cảnh.

## 3. Nhận định cân bằng - luôn ghi đủ bốn mục

(1) Điểm mạnh và giá trị có thể học/kế thừa · (2) Giới hạn và điều kiện áp dụng · (3) Đánh đổi kỹ thuật (lợi ích gì, chấp nhận chi phí nào) · (4) Điểm chưa đủ thông tin cần kiểm tra thêm. Nhận ra mặt tích cực quan trọng ngang nhận ra điểm yếu (Roughgarden 2015).

## 4. Không suy đoán động cơ

Bám văn bản và dữ liệu. Thay "tác giả cố tình giấu kết quả thất bại" bằng: "bài hiện chưa cung cấp kết quả trên trường hợp…"; "thiết kế đánh giá chưa cho phép tách tác động của yếu tố A và B"; "kết luận ở mục X rộng hơn phạm vi dữ liệu ở Bảng Y".

## 5. Câu hỏi thẩm định theo 4 loại bài

Không áp một bảng kiểm học máy thực nghiệm cho mọi bài.

**Lý thuyết.** Định nghĩa và mô hình toán học có chính xác, rõ ràng không? Lượng từ (với mọi/tồn tại), giả định, điều kiện biên trong phát biểu bổ đề/định lý là gì; giả định nào là _cần_ để bước chứng minh đi qua? Các bước suy diễn (thân bài và phụ lục) đầy đủ không, có bước nhảy nào cần tự kiểm tra bằng ví dụ nhỏ?

**Hệ thống & kiến trúc.** Kiến trúc nhắm điểm nghẽn nào, dưới giả định môi trường nào? Workload, kịch bản, cấu hình phần cứng/phần mềm, môi trường đo có được mô tả tường minh? Các phép đo (throughput, latency, bộ nhớ, chịu lỗi) đã tính đủ overhead toàn hệ thống chưa? Trade-off giữa các chỉ số là gì?

**ML thực nghiệm.** (Tham khảo NeurIPS Paper Checklist.) Chia tách train/validation/test có rõ? Có số lần chạy và mức biến thiên khi biến thiên ấy ảnh hưởng khẳng định? **Rò rỉ dữ liệu** (Kapoor & Narayanan 2023): theo dõi đường đi thông tin qua tiền xử lý, chuẩn hóa, chọn đặc trưng, tinh chỉnh siêu tham số, chia tập (đặc biệt chuỗi thời gian/dữ liệu phụ thuộc cấu trúc) xem thông tin tập test có lọt vào xây dựng mô hình không. Chỉ nêu nghi vấn rò rỉ khi có căn cứ trong văn bản; nếu bài không mô tả đủ để loại trừ thì ghi "bài không mô tả chi tiết quy trình X".

**Dữ liệu & benchmark.** Thu thập, làm sạch, gán nhãn, kiểm soát chất lượng nhãn thế nào? Dữ liệu đại diện cho phạm vi hiện tượng nào, có thiên lệch/giới hạn đại diện nào? Metric đề xuất có phản ánh đúng mục tiêu bài toán thực tế?

## 6. Đánh giá phép so sánh thực nghiệm

Bắt đầu từ _mục tiêu của phép so sánh_. Không mặc định mọi nghiên cứu phải giữ y hệt dữ liệu, tài nguyên, cấu hình cho mọi mô hình ở mọi bảng (vd. so mô hình nhỏ chuyên biệt với mô hình nền tảng pretrain lớn thì điều kiện tài nguyên tự nhiên khác nhau). Điều cần kiểm tra: tác giả có **minh bạch yếu tố nào giữ cố định, yếu tố nào thay đổi, vì sao**; kết luận có giới hạn đúng theo điều kiện thực tế đó không. Khi đưa vào bảng tổng hợp, giữ riêng các kết quả khác điều kiện (như chú thích dưới bảng về tập test đã loại bớt ảnh).

## 7. Socratic và câu hỏi phân biệt

Dựa trên Paul & Elder (2006):

- **Làm rõ khái niệm:** "nhanh hơn", "bền vững hơn", "đơn giản hơn" được định nghĩa bằng thước đo cụ thể nào trong bài?
- **Kiểm tra giả định:** bước chuyển từ lập luận A sang B dựa vào điều kiện ngầm định nào?
- **Căn cứ & góc nhìn khác:** căn cứ nào trong bài hỗ trợ trực tiếp? Có cách giải thích thay thế nào cho cùng kết quả?
- **Hệ quả & điều kiện biên:** điều kiện đầu vào đổi vượt phạm vi thử nghiệm thì kết luận còn giữ không?
- **Phân biệt các cách giải thích:** khi hiệu quả có thể do hai yếu tố (vd. cơ chế chọn đặc trưng mới _hay_ cấu trúc phân tầng mới): trong bài có phép kiểm tra tách hai yếu tố chưa? Nếu chưa, cần phép so sánh tối thiểu nào giữ các điều kiện khác tương đương? (Kiểm tra Ablation và Appendix trước khi kết luận "bài chưa làm".)
  Kịch bản biên do AI nêu ra mới là suy luận giả thuyết, chưa phải bằng chứng phương pháp sẽ thất bại.

## 8. Chuỗi tương tác ngắn có điểm kiểm tra

1. **Định vị:** tìm nơi tác giả phát biểu khẳng định X và các bảng/hình/định lý dùng làm căn cứ. _Chưa đánh giá đúng sai._ → **Điểm dừng:** người dùng tự mở đúng các vị trí đó.
2. **Đối chiếu phạm vi:** sau khi người dùng đã xem nguồn, đọc cách đo (đơn vị, cao/thấp tốt, baseline, cấu hình, footnote), rồi so phạm vi khẳng định với phạm vi bằng chứng; đề xuất câu kết luận có điều kiện vừa vặn. Kiểm tra Discussion/Limitations xem tác giả đã tự thu hẹp chưa. → **Điểm dừng:** người dùng chọn một điểm mấu chốt (giả định hoặc biến gây nhiễu).
3. **Đào sâu điểm mấu chốt:** giả định ngầm, kịch bản biên, cách giải thích thay thế, phép kiểm tra phân biệt. Tách rõ "điều được viết trong bài" và "suy luận kỹ thuật".
