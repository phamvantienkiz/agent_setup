# Phối hợp với AI có kiểm soát và truy vết

## Mục lục

1. Ai làm gì: bốn câu hỏi phân định
2. Hệ thống nhãn hai trường
3. Năm cạm bẫy
4. Xử lý nhiều tài liệu (hai tầng, "lost in the middle")
5. Phân công công cụ theo chức năng
6. Vai trò của chính bạn (agent) ở từng điểm

## 1. Phân định trách nhiệm

Ranh giới đúng không phải là cấm giao việc cho AI mà là bốn câu hỏi:
| Câu hỏi | Nguyên tắc |
|---|---|
| Thao tác nào ủy quyền cho AI? | Cơ học/định hướng sơ bộ: tìm vị trí mục/bảng chứa từ khóa, định dạng lại bảng ghi chú từ dữ liệu đã kiểm tra, dịch thuật ngữ ban đầu, gợi ý danh sách câu hỏi cần kiểm tra |
| Năng lực nào người học phải tự rèn? | Đọc hiểu trực tiếp đoạn lập luận cốt lõi, tái dựng quy trình, tự giải thích bằng lời mình, kiểm tra tính hợp lệ của chứng minh/thực nghiệm, kết nối vào đề tài |
| Đầu ra AI nào bắt buộc kiểm chứng? | Thông tin thư mục, con số thực nghiệm, công thức, điều kiện định lý, khẳng định gán cho tác giả, nhận định về gap - luôn mở văn bản gốc đối chiếu |
| Quyết định nào người nghiên cứu tự chịu trách nhiệm? | Chọn/loại tài liệu, nhận định điểm mạnh/giới hạn, trích dẫn vào bài viết, hướng đi tiếp |
Ngay cả khi AI "đóng vai đối tác phản biện", người học vẫn lệ thuộc nếu chỉ chép lại câu hỏi/nhận xét của AI mà không tự mở văn bản gốc.

## 2. Hệ thống nhãn hai trường

Một thông tin thường đi qua nhiều bước (tác giả viết → AI rút trích → người đọc đối chiếu). Một nhãn duy nhất sẽ lẫn "ai nói" với "đã kiểm tra đến đâu", nên tách hai trường.

**Trường 1 - Nguồn:** `Tác giả` · `Người đọc` (suy luận, câu hỏi phản biện, ví dụ kiểm tra, ý tưởng mở rộng) · `AI` (giải thích, gom nhóm, rút trích, gợi ý) · `Tài liệu khác` (kèm tên).

**Trường 2 - Mức kiểm tra:**

- **Mức 0 - Chưa đối chiếu:** chưa mở kiểm tra trên văn bản gốc (thường là do AI rút trích hoặc từ trí nhớ).
- **Mức 1 - Đã đối chiếu văn bản:** người đọc đã mở đúng trang/mục/bảng/hình và xác nhận thông tin/số xuất hiện đúng như vậy.
- **Mức 2 - Đã phân tích căn cứ:** đã kiểm tra thiết kế thực nghiệm, điều kiện đo, chú thích bảng, các bước lập luận đi kèm.
- **Mức 3 - Đã kiểm chứng độc lập:** tự chứng minh lại công thức, tính lại ví dụ nhỏ, hoặc chạy lại mã/thực nghiệm.

Ví dụ ghi chú: "Hệ thống đạt ~15 khung hình/giây [Nguồn: Tác giả, AI hỗ trợ định vị] | [Mức 1: đã đối chiếu tại Abstract và Mục 5, cần đọc tiếp điều kiện phần cứng và kích thước ảnh - chuyển lên Mức 2]".

**Quy ước khi bạn là AI trong phiên làm việc:**

- Bạn không tự nâng mức thay người dùng. Con số bạn định vị trong văn bản người dùng đưa vẫn là `Mức 0 (AI đã định vị, chờ bạn mở kiểm tra)`.
- Có thể ghi `Mức 2 - AI phân tích, chờ bạn xác nhận` khi bạn đã cùng người dùng đọc kỹ bảng, chú thích và điều kiện trong phiên.
- Mức 1 chỉ xác nhận _con số có trong bài_, không xác nhận kết luận khoa học đúng trong mọi điều kiện. Với khẳng định giữ vai trò quyết định trong đề tài, cần tiến tới Mức 2-3.
- Chỉ gắn nhãn cho khẳng định chính, số liệu, suy luận - không gắn từng câu.

## 3. Năm cạm bẫy

1. **Sycophancy (đồng thuận chiều theo người dùng)** - Sharma và cs. (2024): mô hình có xu hướng điều chỉnh câu trả lời theo quan điểm/mong muốn ngầm của người dùng. Câu hỏi dẫn dắt ("chỉ ra vì sao thực nghiệm này không đáng tin") kéo suy diễn sang phủ định. **Kiểm soát:** đặt câu hỏi trung lập; nêu cả căn cứ ủng hộ lẫn giới hạn; cho phép "chưa đủ thông tin trong văn bản"; nếu câu hỏi của người dùng mang tính dẫn dắt, diễn đạt lại thành dạng trung lập rồi trả lời, và nói rõ bạn đã làm vậy.
2. **Phản biện cưỡng ép** - đừng nhận "tìm đủ 3 lỗi nghiêm trọng". Phân biệt 4 nhóm: (a) giới hạn có căn cứ rõ trong văn bản; (b) rủi ro khi đổi điều kiện; (c) thông tin bài chưa mô tả; (d) vấn đề chính tác giả đã giải quyết/nêu ở Discussion.
3. **Khoảng trống nghiên cứu giả** - khi chưa thấy phương pháp X áp dụng cho bài toán Y trong tài liệu được cung cấp, chỉ ghi "Chưa quan sát thấy nội dung này trong tập tài liệu hiện tại", không kết luận "chưa ai trên thế giới nghiên cứu" trước khi tìm kiếm mở rộng.
4. **Nhầm sản phẩm công cụ với năng lực bản thân** - duy trì bước tự giải thích không dùng công cụ cho bài cốt lõi (`reading-passes.md` mục 5). Nghiên cứu khảo sát tự báo cáo của Lee và cs. (2025) ghi nhận mối liên hệ giữa tin tưởng AI tạo sinh và giảm nỗ lực tư duy phản biện; đây không phải bằng chứng nhân quả, nhưng gợi ý rằng độ trôi chảy của văn bản AI và mức hiểu của người dùng là hai thứ cần đánh giá riêng.
5. **Bảo mật & đạo đức học thuật** - không tải bản thảo đang bình duyệt mật, dữ liệu cá nhân/nhạy cảm, tài liệu chưa được phép công khai lên công cụ bên ngoài; tôn trọng bản quyền và quyền tự quyết của con người (UNESCO 2023).

## 4. Nhiều tài liệu cùng lúc

Làm hai tầng:

- **Tầng danh mục:** dùng AI rút trích trường cơ bản (bài toán, phương pháp chính, dữ liệu, kết quả báo cáo) để phân nhóm sơ bộ; _không để tóm tắt tự động quyết định hoàn toàn việc loại bài có cách tiếp cận khác biệt hoặc kết quả trái chiều_.
- **Tầng công trình cốt lõi:** người nghiên cứu trực tiếp đọc toàn văn, kiểm tra giả định, thiết kế đánh giá, chứng minh của các bài hạt giống/đối chứng trực tiếp.

"Lost in the Middle" (Liu và cs. 2024): với các mô hình và tác vụ được khảo sát, khả năng dùng thông tin thay đổi theo vị trí trong ngữ cảnh dài (thường kém ở giữa). Dù hệ thống mới có thể tốt hơn, đừng đồng nhất "nạp được hàng chục PDF" với "đã xử lý đầy đủ mọi chi tiết". Làm theo nhóm nhỏ cùng một câu hỏi, và với câu hỏi quan trọng thì mở lại đúng đoạn nguồn thay vì dựa vào trí nhớ ngữ cảnh.

## 5. Phân công công cụ theo chức năng (theo tài liệu chính thức của từng nền tảng)

- Đọc lướt có hỗ trợ: Semantic Reader (lớp đánh dấu mục tiêu/phương pháp/kết quả, giải thích ký hiệu trên trang).
- Hỏi đáp có truy vết trên tập tài liệu đã chọn: NotebookLM (chỉ mục trích dẫn về đoạn nguồn).
- Rút trích thông tin thành bảng: Elicit (rút theo cột, truy vết về bài gốc; nhưng tài liệu hỗ trợ của Elicit tự lưu ý trích xuất từ bảng/hình phức tạp có thể sai hoặc thất bại).
  Mô tả chức năng không phải bảo chứng độ chính xác; luôn kiểm tra lại.

## 6. Vai trò của bạn (agent) ở từng điểm

- Định vị, chỉ mục, định dạng lại, dịch thuật ngữ, soạn câu hỏi gợi mở: làm tốt và nhanh.
- Khi người dùng muốn bạn "đọc hộ rồi kết luận": làm phần định vị và tóm tắt có nhãn, nhưng trả lại các quyết định (giữ/loại, trích dẫn, hướng đi) cho họ và nói rõ vì sao.
- Khi lời giải thích của bạn khác văn bản gốc: văn bản gốc thắng; đánh dấu "Chưa xác định".
- Khi không biết hoặc văn bản không có: nói thẳng. Không điền khuyết để câu trả lời "đầy đủ".
