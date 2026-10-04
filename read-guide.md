Repo forrestchang/andrej-karpathy-skills là một bộ hướng dẫn giúp Claude Code làm việc “đỡ đoán mò hơn, ít over-engineer hơn, sửa đúng chỗ hơn, và bám mục tiêu kiểm chứng được hơn”. Repo này xoay quanh một file CLAUDE.md, đồng thời cũng đóng gói dưới dạng plugin/skill cho Claude Code. Nó được xây dựng từ các nhận xét của Andrej Karpathy về những lỗi điển hình khi LLM viết code.
Bốn nguyên tắc cốt lõi của repo:
Nguyên tắc 1: Think Before Coding
Repo định nghĩa rất rõ: đừng giả định, đừng giấu sự mơ hồ, hãy nêu trade-off. Trước khi implement, AI phải:
• nêu rõ giả định,
• nếu không chắc thì hỏi,
• nếu có nhiều cách hiểu thì trình bày ra,
• nếu có cách đơn giản hơn thì nói,
• nếu có gì chưa rõ thì dừng lại để làm rõ.
Ý nghĩa thực tế của nguyên tắc này là: AI không được “im lặng chọn một cách hiểu rồi code tiếp”. Ví dụ trong EXAMPLES.md, khi người dùng nói “Add a feature to export user data”, LLM thường tự giả định là export toàn bộ user, tự chọn format, tự chọn field, tự chọn file location. Trong khi cách đúng là phải hỏi hoặc ít nhất phải lộ rõ các giả định: export tất cả hay một tập lọc? tải file trên browser hay background job hay API endpoint? có field nhạy cảm không? số lượng user bao nhiêu?
Đây là nguyên tắc cực kỳ quan trọng trong môi trường doanh nghiệp. Vì lỗi nguy hiểm nhất của AI không phải lúc nào cũng là syntax error, mà là làm đúng kỹ thuật nhưng sai bài toán.
Nguyên tắc 2: Simplicity First
Repo yêu cầu: chỉ viết lượng code tối thiểu để giải quyết vấn đề, không thêm thứ suy đoán trước. Cụ thể:
• không thêm tính năng ngoài yêu cầu,
• không tạo abstraction cho logic chỉ dùng một lần,
• không thêm “flexibility/configurability” khi chưa được yêu cầu,
• không thêm error handling cho kịch bản gần như không thể xảy ra,
• nếu 200 dòng có thể viết thành 50 dòng, hãy viết lại.
Ví dụ trong EXAMPLES.md, khi người dùng chỉ yêu cầu “Add a function to calculate discount”, kiểu làm sai là dựng cả DiscountStrategy, PercentageDiscount, FixedDiscount, config object, class manager… Tức là bê cả textbook design pattern vào một nhu cầu đơn giản. Cách đúng là viết một hàm calculate_discount(amount, percent) trước; khi thực sự phát sinh nhiều loại discount thì mới refactor.
Bài học ở đây rất rõ:
Đừng thiết kế cho “tương lai tưởng tượng”. Hãy giải quyết “vấn đề hôm nay” trước.
Nguyên tắc 3: Surgical Changes
Repo nhấn mạnh: chỉ đụng vào phần thật sự cần đụng; chỉ dọn “rác” do chính thay đổi của bạn sinh ra. Khi sửa code có sẵn:
• không “tiện tay” cải thiện comment, format, style vùng lân cận,
• không refactor phần chưa hỏng,
• phải match style hiện có của codebase,
• nếu thấy dead code không liên quan, hãy ghi nhận chứ đừng tự xóa.
Chỉ những import/biến/hàm trở nên thừa do chính sửa đổi mới thì mới nên dọn đi. Repo còn đưa ra một bài test tư duy rất hay: mọi dòng thay đổi đều phải truy ngược được trực tiếp về yêu cầu của người dùng.
Ví dụ minh họa cực điển hình: user chỉ yêu cầu “Fix the bug where empty emails crash the validator”, nhưng LLM lại:
• đổi comment,
• thêm docstring,
• “cải tiến” email validation,
• thêm username validation,
• chỉnh style.
Cách đúng là chỉ sửa đúng vài dòng liên quan đến xử lý email rỗng.
Một ví dụ khác: user chỉ yêu cầu thêm logging vào hàm upload, nhưng LLM lại đổi quote style, thêm type hint, docstring, đổi logic boolean. Cách đúng là thêm logging nhưng vẫn giữ nguyên style code đang có.
Trong thực tế teamwork, nguyên tắc này giúp giảm hẳn tình trạng PR rối, diff to, review mệt, và nguy cơ phát sinh bug ngoài phạm vi.
Nguyên tắc 4: Goal-Driven Execution
Repo coi đây là insight rất quan trọng: thay vì chỉ bảo AI “làm gì”, hãy cho nó tiêu chí thành công có thể kiểm chứng. Nội dung của nguyên tắc này là:
• xác định success criteria,
• biến task mệnh lệnh thành goal có thể verify,
• với task nhiều bước thì nêu plan ngắn gọn, mỗi bước kèm một cách kiểm chứng.
Ví dụ:
• “Add validation” → “Viết test cho invalid inputs, rồi làm cho test pass”
• “Fix the bug” → “Viết test tái hiện bug, rồi sửa để test pass”
• “Refactor X” → “Đảm bảo test pass trước và sau refactor”
EXAMPLES.md làm phần này rất hay. Khi user nói “Fix the authentication system”, cách làm mơ hồ là: review code, identify issue, make improvements, test changes. Cách làm đúng là yêu cầu xác định bug cụ thể, rồi chuyển thành kế hoạch có xác minh ở từng bước: viết test tái hiện, implement fix, kiểm tra edge case, chạy full test suite.
Đây là nguyên tắc giúp AI từ “thợ code theo lệnh” chuyển thành “tác nhân thực thi có điều kiện dừng rõ ràng”.
Mẫu CLAUDE.md gợi ý để áp dụng thực chiến
Repo cung cấp bản gốc khá ngắn. Khi triển khai thật, bạn nên giữ nguyên tinh thần cốt lõi nhưng thêm rule riêng của team. Ví dụ dưới đây là một bản Việt hóa và mở rộng vừa đủ:

# Claude Working Rules

## Core Behavior

### 1. Think Before Coding

- Không được tự giả định yêu cầu nếu còn mơ hồ.
- Nếu có nhiều cách hiểu, phải nêu ra các khả năng.
- Nếu có cách đơn giản hơn, phải nói rõ.
- Nếu chưa chắc, dừng lại và hỏi.

### 2. Simplicity First

- Chỉ viết lượng code tối thiểu để giải quyết đúng yêu cầu.
- Không thêm abstraction cho logic dùng một lần.
- Không thêm config/flexibility khi chưa được yêu cầu.
- Không thêm feature suy đoán trước.
- Nếu giải pháp có thể ngắn hơn đáng kể, chọn cách ngắn hơn.

### 3. Surgical Changes

- Chỉ sửa đúng phạm vi user yêu cầu.
- Không refactor hoặc reformat phần không liên quan.
- Giữ nguyên style code hiện có.
- Chỉ xóa import/biến/hàm thừa do chính thay đổi mới tạo ra.

### 4. Goal-Driven Execution

- Mọi task phải được diễn dịch thành tiêu chí thành công có thể kiểm chứng.
- Với bug: ưu tiên tái hiện bằng test trước.
- Với task nhiều bước: nêu plan ngắn và cách verify sau từng bước.

## Project-Specific Rules

- Dùng TypeScript strict mode.
- Mọi API mới phải có test.
- Không thay đổi public API nếu chưa được yêu cầu.
- Ưu tiên sửa tối thiểu trước khi refactor.

## Output Expectations

- Trước khi code: nêu assumptions nếu có.
- Khi hoàn thành: báo rõ đã sửa gì, chưa sửa gì, và cách verify.
  Đây là bản mở rộng theo đúng tinh thần README: merge guideline chung với guideline riêng của dự án.
  EXAMPLES.md không chỉ để xem qua. Bạn nên đọc theo 3 lớp.
  Lớp 1: nhìn ra anti-pattern
  Repo tổng kết 4 anti-pattern rất rõ:
  • âm thầm giả định,
  • over-abstraction quá sớm,
  • sửa lan sang phần không liên quan,
  • làm việc bằng mô tả mơ hồ thay vì success criteria.
  Lớp 2: nhìn cách chuyển hóa
  Mỗi ví dụ đều có dạng:
  • user request,
  • LLM thường làm sai,
  • cách đúng nên làm.
  Lớp 3: biến thành checklist làm việc
  Sau khi đọc xong, bạn có thể tự hình thành checklist nhanh trước mọi task code:

1. Có chỗ nào đang mơ hồ không?
2. Cách đơn giản nhất là gì?
3. Mình sắp sửa đúng chỗ hay sắp “đụng lan”?
4. Xong rồi thì verify bằng gì?
   Nếu dùng repo đúng cách, đây mới là thứ thay đổi chất lượng làm việc của AI.
