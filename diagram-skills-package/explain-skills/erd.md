---
type: skill-explainer
skill: erd
updated: 2026-07-14
---

# `/erd` là gì và nó chạy như thế nào?

## 1. Dùng để làm gì, khi nào nên gõ lệnh này

`/erd` vẽ **sơ đồ dữ liệu** — tiếng chuyên môn gọi là ERD (Entity-Relationship Diagram). Nói dễ hiểu: đây là hình mô tả **tính năng của bạn cần lưu những loại thông tin gì, và các loại thông tin đó liên hệ với nhau ra sao**.

Hãy hình dung mỗi "loại thông tin" là một cái bảng: bảng "Khách hàng" (lưu email, số điện thoại, ngày tạo...), bảng "Đơn hàng" (lưu số tiền, trạng thái, thuộc khách nào...), bảng "Giao dịch" (lưu kết quả thanh toán, thuộc đơn nào...). Sơ đồ dữ liệu vẽ các bảng này ra thành ô, liệt kê các thông tin trong mỗi bảng, rồi nối chúng bằng đường có ghi chú nghiệp vụ — ví dụ "một Khách hàng **đặt** nhiều Đơn hàng", "một Đơn hàng **phát sinh** nhiều Giao dịch". Nhìn vào là hiểu ngay bức tranh dữ liệu của tính năng.

Điểm đặc trưng của `/erd`: hình nó vẽ ra được **nhúng thẳng vào tài liệu** của tính năng, và **tự hiện thành hình** khi bạn mở tài liệu trong công cụ đọc phổ biến (VS Code / Obsidian / GitHub) — không cần cài thêm công cụ gì, không cần file ảnh rời. Sơ đồ nằm chung một chỗ với các mô tả nghiệp vụ khác, nên tiện cho người đọc tài liệu.

Vài tình huống điển hình nên dùng `/erd`:

- Bạn muốn một sơ đồ dữ liệu **nằm ngay trong tài liệu đặc tả** của tính năng, để ai mở tài liệu ra cũng thấy — không phải mở file ảnh riêng.
- Tính năng có vài loại thông tin cần lưu và bạn muốn ghi lại "chúng gắn với nhau thế nào" cho dev và cho chính bạn tra sau này.

Gõ lệnh đơn giản như:

```
/erd --feature payment
```

Phần `--feature payment` cho hệ thống biết vẽ sơ đồ dữ liệu cho tính năng nào. (Nếu bạn không ghi, và trong dự án chỉ có một tính năng đang làm dở, hệ thống tự đoán ra; còn nhiều tính năng thì nó hỏi bạn chọn.)

**Một câu để nhớ:** `/erd` vẽ **bức tranh dữ liệu** của một tính năng và **nhúng thẳng vào tài liệu** — hợp nhất khi bạn muốn sơ đồ nằm chung với đặc tả, tự hiện khi mở tài liệu, không cần công cụ ngoài.

---

## 2. Toàn bộ luồng chạy — sơ đồ

Điều cần nhớ về `/erd`: hình nó vẽ ra là dạng **mã chữ** (Mermaid) nhúng trong tài liệu — nghĩa là bạn không nhìn thấy hình ngay trong khung chat, mà mở tài liệu ra thì hình mới hiện. Vì vậy hệ thống có một bước **tự vẽ thử ra ảnh và tự soi lại** trước khi báo xong — đảm bảo hình vừa vẽ được, vừa đúng nội dung.

```
 BẠN GÕ LỆNH
 /erd --feature X
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 1 — Xác định đang vẽ cho tính năng nào            │
 │  Đọc yêu cầu của bạn, xác định tính năng. Nhiều tính  │
 │  năng, không rõ → hỏi bạn chọn. Tính năng chưa có →   │
 │  tự đặt tên rồi tạo mới (không bắt chuẩn bị gì trước).│
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 2 — Lấy "bức tranh dữ liệu" cho đúng              │
 │  Đọc tài liệu đặc tả sẵn có để rút ra các bảng cần    │
 │  lưu. Thiếu thông tin → HỎI bạn: có những loại thông  │
 │  tin nào, mỗi loại lưu gì, liên hệ với nhau ra sao.   │
 │  KHÔNG tự bịa bảng, không tự đoán liên hệ.            │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 3 — Xem trước rồi mới ghi (xin phép)              │
 │  Hệ thống mô tả bằng lời: "sẽ vẽ N bảng dữ liệu       │
 │  (Khách hàng, Đơn hàng...), M liên hệ chính". Bạn     │
 │  gật (Y) mới ghi vào tài liệu.                        │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 4 — Ghi sơ đồ vào tài liệu của tính năng          │
 │  Thêm sơ đồ vào file dữ liệu của tính năng (nhúng     │
 │  thẳng, không tạo file ảnh rời).                      │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 5 — Tự vẽ thử ra ảnh + TỰ SOI lại                │
 │  Vì hình không hiện trong chat, hệ thống tự "vẽ thử"  │
 │  ra ảnh. Lỗi cú pháp → tự sửa, thử lại. Vẽ được rồi   │
 │  thì tự MỞ ẢNH RA NHÌN, kiểm bằng mắt:                │
 │   • đủ bảng chưa?                                      │
 │   • các đường liên hệ có đúng CHIỀU không?             │
 │   • ghi chú có đọc được, không bị che không?           │
 │  Sai → tự sửa rồi vẽ lại. (Vẽ được hình ≠ vẽ đúng.)   │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 6 — Báo hoàn tất                                  │
 │  Cho biết đã ghi sơ đồ vào file nào, hình vẽ được và  │
 │  đã tự soi. Ghi lại vào sổ theo dõi tính năng.        │
 └──────────────────────────────────────────────────────┘
        │
        ▼
     HOÀN TẤT — mở tài liệu trong công cụ đọc là thấy hình
```

---

## 3. Cách đọc một sơ đồ dữ liệu (dành cho người không kỹ thuật)

Phần này giúp bạn **nhìn vào hình mà hiểu**, không cần biết gì về cơ sở dữ liệu.

**Mỗi ô là một "bảng" — một loại thông tin cần lưu.** Ví dụ: bảng "Khách hàng", bảng "Đơn hàng". Tên bảng nằm trên cùng của ô.

**Bên trong mỗi ô là các dòng — các thông tin của bảng đó.** Mỗi dòng là một mẩu thông tin. Cạnh mỗi dòng thường có một ghi chú tiếng Việt nói rõ nghĩa nghiệp vụ — ví dụ "email — địa chỉ liên hệ, duy nhất", hoặc liệt kê các giá trị có thể có ("trạng thái: chờ | đã xác nhận | đã thanh toán | đã huỷ").

**Vài dòng được đánh dấu chữ viết tắt ở cuối:**

- **PK** (khóa chính) — là dòng dùng để phân biệt từng bản ghi cho khỏi trùng (giống số căn cước phân biệt từng người). Mỗi bảng thường có một dòng như vậy.
- **FK** (khóa liên kết) — là dòng "trỏ sang" một bảng khác để tạo mối liên hệ. Ví dụ bảng "Đơn hàng" có một dòng trỏ về bảng "Khách hàng" để biết đơn này của ai.

**Các đường nối giữa các ô** — mỗi đường là một mối liên hệ, có ghi chú nghiệp vụ ("đặt", "phát sinh", "sở hữu"...). Đầu đường có ký hiệu nhỏ cho biết liên hệ là **"một–nhiều"** hay **"một–một"** — ví dụ một Khách hàng đặt *nhiều* Đơn hàng. (Các ký hiệu này hơi khó đọc với người mới, nhưng phần ghi chú chữ luôn nói rõ bản chất liên hệ, nên bạn cứ đọc ghi chú là hiểu.)

Nhìn tổng thể, sơ đồ này trả lời được câu hỏi: *"Tính năng này lưu những loại thông tin gì, và chúng gắn với nhau như thế nào?"*

---

## 4. Một điều cần nói rõ: ERD được phép có chút "kỹ thuật gọn"

Trong bộ tài liệu này có một nguyên tắc chung: các lệnh dành cho BA **không hỏi bạn những câu kỹ thuật của dân lập trình database** (kiểu "cột này dùng kiểu dữ liệu gì", "dài bao nhiêu ký tự", "có đánh chỉ mục không"). `/erd` vẫn giữ nguyên tắc đó khi **phỏng vấn** bạn — nó chỉ hỏi bằng ngôn ngữ nghiệp vụ ("bảng này lưu những thông tin gì", "liên hệ với bảng kia thế nào").

Tuy nhiên, có một điểm cần nói rõ để tránh hiểu nhầm: **bản thân sơ đồ ERD vốn là một loại hình có tính kỹ thuật** — nên khi vẽ, hệ thống sẽ **tự** gắn cho mỗi thông tin một "kiểu" ở mức gọn, dễ hiểu: chữ, số, số tiền, ngày giờ, đúng/sai. Đây không phải lệch vai — đó là cách một sơ đồ ERD chuẩn vẫn thể hiện. Bạn **không cần** cung cấp những kiểu này; hệ thống tự lo, còn bạn chỉ mô tả nghĩa nghiệp vụ.

Điều hệ thống **cố tình không làm** trên sơ đồ này: không đi vào các chi tiết sâu của database (kiểu dữ liệu chuyên biệt, chỉ mục, kế hoạch tối ưu, ghi chú bảo mật/mã hóa). Những thứ đó là việc của dev/kỹ sư database khi triển khai. Nếu bạn cần một sơ đồ đi sâu tới mức đó — có kiểu database thật, có chỉ mục, và xuất được ra mã lệnh để bàn giao — thì đó là việc của lệnh `/dbdiagram` (xem Mục 6).

---

## 5. Vì sao phải "tự vẽ thử ra ảnh rồi tự soi lại" (Bước 5)?

Đây là bước tự-kiểm-tra quan trọng nhất, làm nên sự khác biệt giữa "báo xong nhưng hình lỗi/sai" và "báo xong là dùng được".

**Phần 1 — tự vẽ thử để bắt lỗi cú pháp.** Sơ đồ được lưu dưới dạng **mã chữ** để công cụ đọc tài liệu tự biến thành hình. Đoạn mã đó có thể viết sai một chỗ nhỏ khiến khi bạn mở tài liệu ra thì **cả khối hình báo lỗi, không hiện gì**. Và vì hình không hiện trong khung chat, nếu hệ thống không tự kiểm, bạn sẽ chỉ phát hiện lỗi khi tự mở file — mất công. Nên hệ thống tự vẽ thử ra ảnh; vẽ không ra thì tự đọc lỗi, sửa, thử lại vài lần.

**Phần 2 — tự mở ảnh ra nhìn để bắt lỗi nội dung.** Đây là điểm tinh tế: **hình vẽ ra được (đúng cú pháp) không có nghĩa là hình vẽ đúng.** Một lỗi hay gặp với sơ đồ dữ liệu là **vẽ ngược chiều liên hệ** — ví dụ định vẽ "một Khách hàng có nhiều Đơn hàng" nhưng lại vẽ thành "một Đơn hàng có nhiều Khách hàng". Lỗi này khiến hình vẫn hiện ra bình thường, không báo lỗi cú pháp gì, nhưng nội dung thì sai hẳn. Máy kiểm cú pháp không bắt được loại lỗi này — chỉ có "nhìn bằng mắt" mới thấy.

Vì vậy sau khi vẽ được, hệ thống **tự mở ảnh ra và tự soi**: đủ bảng chưa, các đường liên hệ có đúng chiều không (một–nhiều đặt đúng đầu chưa), có dòng nào ghi trùng lặp vô nghĩa không, ghi chú có bị che khuất không. Sai chỗ nào thì tự sửa rồi vẽ lại. Giống như viết xong một câu rồi đọc lại to lên xem có nghe xuôi không, chứ không chỉ kiểm chính tả.

---

## 6. Ba anh em cùng vẽ "bức tranh dữ liệu" — chọn cái nào?

`/erd` là một trong ba lệnh cùng mô tả dữ liệu của một tính năng. Chúng khác nhau ở **ai xem và dùng để làm gì** — chọn nhầm sẽ mất công. Đây là cách phân biệt cho dễ nhớ:

Cả ba vẽ **cùng một loại nội dung** (bảng + liên hệ) — khác nhau ở hai chuyện: **vẽ bằng kiểu nào** và **chi tiết tới mức nào**.

| Lệnh | Khác biệt chính | Ai xem / dùng làm gì |
|---|---|---|
| **`/erd`** (lệnh này) | Kiểu vẽ Mermaid — **nhúng thẳng vào tài liệu**, tự hiện khi mở, không cần cài công cụ | BA/stakeholder đọc trong tài liệu |
| **`/d2-erd`** | **Cùng nội dung như `/erd`, chỉ khác kiểu vẽ** (công cụ D2 thay cho Mermaid) — cho ra một file hình riêng (`.svg`), cần cài công cụ D2 | ai thích style vẽ này hơn, hoặc cần file hình tách khỏi tài liệu |
| **`/dbdiagram`** | Đi **sâu hơn về kỹ thuật** — kiểu database thật, danh sách lựa chọn, chỉ mục, **xuất ra mã SQL** để bàn giao | dev / kỹ sư database triển khai |

Cách chọn nhanh:

- **`/erd` và `/d2-erd` là hai kiểu vẽ của cùng một thứ** — chọn theo sở thích hiển thị: muốn nhúng thẳng trong tài liệu (không cần cài gì) → `/erd`; muốn một file hình riêng hoặc thử một kiểu dàn hình khác → `/d2-erd`. Không cái nào "đẹp hơn" — chỉ là hai style, dùng cái nào hợp mắt bạn.
- Chỉ khi cần **bàn giao cho dev, xuất SQL** (dữ liệu có nhiều danh sách lựa chọn, chỉ mục) mới cần lên `/dbdiagram` — đây là khác biệt về *độ chi tiết*, không phải kiểu vẽ.

---

## 7. Vì sao lệnh này KHÔNG "vẽ đi vẽ lại nhiều vòng trong chat"?

Giống các lệnh vẽ sơ đồ khác dùng mã chữ, `/erd` **cố tình không** cho bạn "sửa nhiều vòng ngay trong chat" — vì lý do đơn giản: **mã chữ đó không hiện thành hình trong khung chat**, chat chỉ in ra một đống ký tự thô mà nhìn vào bạn khó "duyệt" được hình đúng hay sai. Cho sửa nhiều vòng trên một thứ bạn không nhìn thấy hình là vô nghĩa.

Thay vào đó: hệ thống ghi hình vào tài liệu, tự kiểm cho vẽ được và tự soi cho đúng, rồi bạn **mở tài liệu trong công cụ đọc** để xem hình thật. Muốn sửa, bạn **gọi lại lệnh** và nói cần đổi gì — hệ thống tự hiểu là đang sửa bản cũ (không tạo trùng), cho bạn xem phần thay đổi "trước/sau" rồi mới ghi đè.

---

## 8. Ví dụ thực tế

Chị **Lan**, một BA phụ trách tính năng "payment" (thanh toán), cần ghi lại rõ "tính năng này lưu những loại thông tin gì" ngay trong tài liệu đặc tả, để dev đọc tài liệu là thấy luôn, không phải mở file ảnh riêng.

Chị Lan mở terminal, gõ:

```
/erd --feature payment
```

1. Hệ thống nhận ra đây là tính năng `payment` (chị Lan ghi rõ) — không cần hỏi lại.

2. Hệ thống đọc tài liệu đặc tả sẵn có của `payment`, rút ra các bảng dữ liệu: Khách hàng, Đơn hàng, Giao dịch, Phương thức thanh toán. Có chỗ chưa rõ liên hệ giữa "Đơn hàng" và "Giao dịch" là một–một hay một–nhiều, hệ thống hỏi lại — chị Lan trả lời "một đơn có thể phát sinh nhiều giao dịch (trả lần đầu thất bại, trả lại lần hai)".

3. Hệ thống mô tả bằng lời: *"Em sẽ vẽ sơ đồ dữ liệu cho payment: 4 bảng (Khách hàng, Đơn hàng, Giao dịch, Phương thức thanh toán); 4 liên hệ chính (Khách hàng đặt Đơn hàng, Đơn hàng phát sinh Giao dịch, Giao dịch dùng Phương thức thanh toán, Khách hàng sở hữu Phương thức thanh toán). Apply?"* Chị Lan gõ `Y`.

4. Hệ thống ghi sơ đồ vào file `docs/payment/srs/payment-erd.md` — nhúng thẳng, không tạo file ảnh rời.

5. Hệ thống tự vẽ thử ra ảnh. Lần đầu compile được, hệ thống tự mở ảnh ra soi: đủ 4 bảng chưa? — đủ. Các đường có đúng chiều không? — kiểm thấy đường "Khách hàng – Đơn hàng" đang đúng (một khách nhiều đơn), nhưng ghi chú một liên hệ bị wrap dài che mất một góc, hệ thống rút gọn ghi chú rồi vẽ lại cho gọn.

6. Hệ thống báo xong: đã ghi sơ đồ vào `payment-erd.md`, hình vẽ được và đã tự soi. Chị Lan mở file trong VS Code, thấy sơ đồ hiện ra ngay giữa tài liệu — 4 bảng, các dòng thông tin có ghi chú tiếng Việt, cột PK/FK đánh dấu rõ. Chị gửi tài liệu cho dev, dev đọc là hiểu ngay cấu trúc dữ liệu, không cần hỏi thêm.

Vài hôm sau, nghiệp vụ thêm chức năng "phiếu giảm giá". Chị Lan chỉ cần gõ lại `/erd --feature payment` và nói thêm bảng "Phiếu giảm giá" — hệ thống tự hiểu là đang cập nhật sơ đồ cũ, giữ nguyên các bảng đã có, thêm bảng mới, cho chị xem trước phần thay đổi rồi mới ghi đè.

---

## Xem thêm

Tài liệu này chỉ giải thích ý tưởng và luồng chạy ở mức dễ hiểu. Muốn xem đầy đủ chi tiết kỹ thuật (cú pháp Mermaid, cách kiểm tra hình, các bước 1-10, các trường hợp đặc biệt), đọc file gốc: `.claude/skills/erd/SKILL.md`.

Các lệnh cùng họ mô tả dữ liệu:

- `explain-skills/d2-erd.md` — **cùng nội dung như `/erd`, chỉ khác kiểu vẽ** (dùng công cụ D2 thay Mermaid), cho ra một file hình riêng.
- `.claude/skills/dbdiagram/SKILL.md` — sơ đồ dữ liệu **gần với lập trình** (kiểu database thật, xuất SQL), dùng khi bàn giao cho dev.

Các lệnh vẽ sơ đồ khác trong cùng bộ công cụ:

- `explain-skills/sequence.md` — vẽ **cuộc trao đổi giữa nhiều bên theo thời gian** (ai gọi ai, trả về gì).
- `explain-skills/state.md` — vẽ **vòng đời trạng thái** của một đối tượng.

Chọn loại sơ đồ:

- `explain-skills/erd-family.md` — so sánh nhanh cả 3 lệnh vẽ dữ liệu (`/erd`, `/d2-erd`, `/dbdiagram`), giúp chọn đúng cái cần.
- `explain-skills/diagram-selection.md` — bàn chỉ đường cho **mọi loại sơ đồ** (khi chưa biết cần loại nào).
- Quy tắc gốc (bản kỹ thuật, cho máy): `.claude/rules/diagram-selection.md`.
