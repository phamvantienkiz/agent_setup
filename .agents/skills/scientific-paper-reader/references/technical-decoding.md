# Giải mã kỹ thuật: Tư duy máy tính, xử lý vướng mắc, điểm dừng

## Mục lục

1. Bốn thao tác Tư duy máy tính (Wing)
2. Bảng xử lý vướng mắc (6 tình huống)
3. Quy tắc điểm dừng
4. Mẫu trình bày khi hỏi người hướng dẫn

## 1. Bốn thao tác Tư duy máy tính

**Phân rã.** Chia công trình theo chức năng; xác định input/output từng thành phần; quan hệ phụ thuộc (thành phần nào cần kết quả của thành phần nào); luồng biến đổi dữ liệu/trạng thái; đối chiếu từng thành phần với thách thức kỹ thuật nó giải. Ví dụ cho một số bài học máy: biểu diễn & xử lý dữ liệu / kiến trúc mô hình / hàm mục tiêu & cơ chế huấn luyện / quy trình suy luận. (Bài lý thuyết thuật toán thì phân rã theo bổ đề; bài hệ thống thì theo tầng giao thức.) Sau phân rã phải _nối lại_ quan hệ giữa các phần, tránh ghi chú thành mảnh rời.

**Nhận diện mẫu hình.** Khi đọc nhiều bài cùng chủ đề: những bài nào giải cùng dạng bài toán? Giả định giống/khác? Tên khác nhưng cùng nguyên lý toán học/cơ chế kiểm tra? Giới hạn nào lặp lại?

**Trừu tượng hóa.** Thử nói nguyên lý ở mức khái quát: "Gác tên riêng và cấu hình, nguyên lý nào giúp giải điểm nghẽn của bài toán?". Chi tiết chia ba nhóm: _có thể hoãn ở lượt này_ · _quyết định cách hiểu và diễn giải kết quả_ (giả định, điều kiện biên, thiết kế kỹ thuật) · _phục vụ tái hiện và triển khai_ (tham số, quy trình xử lý). Nhóm nào được hoãn tùy mục đích đọc.

**Tư duy quy trình.** Viết lại thuật toán/cơ chế thành: (1) Đầu vào (2) Các bước biến đổi chính (3) Tham số & điều kiện cần thỏa (4) Đầu ra (5) Cách đánh giá. Bước nào bài mô tả ngắn hoặc bỏ qua: **ghi rõ chỗ thiếu để kiểm tra thêm, không tự suy diễn điền khuyết.**

## 2. Bảng xử lý vướng mắc

| Tình huống                                              | Hành động                                                                                                                                                                                                                                             |
| ------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Không hiểu thuật ngữ/khái niệm                       | Kiểm tra tác giả có định nghĩa ở đoạn trước/mục Preliminaries không → tìm ví dụ cụ thể trong ngữ cảnh bài → giải thích theo ngữ cảnh đoạn văn, _tách phần định nghĩa của tác giả với kiến thức nền chung AI bổ sung_, rồi đối chiếu giáo trình/survey |
| 2. Không theo dõi được công thức/biến đổi               | Liệt kê từng ký hiệu: ý nghĩa, kiểu (vô hướng/véc-tơ/ma trận/tập hợp), kích thước chiều → điều kiện áp dụng, biến đổi đầu vào nào thành đầu ra nào → thay một bộ số rất nhỏ (toy example)                                                             |
| 3. Hiểu từng mô-đun nhưng không hình dung toàn hệ thống | Vẽ lại sơ đồ khối từ đầu vào đến đầu ra; ghi trên mỗi mũi tên dữ liệu nào đi qua                                                                                                                                                                      |
| 4. Không đọc được bảng/đồ thị                           | Đọc caption + đoạn văn nhắc đến; xác định mỗi dòng/cột là gì, đơn vị thước đo, cao hay thấp là tốt, baseline là dòng nào, chú thích dưới bảng                                                                                                         |
| 5. Thiếu kiến thức nền                                  | Xác định _một_ nội dung nền cụ thể nhất đang cản; dành thời gian giới hạn (vd. 30-60 phút) đọc mục tương ứng trong giáo trình hoặc bài nền được trích ngay tại câu đó; tránh tra cứu lan man                                                          |
| 6. Giải thích của AI khác văn bản gốc                   | Không để lời giải thích nghe hợp lý của AI ghi đè văn bản gốc. Giữ trạng thái "Chưa xác định", quay lại đoạn gốc và phụ lục; nếu bài thực sự thiếu/mơ hồ thì ghi là điểm chưa rõ của văn bản                                                          |

Khi **chính mình (AI)** giải thích công thức/bảng: nêu rõ ký hiệu nào đã được bài định nghĩa, ký hiệu nào đang suy đoán; tính toy example cẩn thận và nhắc người dùng tự tính lại (Mức 3). Cảnh giác lỗi đọc chỉ số trên/dưới và dòng/cột lệch ở bảng gộp ô trong PDF trích xuất.

## 3. Quy tắc điểm dừng

- **Tạm hoãn hợp lý:** vướng ở bước chứng minh phụ/cấu hình chi tiết chưa ảnh hưởng mục tiêu lượt hiện tại (đặc biệt Lượt 1 hoặc chỉ đọc nắm ý). Đánh dấu và đọc tiếp.
- **Tiếp tục tự xử lý:** vướng ngay nguyên lý cốt lõi của phương pháp định dùng/đối sánh, và có thể tháo bằng kiểm tra ký hiệu, vẽ sơ đồ luồng, hoặc đọc thêm _một_ tài liệu nền trực tiếp.
- **Trao đổi với người hướng dẫn/đồng nghiệp:** đã phân rã, tra định nghĩa, kiểm tra ngữ cảnh trong khoảng thời gian xác định mà vẫn chưa gỡ được bước lập luận cốt lõi.

## 4. Mẫu trình bày khi hỏi người hướng dẫn

"Em đang đọc mục X để tìm hiểu vấn đề Y; em đã hiểu đến bước A, nhưng từ A sang B em chưa rõ điều kiện Z; em đang phân vân giữa hai cách hiểu 1 và 2..." Khi thấy người dùng đã ở trạng thái này, hãy giúp soạn câu hỏi như vậy.
