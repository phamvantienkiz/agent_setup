# 00 — Bắt đầu nhanh (5 phút)

> Mục tiêu: cài xong và vẽ được sơ đồ đầu tiên trong ~5 phút. Nếu chỉ muốn thử **một** loại sơ đồ, cài đúng công cụ cho engine đó là đủ (không cần cài hết).

---

## Bước 1 — Chọn engine bạn muốn thử

| Muốn vẽ | Skill | Cần cài |
|---|---|---|
| Sequence / flowchart / state / ERD (nhúng inline .md) | `/sequence` `/activity` `/state` `/erd` | Node + `mmdc` + Chrome |
| Swimlane thật / use case diagram | `/activity-swimlane` `/usecase-diagram` | **Chỉ cần internet** (render qua plantuml.com) |
| Sơ đồ D2 đẹp (activity / erd / kiến trúc) | `/d2-activity` `/d2-erd` `/d2-architect` | Binary `d2` |
| BPMN chuẩn OMG | `/bpmn` | Node + `npm install` trong engine |
| Schema DBML + SQL | `/dbdiagram` | `@dbml/cli` |

> **Dễ nhất để thử ngay:** `/activity-swimlane` hoặc `/usecase-diagram` — chỉ cần mạng, không cài gì thêm.

Cài chi tiết: `01-cai-dat-cong-cu.md`.

---

## Bước 2 — Copy skill vào workspace BA

Từ thư mục gốc gói này:

```bash
# Thay <workspace> bằng workspace BA của bạn (nơi có CLAUDE.md + docs/)
cp -R claude-code/.claude/skills/*      <workspace>/.claude/skills/
cp    claude-code/.claude/agents/*.md   <workspace>/.claude/agents/
cp    claude-code/.claude/rules/*.md    <workspace>/.claude/rules/
cp    claude-code/.claude/scripts/*.mjs <workspace>/.claude/scripts/
cp    claude-code/_templates/*.md       <workspace>/_templates/
```

Nếu workspace **chưa có** các thư mục này thì tạo trước:
```bash
mkdir -p <workspace>/.claude/{skills,agents,rules,scripts} <workspace>/_templates
```

> Rule trùng tên với bộ BA-KIT sẵn có → cứ giữ bản của workspace, không đè.

---

## Bước 3 — Mở Claude Code tại workspace và chạy

```bash
cd <workspace>
claude
```

Trong chat gõ (không cần chuẩn bị gì — skill sẽ hỏi lại chỗ thiếu):

```
/activity-swimlane "Khách đặt món; hệ thống tính tiền và gọi cổng thanh toán;
nhà hàng xác nhận rồi chuẩn bị; hệ thống gán shipper; shipper giao;
khách nhận. Nhánh lỗi: thanh toán fail, nhà hàng từ chối, giao thất bại" --feature food-delivery
```

Skill sẽ:
1. Hỏi lại vài điểm còn mơ hồ (ai làm bước nào, nhánh rẽ ở đâu).
2. Xem trước kế hoạch ghi file (**L1 plan** — bạn gõ `Y` để đồng ý).
3. Vẽ + render `.svg`/`.png` + tự kiểm.

---

## Bước 4 — Xem kết quả mẫu trước khi tự làm

Mở thư mục `example/food-delivery/` trong gói này — đó là **feature nhiều luồng** đã vẽ sẵn qua **cả 11 skill**, kèm ảnh render trong `example/food-delivery/_rendered/`. Đối chiếu output của bạn với bản mẫu để biết "đúng thì trông thế nào".

Đọc `example/README.md` để có bản đồ file → skill.

---

## Không chắc chọn skill nào?

→ `02-chon-skill-nao.md` (cây quyết định) hoặc `explain-skills/diagram-selection.md` (hub đầy đủ).

## Gặp lỗi?

→ `05-cau-hoi-thuong-gap.md` (FAQ + xử lý sự cố render).
