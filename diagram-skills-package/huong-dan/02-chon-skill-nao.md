# 02 — Chọn skill nào? (cây quyết định)

> 11 skill nghe nhiều, nhưng chọn đúng rất nhanh nếu hỏi đúng câu. Bản này là rút gọn; bản đầy đủ ở `explain-skills/diagram-selection.md`.

---

## Cây quyết định 30 giây

**Bạn muốn thể hiện điều gì?**

- **Ai gọi ai, theo trình tự thời gian** (login, thanh toán, webhook, gọi API bên ngoài)
  → **`/sequence`**

- **Một đối tượng có nhiều trạng thái + chuyển trạng thái** (Đơn: chờ → đã trả → đang giao → hoàn tất)
  → **`/state`**

- **Một quy trình có nhiều bước + nhánh quyết định**
  - Nhiều vai trò làm bước khác nhau, tương tác chéo nhiều → **`/activity-swimlane`** ⭐ (swimlane thật)
  - Cần chuẩn OMG / import Camunda-Bizagi → **`/bpmn`**
  - 1-2 vai, đơn giản, muốn nhúng thẳng vào file .md (GitHub/Obsidian tự hiện) → **`/activity`**
  - Nhiều nhánh, muốn hình **đẹp** đứng riêng (slide/export), không cần swimlane thật → **`/d2-activity`**

- **Mô hình dữ liệu (bảng + quan hệ)**
  - Cho BA đọc trong tài liệu, nhúng inline → **`/erd`**
  - Hình đẹp standalone (PK/FK rõ, cho slide) → **`/d2-erd`**
  - Bàn giao dev / export SQL / dbdocs (có enum, index, kiểu DB thật) → **`/dbdiagram`**

- **Phạm vi hệ thống — ai (actor) làm được những gì (use case)**
  → **`/usecase-diagram`**

- **Kiến trúc hệ thống** (app, service, DB, dịch vụ ngoài lồng nhau)
  → **`/d2-architect`**

---

## Bảng so sánh 3 họ dễ nhầm

### Họ "quy trình" (4 skill cùng vẽ flow)

| | Engine | Swimlane thật? | Nhúng inline? | Import BPM tool? | Khi nào |
|---|---|---|---|---|---|
| `/activity` | Mermaid | ✗ (subgraph giả) | ✓ | ✗ | Flow gọn, muốn hiện thẳng trong .md |
| `/d2-activity` | D2 | ✗ | ✗ | ✗ | Hình đẹp standalone nhiều nhánh |
| `/activity-swimlane` ⭐ | PlantUML | ✓ | ✗ (nhúng ảnh) | ✗ | **Mặc định đa vai trò** |
| `/bpmn` | Engine OMG | ✓ (pool/lane) | ✗ | ✓ | Cần chuẩn OMG / Camunda |

### Họ "dữ liệu" (3 skill cùng vẽ data model)

| | Engine | Ai xem | Enum/index | Export SQL |
|---|---|---|---|---|
| `/erd` | Mermaid | BA trong tài liệu | ✗ | ✗ |
| `/d2-erd` | D2 | Slide/export đẹp | ✗ | ✗ |
| `/dbdiagram` | DBML | **Dev/DBA** | ✓ | ✓ (`dbml2sql`) |

### Use case: diagram vs text

- **`/usecase-diagram`** = hình tổng quan (actor + use case + include/extend). Trong bộ này.
- **`/usecase`** (skill text, KHÔNG có trong bộ này) = viết chi tiết từng use case dạng prose. Nếu cần, lấy từ bộ BA-KIT đầy đủ.

---

## Gợi ý: một feature thường cần nhiều sơ đồ

Xem `example/food-delivery/` — cùng một feature "đặt & giao đồ ăn" được vẽ bằng:

- `/sequence` (đặt món + thanh toán, giao hàng)
- `/activity` + `/activity-swimlane` + `/bpmn` (cùng quy trình xử lý đơn, 3 cách trình bày)
- `/state` (vòng đời Order + Payment)
- `/erd` + `/d2-erd` + `/dbdiagram` (cùng data model, 3 độ chi tiết)
- `/usecase-diagram` (phạm vi hệ thống)
- `/d2-architect` (kiến trúc)

→ Đừng vẽ mọi sơ đồ cho mọi flow. Nguyên tắc: **sơ đồ phục vụ giao tiếp, không phải để khoe.** Vẽ cái giúp người đọc hiểu nhanh nhất.
