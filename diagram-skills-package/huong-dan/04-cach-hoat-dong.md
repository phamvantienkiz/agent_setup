# 04 — Cách skill hoạt động (luồng chung)

> Hiểu luồng chạy giúp bạn biết khi nào skill sẽ hỏi, khi nào chờ bạn duyệt, và tại sao nó tự sửa lỗi. Cả 11 skill theo cùng khung này.

---

## Luồng 6 bước

```
1. Nhận input        →  bạn gõ /skill "<mô tả>" --feature <slug>
2. Đọc ngữ cảnh      →  skill đọc docs/{slug}/ có sẵn (SRS, use case...) nếu có
3. Hỏi bù chỗ thiếu  →  hỏi bằng ngôn ngữ nghiệp vụ, KHÔNG hỏi lại cái đã có
4. L1 — xem kế hoạch →  in bảng "sẽ ghi file gì" — bạn gõ Y / sửa
5. Vẽ + ghi file     →  sinh source diagram, ghi vào đúng path
6. Render + tự kiểm  →  compile-check / validate / semcheck → báo kết quả
```

Nếu file đã tồn tại (chạy lại): giữa bước 4-5 có **L2 — xem diff** trước khi ghi đè.

---

## Bước 3 — Skill hỏi gì (và KHÔNG hỏi gì)

Skill phục vụ **IT Business Analyst**, nên hỏi bằng ngôn ngữ nghiệp vụ:

✅ **Được hỏi:** ai làm bước nào · khi nào rẽ nhánh · kết quả nghiệp vụ user thấy · loại thông tin cần lưu (email, trạng thái, ngày) · có gọi dịch vụ ngoài nào (chỉ tên + mục đích).

❌ **Không hỏi:** tên column DB · schema table · endpoint API · framework · thuật toán mã hóa · cấu trúc payload.

> Quyết định kỹ thuật là việc của dev/architect, không phải các skill này (trừ `/dbdiagram` và `/erd` — vốn là artifact dữ liệu, được phép kiểu gọn/PK-FK). Xem `rules/ba-conventions.md`.

**No re-ask:** skill quét mô tả + câu trả lời trước + file có sẵn, **không hỏi lại** cái đã biết.

---

## Bước 4-5 — Approval gate (bạn luôn kiểm soát)

Skill **không bao giờ tự ghi file im lặng**. Ba mức:

| Mức | Khi nào | Bạn thấy gì | Trả lời |
|---|---|---|---|
| **L1 Plan** | Trước khi ghi file mới | Bảng: path · tạo/sửa · tóm tắt | `Y` (đồng ý) / `n` (hủy) / gõ yêu cầu đổi |
| **L2 Diff** | Ghi đè file đã có | Unified diff | `Y` / `n` / `edit-prompt: <sửa>` |
| **L3 Iterate** | Chỉ output ASCII/prose | Bản nháp trong chat | `Đồng ý` / `Sửa: ...` |

> Diagram Mermaid/PlantUML/D2/BPMN **bỏ qua L3** — chat không render được sơ đồ, nên skill ghi file rồi bạn xem từ ảnh render / IDE / editor. Xem `rules/approval-gate.md`.

---

## Bước 6 — Tự kiểm (điểm mạnh của bộ)

Mỗi engine có cách bắt lỗi riêng, chạy **trước khi báo "xong"**:

| Engine | Cách kiểm | Bắt được gì |
|---|---|---|
| Mermaid | `mermaid-verify.mjs` compile mọi block qua `mmdc` | Lỗi cú pháp (ký tự cấm trong label, thiếu token) |
| D2 | `render.sh` compile `.d2` → `.svg` | Lỗi cú pháp D2 |
| DBML | `dbml2sql {feature}.dbml --postgres` | DBML sai cú pháp |
| BPMN | `bpmn-semcheck.mjs` | Thiếu actor/branch/error so với facts, gateway thiếu nhánh, dead-end |
| PlantUML | server trả HTTP != 200 | Encode/network/server fail |

Lỗi → skill **sửa và thử lại** (thường tối đa 2-3 lần), không ghi diagram hỏng ra rồi báo hoàn tất.

**Review nghiệp vụ (tùy skill):** `/sequence` và `/activity` khi diagram phức tạp sẽ spawn `@diagram-reviewer` soi coverage kỹ thuật (actor/lane thiếu, nhánh error bỏ sót) trước khi báo xong.

---

## Vì sao có agent `diagram-reviewer`?

- **`diagram-reviewer`** — soi diagram kỹ thuật (`/sequence`, `/activity`) khi vượt ngưỡng phức tạp: bắt actor/lane thiếu, nhánh error/alt bỏ sót, dead-end, gateway thiếu nhánh.

Đây là agent read-only, trả findings để skill tự cải thiện — không tự ghi file. (Bộ đầy đủ còn có `flow-reviewer` cho `/user-flow`, nhưng `/user-flow` không nằm trong gói diagram này nên không kèm theo.)

---

## Nơi output rơi vào

Mọi skill ghi vào `docs/{slug}/` theo quy ước `rules/naming-conventions.md`:

| Skill | Path |
|---|---|
| `/sequence` `/activity` | `docs/{slug}/srs/{slug}-flows.md` |
| `/state` | `docs/{slug}/srs/{slug}-states.md` |
| `/erd` | `docs/{slug}/srs/{slug}-erd.md` |
| `/activity-swimlane` | `docs/{slug}/srs/{slug}-*-swimlane.puml` + `.svg` |
| `/usecase-diagram` | `docs/{slug}/usecases/{slug}-usecase-diagram.puml` + `.svg` |
| `/bpmn` | `docs/{slug}/bpmn/{process}.bpmn` + editor HTML |
| `/d2-activity` | `docs/{slug}/d2-activity/{slug}.d2` + ảnh |
| `/d2-erd` | `docs/{slug}/d2-erd/{slug}.d2` + ảnh |
| `/d2-architect` | `docs/{slug}/d2-architect/{slug}.d2` + ảnh |
| `/dbdiagram` | `docs/{slug}/dbdiagram/{slug}.dbml` + `.sql` |

Xem `example/food-delivery/` để thấy cấu trúc thật.
