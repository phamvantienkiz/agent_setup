# Báo Cáo Phân Tích Tinh Túy Clean Code: `skilldb_clean-code-skills`

- **Tên kho lưu trữ / thư mục**: `skilldb_clean-code-skills`
- **Định dạng**: Bộ 8 Agent Skills chuyên sâu độc lập
- **Giấy phép**: MIT / Open Source
- **Đường dẫn phân tích**: [skilldb_clean-code-skills](file:///E:/gemini/agent_setup/skilldb_clean-code-skills)

---

## 1. Tổng Quan & Cấu Trúc Khác Biệt (Architecture & Scope)

Không giống như `btseee` (tập trung vào công cụ phân tích tĩnh và ràng buộc AI) hay `ertugrul-dmr` (bảng tra cứu 66 điều luật ngắn gọn), `skilldb_clean-code-skills` là một **bộ bách khoa toàn thư chuyên sâu về tư duy thiết kế phần mềm (Design Thinking & Engineering Philosophy)**.

Thư mục được chia tách thành **8 skill độc lập theo từng chủ đề cốt lõi**:
1. [code-smells](file:///E:/gemini/agent_setup/skilldb_clean-code-skills/code-smells/SKILL.md): Nhận diện và xử lý "mùi code" theo hệ miễn dịch.
2. [dependency-management](file:///E:/gemini/agent_setup/skilldb_clean-code-skills/dependency-management/SKILL.md): Quản lý phụ thuộc, đảo ngược kiểm soát và triệt tiêu coupling ẩn.
3. [error-handling](file:///E:/gemini/agent_setup/skilldb_clean-code-skills/error-handling/SKILL.md): Xử lý lỗi sạch, tách luồng happy path, triệt tiêu `null`.
4. [function-design](file:///E:/gemini/agent_setup/skilldb_clean-code-skills/function-design/SKILL.md): Thiết kế hàm như một "đơn vị tư duy", tuân thủ SLAP và CQS.
5. [naming-conventions](file:///E:/gemini/agent_setup/skilldb_clean-code-skills/naming-conventions/SKILL.md): Nghệ thuật đặt tên theo ngôn ngữ nghiệp vụ (Domain-driven naming).
6. [refactoring-patterns](file:///E:/gemini/agent_setup/skilldb_clean-code-skills/refactoring-patterns/SKILL.md): Tái cấu trúc bảo toàn hành vi, Characterization Tests và Quy tắc số 3.
7. [solid-principles](file:///E:/gemini/agent_setup/skilldb_clean-code-skills/solid-principles/SKILL.md): 5 nguyên lý SOLID nhìn dưới góc độ lăng kính thực nghiệm.
8. [testing-principles](file:///E:/gemini/agent_setup/skilldb_clean-code-skills/testing-principles/SKILL.md): Kim tự tháp kiểm thử, kiểm thử hành vi thay vì chi tiết triển khai.

Mỗi file `SKILL.md` đều tuân thủ cấu trúc sư phạm chuẩn mực:
- **Core Philosophy**: Triết lý sâu xa giải thích tại sao nguyên lý đó lại quan trọng.
- **Anti-Patterns**: Các cạm bẫy thực tế và cách hiểu sai thường gặp.
- **Overview & Core Principles**: Tóm tắt các nguyên tắc cốt lõi.
- **Implementation Patterns**: So sánh trực quan mã nguồn **Before vs After** trên nhiều ngôn ngữ (Python, TypeScript, JavaScript).
- **Best Practices & Common Pitfalls**: Checklist kiểm tra và cạm bẫy cần tránh.

---

## 2. Chi Tiết Tinh Túy Của Từng Chủ Đề Chuyên Sâu

### 1. `code-smells` — Hệ Miễn Dịch Của Codebase
- **Triết lý**: Mùi code không phải là bug (code vẫn chạy, test vẫn pass), mà là tín hiệu cảnh báo sớm về cấu trúc suy yếu khiến code ngày càng đắt đỏ khi thay đổi.
- **Quy tắc ưu tiên thực dụng**: **Ưu tiên refactor theo tần suất thay đổi (Change Frequency), không phải theo độ nặng của smell**. Một "God class" ở module 2 năm không ai đụng tới có mức ưu tiên thấp hơn một hàm duplicate nhẹ trong file bị sửa đổi mỗi sprint.
- **Các mẫu smell chủ chốt**:
  - *Long Method* $\rightarrow$ Tách hàm theo từng mức độ trừu tượng.
  - *Feature Envy* $\rightarrow$ Chuyển hàm về nơi chứa dữ liệu mà nó thèm muốn.
  - *Primitive Obsession* $\rightarrow$ Đóng gói các kiểu nguyên thủy (`str`, `float`) thành Value Objects (`AccountId`, `Money`).
  - *Data Clumps* $\rightarrow$ Gom nhóm các tham số luôn đi cùng nhau (`x, y, z` thành `Point3D`).

### 2. `dependency-management` — Biến Cái Vô Hình Thành Hữu Hình
- **Triết lý**: Sự trung thực của mã nguồn nằm ở constructor. Một class khai báo tường minh toàn bộ dependencies trong constructor là một thiết kế trung thực. Các phụ thuộc ẩn như Global Singleton, Service Locator, Ambient Context là những lời nói dối ngầm khiến code cực kỳ khó test.
- **Nguyên lý cốt lõi**:
  - *Stable Dependencies Principle*: Module kém ổn định phải phụ thuộc vào module ổn định, không bao giờ có chiều ngược lại.
  - *Inversion of Abstraction Ownership*: High-level module không chỉ phụ thuộc vào abstraction, mà chính nó phải là bên **sở hữu** abstraction đó. Không bao giờ để domain logic import interface được định nghĩa bởi package database hay infrastructure.

### 3. `error-handling` — Tách Biệt Happy Path Và Failure Path
- **Triết lý**: Tách bạch dòng chảy nghiệp vụ bình thường khỏi luồng cứu vãn lỗi.
- **Nguyên tắc hành động**:
  - Dùng Exception thay vì mã lỗi trả về (`-1`, `null`, `false`). Mã lỗi bắt mọi nơi gọi phải nhớ kiểm tra, trong khi Exception buộc hệ thống phải xử lý có chủ đích.
  - **Triệt tiêu `null`**: Không bao giờ trả về `null` (hãy trả về collection rỗng, Default Object, Optional/Result type hoặc raise exception). Tuyệt đối không truyền `null` làm tham số.
  - Bọc các Exception của thư viện bên thứ 3 thành Exception nghiệp vụ của ứng dụng ngay tại ranh giới tích hợp.

### 4. `function-design` — Hàm Là Một Đơn Vị Tư Duy (Unit of Thought)
- **Triết lý**: Hàm phải đọc mượt mà như một bài tường thuật từ trên xuống dưới (Top-down narrative).
- **Nguyên tắc hành động**:
  - **Single Level of Abstraction (SLAP)**: Không bao giờ để một dòng gọi logic cấp cao (`fetchUser()`) nằm cạnh một dòng thao tác chuỗi thô sơ (`date.split('-')[0]`).
  - **Quy tắc kích thước**: Hàm lý tưởng từ 5 đến 15 dòng; vượt quá 20 dòng là dấu hiệu cần trích xuất.
  - **Command-Query Separation (CQS)**: Một hàm hoặc là thay đổi trạng thái (Command), hoặc là trả về dữ liệu (Query) — tuyệt đối không làm cả hai.

### 5. `naming-conventions` — Duy Trì Sự Thật Trong Code
- **Triết lý**: Đổi tên (Renaming) không phải là việc vặt thừa thãi, mà là hành động duy trì sự thật trong code khi hiểu biết về domain ngày càng sâu sắc.
- **Nguyên tắc hành động**:
  - Lấy từ vựng từ Problem Domain (dùng `ledgerEntry` thay cho `row`, `reconcile` thay cho `process`).
  - Nhất quán từ vựng: Không dùng lẫn lộn `fetch`, `get`, `retrieve`, `load` cho cùng một thao tác.
  - Tên biến là danh từ mô tả nội dung; tên hàm là động từ bộc lộ hành vi và phản ánh cả side effects nếu có.

### 6. `refactoring-patterns` — Tái Cấu Trúc Bảo Toàn Hành Vi
- **Triết lý**: Tái cấu trúc mà không có test bảo vệ không phải là refactoring — đó là viết lại liều lĩnh (Rewriting).
- **Nguyên tắc hành động**:
  - Bắt buộc phải có Characterization Tests trước khi bắt tay refactor.
  - Không bao giờ gộp vừa sửa cấu trúc vừa thêm tính năng trong cùng một commit.
  - **Quy tắc số 3 (Rule of Three)**: Chỉ trừu tượng hóa hoặc áp dụng Design Pattern (Strategy, Factory...) khi đã xuất hiện 3 trường hợp cụ thể thực tế.

### 7. `solid-principles` — Lăng Kính Đánh Giá Quyết Định Thiết Kế
- **Triết lý**: SOLID không phải là checklist để làm theo một cách máy móc, mà là các lăng kính để trả lời cho từng trục thay đổi của hệ thống:
  - *SRP*: Class này có bao nhiêu lý do để thay đổi?
  - *OCP*: Có thể thêm hành vi mới mà không sửa code cũ không?
  - *LSP*: Class con có thay thế hoàn hảo cho class cha mà không gây bất ngờ không?
  - *ISP*: Client có bị ép phụ thuộc vào method nó không dùng không?
  - *DIP*: Chính sách cấp cao có bị phụ thuộc vào chi tiết cấp thấp không?

### 8. `testing-principles` — Cơ Sở Hạ Tầng Của Sự Tự Tin
- **Triết lý**: Test không phải là "thuế" phải nộp, mà là cơ sở hạ tầng cho phép thay đổi với sự tự tin tuyệt đối.
- **Nguyên tắc hành động**:
  - **Test hành vi quan sát được (Observable Behavior), không test chi tiết triển khai (Implementation Details)**: Test kiểm tra kết quả trả về và trạng thái public, không assert vào thứ tự gọi hàm private.
  - Kim tự tháp chuẩn: 70-80% Unit Tests (chạy dưới vài mili-giây), 15-20% Integration Tests, 5-10% E2E Tests.
  - Tránh Over-Mocking: Mock quá nhiều khiến test chỉ chứng minh là code tương tác tốt với Mock, chứ không chứng minh code chạy đúng với thực tế.

---

## 3. Ma Trận So Sánh Với 2 Repo Còn Lại

| Tiêu chí | `btseee/clean-code-skills` | `ertugrul-dmr/clean-code-skills` | `skilldb_clean-code-skills` |
| :--- | :--- | :--- | :--- |
| **Độ phủ kiến trúc** | Cực kỳ rộng (Kiến trúc phân tầng, Clean Architecture, Dependency Rule). | Trung bình (Tập trung chủ yếu vào cấp độ hàm, biến, comment, class). | Rất sâu về thiết kế hướng đối tượng, SOLID, Testing Pyramid. |
| **Đặc thù cho AI Agent** | **Số 1** (Có bộ Agent Smells A1-A10, Anti-loopholes, Quản lý session `.clean/`). | Tốt (Mô hình Boy-scout, tinh gọn prompt). | Trung tính (Hướng dẫn kỹ thuật tổng quát cho cả Human Dev & AI). |
| **Quy tắc kiểm chứng (Enforcement)** | Có script Python AST/Lexer tự động kiểm tra vi phạm và vẽ structure map. | Không có script, chỉ dựa trên Prompt Heuristics. | Không có script, tập trung vào giải thích lý do và code mẫu Before/After. |
| **Tính độc lập & Gọn nhẹ** | Cần bộ script nội bộ đi kèm. | 100% Pure Markdown, chia theo ngôn ngữ. | 100% Pure Markdown, chia thành 8 skill chuyên đề riêng lẻ. |

---

## 4. Đánh Giá & Khuyến Nghị Tích Hợp

1. **Điểm mạnh lớn nhất**:
   - Phần giải thích lý thuyết (`Core Philosophy`) và cạm bẫy (`Anti-Patterns`) trong từng skill được viết với văn phong kỹ thuật xuất sắc, sâu sắc và cực kỳ thực tế.
   - Các mẫu code so sánh Before / After rất sát với bài toán đời thực của lập trình viên (tính toán hóa đơn, thanh toán tài khoản, xử lý dữ liệu đơn hàng...).
2. **Khuyến nghị cho Antigravity CLI**:
   - Đây là nguồn tài liệu tham chiếu (Reference materials) chất lượng cao nhất để đưa vào thư mục `references/` của các skill hiện có trong `.agents/skills/`.
   - Có thể trích xuất từng skill (như `solid-principles`, `refactoring-patterns`, `testing-principles`) thành các sub-skill độc lập để agent tự kích hoạt khi gặp các tác vụ chuyên biệt về thiết kế hệ thống và viết unit test.
