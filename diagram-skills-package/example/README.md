# Ví dụ đầy đủ — Feature `food-delivery` (Đặt & giao đồ ăn)

> Một feature **nhiều luồng, nhiều vai trò** (Khách · Nhà hàng · Shipper · Hệ thống · CSKH) được vẽ qua **toàn bộ 11 skill diagram** trong bộ này. Mỗi file dưới đây là **output thật** do skill sinh ra — dùng làm bản mẫu để đối chiếu khi bạn chạy skill trên feature của mình.
>
> Ảnh render sẵn nằm trong `food-delivery/_rendered/` (Mermaid + use case) và ngay cạnh file source (D2 `.svg`/`.png`, PlantUML `.svg`/`.png`). BPMN mở bằng editor HTML hoặc import Camunda/Bizagi.

---

## Bối cảnh nghiệp vụ

Ứng dụng đặt & giao đồ ăn. Khách đặt món → Hệ thống tính tiền + gọi cổng thanh toán → Nhà hàng xác nhận + chuẩn bị → Hệ thống gán Shipper → Shipper giao → Khách nhận. Các nhánh ngoại lệ: thanh toán thất bại, nhà hàng từ chối, hết shipper, giao thất bại, hoàn tiền. Đủ phức tạp để mỗi loại diagram đều có đất dùng.

---

## Bản đồ file → skill

| Skill | Lệnh minh họa | Source | Ảnh render sẵn |
|---|---|---|---|
| `/sequence` | `/sequence "Đặt món và thanh toán" --feature food-delivery` | `food-delivery/srs/food-delivery-flows.md` (2 sequence) | `_rendered/sequence-order-payment.png`, `_rendered/sequence-delivery.png` |
| `/activity` | `/activity "Xử lý đơn hàng đầu-cuối" --feature food-delivery` | `food-delivery/srs/food-delivery-flows.md` (flowchart) | `_rendered/activity-order-flowchart.png` |
| `/state` | `/state Order --feature food-delivery` | `food-delivery/srs/food-delivery-states.md` (Order + Payment) | `_rendered/state-order.png`, `_rendered/state-payment.png` |
| `/erd` | `/erd --feature food-delivery` | `food-delivery/srs/food-delivery-erd.md` | `_rendered/erd-mermaid.png` |
| `/usecase-diagram` | `/usecase-diagram --feature food-delivery` | `food-delivery/usecases/food-delivery-usecase-diagram.puml` | `_rendered/usecase-diagram.png` (+ `.svg` cạnh source) |
| `/activity-swimlane` | `/activity-swimlane "Điều phối đơn & xử lý ngoại lệ" --feature food-delivery` | `food-delivery/activity-swimlane/food-delivery-order-dispatch-swimlane.puml` | `.svg` + `.png` cạnh source (5 lane thật) |
| `/bpmn` | `/bpmn "Đặt & giao đồ ăn đầu cuối" --feature food-delivery` | `food-delivery/bpmn/order-fulfillment.ir.json` → `.bpmn` | mở `food-delivery/bpmn/food-delivery-bpmn-editor.html` |
| `/d2-activity` | `/d2-activity "Xử lý đơn hàng" --feature food-delivery` | `food-delivery/d2-activity/food-delivery.d2` | `food-delivery/d2-activity/food-delivery.png` |
| `/d2-erd` | `/d2-erd --feature food-delivery` | `food-delivery/d2-erd/food-delivery.d2` | `food-delivery/d2-erd/food-delivery.png` |
| `/d2-architect` | `/d2-architect --feature food-delivery` | `food-delivery/d2-architect/food-delivery.d2` | `food-delivery/d2-architect/food-delivery.png` |
| `/dbdiagram` | `/dbdiagram --feature food-delivery` | `food-delivery/dbdiagram/food-delivery.dbml` (+ `.sql` export) | import dbdiagram.io / dbdocs.io |

---

## Cùng một nghiệp vụ — nhiều lớp trừu tượng

Ví dụ này cố tình vẽ **cùng quy trình đặt-giao** bằng nhiều engine để bạn thấy khi nào chọn cái nào (xem `explain-skills/diagram-selection.md`):

- **Luồng xử lý đơn**: `/activity` (Mermaid, nhúng inline) vs `/d2-activity` (D2, hình đẹp standalone) vs `/activity-swimlane` (PlantUML, **swimlane thật 5 lane**) vs `/bpmn` (chuẩn OMG, import Camunda). Cùng logic, khác cách trình bày + đối tượng xem.
- **Data model**: `/erd` (Mermaid, BA đọc) vs `/d2-erd` (D2, hình đẹp) vs `/dbdiagram` (DBML, gần dev — có enum/index/default + export SQL).
- **Tương tác theo thời gian**: `/sequence` (ai gọi ai, webhook, nhánh alt/else).
- **Vòng đời entity**: `/state` (Order 11 trạng thái, Payment 7 trạng thái).
- **Phạm vi hệ thống**: `/usecase-diagram` (actor + use case + include/extend) và `/d2-architect` (component/service/DB/dịch vụ ngoài).

---

## Cách xem

| Loại | Cách mở |
|---|---|
| Mermaid (`srs/*.md`) | Mở file `.md` trong VS Code / Obsidian / GitHub — tự render. Hoặc xem PNG trong `_rendered/`. |
| D2 (`.svg`/`.png`) | Double-click file ảnh, hoặc mở `.svg` bằng browser. |
| PlantUML (`.svg`/`.png`) | Double-click file ảnh. |
| BPMN (`.bpmn`) | Mở `food-delivery-bpmn-editor.html` bằng browser (kéo-thả sửa), hoặc import file `.bpmn` vào Camunda Modeler / Bizagi / draw.io. |
| DBML (`.dbml`) | Dán vào [dbdiagram.io](https://dbdiagram.io) hoặc publish [dbdocs.io](https://dbdocs.io). File `.sql` import thẳng PostgreSQL. |
