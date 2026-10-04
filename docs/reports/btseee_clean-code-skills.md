# Báo Cáo Phân Tích Tinh Túy Clean Code: `btseee/clean-code-skills`

- **Tên kho lưu trữ**: `btseee/clean-code-skills` (Phiên bản 4.0.0)
- **Định dạng**: Agent Skill (Tương thích Google Antigravity, Claude Code, Cursor, Copilot, Windsurf)
- **Giấy phép**: MIT License
- **Đường dẫn phân tích**: [btseee_clean-code-skills](file:///E:/gemini/agent_setup/btseee_clean-code-skills)

---

## 1. Tổng Quan & Triết Lý Cốt Lõi (Core Philosophy)

### Vấn đề thực tế của AI Coding Agents
Kho lưu trữ `btseee/clean-code-skills` được thiết kế dựa trên một quan sát sâu sắc về hành vi của các mô hình AI lập trình hiện đại:
> **"Coding agents rarely fail at syntax. They fail by putting code in the wrong place, duplicating knowledge, mixing responsibilities, and forgetting project context between sessions."**  
> *(Các agent lập trình hiếm khi sai cú pháp. Chúng thất bại vì đặt code sai chỗ, nhân bản tri thức thừa thãi, trộn lẫn trách nhiệm, và mất trí nhớ giữa các phiên làm việc).*

Mục tiêu của skill này không chỉ đơn thuần là nhắc lại lý thuyết Clean Code của Robert C. Martin, mà là **xây dựng một khung kỷ luật thực thi có tính cưỡng chế và kiểm chứng (enforceable & verifiable constraints)** dành riêng cho AI.

### Triết lý "Caution Over Speed" & "Evidence Over Claims"
- **Không bao giờ tin vào tuyên bố suông ("Phantom Success")**: Agent không được phép nói "code đã hoạt động" nếu chưa thực sự chạy lệnh kiểm thử (test/linter/build) và trích dẫn kết quả thực tế.
- **Surgical Changes (Can thiệp chuẩn xác)**: Mọi dòng code thay đổi phải truy vết trực tiếp về yêu cầu của người dùng; nghiêm cấm việc "tiện tay dọn dẹp" (drive-by refactoring) khi không có yêu cầu.
- **Độ bền ngữ cảnh (Context Durability)**: Duy trì trạng thái kiến trúc và quyết định qua thư mục trung gian `.clean/`.

---

## 2. Hệ Thống Luật & Khung Hoạt Động (Operating Loop)

Skill định nghĩa một chu trình 6 bước bắt buộc cho mọi tác vụ code:
```
1. Frame (Xác định phạm vi & tiêu chí nghiệm thu)
2. Read (Đọc code lân cận, idiom của framework, conventions)
3. Place (Xác định đúng layer/folder trước khi gõ code)
4. Edit surgically (Chỉnh sửa tối thiểu, xóa code mồ côi)
5. Verify (Chạy test hẹp nhất, báo cáo rủi ro trung thực)
6. Review diff (Tự soi chiếu diff qua checklist và mã smell)
```

### Các quy tắc bất biến (Rules That Always Apply)
1. **Quy tắc vị trí (Placement by Role)**:
   - Thư mục được quyết định bởi vai trò (Role), không bao giờ vứt code ra thư mục gốc (`root`) hoặc thư mục đang đứng (`cwd`).
   - Tuyệt đối cấm tạo file biến thể hậu tố: `_v2`, `_new`, `_final`, `_copy`.
   - Không được mở rộng các "thùng rác code" (junk drawers) như `utils/`, `helpers/`, `common/` trừ khi đặt tên đúng bản chất domain concept.
2. **Một việc cho một đơn vị (One Job Per Unit - SRP)**:
   - Nếu cần dùng từ nối `"AND"` để mô tả chức năng của class/hàm -> Bắt buộc phải tách.
   - Tách biệt rạch ròi: Parsing, Business Logic, Persistence (DB), External API, UI/Presentation, Wiring (DI).
3. **Mã tối thiểu (Minimal Code / YAGNI)**:
   - Dừng lại ngay ở câu trả lời "Có" đầu tiên: Không cần thiết? -> Không viết. Đã có trong codebase? -> Tái sử dụng. Thư viện chuẩn/package đã có? -> Dùng thư viện. Một dòng giải quyết được? -> Viết một dòng.
4. **Quy tắc Kiến trúc Phân tầng (Layer Rules & Dependency Rule)**:
   - Dependencies chỉ được trỏ hướng vào trong (Inward) về phía Business Policy.
   - Domain/Entities không bao giờ được import ORM (SQLAlchemy, Prisma, Hibernate), framework HTTP (FastAPI, Express) hay UI.

---

## 3. Đỉnh Cao Sáng Tạo: Hệ Thống Agent Smells (A1 - A10)

Điểm tinh túy độc nhất vô nhị của repo này là bộ catalog **10 "Mùi Code" đặc thù của AI (Agent Smells)**:

| Mã Smell | Tên Smell | Dấu hiệu nhận diện ở AI | Biện pháp xử lý bắt buộc |
| :---: | :--- | :--- | :--- |
| **A1** | **Hallucinated API** | Gọi hàm, method, option, tham số không hề tồn tại trong codebase hoặc phiên bản cài đặt. | Tra cứu lockfile/source types thực tế; loại bỏ hoặc viết hàm thay thế. |
| **A2** | **Unverified Dependency** | Tự ý thêm package/import mới mà không kiểm tra lockfile hoặc thư viện đã có. | Kiểm tra tên package chính xác trên registry; ưu tiên dùng hàng có sẵn. |
| **A3** | **Context Loss** | Đọc sót/quên ngữ cảnh: ghi đè quyết định cũ, khôi phục code đã xóa, làm rơi mất error handling. | Đọc lại file mục tiêu và state `.clean/`; diff kỹ trước khi lưu. |
| **A4** | **Scope Creep** | Sửa đổi không liên quan: đổi tên hàm lân cận, format lại file khác, nâng version dependencies. | Revert ngay các dòng lan man; chỉ sửa đúng trọng tâm yêu cầu. |
| **A5** | **Duplicate Implementation** | Tự viết lại helper/hàm mới song song với hàm đã có trong dự án. | Tìm kiếm trước khi viết (`search before writing`); mở rộng hàm cũ hoặc xóa bản copy. |
| **A6** | **Wrong-File Gravity** | Thấy file nào đang mở là nhét logic vào file đó; tạo "God file" phình to; thả file ở root. | Đặt code theo đúng Role/Layer kiến trúc; di dời code về đúng unit sở hữu. |
| **A7** | **Phantom Success** | Nói "xong rồi, code hoạt động tốt" nhưng không hề chạy test/linter; để lại `pass`, `TODO`, `dummy`. | Bắt buộc chạy lệnh kiểm chứng; trích dẫn output thật; nêu rõ phần nào chưa thể chạy. |
| **A8** | **Test Weakening** | Hạ thấp assertion, xóa/comment test fail, sửa test case sai lệch để pass gượng ép. | Khôi phục test gốc; sửa code thật để pass, hoặc dừng lại báo cáo xung đột. |
| **A9** | **Speculative Abstraction** | Tạo interface chỉ có 1 class implement, tạo abstract factory cho 1 loại object, vẽ abstraction tương lai. | Xóa abstraction thừa; viết code trực diện; chỉ trừu tượng hóa khi có từ 3 trường hợp thực tế. |
| **A10** | **Silent Architecture Drift** | Import ngược từ tầng trong ra tầng ngoài; đưa kiểu dữ liệu ORM vào domain logic; nhảy cóc qua middleware. | Dùng script kiểm tra boundary; đảo ngược dependency (DIP); bọc adapter ở rìa hệ thống. |

---

## 4. Các Biện Hộ Tâm Lý Của AI Cần Dập Tắt (Anti-Loopholes)

Repo chỉ ra chính xác các "ngụy biện" mà LLM hay tự đưa ra để lách luật:
- *"Tôi sẽ tiện thể dọn dẹp đoạn này luôn"* $\rightarrow$ **Thực tế**: Đây là scope creep, không phận sự thì không đụng vào.
- *"Thêm framework/thư viện này vào code sẽ sạch hơn"* $\rightarrow$ **Thực tế**: Thêm dependency là tăng chi phí bảo trì và rủi ro bảo mật; phải chứng minh được nhu cầu thiết yếu.
- *"Lớp trừu tượng này sẽ giúp ích cho tương lai"* $\rightarrow$ **Thực tế**: Tương lai nào cần thì tương lai đó trả giá. Bây giờ không cần thì không tạo.
- *"Code cũ tệ quá nên tôi viết lại (rewrite) toàn bộ"* $\rightarrow$ **Thực tế**: Viết lại mang rủi ro hồi quy cực lớn; chỉ refactor từng lát cắt nhỏ có test bảo vệ.
- *"Tạm thời tôi cứ để ở đây đã"* $\rightarrow$ **Thực tế**: Không có gì lâu bền bằng một giải pháp "tạm thời". Hãy đặt đúng chỗ ngay từ đầu.
- *"Hai khối code này giống nhau nên tôi gộp chung vào 1 helper"* $\rightarrow$ **Thực tế**: Chỉ gộp khi hai khối code có cùng lý do thay đổi và cùng một chủ sở hữu (SRP).

---

## 5. Phân Cấp Mức Độ Rủi Ro (Risk Levels) & Khung Review P0-P3

Trước khi hoàn thành tác vụ, Agent phải tự phân loại mức độ rủi ro:

| Mức rủi ro | Định nghĩa | Nghĩa vụ kiểm chứng bắt buộc |
| :---: | :--- | :--- |
| **LOW** | Chỉnh sửa trong 1 hàm/unit, không vượt boundary, dễ rollback. | Chạy targeted test hoặc kiểm tra hẹp nhất bao phủ thay đổi. |
| **MEDIUM** | Nhiều unit, hoặc thay đổi public API, route, CLI flag, config key. | Chạy unit test + integration test khu vực đó; chạy `map_structure.py`. |
| **HIGH** | Đổi cấu trúc DB/migration, security, concurrency, đổi format lưu trữ. | Chạy toàn bộ test suite, `check_boundaries.py`, viết ghi chú phương án rollback. |

Khi xuất review kết quả, lỗi được phân hạng theo thứ tự ưu tiên:
- **P0**: Lỗi hành vi, mất dữ liệu, lỗ hổng bảo mật, test bị suy yếu $\rightarrow$ **Chặn merge ngay lập tức**.
- **P1**: Vi phạm kiến trúc, nuốt lỗi (swallowed error), tuyên bố xong mà chưa test $\rightarrow$ **Phải sửa trước khi merge**.
- **P2**: Code duplicate, đặt sai chỗ, đặt tên vô nghĩa $\rightarrow$ **Sửa nếu chi phí thấp hoặc ghi nhận lại**.
- **P3**: Comment thừa, format lệch chuẩn $\rightarrow$ **Cải thiện độ đọc hiểu**.

---

## 6. Bộ Công Cụ Scripts Phân Tích Tĩnh (Zero External Dependencies)

Repo đi kèm các script Python cực kỳ sạch, viết bằng Python 3.8+ chuẩn, không cài thêm package ngoài, không truy cập mạng:
1. `detect_stack.py`: Tự động nhận diện ngôn ngữ, framework, test runner qua manifest và phần mở rộng.
2. `map_structure.py`: Dùng AST/lexer để quét toàn bộ codebase, liệt kê các function/class, chỉ ra code đặt sai thư mục, class làm nhiều việc, synonym names gây rối.
3. `check_boundaries.py`: Đọc import graph để phát hiện vi phạm ranh giới phân tầng (Layer boundaries).
4. `check_compression.py`: Kiểm tra xem khi viết tóm tắt tài liệu hướng dẫn có làm mất thông tin quan trọng hay không.
5. `scan_repo.py`: Quét toàn diện codebase và xuất báo cáo sức khỏe.

---

## 7. Khả Năng Mở Rộng: 21 Ngôn Ngữ & 27 Frameworks

Repo sở hữu hệ thống rule packs đồ sộ chia thành 2 thư mục:
- **Languages (21)**: Python, TypeScript, JavaScript, Go, Rust, Java, C#, C++, C, PHP, Swift, Kotlin, Ruby, Dart, Scala, R, Objective-C, Shell, PowerShell, CSS, Sass.
- **Frameworks (27)**: FastAPI, Django, Flask, Express, NestJS, React, Next.js, Vue/Nuxt, Angular, Svelte, Tailwind, Spring, ASP.NET Core, Laravel, Symfony, Rails, Flutter, SwiftUI, Jetpack Compose, Unity, PyTorch, TensorFlow...

Agent chỉ nạp đúng pack của stack hiện tại, giữ cho ngữ cảnh prompt luôn nhỏ gọn (<1500 tokens).

---

## 8. Đánh Giá & Đề Xuất Cho Antigravity CLI

- **Giá trị ứng dụng**: **Đặc biệt xuất sắc (10/10)**. Đây là bộ skill được thiết kế hoàn hảo nhất cho tư duy agent tự trị.
- **Tính an toàn**: Rất cao. Các script hoàn toàn offline, chỉ đọc source code và ghi vào `.clean/`, không có lệnh nguy hiểm.
- **Kế hoạch trích xuất**:
  - Nên tích hợp hoặc học hỏi trực tiếp bộ quy tắc **Agent Smells (A1-A10)** và **Anti-Loopholes** vào file chỉ dẫn dự án `AGENTS.md` hoặc thành một skill `clean-code` độc lập cho Antigravity.
  - Tận dụng bộ script `map_structure.py` và `check_boundaries.py` để làm công cụ audit tự động cho codebase.
