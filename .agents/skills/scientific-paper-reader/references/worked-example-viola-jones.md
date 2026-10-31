# Ví dụ hiệu chỉnh: Viola & Jones (2001/2004) và hai lỗi suy diễn điển hình của AI

Nguồn: ví dụ xuyên suốt trong giáo trình. Các con số dưới đây theo giáo trình/bài gốc; khi dùng thật hãy mở bài để đối chiếu (Mức 0 cho đến khi người dùng xác nhận). Hai tình huống AI ở mục 3 là **giả định có chủ đích sư phạm**, không phải kết quả của một sản phẩm cụ thể.

## 1. Phiên bản và nơi công bố (kết nối WHERE & WHEN)

PDF thường tải được là báo cáo kỹ thuật MERL TR2004-043 (đề tháng 5/2004), nhưng trang đầu nội dung ghi "Accepted Conference on Computer Vision and Pattern Recognition 2001". Ghi danh mục: _bản tech report 2004 của MERL lưu bài đã được chấp nhận tại CVPR 2001_ - không coi là hai công trình độc lập, không ghi sai nơi công bố.

## 2. Đọc theo ba lượt

**Lượt 1.** Tiêu đề "Rapid Object Detection Using a Boosted Cascade of Simple Features" thuộc dạng [Mục tiêu X] Using [Cơ chế Y] → dự đoán: phát hiện đối tượng tốc độ cao bằng đặc trưng đơn giản + boosting + cascade. Mục đích đọc mẫu: _Học & Đánh giá_ - hiểu vì sao kết hợp ba thành phần cho tốc độ thời gian thực mà độ chính xác tương đương phương pháp chậm hơn, và kiểm tra điều kiện đi kèm khẳng định tốc độ. Ba đóng góp (Abstract & Mục 1): (1) Integral Image tính đặc trưng rất nhanh; (2) thuật toán học dựa trên AdaBoost chọn số ít đặc trưng quan trọng từ tập rất lớn; (3) cascade các bộ phân loại ngày càng phức tạp, loại nhanh vùng nền.

**Lượt 2 - tái dựng cơ chế (phân rã + nối kết).** Không chỉ chép ba đóng góp mà hỏi _vì sao cần cả ba_:

- Phải quét hàng chục nghìn cửa sổ con ở mọi vị trí/tỷ lệ → tính đặc trưng thông thường quá chậm → **Integral Image** cho tính tổng pixel của hình chữ nhật bất kỳ qua vài phép tra mảng.
- Trong cửa sổ 24×24 số đặc trưng hình chữ nhật có thể có lên tới hàng chục đến hàng trăm nghìn (bài nêu hơn 160.000 ở phần đầu, 180.000 ở phần sau tùy cách tính tập đầy đủ - cần mở bài đối chiếu), vượt xa số pixel → vẫn không thể tính hết lúc chạy → **AdaBoost** (lúc huấn luyện) chọn tập con nhỏ có tính phân biệt cao và kết hợp thành bộ phân loại.
- Bộ phân loại hàng trăm đặc trưng áp lên mọi cửa sổ vẫn tốn trong khi phần lớn cửa sổ là nền → **Attentional Cascade** đặt bộ phân loại đơn giản nhất (1-2 đặc trưng) ở tầng đầu để loại ngay phần lớn cửa sổ nền; chỉ cửa sổ qua tầng trước mới vào tầng phức tạp hơn.
  Chuỗi Integral Image → AdaBoost → Cascade: nhãn `[Người đọc tái dựng từ Tác giả] | [Mức 2]` sau khi đối chiếu Mục 1-4.

**Lượt 3 - thẩm định khẳng định hiệu năng.**

- _Con số tốc độ có điều kiện:_ "~15 fps" đo trên ảnh 384×288, bộ xử lý Intel Pentium III 700 MHz, không dùng phần cứng chuyên dụng, không dùng image differencing hay màu da. Ghi "Viola-Jones có tốc độ 15 fps" là biến kết quả có điều kiện thành thuộc tính cố định.
- _Hai con số dễ nhầm:_ cascade 38 tầng có tổng **6061** đặc trưng, nhưng trung bình chỉ khoảng **10** đặc trưng được đánh giá trên mỗi cửa sổ con vì phần lớn cửa sổ nền bị loại ở các tầng đầu. 6061 = tổng đặc trưng của mô hình đã huấn luyện; 10 = chi phí trung bình thực tế khi quét.
- _Đọc bảng đối sánh (Bảng 2, bộ MIT+CMU 130 ảnh / 507 khuôn mặt):_ đọc chú thích dưới bảng: cột Roth-Yang-Ahuja (94,8%) báo cáo sau khi loại 5 ảnh chứa khuôn mặt vẽ tay (còn 125 ảnh / 483 khuôn mặt). Tác giả báo cáo minh bạch sự khác điều kiện nhẹ này → khi đưa vào bảng tổng hợp, giữ riêng ghi chú điều kiện đánh giá.

## 3. Hai lỗi suy diễn điển hình của AI (dùng để hiệu chỉnh hành vi của bạn)

### Tình huống 1 - lược bỏ điều kiện, nhầm tổng với chi phí trung bình

Lệnh: "Tóm tắt kết quả thực nghiệm bài Viola-Jones." AI (giả định) viết: tốc độ _cố định 15 fps trên mọi loại ảnh_; _mỗi cửa sổ trượt phải tính tới 6061 đặc trưng nên rất nặng_.
Dấu hiệu nghi ngờ: "cố định, mọi loại ảnh" vi phạm nguyên tắc đánh giá hệ thống (tốc độ phụ thuộc độ phân giải, bước nhảy cửa sổ, bộ xử lý); "6061 trên mỗi cửa sổ" mâu thuẫn mục tiêu của cascade. Quay lại: Abstract, Mục 1, Mục 5.
Ghi chú chuẩn: "Bộ phát hiện 38 tầng có tổng 6061 đặc trưng, nhưng nhờ loại bỏ sớm của Cascade trung bình chỉ ~10 đặc trưng được đánh giá mỗi cửa sổ con. Đạt ~15 fps trên ảnh 384×288, Pentium III 700 MHz." `[Tác giả; người đọc sửa lỗi tóm tắt AI] | [Mức 2 tại Mục 5]`.
Chưa thể kết luận: tốc độ trên ảnh 4K hiện đại hay vi điều khiển nhúng nếu chưa tính lại số cửa sổ hoặc chạy thử.
**Bài học cho bạn:** luôn kèm điều kiện đo với con số; phân biệt tổng vs trung bình; không viết "cố định/mọi" khi bài đo trong điều kiện cụ thể.

### Tình huống 2 - bịa "rò rỉ dữ liệu" và quy kết động cơ khi bị ép phản biện

Lệnh: "Hãy đóng vai Reviewer khắt khe và chỉ ra lỗi rò rỉ dữ liệu hoặc gian lận thực nghiệm." AI (giả định) viết: tác giả _cố tình_ đưa khuôn mặt tập test MIT+CMU vào tập huấn luyện 4916 mẫu và _cố tình_ chọn baseline yếu.
Dấu hiệu nghi ngờ: xuất hiện sau câu lệnh dẫn dắt/cưỡng ép (sycophancy + phản biện cưỡng ép); cáo buộc rất nặng mà không dẫn câu/bảng nào làm căn cứ. Quay lại Mục 5: tập huấn luyện gồm 4916 ảnh khuôn mặt cắt tay từ ảnh thu thập ngẫu nhiên trên Web; đánh giá trên bộ chuẩn MIT+CMU của Rowley và cs.; các đối chứng ở Bảng 2 là hệ thống tiêu biểu mạnh được công bố trước đó.
Ghi chú chuẩn: "Tác giả báo cáo tập huấn luyện 4916 mẫu thu từ Web và đánh giá trên MIT+CMU (130 ảnh). Văn bản không có bằng chứng về trùng lặp giữa hai tập; nhận định rò rỉ của AI là suy diễn không có căn cứ do lệnh cưỡng ép. Nếu muốn kiểm tra kỹ quy trình lọc trùng ảnh Web, chỉ ghi 'bài không mô tả chi tiết quy trình kiểm tra trùng lặp ảnh Web' - không gán nhãn 'bài bị rò rỉ dữ liệu'." `[Người đọc kiểm tra lại Mục 5] | [Mức 2]`.
**Bài học cho bạn:** không bao giờ kết luận lỗi phương pháp luận/rò rỉ chỉ từ suy đoán của mô hình ngôn ngữ; phân biệt "không mô tả" và "có lỗi"; khi bị ép tìm lỗi thì trả lời theo bốn nhóm và nói thẳng nếu không có căn cứ.
