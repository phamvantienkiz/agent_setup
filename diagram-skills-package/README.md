# Bộ skill vẽ Diagram cho BA — Diagram Skills Package

> 11 skill vẽ sơ đồ nghiệp vụ cho **IT Business Analyst**, đóng gói sẵn để chia sẻ. Bạn mô tả nghiệp vụ bằng lời — skill hỏi lại chỗ còn thiếu, vẽ sơ đồ đúng loại, tự kiểm cú pháp (compile-check) rồi render ra ảnh. Không phải nhớ cú pháp Mermaid/PlantUML/D2/BPMN.
>
> Gói này viết cho **Claude Code**, kèm hướng dẫn **port sang Codex CLI** và **Google Antigravity IDE**.

Bộ này là một phần của bộ công cụ BA-KIT dạy trong khóa **AI4BA** — [ai4ba.com](https://ai4ba.com). Xem mục [Về AI4BA](#về-ai4ba) ở cuối.

---

## 11 skill trong bộ

| Skill | Vẽ gì | Engine | Khi nào dùng |
|---|---|---|---|
| `/sequence` | Sequence diagram — ai gọi ai theo thời gian | Mermaid | Login, thanh toán, webhook, OAuth callback |
| `/activity` | Activity/flowchart — quy trình có nhánh quyết định | Mermaid | Flow gọn 1-2 vai, cần nhúng inline GitHub/Obsidian |
| `/activity-swimlane` ⭐ | Activity **swimlane thật** — mỗi vai 1 lane | PlantUML | **Mặc định cho quy trình đa vai trò** nhiều tương tác chéo |
| `/bpmn` | BPMN 2.0 chuẩn OMG | Engine Node | Cần import Camunda/Bizagi hoặc chuẩn OMG |
| `/state` | State diagram — vòng đời entity | Mermaid | Order/Account/Subscription có nhiều trạng thái |
| `/erd` | ERD nhúng inline | Mermaid | Data model cho BA đọc trong tài liệu |
| `/d2-erd` | ERD hình đẹp standalone | D2 | Data model cho slide/export, PK/FK rõ |
| `/dbdiagram` | Schema DBML + export SQL | DBML CLI | Bàn giao dev, dbdiagram.io/dbdocs.io, enum/index |
| `/d2-activity` | Activity đẹp standalone | D2 | Flow nhiều nhánh cần hình đẹp (không cần swimlane thật) |
| `/d2-architect` | Sơ đồ kiến trúc hệ thống | D2 | Component/service/DB/dịch vụ ngoài lồng nhau |
| `/usecase-diagram` | Use case diagram (actor + use case) | PlantUML | Kickoff, thể hiện phạm vi hệ thống, include/extend |

> **Không biết chọn skill nào?** Đọc `explain-skills/diagram-selection.md` — hub 6 nhóm câu hỏi dẫn tới đúng loại sơ đồ. Đây là điểm mạnh của bộ này: 11 skill nhưng có kim chỉ nam chọn đúng cái.

---

## Gói này có gì

```
diagram-skills-package/
├── README.md                      ← bạn đang đọc
├── LICENSE                        ← MIT
├── huong-dan/                     ← HƯỚNG DẪN SỬ DỤNG CHI TIẾT (đọc kỹ phần này)
│   ├── 00-bat-dau-nhanh.md        ← cài + chạy thử trong 5 phút
│   ├── 01-cai-dat-cong-cu.md      ← cài Node/mmdc/d2/Chrome cho từng engine
│   ├── 02-chon-skill-nao.md       ← bảng quyết định rút gọn + cây chọn
│   ├── 03-huong-dan-tung-skill.md ← chi tiết 11 skill: cú pháp, input, output, ví dụ
│   ├── 04-cach-hoat-dong.md       ← luồng chạy chung: hỏi → vẽ → compile-check → render
│   └── 05-cau-hoi-thuong-gap.md   ← FAQ + xử lý sự cố
├── explain-skills/                ← GIẢI THÍCH NGHIỆP VỤ từng skill (cho người không rành kỹ thuật)
│   ├── diagram-selection.md       ← ⭐ hub chọn sơ đồ
│   ├── sequence.md · activity.md · state.md · erd.md · bpmn.md · usecase-diagram.md ...
│   └── activity-family.md · erd-family.md · usecase-family.md  ← so sánh trong họ
├── example/                       ← VÍ DỤ ĐẦY ĐỦ: feature food-delivery vẽ qua cả 11 skill
│   ├── README.md                  ← bản đồ file → skill + ảnh render sẵn
│   └── food-delivery/             ← output thật (source + ảnh render sẵn)
├── claude-code/                   ← BỘ NGUYÊN BẢN cho Claude Code (copy vào workspace)
│   ├── .claude/
│   │   ├── skills/                ← 11 skill
│   │   ├── agents/                ← 1 agent review (diagram-reviewer)
│   │   ├── rules/                 ← rule dùng chung (approval-gate, diagram-selection...)
│   │   └── scripts/               ← mermaid-verify.mjs (compile-check Mermaid)
│   └── _templates/                ← khung file diagram (sequence/activity/state/erd/bpmn/usecase-index)
├── INSTALL-CODEX.md               ← port sang Codex CLI (.codex/)
├── INSTALL-ANTIGRAVITY.md         ← port sang Google Antigravity IDE (.agents/)
├── PROMPT-CODEX.md                ← prompt copy-paste để Codex tự cài
└── PROMPT-ANTIGRAVITY.md          ← prompt copy-paste để Antigravity tự cài
```

---

## Bắt đầu ngay (Claude Code)

1. **Cài công cụ render** (tùy skill bạn dùng — xem `huong-dan/01-cai-dat-cong-cu.md`):
   - Mermaid (`/sequence /activity /state /erd`): cần Node + `@mermaid-js/mermaid-cli` + Chrome.
   - PlantUML (`/activity-swimlane /usecase-diagram`): chỉ cần internet (render qua plantuml.com).
   - D2 (`/d2-*`): cần cài binary `d2`.
   - BPMN (`/bpmn`): cần Node + `npm install` trong `.claude/skills/bpmn/engine/`.
   - DBML (`/dbdiagram`): cần `@dbml/cli`.

2. **Copy skill vào workspace** BA của bạn:
   ```bash
   cp -R claude-code/.claude/skills/*      <workspace>/.claude/skills/
   cp    claude-code/.claude/agents/*.md   <workspace>/.claude/agents/
   cp    claude-code/.claude/rules/*.md    <workspace>/.claude/rules/
   cp    claude-code/.claude/scripts/*.mjs <workspace>/.claude/scripts/
   cp    claude-code/_templates/*.md       <workspace>/_templates/
   ```
   > Workspace đã có sẵn bộ BA-KIT → rule có thể trùng, cứ giữ bản đang dùng. Chưa có → copy đủ (skill tham chiếu các rule này ở mục References).

3. **Chạy thử** trong Claude Code mở tại workspace:
   ```
   /sequence "Khách đặt món, hệ thống gọi cổng thanh toán, nhà hàng xác nhận" --feature food-delivery
   /activity-swimlane "Quy trình duyệt hoàn tiền qua CSKH và kế toán" --feature refund
   /dbdiagram --feature food-delivery
   ```

👉 Chi tiết từng bước ở **`huong-dan/00-bat-dau-nhanh.md`**.

---

## Điểm mạnh của bộ này

- **Không cần nhớ cú pháp.** Bạn mô tả nghiệp vụ; skill lo cú pháp Mermaid/PlantUML/D2/BPMN.
- **Hỏi đúng cái BA cần** (business language) — không hỏi tên column DB, endpoint, framework (theo `rules/ba-conventions.md`).
- **Tự bắt lỗi trước khi báo xong.** Mermaid compile-check qua `mermaid-verify.mjs`; D2/DBML validate qua CLI; BPMN semcheck kiểm phủ actor/branch/error.
- **Có kim chỉ nam chọn sơ đồ.** `diagram-selection.md` giải quyết "11 skill biết dùng cái nào".
- **Approval gate (HITL).** Skill không tự ghi file — luôn xem trước (L1 plan) rồi mới ghi (xem `rules/approval-gate.md`).

---

## Port sang công cụ khác

- **Codex CLI** → `INSTALL-CODEX.md` (chi tiết) + `PROMPT-CODEX.md` (prompt copy-paste).
- **Google Antigravity IDE** → `INSTALL-ANTIGRAVITY.md` (chi tiết) + `PROMPT-ANTIGRAVITY.md` (prompt copy-paste).

---

## Về AI4BA

Bộ skill này là công cụ thực hành trong khóa **AI4BA — AI cho Business Analyst** tại **[ai4ba.com](https://ai4ba.com)**.

AI4BA dạy BA/PO dùng AI (Claude Code, Codex, Antigravity…) để làm nhanh và chuẩn hơn toàn bộ vòng đời tài liệu nghiệp vụ: từ brainstorm ý tưởng, viết URD/BRD/PRD/SRS, vẽ sơ đồ (chính là bộ này), tới user story/acceptance criteria, đồng bộ Jira/Confluence và bàn giao. Bộ diagram-skills là một lát cắt — phần "biến mô tả nghiệp vụ thành sơ đồ đúng chuẩn".

### Triết lý: Human-in-the-loop — BA vẫn là cốt lõi

AI4BA **không** thay BA bằng AI. Ngược lại: **BA là người điều khiển, AI là công cụ tăng tốc.** Toàn bộ bộ skill được thiết kế quanh nguyên tắc này:

- **BA cung cấp context — AI mới hiểu đúng nghiệp vụ.** Chất lượng output phụ thuộc vào thông tin BA đưa vào (mô tả luồng, số liệu, wording, ràng buộc). Skill hỏi lại đúng cái còn thiếu bằng ngôn ngữ nghiệp vụ; AI không tự bịa số liệu/luật khi không có nguồn. "Rác vào → rác ra" — BA nắm phần "vào".
- **BA duyệt trước khi ghi (approval gate).** Skill không tự ghi file: luôn xem trước kế hoạch (L1), file đã có thì xem diff (L2), output sáng tạo thì lặp tinh chỉnh (L3). BA gõ `Y` mới ghi — mọi thay đổi đều qua tay người.
- **BA review output đầu ra — không giao khoán cho AI.** Sơ đồ AI vẽ là **bản nháp chất lượng cao để BA thẩm định**, không phải chân lý. Compile-check/semcheck chỉ bắt lỗi cú pháp/coverage; đúng-sai **nghiệp vụ** là quyết định của BA. Skill có agent review (`diagram-reviewer`) soi coverage, nhưng người chốt vẫn là BA.
- **AI lo phần máy móc, BA lo phần tư duy.** AI nhớ cú pháp Mermaid/PlantUML/D2/BPMN, dàn layout, kiểm lỗi — để BA tập trung vào cái chỉ con người làm được: hiểu nghiệp vụ, đặt câu hỏi đúng, phán đoán đánh đổi, chịu trách nhiệm với stakeholder.

> Nói ngắn: **AI làm nhanh hơn, BA làm chuẩn hơn.** Bộ skill này ép đúng vòng lặp đó — AI đề xuất, BA kiểm soát và quyết.

Muốn học đầy đủ quy trình BA-with-AI, workflow, và các bộ skill khác → **[ai4ba.com](https://ai4ba.com)**.

---

## License

MIT — xem `LICENSE`. Dùng tự do, ghi nguồn AI4BA nếu chia sẻ lại.
