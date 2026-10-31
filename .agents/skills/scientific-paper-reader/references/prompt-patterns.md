# Hành vi mẫu cho 14 tình huống quen thuộc (P1-P14 của giáo trình)

Giáo trình gốc có 14 mẫu lời nhắc dành cho _người học_ gửi AI. Ở đây chúng được chuyển thành **hành vi của bạn (agent)** khi người dùng nêu yêu cầu tương tự (dù họ nói tự nhiên, không dùng tên mẫu). Mỗi mục: khi nào · việc người dùng nên làm trước · bạn làm gì · giới hạn · việc người dùng tự kiểm tra sau.

Nguyên tắc chung: nếu người dùng chưa tự làm bước "làm trước" và không có dấu hiệu họ muốn bạn làm hộ hết, vẫn hãy giúp - nhưng đề xuất bước tự làm như một lựa chọn, đặc biệt với bài cốt lõi (xem chế độ self-first trong `SKILL.md`).

## Lượt 1 - Định hướng

**P1 - Câu hỏi đọc từ mục đích.** Khi: người dùng sắp đọc, đưa tiêu đề/abstract + mục đích. Bạn: chỉ dựa riêng trên Abstract, gợi ý 3-4 câu hỏi dẫn đường sát mục đích; _không suy đoán nội dung bên trong bài khi chưa có văn bản_. Giới hạn: chỉ là câu hỏi, không trả lời thay nội dung bài. Người dùng: chọn 2-3 câu thật sát đề tài, ghi đầu phiếu.

**P2 - Định vị thông tin (Scanning).** Khi: "tác giả chia tập dữ liệu thế nào / điều kiện của định lý X ở đâu / cách tính chi phí thời gian?" Bạn: chỉ ra mục, đoạn, bảng, phụ lục chứa thông tin kèm câu đầu của đoạn để người dùng tự mở; _chưa tóm tắt/đánh giá_; nếu không có: "Không tìm thấy trong phạm vi văn bản đã cung cấp" + liệt kê phạm vi đã quét. Giới hạn: có thể bỏ sót nếu tác giả dùng thuật ngữ tương đương ở phụ lục. Người dùng: mở PDF đúng chỗ, đọc ngữ cảnh quanh đó.

## Lượt 2 - Tái dựng & giải mã

**P3 - Giải thích thuật ngữ theo ngữ cảnh bài.** Bạn: (1) nghĩa tác giả dùng trong đoạn này; (2) _tách_ phần định nghĩa có trong văn bản với kiến thức nền chung bạn bổ sung; (3) một ví dụ nhỏ. Giới hạn: kiến thức nền chung có thể rộng/lệch hơn quy ước hẹp của nhóm tác giả. Người dùng: thế lời giải thích ngược lại vào câu gốc xem mạch có thông không.

**P4 - Đối chiếu bản tái dựng 7 thành phần của người dùng.** Bạn: với từng mục, chỉ ra (1) điểm đúng có căn cứ (kèm vị trí) (2) điểm thiếu điều kiện/giả định quan trọng (3) điểm suy diễn vượt quá điều tác giả viết; tại (2) và (3) **đặt câu hỏi gợi mở, chưa viết lại bản hoàn chỉnh**. Giới hạn: chỉ đối chiếu trên phần văn bản được cung cấp; không thay kiểm tra chứng minh. Người dùng: mở lại đoạn lệch, tự sửa, gắn Mức 1 hoặc 2.

**P5 - Công thức/bước biến đổi.** Khi người dùng đã liệt kê ký hiệu mình biết và chỉ ra chỗ chưa hiểu. Bạn: bảng ký hiệu (kiểu dữ liệu/chiều nếu bài nêu); công thức nhận đầu vào gì, tạo đầu ra gì; một toy example số nhỏ; báo vị trí cần tìm nếu ký hiệu chưa được định nghĩa. Giới hạn: có thể đọc nhầm chỉ số trên/dưới từ PDF lỗi, tính nhẩm sai. Người dùng: tự tính lại ví dụ trên giấy, đối chiếu mục Preliminaries/Notation (→ Mức 3).

**P6 - Rà soát quy trình/mã giả người dùng tự dựng.** Bạn: (1) bước trung gian/luồng phụ thuộc dữ liệu nào người dùng bỏ sót hoặc xếp sai thứ tự? (2) bước nào bài _thực chất không mô tả_ mà người dùng đang tự đoán? Chỉ rõ đoạn tương ứng. Giới hạn: chỉ phản ánh mức khớp với mô tả văn bản, chưa khẳng định mã thực tế. Người dùng: cập nhật sơ đồ, đánh dấu chỗ bài mô tả chưa đủ (kiểm tra phụ lục/mã nguồn).

## Lượt 3 - Thẩm định (chuỗi P7 → P11, từng nhịp có điểm dừng)

**P7 - Định vị khẳng định và căn cứ được viện dẫn.** Bạn: nơi tác giả lặp lại/cụ thể hóa khẳng định; bảng/hình/thí nghiệm/định lý được dẫn. _Chưa đánh giá đúng sai._ Dừng: người dùng tự mở các vị trí đó.

**P8 - Đọc bảng/hình, thước đo, điều kiện.** Bạn: định nghĩa & đơn vị từng thước đo (cao hay thấp là tốt); cấu hình/kích thước dữ liệu/số lần chạy nêu ở đâu; footnote hay ngoại lệ riêng cho dòng/cột nào. Giới hạn: dễ đọc lệch dòng/cột với bảng gộp ô. Người dùng: dò tay từng dòng/cột trên PDF gốc (→ Mức 2).

**P9 - Phạm vi khẳng định vs phạm vi bằng chứng.** Bạn: (1) phần nào của khẳng định được kết quả hỗ trợ trực tiếp (2) gắn với điều kiện dữ liệu/cấu hình/workload/giả định nào (3) đề xuất câu kết luận có điều kiện vừa vặn. Không suy đoán động cơ. Giới hạn: phụ thuộc đoạn được cung cấp; tác giả có thể đã nêu giới hạn ở Discussion. Người dùng: kiểm tra Discussion/Limitations.

**P10 - Giả định và điều kiện biên.** Bạn: (1) giả định ngầm nào về đặc tính dữ liệu/phân phối/môi trường mà bước A→B dựa vào? (2) bối cảnh thực tế nào điều kiện đó có nguy cơ không được đáp ứng? _Tách rõ "điều được viết trong bài" và "phân tích suy luận kỹ thuật"._ Giới hạn: kịch bản biên chỉ là giả thuyết suy luận. Người dùng: xem kịch bản có xảy ra trong miền dữ liệu đề tài mình không.

**P11 - Cách giải thích thay thế & phép kiểm tra phân biệt.** Bạn: (1) trong bài có ablation/bảng phụ giữ cố định yếu tố B để kiểm tra riêng vai trò A chưa? (2) nếu chưa, gợi ý phép so sánh tối thiểu. Giới hạn: phép thử gợi ý có thể tốn tài nguyên/bỏ sót ràng buộc đặc thù. Người dùng: kiểm tra Ablation & Appendix trước khi kết luận "tác giả chưa làm".

## Tổng hợp & tự kiểm tra

**P12 - Đối sánh nhiều bài (synthesis).** Xem `note-templates.md` mục 4. Chỉ dựa trên ghi chú đã kiểm tra; giữ riêng kết quả khác điều kiện; chỉ chỗ các bài mâu thuẫn; không biến ô trống thành "chưa ai nghiên cứu".

**P13 - Rà soát nguồn gốc & trạng thái xác minh của Phiếu ghi chú.** Bạn: (1) câu nào viết như sự thật hiển nhiên mà thiếu điều kiện/vị trí; (2) câu nào trộn điều tác giả báo cáo với suy luận cá nhân mà chưa tách nhãn; (3) điểm nào cần nâng Mức 0/1 lên Mức 2 trước khi trích dẫn. Giới hạn: chỉ rà hình thức lập luận và đối chiếu văn bản; trách nhiệm xác nhận cuối thuộc người đọc.

**P14 - Kiểm tra tự giải thích sau khi đóng tài liệu.** Người dùng đưa đoạn tự giải thích. Bạn: (1) điểm đã hiểu đúng bản chất; (2) chỗ mơ hồ/thiếu điều kiện/mâu thuẫn với bài gốc. **Trước tiên chỉ đặt 1-2 câu hỏi gợi mở** tại chỗ mơ hồ, chưa viết hộ đoạn hoàn chỉnh. Người dùng: tự trả lời, mở lại đoạn gốc, chỉnh đến khi rõ và chính xác.

## Các tình huống thường gặp khác

- **"Tóm tắt paper này":** chế độ S (khung 7 điểm); không chép abstract; có quyết định độ sâu.
- **"Paper này có đáng tin không?":** chuyển thành câu hỏi trung lập: _căn cứ nào hỗ trợ khẳng định nào, trong điều kiện nào?_ Trả lời bằng nhận định cân bằng 4 mục; nói rõ không thể kết luận "đáng tin" tuyệt đối.
- **"Tìm lỗi/điểm yếu của bài":** không cam kết số lượng; phân 4 nhóm (a-d); kiểm tra phần tác giả đã tự nêu.
- **"Tìm research gap":** phân biệt gap / unknown / thiếu kiến thức cá nhân; ghi gap theo 3 dòng; chỉ nói "chưa quan sát thấy trong tập tài liệu hiện tại".
- **"Viết related work / literature review":** chỉ dùng thông tin đã kiểm tra; trích dẫn đúng nguồn (survey ≠ bài gốc); hỗ trợ cấu trúc theo nhóm phương pháp, không bịa tài liệu tham khảo.
