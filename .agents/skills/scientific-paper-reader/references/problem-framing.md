# Bài toán thực tiễn hay bài toán nghiên cứu?

Dùng khi người dùng định hình đề tài, hoặc khi đánh giá một bài báo/đề tài có "hàm lượng khoa học" hay chỉ là triển khai kỹ thuật. Bước đầu tiên không phải chọn mô hình mà là xác định đúng bản chất vấn đề: đang gặp vấn đề gì trong bối cảnh nào? ai bị ảnh hưởng? giá trị nếu giải quyết? tiêu chí nào đo thành công? Xác định sai bản chất sẽ lệch toàn bộ thiết kế nghiên cứu, chọn dữ liệu và tiêu chí đánh giá.

## Bảng đối chiếu

| Tiêu chí            | Thực tiễn (Practical/Engineering)       | Nghiên cứu (Research)                          |
| ------------------- | --------------------------------------- | ---------------------------------------------- |
| Câu hỏi cốt lõi     | Cần làm gì để giải quyết nhu cầu này?   | Phương pháp giải quyết vấn đề tốt đến mức nào? |
| Trọng tâm           | Vận hành & triển khai kỹ thuật          | Đo lường, so sánh & kiểm chứng                 |
| Đầu ra              | Phần mềm, công cụ, quy trình hoạt động  | Bằng chứng, kết luận, phân tích dữ liệu        |
| Tiêu chí thành công | Hệ thống chạy được, cải thiện công việc | Chỉ số khách quan, giải thích được kết quả     |

Thực tiễn: _Nhu cầu thực tế → triển khai công nghệ → sản phẩm phần mềm → tối ưu vận hành._
Nghiên cứu cần: (1) câu hỏi hẹp & rõ; (2) dữ liệu xác định (đầu vào/đầu ra chuẩn hóa); (3) phương pháp minh bạch (thiết kế thực nghiệm); (4) tiêu chí khách quan (Accuracy, F1, Error Rate…); (5) phân tích & kết luận (giải thích vì sao đúng/sai).

## Những lầm tưởng phổ biến

- **"Dùng AI/ML/DL = làm nghiên cứu."** Lấy thư viện có sẵn tích hợp cho chạy là triển khai thực tiễn; nghiên cứu đòi hỏi đánh giá, so sánh hoặc cải tiến phương pháp.
- **"Viết phần mềm phức tạp nhiều chức năng = làm nghiên cứu."** Đăng nhập, phân quyền, xuất Excel là kỹ thuật phần mềm; nghiên cứu cần một câu hỏi khoa học nằm trong hoặc cạnh hệ thống.
- **"Thu thập/lưu trữ dữ liệu lớn = làm nghiên cứu."** Dữ liệu lớn không có câu hỏi phân tích/đo lường chỉ phục vụ quản lý; thành nghiên cứu khi dùng để trả lời một câu hỏi cụ thể.
- **"Giải quyết triệt để một vấn đề cho tổ chức = đề tài khoa học."** Sản phẩm hữu ích không tự động là nghiên cứu; ngược lại, chứng minh một mô hình AI _thất bại_ trên dữ liệu thực vẫn là kết quả nghiên cứu rất có giá trị.

## Chuyển đổi hai chiều

**Thực tiễn → Nghiên cứu (thu hẹp từ giải pháp chung xuống câu hỏi đo lường được):** Nhu cầu (khoa cần quản lý báo cáo văn bản tự do) → Khoảng trống (chưa rõ AI trích xuất tiếng Việt tốt đến đâu) → Câu hỏi hẹp (AI trích xuất chẩn đoán đạt F1 bao nhiêu?) → Dữ liệu & chỉ số (1.000 báo cáo gán nhãn, Precision/Recall) → Phân tích (so sánh rule-based với mô hình ngôn ngữ lớn).
**Nghiên cứu → Thực tiễn:** nghiên cứu trả lời "phương pháp có hiệu quả không?", thực tiễn trả lời "làm sao hệ thống chạy ổn định?": đóng gói (API/Container) → thiết kế UI/UX → tích hợp vào hệ thống sẵn có → vận hành & đào tạo (theo dõi lỗi, huấn luyện) → cập nhật (fine-tune).

## Cặp ví dụ cùng nghiệp vụ, hai lăng kính

- **Lịch trực:** TT: phần mềm nhập/chỉnh lịch, phân quyền, thông báo, báo cáo; thành công = giao diện trực quan, không sập. NC: thuật toán xếp lịch tự động có giảm số vi phạm quy định trực so với xếp thủ công không? đánh giá ràng buộc, so sánh thuật toán.
- **Số hóa báo cáo y khoa:** TT: lưu PDF + tìm theo từ khóa (2 giây thay vì 2 giờ). NC: mô hình trích chẩn đoán/vị trí tổn thương đạt F1 bao nhiêu; confusion matrix, phân tích lỗi.
- **OCR:** TT: dùng tool có sẵn quét văn bản vào database. NC: tiền xử lý ảnh có giảm error rate trên chữ viết tay không?
- **Dashboard lãnh đạo:** TT: biểu đồ số lượt khám theo ngày. NC: dashboard thời gian thực có thực sự giảm thời gian ra quyết định so với báo cáo thủ công?

## Quy tắc ngón tay cái

Mục tiêu chính là làm cho **hệ thống chạy được** → bài toán thực tiễn. Mục tiêu chính là **đo lường, so sánh và rút ra kết luận** → bài toán nghiên cứu.

## Hành vi của agent (chế độ F, hoặc khi đánh giá một bài/đề tài)

- Hỏi (tối đa một câu) hoặc suy ra mục tiêu tối thượng; áp quy tắc ngón tay cái; chỉ ra lầm tưởng nào đang xuất hiện.
- Đề xuất chuỗi thu hẹp 5 bước cho đề tài cụ thể của người dùng và gợi ý chỉ số/dữ liệu; không áp đặt - đây là gợi ý để người dùng quyết định.
- Với một bài báo "ứng dụng": kiểm tra xem có câu hỏi khoa học, dữ liệu xác định, so sánh với baseline, tiêu chí khách quan, phân tích lỗi hay chỉ trình bày hệ thống.
