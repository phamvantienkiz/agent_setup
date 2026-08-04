# Port bộ diagram-skills sang Google Antigravity IDE

> Đưa 11 skill vẽ diagram (vốn viết cho Claude Code) sang **Google Antigravity IDE**. Gồm: (A) cấu trúc cấu hình Antigravity, (B) ánh xạ Claude Code → Antigravity, (C) prompt copy-paste ở `PROMPT-ANTIGRAVITY.md`.
>
> Cập nhật theo tài liệu Antigravity tới ~6/2026. Path có thể đổi giữa các bản — luôn đối chiếu cây thư mục thật trong IDE (xem cảnh báo A.3).

---

## A. Antigravity cấu hình thế nào

### A.1 — Vị trí (workspace / project scope)

| Loại | Đường dẫn | Vai trò |
|---|---|---|
| **Skills** | `<project-root>/.agents/skills/{name}/SKILL.md` | "Sổ tay" agent nạp khi liên quan. Tương đương skill Claude Code. |
| **Rules** | `<project-root>/.agents/rules/*.md` | Như system instruction — luôn áp dụng. |
| **Workflows** | `<project-root>/.agent/workflows/*.md` | Prompt lưu sẵn, gọi bằng `/<tên>` trong chat. |
| **AGENTS.md** | `<project-root>/AGENTS.md` | Nền tảng chung (Antigravity + Cursor + Claude Code đều đọc). |

### A.2 — Global scope (mọi project)

| Loại | Đường dẫn |
|---|---|
| Skills | `~/.gemini/config/skills/` |
| Rules | `~/.gemini/GEMINI.md` |

### A.3 — ⚠️ Cảnh báo tên thư mục (`.agent` vs `.agents`)

Điểm dễ sai nhất — nguồn tài liệu lẫn số ít/số nhiều:
- **Skills/Rules:** đa số dùng **`.agents/`** (số nhiều).
- **Workflows:** có nguồn ghi `.agent/workflows/`, có nguồn `.agents/workflows/`; Antigravity còn cho tạo workflow qua UI.

👉 **Trước khi copy, tạo thử 1 skill rỗng qua UI/lệnh của Antigravity để xem nó đẻ ra thư mục tên gì.** Dùng đúng tên đó. Hướng dẫn dưới mặc định `.agents/`.

### A.4 — SKILL.md của Antigravity

Frontmatter tối giản:
```yaml
---
name: sequence
description: <trigger phrase NGỮ NGHĨA, càng cụ thể càng dễ kích hoạt đúng>
---
```
- `description` là **bắt buộc** và là "trigger phrase" — mô tả cụ thể ("Vẽ sequence diagram cho flow login/thanh toán/webhook, xuất Mermaid vào srs/flows.md") mới được nạp đúng.
- Kích hoạt qua ngôn ngữ tự nhiên; muốn gõ `/sequence` thì tạo thêm Workflow mỏng (B.4).

---

## B. Ánh xạ Claude Code → Antigravity

| Thành phần Claude Code | Trong gói | → Antigravity |
|---|---|---|
| `.claude/skills/{name}/SKILL.md` | `claude-code/.claude/skills/` | `.agents/skills/{name}/SKILL.md` (sửa frontmatter, B.1) |
| `.claude/agents/diagram-reviewer.md` | `claude-code/.claude/agents/` | nhúng inline vào skill (B.2) hoặc subagent Antigravity 2.0 |
| `.claude/rules/*.md` | `claude-code/.claude/rules/` | `.agents/rules/*.md` (giữ nội dung) |
| `.claude/scripts/mermaid-verify.mjs` | `claude-code/.claude/scripts/` | `.agents/skills/_shared/mermaid-verify.mjs` (hoặc cạnh skill dùng nó) |
| engine (render.sh, plantuml_encode.py, bpmn/engine/) | trong từng skill | giữ trong `.agents/skills/{name}/` |

### B.1 — Frontmatter SKILL.md

- **Giữ:** `name`, `description`.
- **Bỏ:** `allowed-tools`, `user-invocable`, `context`, `argument-hint`.
- Cú pháp tham số (`/sequence "<desc>" --feature <slug>`) → chuyển xuống mục "Cách gọi" trong body.

### B.2 — Agent review (`diagram-reviewer`)

Claude Code spawn qua Task tool; Antigravity không có y hệt. Hai cách:
1. **Inline (khuyến nghị khi mới port):** nhúng nội dung `diagram-reviewer.md` thành mục "Tiêu chí tự review diagram" trong SKILL.md của `/sequence` + `/activity`, để agent tự soi coverage (actor/lane thiếu, nhánh error bỏ sót, dead-end) trước khi báo xong.
2. **Subagent (Antigravity 2.0):** nếu bản của bạn hỗ trợ subagents, tách thành subagent và gọi như một bước.

### B.3 — Path scripts/engine trong SKILL.md

Rà mọi chuỗi `.claude/scripts/mermaid-verify.mjs`, `.claude/skills/d2-activity/render.sh` → đổi cho khớp vị trí mới trong `.agents/`. Reference `@../../rules/...` → bỏ (rule ở `.agents/rules/` được auto-load) hoặc sửa path.

### B.4 — (Tùy chọn) Lệnh `/sequence`, `/erd`...

Muốn gõ lệnh như Claude Code: tạo Workflow mỏng `.agent/workflows/{name}.md` (frontmatter có `description`) trỏ về skill.

---

## C. Điểm cần chú ý

- **Engine render vẫn cần cài ở máy** (mmdc, d2, dbml2sql, npm install bpmn engine) — Antigravity chỉ thay lớp điều phối AI, không thay engine. Xem `huong-dan/01-cai-dat-cong-cu.md`.
- **PlantUML** (`/activity-swimlane`, `/usecase-diagram`) render qua internet — giữ nguyên.

---

## D. Prompt tự động

Không cần làm tay từng bước — mở gói này trong Antigravity IDE, **mở `PROMPT-ANTIGRAVITY.md` và dán toàn bộ prompt trong đó vào chat agent**. AI sẽ tự sao chép + chuyển đổi bộ skill Claude Code sang chuẩn Antigravity IDE (prompt đã dặn agent bám tài liệu Antigravity mới nhất ~06/2026).

---

## E. Checklist sau khi port

- [ ] `.agents/skills/` có đủ 11 skill, frontmatter chỉ còn `name` + `description`.
- [ ] `.agents/rules/` có các rule.
- [ ] Path scripts/engine trong SKILL.md đã trỏ đúng vị trí `.agents/`.
- [ ] Tiêu chí `diagram-reviewer` nằm inline trong `/sequence` + `/activity` (hoặc subagent).
- [ ] Engine đã cài (mmdc/d2/dbml2sql/bpmn npm install).
- [ ] Chạy thử 1 skill mỗi engine → render OK.

---

## Nguồn tham khảo (Antigravity, tới ~6/2026)

- [Getting Started with Google Antigravity — Codelabs](https://codelabs.developers.google.com/getting-started-google-antigravity)
- [Authoring Antigravity Skills — Codelabs](https://codelabs.developers.google.com/getting-started-with-antigravity-skills)
- [Antigravity Docs — Skills](https://antigravity.google/docs/skills) · [Rules & Workflows](https://antigravity.google/docs/rules-workflows)
