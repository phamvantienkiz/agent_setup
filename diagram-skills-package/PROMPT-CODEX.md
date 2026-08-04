# Prompt cài bộ diagram-skills vào Codex CLI

> **Cách dùng:** mở thư mục gói này trong project của bạn (hoặc copy gói vào project) → mở Codex CLI tại project → copy NGUYÊN khối prompt dưới đây → dán vào chat → gửi. Codex sẽ tự copy + chuyển đổi skill. Muốn hiểu cơ chế, xem `INSTALL-CODEX.md`.

---

````text
Đây là bộ diagram-skills gồm 11 skill vẽ sơ đồ cho BA, được viết ban đầu cho Claude Code.
Bạn là Codex CLI. Hãy SAO CHÉP bộ skill Claude Code có sẵn trong thư mục gói
"diagram-skills-package/" sang .codex/ của project này và CHUYỂN ĐỔI cấu trúc, path và
cơ chế cho tương thích với Codex.

NGUỒN (đọc trước khi làm):
- 11 skill:   diagram-skills-package/claude-code/.claude/skills/
              (sequence, activity, activity-swimlane, bpmn, erd, state,
               usecase-diagram, d2-activity, d2-erd, d2-architect, dbdiagram)
- Rules:      diagram-skills-package/claude-code/.claude/rules/*.md
- Agent:      diagram-skills-package/claude-code/.claude/agents/diagram-reviewer.md
- Script:     diagram-skills-package/claude-code/.claude/scripts/mermaid-verify.mjs
- Ví dụ mẫu:  diagram-skills-package/example/food-delivery/  (output đúng trông thế nào)

CÁC BƯỚC:

1. Copy skills + templates GIỮ NGUYÊN:
   cp -R diagram-skills-package/claude-code/.claude/skills/*  .codex/skills/
   cp    diagram-skills-package/claude-code/_templates/*.md   _templates/
   (tạo .codex/skills/ và _templates/ nếu chưa có; templates diagram-*.md + usecase-index.md
    được /sequence /activity /state /erd /bpmn /usecase-diagram tham chiếu)

2. Copy rules GIỮ NGUYÊN:
   cp diagram-skills-package/claude-code/.claude/rules/*.md  .codex/rules/

3. Copy script:
   cp diagram-skills-package/claude-code/.claude/scripts/mermaid-verify.mjs  .codex/scripts/

4. SỬA PATH trong mọi SKILL.md: đổi mọi chuỗi ".claude/" thành ".codex/"
   (đặc biệt: node .claude/scripts/mermaid-verify.mjs → .codex/scripts/...;
    .claude/skills/d2-activity/render.sh → .codex/skills/d2-activity/render.sh).
   Nếu Codex báo lỗi parse frontmatter SKILL.md, chỉ giữ name + description và
   đưa cú pháp tham số (argument-hint) xuống mục "Cách gọi" trong body.

5. CHUYỂN AGENT REVIEW sang TOML:
   - Tạo .codex/agents/diagram-reviewer.toml với:
       description = '<dòng description trong frontmatter của diagram-reviewer.md>'
       developer_instructions = """<toàn bộ body của diagram-reviewer.md>"""

6. CÀI dependency engine BPMN (một lần):
   cd .codex/skills/bpmn/engine && npm install

RÀNG BUỘC:
- KHÔNG đổi logic nghiệp vụ của skill (vẫn hỏi bằng ngôn ngữ nghiệp vụ, approval gate L1/L2,
  compile-check/validate/semcheck trước khi báo xong).
- Engine render (Mermaid mmdc, PlantUML plantuml.com, D2 binary, BPMN engine, dbml2sql)
  cần cài sẵn ở máy — nếu thiếu, báo tôi lệnh cài (xem huong-dan/01-cai-dat-cong-cu.md).

BÁO CÁO sau khi xong:
1. Cây thư mục .codex/ đã tạo.
2. Danh sách path đã sửa (.claude → .codex).
3. Engine nào chưa cài trên máy này + lệnh cài.
Rồi chạy thử: /usecase-diagram --feature food-delivery (hoặc 1 skill Mermaid) và xác nhận
skill DỪNG ở L1 plan trước khi ghi, không tự ghi im lặng.
````
