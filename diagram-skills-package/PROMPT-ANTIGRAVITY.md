# Prompt cài bộ diagram-skills vào Antigravity IDE

> **Cách dùng:** mở thư mục gói này (`diagram-skills-package/`) trong Google Antigravity IDE → mở chat agent → copy NGUYÊN khối prompt dưới đây → dán → gửi. Agent tự đọc file trong gói, sao chép và chuyển skill vào đúng chỗ. Muốn hiểu cơ chế, xem `INSTALL-ANTIGRAVITY.md`.

---

````text
Đây là bộ diagram-skills gồm 11 skill vẽ sơ đồ cho BA, được viết ban đầu cho Claude Code.
Bạn là agent của Google Antigravity IDE. Nhiệm vụ của bạn là SAO CHÉP bộ này sang Antigravity
và CHUYỂN ĐỔI đúng chuẩn Antigravity, không cài trực tiếp cấu trúc Claude Code.

Bám tài liệu Antigravity mới nhất khoảng 06/2026 khi thực hiện:
antigravity.google/docs/skills, antigravity.google/docs/rules-workflows và codelab
Authoring Antigravity Skills. Nếu có thể đọc web, hãy đối chiếu trực tiếp; nếu không, làm theo
INSTALL-ANTIGRAVITY.md trong gói này vì file đã được cập nhật theo tài liệu khoảng 06/2026.
Path và format có thể khác giữa các bản Antigravity, nên không được đoán theo bản cũ.

══════════ BƯỚC 0 — CHỌN PHẠM VI VÀ XÁC MINH CẤU HÌNH ══════════
TRƯỚC KHI sao chép, hỏi tôi và chờ câu trả lời: cài cho workspace hiện tại hay cài global cho
mọi project. Không được tự chọn phạm vi.

- Workspace: xác minh thư mục cấu hình thực tế là .agents/ hay .agent/.
- Global: dùng phạm vi global dưới ~/.gemini/ theo đúng cấu trúc mà phiên bản Antigravity hiện
  tại hỗ trợ.
- Kiểm tra tài liệu, cấu trúc workspace hiện có và màn hình/câu lệnh tạo skill của IDE.
- Nếu vẫn chưa chắc, tạo một skill thử nghiệm rỗng bằng UI hoặc lệnh chính thức, reload IDE,
  xác nhận Antigravity đã nhận diện skill và ghi lại path thực tế.
- Xóa skill thử nghiệm sau khi xác minh. Dùng đúng path đã xác minh thay cho mọi path mẫu bên
  dưới, rồi báo tôi biết phạm vi và thư mục cấu hình đã chọn.

Gọi thư mục cấu hình đã xác minh là THU_MUC_CAU_HINH trong các bước tiếp theo.

══════════ BƯỚC 1 — ĐỌC NGUỒN TRONG GÓI NÀY ══════════
Đọc đầy đủ nội dung nguồn trước khi tạo file đích:

- 11 skill tại claude-code/.claude/skills/: sequence, activity, activity-swimlane, bpmn,
  erd, state, usecase-diagram, d2-activity, d2-erd, d2-architect và dbdiagram.
- Rules tại claude-code/.claude/rules/*.md.
- Agent review tại claude-code/.claude/agents/diagram-reviewer.md.
- Script tại claude-code/.claude/scripts/mermaid-verify.mjs.
- Ví dụ mẫu tại example/food-delivery/ để hiểu output đúng phải trông như thế nào.
- Đọc cả engine, script và References mà từng SKILL.md đang trỏ tới trước khi chuyển đổi.

══════════ BƯỚC 2 — TẠO 11 SKILL CHO ANTIGRAVITY ══════════
Với MỖI skill, sao chép sang THU_MUC_CAU_HINH/skills/{name}/SKILL.md theo cấu trúc hiện hành
của Antigravity.

- Giữ TOÀN BỘ nội dung nghiệp vụ: Goal, Constraints, các Phase, Gotchas và References.
- Chuyển các phần phụ thuộc Claude Code sang cơ chế tương đương của Antigravity.
- Frontmatter chỉ giữ name và description, trừ khi tài liệu Antigravity hiện hành bắt buộc thêm
  field khác; nếu có, chỉ thêm field bắt buộc và ghi rõ trong báo cáo.
- Bỏ field chỉ dành cho Claude Code: allowed-tools, user-invocable, context và argument-hint.
- Chuyển cú pháp gọi cũ, ví dụ /sequence "<desc>" --feature <slug>, vào mục Cách gọi.
- Copy kèm engine của từng skill, gồm render.sh, plantuml_encode.py và bpmn/engine/, vào đúng
  thư mục skill; sửa mọi path trong SKILL.md để khớp vị trí mới.

Description là trigger phrase quyết định skill có được Antigravity nhận diện và nạp đúng hay
không. Viết cụ thể theo loại sơ đồ, engine, đầu vào và nơi xuất output.

- Description xấu: Hỗ trợ sơ đồ.
- Description tốt: Tạo sequence diagram Mermaid từ luồng nghiệp vụ BA, xác nhận kế hoạch trước
  khi ghi vào tài liệu feature và kiểm tra cú pháp Mermaid trước khi hoàn tất.

Không dùng description chung chung, không để 11 skill có description gần như giống nhau.

══════════ BƯỚC 3 — SCRIPT VÀ RULE ══════════
- Copy mermaid-verify.mjs vào THU_MUC_CAU_HINH/skills/_shared/ hoặc cạnh các skill dùng nó.
- Sửa mọi lệnh node .claude/scripts/mermaid-verify.mjs trong SKILL.md sang path đích đúng.
- Copy rules vào THU_MUC_CAU_HINH/rules/ nếu phiên bản Antigravity tự nạp rules tại đó.
- Nếu rules/workflows có cơ chế khác theo tài liệu hiện hành, dùng cơ chế đó thay thế và ghi rõ.
- Sửa hoặc bỏ các mục References trong SKILL.md nếu chúng còn trỏ tới path Claude Code cũ.
- Không để bất kỳ script, engine hay reference nào còn trỏ tới .claude/ ngoài thư mục nguồn.

══════════ BƯỚC 4 — CHUYỂN ĐỔI AGENT REVIEW ══════════
Claude Code gọi @diagram-reviewer qua Task tool; Antigravity có thể không có cơ chế y hệt.
Hãy chuyển đổi review mà không làm mất tiêu chí chất lượng.

- Nếu Antigravity không hỗ trợ subagent đáng tin cậy, nhúng nội dung relevant từ
  diagram-reviewer.md thành mục Tiêu chí tự review diagram trong SKILL.md của sequence và
  activity.
- Self-review phải diễn ra SAU khi tạo diagram nhưng TRƯỚC khi báo hoàn tất: kiểm actor/lane
  thiếu, nhánh error hoặc alt bỏ sót, dead-end, gateway thiếu nhánh và luồng không nhất quán.
- Dùng inline self-review khi diagram đơn giản, một luồng ngắn, hoặc IDE không hỗ trợ subagent.
- Dùng subagent khi Antigravity hỗ trợ thật sự, diagram có nhiều actor/lane/nhánh, hoặc cần
  review độc lập trước khi hoàn tất.
- Nếu dùng subagent, truyền cho nó nội dung diagram, yêu cầu review cụ thể và xử lý lỗi tìm được
  trước khi báo xong; không chỉ nói rằng đã review.

══════════ BƯỚC 5 — WORKFLOW HOẶC LỆNH /<SKILL> TÙY CHỌN ══════════
Nếu phiên bản Antigravity hỗ trợ workflows hoặc slash command, tạo workflow mỏng cho từng skill
theo path và format chính thức của IDE. Workflow chỉ cần description rõ ràng và trỏ về skill
tương ứng để người dùng có thể gọi /sequence, /erd, v.v.

Nếu workspace không dùng workflows hoặc tài liệu hiện hành không hỗ trợ cách này, bỏ qua bước
này và nêu rõ cách kích hoạt bằng câu tự nhiên. Không tạo file workflow theo cấu trúc đoán mò.

══════════ BƯỚC 6 — KIỂM TRA SAU CÀI ══════════
Reload hoặc khởi động lại Antigravity theo cách tài liệu hiện hành yêu cầu, rồi kiểm tra từng
skill trong danh sách 11 skill.

- Mở Skills panel, command palette, log nạp skill hoặc cơ chế tương đương trong IDE.
- Xác nhận từng skill được nhận diện theo name và description, không chỉ kiểm tra file đã tồn tại.
- Nếu skill không xuất hiện hoặc không được kích hoạt bởi câu phù hợp, sửa path, frontmatter hoặc
  description rồi kiểm tra lại.
- Chạy thử một skill: vẽ use case diagram cho feature food-delivery.
- Xác nhận agent DỪNG ở bước xem trước kế hoạch L1 trước khi ghi file, không tự ghi im lặng.

══════════ RÀNG BUỘC KHÔNG ĐỔI ══════════
- Giữ nguyên LOGIC: hỏi bằng ngôn ngữ nghiệp vụ, không hỏi tên column DB, endpoint hay framework.
- Giữ approval gate: xem trước kế hoạch rồi mới ghi file.
- Giữ compile-check, validate hoặc semcheck trước khi báo xong; KHÔNG ghi diagram hỏng.
- Vietnamese-first.
- Engine render như mmdc Mermaid, plantuml.com, binary d2, bpmn engine npm install và dbml2sql
  cần có trên máy. Nếu thiếu, báo tôi lệnh cài từ huong-dan/01-cai-dat-cong-cu.md.

══════════ BÁO CÁO ══════════
Sau khi xong, in ra:

1. Cây thư mục đã tạo, dùng path thực tế đã xác minh.
2. Danh sách đủ 11 skill và trạng thái Antigravity đã nhận diện từng skill.
3. Cách kích hoạt: câu tự nhiên và /<skill> nếu có workflow.
4. Những gì đã đổi so với Claude Code: frontmatter, agent review, path script/engine và workflow.
5. Kết quả chạy thử use case diagram cho food-delivery, xác nhận đã dừng ở L1 trước khi ghi file.
````
