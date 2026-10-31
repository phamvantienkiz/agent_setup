# Tìm kiếm, lọc và ưu tiên tài liệu (WHERE & WHEN)

## Mục lục

1. Triết lý
2. Nguồn & cách tiếp cận
3. Thứ cấp vs sơ cấp
4. Thời điểm & độ sâu
5. Bộ lọc nguồn và cạm bẫy
6. Quy trình 8 bước
7. Khi nào dừng

## 1. Triết lý

Tìm kiếm ≠ gõ từ khóa + tải hàng loạt PDF. Tìm kiếm = xây dựng danh mục có chủ đích + lọc theo mức ưu tiên. Mục tiêu không phải số lượng mà là một **hệ thống tài liệu có thể hành động**. Hai câu hỏi: _Where_ (nguồn & cách tiếp cận) và _When_ (thời điểm & độ sâu).

## 2. Nguồn & cách tiếp cận (phân biệt ba lớp)

- **Nơi công bố** (tạp chí, hội nghị): nơi định chuẩn chất lượng.
- **Nơi lưu trữ** (arXiv, thư viện, web cá nhân): nơi chứa tệp.
- **Công cụ phát hiện** (Google Scholar, DBLP...): nơi tìm ra.
  **Cảnh báo preprint (arXiv):** tìm thấy ≠ đã được thẩm định (peer-reviewed); kiểm duyệt nhẹ (moderation) không thay đánh giá chuyên gia. Luôn đối chiếu phiên bản chính thức (và lưu ý bản tech report/bản mở rộng có thể khác bản hội nghị).

## 3. Thứ cấp vs sơ cấp

|          | Thứ cấp (Survey/Review)                                | Sơ cấp (bài báo gốc)                             |
| -------- | ------------------------------------------------------ | ------------------------------------------------ |
| Bản chất | Phân loại, so sánh, hệ thống hóa                       | Trình bày trực tiếp thuật toán, mô hình, kết quả |
| Khi dùng | Điểm khởi đầu: định hình thuật ngữ và nhóm phương pháp | Đào sâu: triển khai, tái hiện thực nghiệm        |

**Nguyên tắc trích dẫn:** dùng khẳng định của ai thì trích dẫn người đó; không mượn danh mục của survey để tạo cảm giác đã đọc bài gốc.

## 4. Thời điểm & độ sâu

Khảo sát nhanh (nhận diện chủ đề, đóng góp) → Đọc chọn lọc (lấy dữ liệu, thuật toán, giả định) → Đọc sâu (phân tích lập luận, tái hiện chứng minh). Hai hướng mở rộng: **công trình nền tảng** (truy nguồn gốc lý thuyết) và **nghiên cứu gần đây** (cập nhật phương pháp, benchmark mới). Tương ứng ba lượt đọc ở `reading-passes.md`.

## 5. Bộ lọc nguồn

**Ưu tiên:** hội nghị xếp hạng ICORE (A*, A, B); tạp chí SCImago (Q1, Q2); tác giả/nhóm đầu ngành; tư vấn người hướng dẫn. (Xếp hạng thay đổi theo năm - kiểm tra bản mới nhất khi cần.)
**Cạm bẫy:** *bẫy trích dẫn* - số trích dẫn cao ≠ chân lý tuyệt đối; *bài mới* - đừng loại bài xuất sắc chỉ vì chưa kịp có trích dẫn.
**Nguyên tắc DORA:** bộ lọc nguồn dùng để *phân bổ sự chú ý\*, **không** thay thế việc tự thẩm định nội dung.

## 6. Quy trình 8 bước

1. **Từ khóa & yêu cầu:** lấy từ khóa từ CFP và DBLP; xác định mục đích, loại tài liệu, phạm vi thời gian.
2. **Khảo sát tổng quan:** bắt đầu với 1-2 survey; mục tiêu là bảng phân loại và 3-5 bài hạt giống (seed).
3. **Lọc nguồn (ICORE/SJR):** loại bỏ nhiều; chưa cần đọc sâu kỹ thuật ở bước này.
4. **Đọc lướt sàng lọc (5-10 phút/bài):** Tiêu đề → Tóm tắt → Vấn đề → Bảng kết quả → Kết luận; quyết định Giữ / Loại / Đọc thêm.
5. **Mở rộng mạng lưới từ seed paper:** _backward_ (lần theo tài liệu tham khảo → công trình gốc), _forward_ (ai trích dẫn bài này → nghiên cứu phản biện/mới hơn), _khám phá tương đồng_ (vd. Connected Papers).
6. **Tích hợp AI:** AI gợi ý từ khóa/nhóm chủ đề, hỗ trợ tóm tắt văn bản đã cung cấp, khám phá đầu mối mở rộng; con người đối chiếu tác giả/DOI/nơi công bố với nguồn chính thức và kiểm tra chéo tóm tắt với PDF gốc. _AI là trợ lý, không phải nguồn xác nhận độc lập; bạn chịu trách nhiệm về thông tin trích dẫn._
7. **Lưu trữ chuẩn hóa:** Zotero/Mendeley; sửa lỗi metadata tự động; đính kèm PDF; nhãn phân loại.
8. **Ma trận chú giải:** chuyển danh sách PDF thành ma trận chú giải (xem `note-templates.md`) - "trái tim" của quá trình tổng quan tài liệu.

## 7. Khi nào dừng

Bộ 15-20 bài cốt lõi (1-2 tổng quan · 2-3 nền tảng · 6-8 phương pháp · 2-3 dữ liệu/benchmark). Dừng khi: hiểu cấu trúc lĩnh vực; chọn được phương pháp đối sánh; có đủ căn cứ để hành động tiếp. Đừng chỉ tải tài liệu - xây dựng hệ thống tri thức: lọc là bắt buộc (review làm la bàn, ICORE/SJR làm lá chắn), đọc có chiến lược (lướt để sàng lọc, sâu để vận dụng), làm chủ AI (AI tăng tốc, bạn giữ tính xác thực), output là ma trận chứ không phải số lượng PDF.

## Hành vi của agent trong chế độ T

- Nếu người dùng cung cấp danh sách bài: dựng ma trận chú giải sơ bộ từ thông tin có sẵn, ô chưa biết = "chưa xác định"; đề xuất thứ tự đọc (Sâu/Lướt/Lưu) kèm lý do.
- Không bịa DOI, nơi công bố, xếp hạng ICORE/SJR, số trích dẫn. Nếu có công cụ web thì tra; nếu không thì ghi "cần kiểm tra".
- Phân biệt rõ survey và bài gốc khi gợi ý nên trích dẫn gì.
