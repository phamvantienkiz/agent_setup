---
type: skill-explainer
skill: activity-swimlane
updated: 2026-07-14
---

# `/activity-swimlane` là gì và nó chạy như thế nào?

## 1. Dùng để làm gì, khi nào nên gõ lệnh này

`/activity-swimlane` là lệnh bạn gõ khi cần **vẽ sơ đồ một quy trình nghiệp vụ có nhiều người/nhiều bộ phận cùng tham gia**, và bạn muốn nhìn phát là biết ngay **ai chịu trách nhiệm bước nào**.

Từ khoá quan trọng là **"swimlane" — tức chia sơ đồ thành các "làn" theo vai trò** (tạm gọi là *phân làn*). Hãy tưởng tượng một **hồ bơi có nhiều làn**: mỗi làn dành cho một vai trò — làn của Khách hàng, làn của Hệ thống, làn của Nhân viên, làn của Quản lý. Mỗi bước công việc được đặt nằm trong làn của người phụ trách bước đó. Khi công việc chuyển từ người này sang người khác, đường đi trong sơ đồ sẽ **"nhảy làn"** sang cột kế bên. Nhờ vậy, chỉ cần liếc mắt theo cột dọc là biết ngay "phần này ai làm".

Vài tình huống điển hình nên dùng `/activity-swimlane`:

- Vẽ quy trình **hoàn tiền**: Khách yêu cầu → Hệ thống kiểm tra → Nhân viên xem xét → Quản lý duyệt → Hệ thống chuyển tiền. Có tới 4 vai trò và họ "chuyền bóng" qua lại liên tục.
- Vẽ quy trình **duyệt nhiều cấp** (ví dụ duyệt nội dung, duyệt đơn nghỉ phép qua nhiều người ký).
- Vẽ quy trình **onboarding** (tiếp nhận khách/nhân viên mới) đi qua nhiều bộ phận.

Nói ngắn gọn: **khi một quy trình có từ 2 vai trò trở lên và họ tương tác qua lại nhiều lần**, đây là lệnh phù hợp nhất — vì nó là công cụ duy nhất trong nhóm giữ được các "phân làn" thẳng cột cố định (lý do vì sao, xem Mục 3).

Gõ lệnh đơn giản như:

```
/activity-swimlane "khách yêu cầu hoàn tiền, hệ thống kiểm tra, nhân viên xem xét, quản lý duyệt" --feature payment
```

**Một câu để nhớ:** quy trình nhiều người, muốn thấy rõ ai làm bước nào → gõ `/activity-swimlane`.

---

## 2. Toàn bộ luồng chạy — sơ đồ

Điểm cần nhớ: trước khi vẽ, hệ thống **hỏi bạn xác nhận danh sách vai trò**; sau khi vẽ xong, nó **tự mở ảnh ra soi lại** xem có sai chỗ nào không, rồi mới báo bạn.

```
 BẠN GÕ LỆNH
 /activity-swimlane "mo ta quy trinh" --feature X
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 0 — Kiểm tra điều kiện vẽ được                    │
 │  Việc dựng hình được thực hiện qua dịch vụ web        │
 │  plantuml.com, nên máy cần công cụ mã hoá + kết nối   │
 │  được tới đó. Thiếu 1 trong                            │
 │  2 → DỪNG ngay, báo 1 dòng, KHÔNG tạo file rỗng.      │
 └──────────────────────────────────────────────────────┘
        │  (đủ điều kiện → đi tiếp)
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ GIAI ĐOẠN 1 — Tìm đúng tính năng + đọc nghiệp vụ      │
 │  Hệ thống đoán bạn đang nói về tính năng nào, rồi     │
 │  đọc các tài liệu đã có (mô tả, bản đặc tả) để hiểu   │
 │  các bước, các nhánh rẽ, ai làm gì. Thiếu thông tin  │
 │  → hỏi bạn (bằng ngôn ngữ nghiệp vụ, không hỏi kỹ    │
 │  thuật).                                              │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ GIAI ĐOẠN 2 — HỎI XÁC NHẬN CÁC LÀN (vai trò)          │
 │  Vì swimlane luôn có nhiều làn, hệ thống nói: "Em    │
 │  phát hiện 4 vai trò: Khách / Hệ thống / Nhân viên /  │
 │  Quản lý. Đủ chưa?" → CHỜ bạn gật đầu hoặc bổ sung.   │
 │  (Vì sao bước này quan trọng: xem Mục 4.)             │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ GIAI ĐOẠN 3 — Xin phép trước khi ghi (bản tóm tắt)   │
 │  Hệ thống mô tả bằng lời: sẽ vẽ mấy làn, mấy bước,    │
 │  mấy điểm rẽ nhánh, bắt đầu ở đâu kết thúc ở đâu.     │
 │  Bạn gõ Y (đồng ý) thì mới đi tiếp.                   │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ GIAI ĐOẠN 4 — Vẽ hình + đòi VẼ RA ĐƯỢC mới đi tiếp    │
 │  Hệ thống viết "bản mô tả sơ đồ" rồi gửi lên trang    │
 │  web chuyên vẽ; web trả về file ảnh. Nếu bản mô tả    │
 │  có lỗi khiến vẽ không ra → tự sửa, vẽ lại (tối đa 2  │
 │  lần). Chỉ đi tiếp khi đã ra được ảnh hợp lệ.         │
 │  (Việc dựng hình do dịch vụ plantuml.com thực hiện.)  │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ GIAI ĐOẠN 5 — TỰ SOI LẠI ẢNH (bước đặc biệt)          │
 │  Vẽ ra được ảnh CHƯA đủ — hệ thống còn tự mở ảnh ra   │
 │  soi bằng "mắt" xem VẼ CÓ ĐÚNG NGHIỆP VỤ không:       │
 │   • mũi tên có đi đúng chiều không?                   │
 │   • mỗi bước có nằm đúng làn của người phụ trách?     │
 │   • có nhánh nào bị cụt (đi vào ngõ chết) không?      │
 │  Thấy sai → tự sửa và vẽ lại (tối đa 2 vòng).         │
 │  (Vì sao có bước này: xem Mục 5.)                    │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ GIAI ĐOẠN 6 — Lưu file + báo hoàn tất                 │
 │  Lưu 2 thứ trong thư mục srs/ của tính năng: bản gốc  │
 │  .puml (để sửa về sau) + ảnh .svg. Rồi nhúng ảnh .svg │
 │  vào file tập hợp sơ đồ luồng (flows.md, dùng chung   │
 │  với các sơ đồ khác). Báo bạn mở ảnh ra xem.          │
 └──────────────────────────────────────────────────────┘
        │
        ▼
     HOÀN TẤT — có sơ đồ swimlane để dùng trong tài liệu BA
```

Lưu ý: lệnh này **không có bước "sửa đi sửa lại ngay trong màn hình chat"**. Lý do đơn giản: cửa sổ chat không hiển thị được hình vẽ (nó chỉ thấy dòng chữ). Vì vậy hệ thống vẽ ra file ảnh, tự soi lại giúp bạn (Giai đoạn 5), rồi bạn mở file ảnh ra xem. Muốn sửa, bạn gõ lại lệnh với mô tả thay đổi.

---

## 3. Vì sao phải có lệnh riêng cho "swimlane thật"?

Đây là lý do ra đời của lệnh này, nên đáng giải thích kỹ.

Trong bộ công cụ có sẵn một lệnh anh em là `/activity` (xem Mục "Xem thêm"). Cả hai đều vẽ sơ đồ quy trình, nhưng dùng **hai công cụ vẽ khác nhau**, và đây là điểm mấu chốt:

- `/activity` dùng một công cụ vẽ tên là **Mermaid**. Với công cụ này, các "phân làn" chỉ là **cái khung trang trí vẽ thêm cho đẹp** — nó không thực sự "giữ" các bước nằm đúng làn. Khi quy trình có nhiều vai trò và nhiều lần chuyền việc qua lại, các bước bị **trôi lung tung**, làn bị **xô lệch**, nhìn rất rối, khó biết bước nào thuộc ai.

- `/activity-swimlane` dùng một công cụ vẽ tên là **PlantUML**. Công cụ này có khả năng vẽ **phân làn thật**: mỗi làn là một cột thẳng đứng **cố định**, và mỗi bước bị "khoá" đúng vào làn của người phụ trách. Dù việc có nhảy qua nhảy lại giữa các vai trò bao nhiêu lần, các cột vẫn thẳng hàng, đọc rất dễ.

Hình dung nôm na: làn của `/activity` (Mermaid) giống như mấy ô vẽ bằng phấn trên sân — có ranh giới cho đẹp, nhưng người chơi vẫn chạy lấn sang ô khác. Còn làn của `/activity-swimlane` (PlantUML) giống như một cái tủ có ngăn cứng — mỗi món đồ (mỗi bước) luôn nằm gọn trong ngăn của người phụ trách, không xê dịch dù có lấy ra lấy vào bao nhiêu lần.

Vì thế, với **quy trình nhiều vai trò và nhiều tương tác qua lại**, `/activity-swimlane` là **lựa chọn được ưu tiên mặc định** (đánh dấu ⭐ trong tài liệu chọn sơ đồ). Còn `/activity` (Mermaid) chỉ nên dùng cho luồng **gọn, 1-2 vai trò, ít chuyền việc qua lại**.

---

## 4. Vì sao phải HỎI XÁC NHẬN các làn trước khi vẽ?

Trước khi vẽ, hệ thống dừng lại và hỏi bạn: *"Em phát hiện những vai trò này... đủ chưa?"* — rồi chờ bạn trả lời. (Với swimlane thì bước hỏi này gần như luôn xảy ra, vì bản chất sơ đồ phân làn phải có từ 2 làn trở lên — không có vai trò thì cũng chẳng có làn nào để vẽ.)

Lý do rất thực tế: **vai trò thường ẩn trong câu chữ, rất dễ bị bỏ sót**. Khi bạn mô tả một quy trình bằng lời, có những người tham gia không được gọi tên rõ ràng. Ví dụ bạn nói *"khách yêu cầu hoàn tiền, sau khi kiểm tra thì tiền được chuyển lại"* — câu này nghe qua chỉ thấy 1 vai (Khách). Nhưng thực ra có ít nhất 2-3 vai ẩn: ai "kiểm tra"? ai "chuyển tiền"? Có cần người "duyệt" không?

Nếu hệ thống tự đoán rồi vẽ luôn, nó có thể **sót hẳn một làn** — nghĩa là sơ đồ thiếu mất một người quan trọng trong quy trình, khiến tài liệu sai lệch. Sót một làn nghiêm trọng hơn sót một bước, vì nó làm hiểu sai cả bức tranh "ai chịu trách nhiệm gì".

Vì vậy hệ thống chọn cách an toàn: liệt kê các vai trò nó nhận ra, rồi để bạn — người hiểu nghiệp vụ nhất — xác nhận hoặc bổ sung, **trước khi** đặt bút vẽ.

---

## 5. Vì sao có bước "tự soi lại ảnh" (Giai đoạn 5)?

Đây là bước thể hiện sự cẩn thận đáng chú ý nhất của lệnh này.

Sau khi vẽ xong, hệ thống làm một việc mà đa số công cụ bỏ qua: nó **tự mở ảnh vừa vẽ ra và nhìn bằng "mắt"** để kiểm tra, thay vì chỉ kiểm tra kiểu máy móc.

Có một sự khác biệt quan trọng ở đây. Bình thường công cụ chỉ kiểm được "câu chữ mô tả có đúng ngữ pháp không" — giống như kiểm chính tả một câu văn. Nhưng câu văn đúng chính tả vẫn có thể **vẽ ra hình sai**: mũi tên chỉ ngược chiều, một bước nằm nhầm sang làn của người khác, hoặc một nhánh đi vào ngõ cụt không có lối ra. Những lỗi này chỉ **nhìn hình mới thấy**, kiểm chính tả không bắt được.

Vì vậy hệ thống tự đặt cho mình một danh sách câu hỏi và soi từng mục trên ảnh thật:

- Mọi mũi tên có đi đúng chiều tiến trình không?
- Mỗi bước có nằm đúng làn của người thật sự làm bước đó không? (ví dụ: bước "chuyển tiền" phải nằm ở làn Hệ thống, không phải làn Khách hàng)
- Có nhánh nào bị cụt — dẫn vào chỗ không có đường ra không?
- Mỗi điểm rẽ nhánh (câu hỏi có/không) có đủ cả hai đường rẽ không?

Nếu phát hiện sai, nó **tự sửa và vẽ lại** (tối đa 2 vòng) rồi mới báo bạn. Nghĩa là khi bạn nhận được sơ đồ, nó đã được "soi" một lượt giúp bạn rồi — bạn ít phải bắt lỗi thủ công hơn.

---

## 6. Ví dụ thực tế

Anh **Minh**, một BA phụ trách tính năng "payment" (thanh toán), được giao vẽ sơ đồ quy trình **hoàn tiền** để đưa vào tài liệu đặc tả. Quy trình có nhiều người tham gia và chuyền việc qua lại, nên anh chọn `/activity-swimlane`.

Anh Minh mở terminal, gõ:

```
/activity-swimlane "khách gửi yêu cầu hoàn tiền, hệ thống kiểm tra đơn hợp lệ, nhân viên xem xét, quản lý duyệt nếu số tiền lớn, rồi hệ thống chuyển tiền" --feature payment
```

1. Hệ thống nhận ra ngay đây là tính năng `payment` (vì anh Minh ghi rõ `--feature payment`) và đọc các tài liệu đã có của tính năng này để hiểu các bước và các nhánh rẽ.

2. Hệ thống dừng lại, nói với anh Minh: *"Em phát hiện 4 vai trò: Khách hàng, Hệ thống, Nhân viên, Quản lý. Đủ chưa ạ?"* Anh Minh nhận ra còn thiếu bước "gửi email báo kết quả cho khách", nhưng vai trò thì đủ 4, nên anh trả lời *"đủ, nhưng thêm bước hệ thống gửi email cuối cùng"*. Hệ thống ghi nhận.

3. Hệ thống mô tả bằng lời sẽ vẽ gì: *"4 làn, 8 bước, 2 điểm rẽ nhánh (Đơn có hợp lệ không? / Số tiền có vượt hạn mức cần quản lý duyệt không?), bắt đầu khi khách gửi yêu cầu, kết thúc khi hệ thống gửi email. Đồng ý?"* Anh Minh gõ `Y`.

4. Hệ thống viết bản mô tả sơ đồ và gửi lên trang web plantuml.com để vẽ. Trang web trả về file ảnh.

5. Hệ thống **tự mở ảnh ra soi**. Nó phát hiện một lỗi: bước "chuyển tiền" đang bị đặt nhầm ở làn Nhân viên, trong khi thực tế Hệ thống mới là bên chuyển tiền. Nó tự sửa lại bản mô tả, vẽ lại, soi lại lần nữa — lần này mọi bước đều đúng làn, mọi nhánh đều có lối ra.

6. Hệ thống nhúng ảnh sơ đồ vào file tập hợp các sơ đồ luồng của tính năng payment, rồi báo anh Minh: *"Sơ đồ swimlane hoàn tiền đã xong, 4 làn / 8 bước / 2 nhánh, tự soi ảnh: đạt. Anh mở file ảnh ra xem nhé."*

7. Anh Minh mở file ảnh, thấy 4 cột thẳng hàng rõ ràng, nhìn phát biết ngay bước nào của ai. Anh thấy ổn, không cần sửa gì thêm.

Toàn bộ quá trình, anh Minh chỉ cần xác nhận vai trò một lần và gật đầu cho vẽ một lần — phần soi lỗi hình vẽ đã có hệ thống làm giúp.

---

## Xem thêm

Đây là một trong ba lệnh cùng họ "vẽ sơ đồ quy trình". Tùy nhu cầu mà chọn:

- `explain-skills/activity.md` — lệnh `/activity` (công cụ Mermaid): nhẹ nhất, nhúng thẳng vào tài liệu và tự hiện hình trên GitHub/Obsidian. Hợp luồng **gọn, 1-2 vai trò**.
- `explain-skills/d2-activity.md` — lệnh `/d2-activity` (công cụ D2): vẽ **hình đẹp đứng riêng** để đưa cho sếp/khách xem hoặc xuất ra file.
- `explain-skills/activity-family.md` — bài so sánh tổng hợp cả ba lệnh, giúp bạn chọn đúng lệnh cho từng tình huống.

Muốn xem đầy đủ chi tiết kỹ thuật (từng bước, quy tắc viết, các trường hợp đặc biệt), đọc file gốc: `.claude/skills/activity-swimlane/SKILL.md`.
