# Tư duy phản biện áp dụng cho việc đọc bài báo và dùng AI

Nguồn: Cẩm nang Tư duy Phản biện của giảng viên (đề cương câu hỏi) + hiểu biết chuẩn về logic. Dùng để _hiệu chỉnh cách hỏi và cách đọc_, không để tranh luận học thuật suông.

## 1. Bản chất

Tư duy phản biện khác với tiếp thu hay tóm tắt: nó là việc đánh giá có căn cứ. Bốn hành vi tư duy nguyên bản cho thực hành: **quan sát phân tích chi tiết → làm rõ câu hỏi phức tạp → đánh giá đa biến (nguy cơ/phần thưởng, được/mất) → đưa ra kết luận phức tạp (có sắc thái, có điều kiện)**. Ánh xạ vào đọc bài: quan sát (đọc kỹ bảng/chú thích) → làm rõ (câu hỏi nghiên cứu, thuật ngữ) → đánh giá (căn cứ, trade-off) → kết luận có điều kiện.

**Ý kiến vs lập luận:** ý kiến là một quan điểm; lập luận học thuật nêu khẳng định, căn cứ, và mối liên hệ giữa chúng. Khi người dùng nói "bài này tệ/hay", hỏi lại: dựa vào căn cứ nào, ở đâu trong bài?

## 2. Thiên kiến và bẫy tư duy (của người đọc, của AI, của tác giả)

- **Thiên kiến xác nhận:** chỉ tìm thông tin củng cố niềm tin sẵn có. Đối trị: chủ động tìm căn cứ _ngược_ với giả thuyết đang ưa, và để AI trả lời câu hỏi trung lập, nêu cả căn cứ ủng hộ lẫn giới hạn. Đặc biệt cẩn trọng khi người dùng đang cần bài "ủng hộ đề tài của mình".
- **Tư duy đen-trắng:** "tốt hoàn toàn/tệ hoàn toàn" dẫn đến thông tin sai lệch. Kết luận nên có sắc thái: đúng trong điều kiện nào, yếu ở đâu.
- **Spin (thêu dệt):** diễn đạt nâng khẳng định vượt dữ kiện (vd. abstract mạnh hơn bảng kết quả; "significantly" không kèm kiểm định). **Cherry-picking:** chỉ trình bày kết quả/dữ liệu/baseline có lợi. Cách xử lý đúng: so sánh phát biểu với bảng; ghi "bài chưa cung cấp kết quả trên…" thay vì buộc tội.
- **Tương quan ≠ nhân quả:** hai thứ cùng xảy ra không có nghĩa cái này gây ra cái kia; có thể do biến gây nhiễu hoặc chiều ngược lại. Trong ML: cải thiện đi kèm thay đổi nhiều yếu tố cùng lúc cần ablation/phép kiểm tra phân biệt mới quy được cho một yếu tố.
- **Sycophancy của AI:** xem `ai-guardrails.md`.

## 3. Ngụy biện thường gặp khi tranh luận về bài báo

- **Straw man (người rơm):** bóp méo khẳng định của tác giả thành phiên bản dễ bác bỏ rồi bác bỏ nó. Đối trị: diễn đạt lại khẳng định _đúng như bài viết_ (kèm vị trí) trước khi phê bình.
- **Ad hominem:** công kích tác giả/nhóm/hãng thay vì căn cứ. Uy tín nơi công bố hay tác giả giúp _phân bổ sự chú ý_, không thay thế thẩm định.
- **Appeal to authority / số trích dẫn:** trích dẫn cao ≠ chân lý tuyệt đối; bài mới chưa có trích dẫn vẫn có thể xuất sắc.
- **Hasty generalization:** từ một dataset/cấu hình kết luận cho mọi bối cảnh.
- **False dilemma:** chỉ có "hoặc A hoặc B" trong khi còn cách giải thích thứ ba.

## 4. Thấu cảm trí tuệ và hoài nghi lành mạnh

- **Thấu cảm trí tuệ:** thử đặt mình vào góc nhìn tác giả, diễn đạt lập luận của họ ở dạng mạnh nhất, rồi mới phản biện; nghiêm túc cân nhắc khả năng _mình_ sai (hoặc AI sai).
- **Hoài nghi lành mạnh / năng lực truyền thông:** trong kỷ nguyên bùng nổ thông tin và tin giả, không tin ngay, cũng không bác bỏ ngay: hỏi nguồn gốc, căn cứ, điều kiện, và kiểm chứng ở nguồn gốc. Áp dụng cả cho nội dung do AI tạo, bản tin về "paper mới", và tóm tắt trên mạng xã hội.

## 5. Mẫu câu hỏi hiệu chỉnh (dùng với người dùng hoặc tự hỏi)

- "Khẳng định chính xác là gì, ở đâu trong bài?" · "Căn cứ nào trực tiếp hỗ trợ?" · "Có cách giải thích khác cho cùng kết quả không?" · "Điều gì sẽ làm khẳng định này sai?" · "Mình đang tìm bằng chứng cho điều mình muốn tin chăng?"
