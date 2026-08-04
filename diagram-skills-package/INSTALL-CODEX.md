# Port bộ diagram-skills sang Codex CLI

> Đưa 11 skill vẽ diagram (vốn viết cho Claude Code) sang **Codex CLI**. Codex đọc thư mục `.codex/` ở gốc project (song song với `.claude/` của Claude Code) và file nền `AGENTS.md`. Gồm: (A) cấu trúc Codex, (B) ánh xạ Claude Code → Codex, (C) prompt copy-paste ở `PROMPT-CODEX.md`.

---

## A. Codex đọc cấu hình thế nào

| Loại | Claude Code | Codex CLI |
|---|---|---|
| Skills | `.claude/skills/{name}/SKILL.md` | `.codex/skills/{name}/SKILL.md` |
| Rules | `.claude/rules/*.md` | `.codex/rules/*.md` |
| Agents | `.claude/agents/{name}.md` (Markdown + frontmatter) | `.codex/agents/{name}.toml` (`description` + `developer_instructions`) |
| Scripts | `.claude/scripts/*.mjs` | `.codex/scripts/*.mjs` (giữ nguyên, Node) |
| File nền | `CLAUDE.md` | `AGENTS.md` |

Điểm khác chính: **skill/rule/script gần như giữ nguyên**; chỉ **agent** đổi định dạng (Markdown → TOML). Engine (D2 `render.sh`, PlantUML `plantuml_encode.py`, BPMN engine, `mermaid-verify.mjs`) là script độc lập engine, chạy y hệt.

---

## B. Ánh xạ chi tiết

### B.1 — Skills (giữ nguyên)

```bash
mkdir -p <project>/.codex/skills <project>/_templates
cp -R claude-code/.claude/skills/*  <project>/.codex/skills/
cp    claude-code/_templates/*.md   <project>/_templates/   # khung file diagram
```

> `_templates/diagram-*.md` + `usecase-index.md` được `/sequence /activity /state /erd /bpmn /usecase-diagram` tham chiếu (`@../../../_templates/...`). Copy đủ, nếu không skill thiếu khung file.

SKILL.md frontmatter của Claude Code (`allowed-tools`, `user-invocable`, `argument-hint`, `context`) — Codex chủ yếu dùng `name` + `description` để kích hoạt. Các field thừa Codex bỏ qua, **không cần xóa** nhưng nên rà: nếu Codex báo lỗi parse frontmatter, chỉ giữ `name` + `description` và đưa cú pháp tham số xuống một mục "Cách gọi" trong body.

### B.2 — Rules (giữ nguyên)

```bash
mkdir -p <project>/.codex/rules
cp claude-code/.claude/rules/*.md  <project>/.codex/rules/
```

Sửa reference trong SKILL.md nếu trỏ `@.claude/rules/...` → `.codex/rules/...`. (Hoặc để nguyên tương đối `rules/...` nếu Codex resolve được — kiểm thử.)

### B.3 — Scripts / engine (giữ nguyên)

```bash
mkdir -p <project>/.codex/scripts
cp claude-code/.claude/scripts/mermaid-verify.mjs  <project>/.codex/scripts/
```

Engine sống trong từng skill (`bpmn/engine/`, `d2-activity/render.sh`, `usecase-diagram/` + `activity-swimlane/` `plantuml_encode.py`) — đã copy cùng B.1. Nhớ `npm install` trong `.codex/skills/bpmn/engine/` một lần.

> Nếu SKILL.md gọi `node .claude/scripts/mermaid-verify.mjs`, sửa thành `.codex/scripts/mermaid-verify.mjs`. Tương tự path `.claude/skills/d2-activity/render.sh` → `.codex/skills/d2-activity/render.sh`.

### B.4 — Agents (đổi Markdown → TOML)

Agent `diagram-reviewer` cần chuyển sang `.toml`:

```toml
# .codex/agents/diagram-reviewer.toml
description = '<copy dòng mô tả từ frontmatter description của diagram-reviewer.md>'
developer_instructions = """
<copy TOÀN BỘ nội dung body của diagram-reviewer.md vào đây>
"""
```

Nội dung review giữ nguyên, chỉ đổi vỏ.

---

## C. Điểm cần xử lý tay

- **Path trong SKILL.md:** rà mọi chuỗi `.claude/` → `.codex/` (scripts, render.sh, engine). Đây là chỗ hay sót nhất.
- **BPMN engine:** `npm install` trong `.codex/skills/bpmn/engine/`.
- **Kiểm thử từng engine:** chạy thử 1 skill mỗi engine (Mermaid / PlantUML / D2 / BPMN / DBML) và xác nhận render + compile-check chạy.

---

## D. Prompt tự động

Không cần làm tay từng bước — mở project trong Codex CLI, **mở `PROMPT-CODEX.md` và dán toàn bộ prompt trong đó vào chat**. Codex sẽ tự sao chép + chuyển đổi bộ skill Claude Code sang thư mục `.codex/` đúng chuẩn.

---

## E. Checklist sau khi port

- [ ] `.codex/skills/` có đủ 11 skill.
- [ ] `.codex/rules/` có các rule (approval-gate, ba-conventions, diagram-selection, feature-bootstrap, naming-conventions...).
- [ ] `.codex/scripts/mermaid-verify.mjs` có; path trong SKILL.md đã trỏ `.codex/`.
- [ ] Agent `diagram-reviewer` thành `.codex/agents/diagram-reviewer.toml`.
- [ ] `npm install` xong trong `.codex/skills/bpmn/engine/`.
- [ ] Chạy thử mỗi engine 1 skill → render OK, compile-check OK.
