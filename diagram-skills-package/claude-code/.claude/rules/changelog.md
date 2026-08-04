---
paths:
  - "docs/**/*.md"
  - ".claude/hooks/**"
---

# Activity Log Convention

> Lịch sử thay đổi của TOÀN BỘ vault sống ở **một file duy nhất**: `docs/_shared/activity.log` (append-only). Doc KHÔNG mang `changelog:` trong frontmatter. Không còn routing table, không còn prefix, không còn echo 1 sự kiện vào nhiều file.

## Vì sao 1 log tập trung

Kiến trúc cũ (changelog YAML per review-unit + routing file con → file cha) tạo ra: 49 file mang changelog, 1 sự kiện CR apply chép vào 11 file, bảng routing tồn tại 3 bản sao (rule + hook + SKILL.md) từng lệch nhau, hook phải rewrite YAML + dedupe mỗi lần Write. Log tập trung xoá cả 4 vấn đề: **path của file được sửa chính là thông tin routing** — không cần bảng nào nữa.

## Format

```
{date} | {skill} | {@author} | {file-path} | {note}
```

- 1 dòng = 1 sự kiện. Append cuối file (mới nhất ở cuối, giống `staleness.log`).
- **date**: ISO `YYYY-MM-DD`.
- **skill**: `/urd`, `/sequence`, `/cr`, `/jira`, ... hoặc `manual` (edit tay ngoài skill).
- **@author**: @handle người chạy — resolve từ memory `user-identity` key `current_user` (xem `ba-conventions.md` Mục 1). Hook fallback: env `CLAUDE_CHANGELOG_AUTHOR` → `git config user.name`.
- **file-path**: project-relative path của file vừa Write/Edit (vd `docs/payment/srs/payment-spec.md`).
- **note**: what changed — imperative/past-tense, factual, ≤80 chars, tiếng Việt hoặc Anh.

**Ví dụ:**

```
2026-07-12 | /srs | @hoangpm | docs/payment/srs/payment-spec.md | initial spec 12 FR + 9 error
2026-07-12 | /erd | @hoangpm | docs/payment/srs/payment-erd.md | 5 entities, 4 relationships
2026-07-13 | /cr | @hoangpm | docs/payment/srs/payment-spec.md | applied CR-20260713-001: FR-payment-013 thêm
2026-07-13 | /jira | @hoangpm | docs/payment/userstories/payment-story-index.md | pushed 7 US → KAN-127..133
```

## Cơ chế ghi — hook là writer duy nhất

Skill KHÔNG tự ghi activity.log. Trước mỗi Write/Edit, skill set env vars (như cũ):

- `CLAUDE_SKILL_NAME` — tên skill đang chạy
- `CLAUDE_CHANGELOG_NOTE` — note cho sự kiện
- `CLAUDE_CHANGELOG_AUTHOR` — @handle (thường skill resolve 1 lần đầu session)

Hook `auto-changelog.sh` (PostToolUse Write|Edit) đọc env + path vừa sửa → append 1 dòng. Thiếu env → fallback `manual | {git user.name} | manual edit`. Một writer duy nhất = không race khi /srs chạy sub-agent song song (append-only O_APPEND an toàn).

## Dedupe

Bỏ qua nếu dòng **giống hệt** (cùng date + skill + path + note) đã tồn tại — tránh double-fire khi 1 skill Write cùng file 2 lần với cùng note. Khác note → ghi bình thường (nhiều sự kiện/ngày/file là hợp lệ).

## Files excluded

Hook skip (không log):
- `docs/_shared/*` (gồm chính activity.log — tránh đệ quy)
- `docs/exports/*` (regenerated)
- `docs/inbox/*` (raw capture)
- `docs/feature-list.md`, `docs/README.md` (auto-gen)

## Đọc lịch sử

- Lịch sử 1 feature: `grep " docs/payment/" docs/_shared/activity.log`
- Lịch sử 1 file: `grep " docs/payment/srs/payment-spec.md " docs/_shared/activity.log`
- Stakeholder-facing: `/export` render section "Lịch sử thay đổi" từ log (lọc theo feature) khi cần — KHÔNG nhét lịch sử vào doc.
- `/dashboard`, KG engine ingest log như event stream (cùng cách đọc `staleness.log`).

## Note style

- Good: `added refund webhook sequence`, `AC for invalid password updated`, `applied CR-20260512-001: added OTP requirement`.
- Bad: `updated stuff`, `fixed things`, `per Hoang's request` (người đã có ở field @author).

## Backward-compat

Docs demo cũ còn `changelog:` frontmatter → **giữ nguyên, không migrate** (docs demo sẽ bỏ khi rebuild). Parser/reader gặp field `changelog:` trong frontmatter hiểu là di sản, bỏ qua. Không tạo entry mới vào frontmatter trong bất kỳ trường hợp nào.
