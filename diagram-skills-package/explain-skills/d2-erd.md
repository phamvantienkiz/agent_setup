---
type: skill-explainer
skill: d2-erd
updated: 2026-07-14
---

# `/d2-erd` là gì và nó chạy như thế nào?

## 1. Dùng để làm gì, khi nào nên gõ lệnh này

`/d2-erd` vẽ **sơ đồ dữ liệu** — tiếng chuyên môn gọi là ERD (Entity-Relationship Diagram). Nói dễ hiểu: đây là hình mô tả **tính năng của bạn cần lưu những loại thông tin gì, và các loại thông tin đó liên hệ với nhau ra sao**.

Hãy hình dung mỗi "loại thông tin" là một cái bảng: bảng "Người dùng" (lưu email, trạng thái, ngày tạo...), bảng "Bộ thẻ" (lưu tên bộ thẻ, thuộc về người dùng nào...), bảng "Thẻ" (lưu nội dung thẻ, thuộc bộ nào...). Sơ đồ dữ liệu vẽ các bảng này ra thành ô, liệt kê các cột trong mỗi bảng, rồi nối chúng bằng mũi tên có ghi chú nghiệp vụ — ví dụ "một Người dùng **sở hữu** nhiều Bộ thẻ", "một Bộ thẻ **chứa** nhiều Thẻ". Nhìn vào là hiểu ngay bức tranh dữ liệu của tính năng.

Chữ "D2" trong tên lệnh là tên **công cụ vẽ** mà lệnh này dùng phía sau. `/d2-erd` **cùng nội dung** với `/erd` (đều là sơ đồ dữ liệu bảng + liên hệ) — chỉ khác **cách vẽ**: `/erd` dùng công cụ Mermaid (nhúng mã hình thẳng vào tài liệu), còn `/d2-erd` dùng công cụ D2 và cho ra một **file hình riêng** (đuôi `.svg`). Nói ngắn gọn: **D2 là một phương án vẽ thay thế cho Mermaid — một kiểu (style) vẽ khác để bạn chọn cho phù hợp**, chứ không phải "đẹp hơn" hay "xịn hơn".

Cả hai đều có chung một điểm tiện: **bạn chỉ cần mô tả nội dung** (có bảng nào, cột nào, liên hệ ra sao), còn việc **sắp xếp các bảng, kẻ đường nối** thì công cụ tự lo. Điểm khác biệt thực tế giữa hai lệnh là **nơi kết quả nằm** và **cần cài công cụ hay không** (xem Mục 6), chứ không phải chuyện đẹp/xấu.

Vài tình huống điển hình nên dùng `/d2-erd`:

- Bạn muốn một **file hình riêng** (`.svg`) để mở bằng trình duyệt, dán vào slide, gửi qua email — thay vì hình nằm lẫn trong tài liệu đặc tả.
- Bạn đã thử vẽ bằng `/erd` (Mermaid) nhưng thấy **kiểu dàn hình của nó chưa hợp mắt** với trường hợp của bạn — muốn thử một **kiểu vẽ khác** xem có vừa ý hơn không.

Gõ lệnh đơn giản như:

```
/d2-erd --feature flashcard
```

Phần `--feature flashcard` cho hệ thống biết vẽ sơ đồ dữ liệu cho tính năng nào. (Bạn cũng có thể mô tả trực tiếp bằng lời nếu tính năng đó chưa có sẵn tài liệu — xem Bước 2 ở sơ đồ dưới.)

**Một câu để nhớ:** `/d2-erd` vẽ **bức tranh dữ liệu** của một tính năng bằng **một kiểu vẽ khác (công cụ D2 thay cho Mermaid)**, cho ra một file hình riêng — chọn nó khi bạn muốn thử một style vẽ khác hoặc cần một file hình tách khỏi tài liệu.

---

## 2. Toàn bộ luồng chạy — sơ đồ

```
 BẠN GÕ LỆNH
 /d2-erd --feature X
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
 │  Đọc yêu cầu của bạn, xác định tính năng. Tính năng   │
 │  chưa có → tự đặt tên rồi tạo mới (không bắt bạn      │
 │  phải chuẩn bị bước nào trước).                       │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 2 — Lấy "bức tranh dữ liệu" cho đúng              │
 │  Ưu tiên đọc lại sơ đồ dữ liệu sẵn có của tính năng   │
 │  (nếu trước đó đã vẽ bằng /erd). Không có thì đọc     │
 │  tài liệu đặc tả để rút ra các bảng. Vẫn không có →   │
 │  HỎI bạn: có những loại thông tin nào, mỗi loại lưu   │
 │  gì, liên hệ với nhau ra sao. KHÔNG tự bịa bảng.      │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 3 — Xem trước rồi mới vẽ (xin phép)               │
 │  Hệ thống mô tả bằng lời thường: "sẽ vẽ N bảng dữ     │
 │  liệu (Người dùng, Bộ thẻ, Thẻ...), M liên hệ chính   │
 │  (Người dùng sở hữu Bộ thẻ...)". Bạn gật (Y) mới làm. │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 4 — Vẽ + kiểm tra ra được ảnh                     │
 │  Hệ thống viết mô tả sơ đồ, rồi nhờ công cụ D2 "vẽ    │
 │  thật" ra file ảnh. NẾU vẽ lỗi → tự sửa, vẽ lại. Chỉ  │
 │  báo XONG khi đã ra được ảnh hoàn chỉnh.              │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 5 — Báo hoàn tất                                  │
 │  Cho bạn đường dẫn file ảnh (.svg) để mở bằng trình   │
 │  duyệt xem. Ghi lại vào sổ theo dõi tính năng.        │
 └──────────────────────────────────────────────────────┘
        │
        ▼
     HOÀN TẤT — có 1 file hình (.svg) mở bằng trình duyệt là xem được
```

---

## 3. Cách đọc một sơ đồ dữ liệu (dành cho người không kỹ thuật)

Phần này giúp bạn **nhìn vào hình mà hiểu**, không cần biết gì về cơ sở dữ liệu.

**Mỗi ô là một "bảng" — một loại thông tin cần lưu.** Ví dụ: bảng "Người dùng", bảng "Bộ thẻ". Tên bảng nằm in đậm ở trên cùng của ô.

**Bên trong mỗi ô là các dòng — các "cột" của bảng đó.** Mỗi cột là một mẩu thông tin thuộc loại đó. Ví dụ bảng "Người dùng" có các cột: email, trạng thái (đang hoạt động / bị khóa), ngày tạo. Cạnh mỗi cột có ghi loại thông tin ở mức dễ hiểu — chữ, số, ngày giờ, hoặc danh sách lựa chọn ("miễn phí | trả phí").

**Vài cột được đánh dấu đặc biệt ở lề phải:**

- **Khóa chính** (viết tắt PK) — là cột dùng để phân biệt từng dòng trong bảng cho khỏi trùng (giống số căn cước phân biệt từng người). Mỗi bảng thường có một cột như vậy.
- **Khóa liên kết** (viết tắt FK) — là cột "trỏ sang" một bảng khác để tạo mối liên hệ. Ví dụ bảng "Bộ thẻ" có một cột trỏ về bảng "Người dùng" để biết bộ thẻ này của ai.

**Các mũi tên nối giữa các ô** — mỗi mũi tên là một mối liên hệ, có ghi chú bằng tiếng Việt để bạn hiểu ngay: "sở hữu", "chứa", "được ôn qua"... Ví dụ mũi tên từ "Người dùng" sang "Bộ thẻ" ghi "sở hữu" nghĩa là một người dùng sở hữu (nhiều) bộ thẻ.

Nhìn tổng thể, sơ đồ này trả lời được câu hỏi: *"Tính năng này lưu những loại thông tin gì, và chúng gắn với nhau như thế nào?"* — mà không cần đọc một dòng chữ đặc tả nào.

---

## 4. Một điều quan trọng: sơ đồ này ở mức NGHIỆP VỤ, không phải kỹ thuật sâu

Đây là điểm cần nói rõ để tránh hiểu nhầm về phạm vi của lệnh.

`/d2-erd` cố tình **giữ sơ đồ ở mức dễ hiểu cho người làm nghiệp vụ**, chứ không đi sâu vào chi tiết kỹ thuật của cơ sở dữ liệu. Cụ thể:

- Nó ghi loại thông tin ở mức **dễ hiểu** — "chữ", "số", "ngày giờ", "danh sách lựa chọn" — chứ **không** dùng các thuật ngữ kỹ thuật của dân lập trình database (kiểu `varchar(255)`, `uuid`...).
- Nó **không hỏi bạn** những câu kỹ thuật kiểu "cột này dài bao nhiêu ký tự", "có đánh chỉ mục không", "kiểu dữ liệu gì trong database" — vì đó là việc của dev/kỹ sư database khi triển khai, không phải việc của BA khi mô tả nghiệp vụ.

Nếu bạn cần một sơ đồ **gần với việc lập trình hơn** — có kiểu dữ liệu thật của database, có danh sách giá trị (enum), có chỉ mục (index), và xuất được ra mã lệnh SQL để bàn giao cho dev — thì đó là việc của một lệnh khác trong cùng nhóm (`/dbdiagram`, xem Mục 6). `/d2-erd` dừng ở mức bức tranh nghiệp vụ, giống hệt `/erd` — chỉ khác kiểu vẽ.

---

## 5. Vì sao phải kiểm tra công cụ trước, và "vẽ ra được ảnh mới báo xong"?

Hai chi tiết nhỏ nhưng quan trọng trong cách chạy của lệnh này.

**Kiểm tra công cụ trước tiên (Bước 0).** Không giống một số lệnh chạy hoàn toàn bên trong hệ thống, `/d2-erd` cần một công cụ tên "D2" được cài sẵn trên máy tính của bạn thì mới vẽ được. Vì vậy việc đầu tiên nó làm là kiểm tra: công cụ này có chưa? Nếu chưa, nó **dừng lại ngay và chỉ cho bạn đúng một dòng lệnh để cài** — chứ không cố vẽ nửa vời rồi tạo ra file hỏng. Giống như thợ mộc kiểm tra có đủ cưa đục chưa trước khi nhận đơn.

**Vẽ ra được ảnh mới báo xong (Bước 4).** Sau khi viết xong phần mô tả sơ đồ, hệ thống nhờ công cụ D2 "vẽ thật" ra file ảnh. Nếu phần mô tả có lỗi cú pháp khiến vẽ không ra (chỗ hay gặp nhất là quên bọc dấu ngoặc quanh những giá trị có ký tự đặc biệt, ví dụ danh sách lựa chọn "miễn phí | trả phí"), hệ thống **tự đọc lỗi, sửa lại, vẽ lại**. Nó chỉ báo "hoàn tất" khi đã có file ảnh đàng hoàng — chứ không báo xong khi ảnh còn thiếu hoặc mở ra trắng trơn. Đây là cam kết: được báo xong nghĩa là thật sự có hình để xem.

Một điều `/d2-erd` **không** làm: nó không có kiểu "vẽ ra rồi sửa tới sửa lui nhiều vòng ngay trong khung chat". Bản mô tả sơ đồ không hiện được thành hình trong chat, nên bạn xem hình từ chính file ảnh đã vẽ ra. Muốn chỉnh, bạn gọi lại lệnh với yêu cầu thay đổi — hệ thống tự hiểu là đang sửa bản cũ (không tạo trùng), cho bạn xem phần thay đổi rồi vẽ lại.

---

## 6. Ba anh em cùng vẽ "bức tranh dữ liệu" — chọn cái nào?

`/d2-erd` là một trong ba lệnh cùng mô tả dữ liệu của một tính năng. Cả ba vẽ **cùng một loại nội dung** (bảng + liên hệ) — khác nhau ở hai chuyện: **vẽ bằng kiểu nào** và **chi tiết tới mức nào**.

| Lệnh | Khác biệt chính | Ai xem / dùng làm gì |
|---|---|---|
| **`/erd`** | Kiểu vẽ Mermaid — **nhúng thẳng vào tài liệu**, tự hiện khi mở, không cần cài công cụ | BA/stakeholder đọc trong tài liệu |
| **`/d2-erd`** (lệnh này) | **Cùng nội dung như `/erd`, chỉ khác kiểu vẽ** (công cụ D2 thay cho Mermaid) — cho ra một **file hình riêng** (`.svg`), cần cài công cụ D2 | ai thích style vẽ này hơn, hoặc cần file hình tách khỏi tài liệu |
| **`/dbdiagram`** | Đi **sâu hơn về kỹ thuật** — kiểu database thật, danh sách lựa chọn, chỉ mục, **xuất ra mã SQL** để bàn giao | dev / kỹ sư database triển khai |

Cách chọn nhanh:

- **`/erd` và `/d2-erd` là hai kiểu vẽ của cùng một thứ** — chọn theo sở thích hiển thị: muốn nhúng thẳng trong tài liệu (không cần cài gì) → `/erd`; muốn một file hình riêng hoặc thử một kiểu dàn hình khác → `/d2-erd`. Không có cái nào "đẹp hơn" — chỉ là hai style khác nhau, dùng cái nào hợp mắt bạn.
- Chỉ khi cần **bàn giao cho dev, xuất SQL** (dữ liệu có nhiều danh sách lựa chọn, chỉ mục) thì mới cần lên `/dbdiagram` — đây là khác biệt về *độ chi tiết*, không phải về kiểu vẽ.

**Một lưu ý:** đừng chọn `/d2-erd` vì nghĩ "nó đẹp/xịn hơn" — nó **không** đẹp hơn `/erd`, chỉ là một phương án vẽ khác để bạn có thêm lựa chọn về style.

---

## 7. Ví dụ thực tế

Anh **Minh**, một BA phụ trách tính năng "flashcard" (thẻ ghi nhớ) của một app học tiếng Anh, cần một sơ đồ dữ liệu để dán vào slide họp. Trước đó anh đã vẽ bản nhúng trong tài liệu bằng `/erd` (Mermaid), nhưng với slide anh muốn một **file hình riêng** và muốn thử **kiểu vẽ khác** xem có hợp mắt hơn không — nên anh dùng `/d2-erd`.

Anh Minh mở terminal, gõ:

```
/d2-erd --feature flashcard
```

1. Hệ thống kiểm tra trước: công cụ vẽ D2 đã cài trên máy chưa? Có rồi — đi tiếp. (Nếu chưa, nó đã dừng ngay và đưa anh Minh một dòng lệnh cài đặt.)

2. Hệ thống nhận ra đây là tính năng `flashcard`, và tìm thấy trước đó anh đã vẽ một sơ đồ dữ liệu bằng `/erd`. Nó đọc lại bản đó để lấy đúng các bảng và liên hệ — không bắt anh mô tả lại từ đầu.

3. Hệ thống mô tả bằng lời thường: *"Em sẽ vẽ sơ đồ dữ liệu cho flashcard: 4 bảng (Người dùng, Bộ thẻ, Thẻ, Lượt ôn thẻ); 3 liên hệ chính (Người dùng sở hữu Bộ thẻ, Bộ thẻ chứa Thẻ, Thẻ được ôn qua Lượt ôn thẻ). Apply?"* Anh Minh gõ `Y`.

4. Hệ thống viết phần mô tả sơ đồ, rồi nhờ công cụ D2 vẽ thật ra file ảnh. Lần vẽ đầu bị lỗi nhỏ (một cột có danh sách lựa chọn "miễn phí | trả phí" chưa được bọc dấu ngoặc) — hệ thống tự đọc lỗi, sửa lại, vẽ lại lần nữa. Lần này ra ảnh hoàn chỉnh.

5. Hệ thống báo xong, đưa anh Minh đường dẫn file ảnh: `docs/flashcard/d2-erd/flashcard.svg`. Anh Minh mở bằng trình duyệt, thấy 4 bảng gọn gàng — tên bảng in đậm, các cột thẳng hàng, cột khóa chính / khóa liên kết đánh dấu rõ ở lề phải, các mũi tên có ghi chú tiếng Việt ("sở hữu", "chứa", "được ôn qua").

6. Anh Minh dán thẳng file ảnh này vào slide họp. Ban giám đốc nhìn hiểu ngay "tính năng flashcard lưu những loại thông tin gì và chúng gắn với nhau ra sao", không cần đọc một dòng đặc tả kỹ thuật nào.

Vài hôm sau, nghiệp vụ thêm tính năng "gắn nhãn cho bộ thẻ". Anh Minh chỉ cần gõ lại `/d2-erd --feature flashcard` và nói thêm bảng "Nhãn" — hệ thống tự hiểu là đang cập nhật sơ đồ cũ, cho anh xem trước phần thay đổi rồi vẽ lại hình mới.

---

## Xem thêm

Tài liệu này chỉ giải thích ý tưởng và luồng chạy ở mức dễ hiểu. Muốn xem đầy đủ chi tiết kỹ thuật (công thức viết sơ đồ, cách render, các trường hợp đặc biệt), đọc file gốc: `.claude/skills/d2-erd/SKILL.md`.

Các lệnh cùng họ mô tả dữ liệu và các lệnh D2 anh em:

- `explain-skills/erd.md` — vẽ sơ đồ dữ liệu bằng Mermaid, **nhúng thẳng vào tài liệu** để GitHub/Obsidian tự hiện.
- `.claude/skills/dbdiagram/SKILL.md` — sơ đồ dữ liệu **gần với lập trình** (kiểu database thật, xuất SQL), dùng khi bàn giao cho dev.
- `explain-skills/d2-activity.md` — cùng công cụ D2 nhưng vẽ **sơ đồ quy trình** (từng bước một việc chạy thế nào), thay vì sơ đồ dữ liệu.

Chọn loại sơ đồ:

- `explain-skills/erd-family.md` — so sánh nhanh cả 3 lệnh vẽ dữ liệu (`/erd`, `/d2-erd`, `/dbdiagram`), giúp chọn đúng cái cần.
- `explain-skills/diagram-selection.md` — bàn chỉ đường cho **mọi loại sơ đồ** (khi chưa biết cần loại nào).
- Quy tắc gốc (bản kỹ thuật, cho máy): `.claude/rules/diagram-selection.md`.
