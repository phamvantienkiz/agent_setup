---
type: skill-explainer
skill: d2-activity
updated: 2026-07-14
---

# `/d2-activity` là gì và nó chạy như thế nào?

## 1. Dùng để làm gì, khi nào nên gõ lệnh này

`/d2-activity` là **một cách thứ ba để vẽ sơ đồ quy trình** — bên cạnh `/activity` (dùng Mermaid) và `/activity-swimlane` (dùng PlantUML). Cả ba cùng vẽ ra một loại hình: sơ đồ diễn tả từng bước một việc chạy như thế nào (bắt đầu ở đâu, tới chỗ nào thì rẽ nhánh, kết thúc ở đâu). Khác nhau là ở **công cụ vẽ** phía sau — mỗi công cụ ra một style hình hơi khác, hợp nhu cầu khác nhau.

Chữ "D2" trong tên lệnh là tên công cụ vẽ mà lệnh này dùng. Điểm đáng chú ý của D2: bạn chỉ cần mô tả nội dung ("có bước A, bước B, chỗ này rẽ nhánh"), còn việc **sắp xếp các ô cho thẳng hàng, đường kẻ gọn, không chồng chéo** thì công cụ tự lo (phần tự sắp xếp này có tên "ELK" — bạn không cần nhớ, chỉ cần biết đó là "cái máy dàn ô"). So với `/activity` (Mermaid), cách dàn của D2 **gọn gàng hơn khi quy trình có nhiều nhánh rẽ** — đó là lý do chính để chọn nó (giải thích kỹ ở Mục 3).

Vài tình huống điển hình nên dùng `/d2-activity`:

- Quy trình của bạn **có nhiều nhánh rẽ**, bạn đã thử vẽ bằng `/activity` (Mermaid) nhưng hình ra rối — đường kẻ cong queo cắt chéo nhau. Đổi sang D2 thường dàn gọn hơn.
- Bạn muốn kết quả ra **một file ảnh** để tiện dán vào slide, tài liệu Word/PowerPoint, hoặc gửi qua email.

Gõ lệnh đơn giản như:

```
/d2-activity "quy trình khách đặt hàng, hệ thống kiểm tra tồn kho, admin duyệt" --feature order
```

**Một câu để nhớ:** `/d2-activity` là **cách vẽ sơ đồ quy trình thứ ba** (sau Mermaid và PlantUML) — một style hình khác, dàn gọn hơn Mermaid khi nhiều nhánh, ra một file ảnh tiện dán vào slide hay gửi đi.

---

## 2. Toàn bộ luồng chạy — sơ đồ

```
 BẠN GÕ LỆNH
 /d2-activity "mo ta quy trinh" --feature X
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 0 — Kiểm tra công cụ vẽ đã cài chưa               │
 │  Hệ thống cần công cụ "D2" cài sẵn trên máy mới vẽ    │
 │  được. Chưa có → DỪNG ngay, chỉ bạn 1 dòng lệnh cài.  │
 │  KHÔNG vẽ dở dang, không tạo file rỗng.               │
 └──────────────────────────────────────────────────────┘
        │  (đã có công cụ → đi tiếp)
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 1 — Xác định đang vẽ cho tính năng nào            │
 │  Đọc mô tả của bạn, đoán đang nói về tính năng nào.   │
 │  Tính năng chưa có → tự đặt tên rồi tạo mới (không    │
 │  bắt bạn phải làm bước chuẩn bị nào trước).           │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 2 — Hiểu quy trình cho đúng                       │
 │  Đọc tài liệu sẵn có của tính năng (nếu có) để hiểu   │
 │  các bước, các nhánh rẽ. Thiếu thông tin → HỎI bạn,   │
 │  KHÔNG tự bịa ra bước không có thật.                  │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 3 — Xác nhận danh sách vai trò (nếu có vai trò)   │
 │  Nếu phát hiện quy trình có vai trò/bộ phận tham gia, │
 │  hệ thống LIỆT KÊ ra: "Phát hiện các vai trò: Khách,  │
 │  Hệ thống, Admin. Đủ chưa?" — chờ bạn gật đầu.        │
 │  Quy trình 1 vai trò (không có làn) → bỏ qua bước này.│
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 4 — Xem trước rồi mới vẽ (xin phép)               │
 │  Hệ thống mô tả bằng lời thường: "sẽ vẽ N bước, M     │
 │  nhánh rẽ, K vai trò". Bạn gật (Y) mới làm tiếp.      │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 5 — Vẽ + kiểm tra ra được ảnh                     │
 │  Hệ thống viết mô tả sơ đồ, rồi nhờ công cụ D2 "vẽ    │
 │  thật" ra file ảnh. NẾU vẽ lỗi → tự sửa, vẽ lại. Chỉ  │
 │  báo XONG khi đã ra được ảnh hoàn chỉnh.              │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 6 — Báo hoàn tất                                  │
 │  Cho bạn đường dẫn file ảnh để mở bằng trình duyệt    │
 │  xem.                                                 │
 └──────────────────────────────────────────────────────┘
        │
        ▼
     HOÀN TẤT — có 1 file ảnh sơ đồ để mở xem
```

---

## 3. Nó khác hai lệnh kia ở chỗ nào?

`/d2-activity` **chỉ là một cách vẽ khác** cho cùng một loại sơ đồ quy trình — không "xịn hơn", không "đẹp hơn" hai lệnh kia. Nó dùng một công cụ vẽ khác (D2), ra một style hình hơi khác. Bạn chọn nó khi cái style đó hợp nhu cầu của bạn hơn, thế thôi.

Điểm khác dễ thấy nhất: cách D2 (với "máy dàn ô" ELK) sắp xếp hình. Khi quy trình có nhiều nhánh rẽ, `/activity` (Mermaid) đôi khi dàn **đường cong queo, cắt chéo qua các ô, chỗ giao nhau chụm lại rối mắt**; còn D2 thường cho:

- **Đường kẻ vuông góc, gom lại thành máng** — thay vì mỗi mũi tên đi một kiểu cong riêng.
- **Các ô thẳng hàng theo cột, theo hàng.**
- **Các ô không chồng lên nhau, mũi tên không đè lên ô.**

Nên nếu bạn vẽ một quy trình nhiều nhánh bằng Mermaid thấy rối, đổi sang D2 là một lựa chọn để thử — nó dàn theo kiểu khác, thường gọn hơn ở trường hợp đó. (Lưu ý: đây là so với Mermaid; nếu quy trình nhiều vai trò cần phân làn thì `/activity-swimlane` mới là lựa chọn hợp — xem Mục 5.)

Một điểm an tâm: vẽ bằng `/d2-activity` **không đụng chạm, không xoá** bản vẽ của các lệnh khác. Cùng một quy trình có thể có nhiều phiên bản hình song song — điều đó bình thường.

---

## 4. Vì sao phải kiểm tra công cụ, xác nhận vai trò, và "vẽ ra được ảnh mới báo xong"?

Ba chi tiết nhỏ nhưng quan trọng trong cách chạy của lệnh này.

**Kiểm tra công cụ trước tiên.** Không giống một số lệnh khác chạy hoàn toàn bên trong hệ thống, `/d2-activity` cần một công cụ tên "D2" được cài sẵn trên máy tính của bạn thì mới vẽ được. Vì vậy việc đầu tiên nó làm là kiểm tra: công cụ này có chưa? Nếu chưa, nó **dừng lại ngay và chỉ cho bạn đúng một dòng lệnh để cài** — chứ không cố vẽ nửa vời rồi tạo ra file hỏng. Giống như thợ mộc kiểm tra có đủ cưa đục chưa trước khi nhận đơn, thay vì nhận rồi mới phát hiện thiếu đồ nghề.

**Xác nhận danh sách vai trò trước khi vẽ.** Khi phát hiện quy trình có vai trò/bộ phận tham gia (khách, hệ thống, admin, kế toán...), hệ thống sẽ **liệt kê ra những vai trò nó nhận ra và hỏi bạn "đủ chưa?"** trước khi bắt tay vẽ. Lý do: đôi khi trong câu mô tả của bạn có một vai trò bị nhắc mờ nhạt, ẩn ý (ví dụ "sau khi được duyệt" — ai duyệt?), rất dễ bị bỏ sót nếu cứ tự đoán rồi vẽ luôn. Hỏi lại một câu ngắn còn hơn vẽ xong mới phát hiện thiếu một người quan trọng. (Nếu quy trình chỉ có một vai trò, không có làn nào để chia, thì bỏ qua bước hỏi này.)

**Vẽ ra được ảnh mới báo xong.** Sau khi viết xong phần mô tả sơ đồ, hệ thống nhờ công cụ D2 "vẽ thật" ra file ảnh. Nếu phần mô tả có lỗi cú pháp khiến vẽ không ra, nó **tự đọc lỗi, sửa lại, vẽ lại** (thử lại vài lần). Nó chỉ báo "hoàn tất" khi đã có file ảnh đàng hoàng — chứ không báo xong khi ảnh còn thiếu hoặc mở ra trắng trơn. Đây là cam kết: bạn được báo xong nghĩa là thật sự có hình để xem.

Một điều `/d2-activity` **không** làm: nó không có kiểu "vẽ ra rồi sửa tới sửa lui nhiều vòng ngay trong khung chat". Bản mô tả sơ đồ không hiện được thành hình trong chat, nên bạn xem hình từ chính file ảnh đã vẽ ra. Muốn chỉnh, bạn gọi lại lệnh với yêu cầu thay đổi, hệ thống tự hiểu là đang sửa bản cũ.

---

## 5. Ba anh em cùng vẽ quy trình — chọn cái nào?

`/d2-activity` là một trong ba lệnh cùng vẽ sơ đồ quy trình. Chúng khác nhau ở chỗ đứng, chọn nhầm sẽ mất công. Đây là cách phân biệt cho dễ nhớ:

| Lệnh | Hợp nhất khi bạn cần... | Đặc điểm |
|---|---|---|
| **`/activity`** | Hình **nhúng thẳng vào tài liệu** để GitHub/Obsidian tự hiện ra | Tiện, gọn cho quy trình đơn giản 1-2 vai trò. Nhiều nhánh thì dễ rối. |
| **`/activity-swimlane`** | Quy trình **nhiều vai trò** cần "phân làn thật" (mỗi vai một làn thẳng cột) | Lựa chọn mặc định cho quy trình đa vai trò, nhiều qua-lại giữa các vai. |
| **`/d2-activity`** | Một **style hình khác**: dàn **gọn hơn Mermaid khi nhiều nhánh**, ra **file ảnh** tiện dán slide/gửi đi | Đường vuông góc không đè. Chỉ là cách vẽ khác, không "hơn" hai lệnh kia. |

**Một lưu ý thực tế:** khi quy trình có **rất nhiều tương tác qua lại giữa các vai trò** (bước nhảy tới nhảy lui giữa khách — hệ thống — admin liên tục), cách vẽ của D2 có xu hướng **kéo các làn ra xa nhau khiến hình bị rối như mì Ý**. Trường hợp đó `/activity-swimlane` (phân làn thật) gọn và rõ hơn. Nói cách khác: D2 hợp khi nhiều nhánh nhưng ít giao cắt vai trò; còn nhiều vai trò đan chéo thì ưu tiên `/activity-swimlane`.

(Còn một lệnh nữa là `/bpmn` — vẽ theo một chuẩn quốc tế để nhập vào các phần mềm quản lý quy trình chuyên nghiệp. Dùng cho việc khác, chỉ cần khi thật sự đòi hỏi chuẩn đó, không bàn sâu ở đây.)

---

## 6. Ví dụ thực tế

Anh **Minh**, một BA phụ trách tính năng "order" (đặt hàng), cần vẽ quy trình xử lý đơn hàng. Quy trình này **nhiều nhánh rẽ nhưng ít giao cắt giữa các vai trò**. Anh đã thử vẽ bằng Mermaid nhưng nhiều nhánh nên hình ra cắt chéo lôi thôi, nên chuyển sang `/d2-activity` cho dàn gọn hơn — và anh cũng muốn một file ảnh riêng để tiện dán vào slide.

Anh Minh mở terminal, gõ:

```
/d2-activity "khách đặt hàng, hệ thống kiểm tra tồn kho, nếu còn hàng thì admin duyệt đơn, hết hàng thì báo khách" --feature order
```

1. Hệ thống kiểm tra trước: công cụ vẽ D2 đã cài trên máy chưa? Có rồi — đi tiếp. (Nếu chưa, nó đã dừng ngay và đưa anh Minh một dòng lệnh cài đặt.)

2. Hệ thống nhận ra đây là tính năng `order`, đọc các tài liệu sẵn có của tính năng này để hiểu đúng các bước và các nhánh rẽ.

3. Vì quy trình có nhiều người tham gia, hệ thống liệt kê ra: *"Phát hiện 3 vai trò tham gia: Khách, Hệ thống, Admin. Đủ chưa?"* Anh Minh nhớ ra còn thiếu "Kho" (bộ phận cập nhật tồn kho), nên trả lời: *"Thêm vai Kho nữa."* Hệ thống ghi nhận — nhờ hỏi lại mà không bỏ sót vai trò quan trọng này.

4. Hệ thống mô tả bằng lời thường: *"Em sẽ vẽ quy trình đặt hàng: 6 bước xử lý, 2 nhánh quyết định ('Còn hàng không?', 'Admin duyệt?'), 4 vai trò. Vẽ bằng D2 cho đường gọn, không đè. Apply?"* Anh Minh gõ `Y`.

5. Hệ thống viết phần mô tả sơ đồ, rồi nhờ công cụ D2 vẽ thật ra file ảnh. Lần vẽ đầu bị lỗi nhỏ (một nhãn có ký tự đặc biệt chưa xử lý) — hệ thống tự đọc lỗi, sửa lại, vẽ lại lần nữa. Lần này ra ảnh hoàn chỉnh.

6. Hệ thống báo xong, đưa anh Minh đường dẫn file ảnh: `docs/order/d2/order-checkout.svg`. Anh Minh mở bằng trình duyệt, thấy một sơ đồ gọn gàng — đường kẻ vuông góc, các ô thẳng hàng, các làn vai trò rõ ràng, không chỗ nào chồng chéo.

7. Anh Minh dán thẳng file ảnh này vào slide họp. Sơ đồ gọn gàng, đường không cắt chéo, ban giám đốc nhìn hiểu ngay.

Vài hôm sau, khách hàng đổi ý muốn thêm bước "gửi email xác nhận cho khách". Anh Minh chỉ cần gõ lại lệnh với yêu cầu thay đổi đó — hệ thống tự hiểu là đang sửa bản cũ, cho anh xem trước phần chỉnh, rồi vẽ lại hình mới.

---

## Xem thêm

Tài liệu này chỉ giải thích ý tưởng và luồng chạy ở mức dễ hiểu. Muốn xem đầy đủ chi tiết kỹ thuật (công thức viết sơ đồ, cách render, các trường hợp đặc biệt), đọc file gốc: `.claude/skills/d2-activity/SKILL.md`.

Các lệnh cùng họ vẽ quy trình:

- `explain-skills/activity.md` — vẽ quy trình bằng Mermaid, **nhúng thẳng vào tài liệu** để GitHub/Obsidian tự hiện.
- `explain-skills/activity-swimlane.md` — vẽ "phân làn thật" cho quy trình **nhiều vai trò**, lựa chọn mặc định khi nhiều tương tác qua lại.
- `explain-skills/activity-family.md` — so sánh tổng quan cả họ lệnh vẽ quy trình, giúp chọn đúng lệnh cho từng tình huống.
