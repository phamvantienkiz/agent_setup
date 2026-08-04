---
type: skill-explainer
skill: dbdiagram
updated: 2026-07-14
---

# `/dbdiagram` là gì và nó chạy như thế nào?

## 1. Dùng để làm gì, khi nào nên gõ lệnh này

`/dbdiagram` cũng vẽ **sơ đồ dữ liệu** (bức tranh "tính năng này lưu những loại thông tin gì, gắn với nhau ra sao") — giống `/erd` và `/d2-erd`. Nhưng nó là **anh em gần dev nhất** trong ba lệnh: kết quả nó tạo ra không chỉ để nhìn, mà còn để **bàn giao thẳng cho lập trình viên dựng cơ sở dữ liệu thật**.

Hãy hình dung ba mức độ của cùng một bức tranh dữ liệu:

- `/erd` — bản vẽ **để đọc trong tài liệu** (kiểu vẽ Mermaid, nhúng thẳng), đủ cho BA và stakeholder hiểu.
- `/d2-erd` — **cùng nội dung như `/erd`, chỉ là một kiểu vẽ khác** (dùng công cụ D2), cho ra một file hình riêng.
- `/dbdiagram` — bản vẽ **để dev dựng database** — chi tiết tới mức kiểu dữ liệu thật của cơ sở dữ liệu, kèm một file "mã lệnh tạo bảng" (SQL) mà dev có thể chạy để tạo ngay cấu trúc dữ liệu.

Điểm đặc trưng của `/dbdiagram`: nó tạo ra một file theo một ngôn ngữ mô tả cơ sở dữ liệu tên là **DBML**, mà bạn có thể **mang lên một trang web tên dbdiagram.io** (hoặc dbdocs.io) — dán vào đó là ra ngay sơ đồ trực quan trên web, có thể chia sẻ link cho cả team. Đồng thời nó xuất kèm một file **SQL** — chính là "công thức tạo bảng" để dev dựng database thật.

Vài tình huống điển hình nên dùng `/dbdiagram`:

- Bạn cần **bàn giao cấu trúc dữ liệu cho dev** để họ dựng database — muốn đưa cho họ thứ import chạy được ngay, không phải tự gõ lại.
- Tính năng có dữ liệu phức tạp — nhiều **danh sách lựa chọn cố định** (ví dụ trạng thái đơn chỉ được là "chờ / đã trả / đã huỷ") hoặc cần đánh dấu những **quy tắc chống trùng lặp** — mà hai lệnh kia không diễn tả được.
- Bạn muốn một sơ đồ dữ liệu **chia sẻ trên web** (qua dbdiagram.io / dbdocs.io) để cả team cùng xem, cùng bình luận.

Gõ lệnh đơn giản như:

```
/dbdiagram --feature flashcard
```

**Một câu để nhớ:** `/dbdiagram` là bản vẽ dữ liệu **gần dev nhất** — chi tiết tới mức database thật, kèm file mã lệnh tạo bảng (SQL), và xem/chia sẻ được trên web dbdiagram.io.

---

## 2. Toàn bộ luồng chạy — sơ đồ

```
 BẠN GÕ LỆNH
 /dbdiagram --feature X
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 0 — Kiểm tra công cụ đã cài chưa                  │
 │  Hệ thống cần một công cụ nhỏ (@dbml/cli) cài sẵn     │
 │  trên máy để kiểm và xuất file SQL. Chưa có → DỪNG    │
 │  ngay, chỉ bạn 1 dòng lệnh cài. Không làm dở dang.    │
 └──────────────────────────────────────────────────────┘
        │  (đã có công cụ → đi tiếp)
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 1 — Xác định đang làm cho tính năng nào           │
 │  Đọc yêu cầu của bạn, xác định tính năng. Tính năng   │
 │  chưa có → tự đặt tên rồi tạo mới (không bắt bạn      │
 │  phải chuẩn bị bước nào trước).                       │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 2 — Lấy "bức tranh dữ liệu" cho đúng              │
 │  Ưu tiên đọc lại sơ đồ dữ liệu sẵn có (nếu trước đó   │
 │  đã vẽ bằng /erd) và nâng cấp lên mức database thật.  │
 │  Không có thì đọc đặc tả. Vẫn không có → HỎI bạn có   │
 │  những loại thông tin nào, lưu gì, liên hệ ra sao.    │
 │  KHÔNG tự bịa bảng.                                   │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 3 — Xem trước rồi mới ghi (xin phép)              │
 │  Hệ thống mô tả bằng lời thường: "sẽ tạo N bảng, M    │
 │  liên hệ, và các danh sách lựa chọn / quy tắc chống   │
 │  trùng (nếu có)". Bạn gật (Y) mới làm.                │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 4 — Ghi file + KIỂM bằng cách xuất SQL thật       │
 │  Hệ thống viết file mô tả (DBML), rồi nhờ công cụ thử │
 │  BIẾN NÓ THÀNH FILE SQL. Nếu ra được SQL nghĩa là mô  │
 │  tả hợp lệ, dev import được. Ra lỗi → tự sửa, thử     │
 │  lại. Chỉ báo XONG khi xuất được SQL sạch.            │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 5 — Báo hoàn tất                                  │
 │  Cho bạn 2 file: bản mô tả (.dbml) để dán lên         │
 │  dbdiagram.io xem sơ đồ, và file .sql để dev tạo DB.  │
 │  Ghi lại vào sổ theo dõi tính năng.                   │
 └──────────────────────────────────────────────────────┘
        │
        ▼
     HOÀN TẤT — có bản mô tả để xem trên web + file SQL cho dev
```

---

## 3. Hai file bạn nhận được — dùng chúng thế nào?

`/dbdiagram` không nhúng hình vào tài liệu như `/erd`, cũng không tạo file ảnh như `/d2-erd`. Nó tạo ra **hai file có thể đem đi dùng thật**, và đây là cách bạn (hoặc dev) dùng chúng:

**File thứ nhất — bản mô tả (đuôi `.dbml`).**
Đây là "bản gốc" viết bằng ngôn ngữ mô tả cơ sở dữ liệu (DBML). Bản thân nó là văn bản, chưa phải hình. Cách xem thành hình: bạn mở trang web **dbdiagram.io**, **dán toàn bộ nội dung file này vào** — trang web lập tức vẽ ra sơ đồ, có thể phóng to thu nhỏ, chia sẻ link cho cả team. (Hoặc đưa lên dbdocs.io để làm thành một trang tài liệu database có thể bình luận.) Muốn sửa sau này, bạn sửa file `.dbml` này rồi dán lại.

**File thứ hai — mã lệnh tạo bảng (đuôi `.sql`).**
Đây là file dành cho **dev**. Nó chính là "công thức" để máy tính tạo ra cấu trúc dữ liệu thật trong database. Dev cầm file này chạy vào hệ quản trị cơ sở dữ liệu là ra ngay các bảng đúng như mô tả — không phải ngồi gõ lại từ đầu theo tài liệu (vừa mất công vừa dễ sai lệch so với tài liệu).

> **Một điểm dễ nhầm, nói rõ luôn:** tên lệnh là `/dbdiagram` (đặt theo tên trang web dbdiagram.io cho dễ nhớ), nhưng file sinh ra có đuôi `.dbml` — vì "DBML" mới là tên *ngôn ngữ*, còn "dbdiagram.io" là tên *công cụ xem*. Đừng tìm file đuôi `.dbdiagram` — không có.

---

## 4. Vì sao lệnh này ĐƯỢC đi sâu vào kỹ thuật database, mà các lệnh kia thì không?

Đây là điểm cần giải thích rõ để bạn hiểu đúng vai trò của lệnh.

Trong bộ tài liệu này có một nguyên tắc chung: các lệnh dành cho BA thường **giữ mọi thứ ở mức nghiệp vụ**, không sa đà vào chi tiết kỹ thuật của database. `/erd` và `/d2-erd` tuân đúng vậy — chúng ghi thông tin ở mức gọn, dễ hiểu.

Nhưng `/dbdiagram` **cố tình khác**: vì mục đích của nó là **bàn giao cho dev dựng database thật**, nên nó *phải* đi sâu hơn — dùng đúng kiểu dữ liệu thật của database, thêm được **danh sách lựa chọn cố định** (ví dụ trạng thái đơn chỉ được là một trong "chờ / đã trả / đã huỷ", không được giá trị lạ), thêm được các **quy tắc chống trùng lặp** và **giá trị mặc định**. Đây không phải lệch vai — đây chính là lý do lệnh này tồn tại: nó là tầng gần dev nhất, nên được phép chi tiết như dev cần.

Tuy vậy, có một chỗ nó vẫn **giữ nguyên tắc BA**: nó **không bắt bạn trả lời những câu kỹ thuật của dân database** (kiểu "cột này dùng kiểu dữ liệu gì", "dài bao nhiêu ký tự"). Bạn chỉ cần mô tả nghĩa nghiệp vụ — ví dụ "email là địa chỉ liên hệ", "số tiền là giá đơn hàng" — còn việc **tự chọn kiểu dữ liệu phù hợp cho database** thì hệ thống tự lo. Nói cách khác: nó *tạo ra* thứ chi tiết-cho-dev, nhưng *không bắt bạn phải nghĩ như dev*.

---

## 5. Vì sao "xuất được file SQL mới báo xong"? (Bước 4)

Đây là cách `/dbdiagram` tự kiểm tra chất lượng, và nó khác một chút so với cách các lệnh vẽ hình khác tự kiểm.

Các lệnh vẽ hình (`/erd`, `/d2-erd`) tự kiểm bằng cách "vẽ thử ra ảnh xem có ra hình không". Còn `/dbdiagram` tự kiểm bằng cách **thử biến bản mô tả thành file SQL thật**. Lý do: nếu bản mô tả có chỗ nào sai (ví dụ một bảng trỏ tới một bảng khác không tồn tại, hoặc quên khai báo một danh sách lựa chọn trước khi dùng nó), thì công cụ sẽ **không xuất ra được SQL** — nó báo lỗi ngay.

Đây là một phép thử rất đáng tin: **xuất ra được SQL sạch nghĩa là bản mô tả chắc chắn hợp lệ, và dev import vào database được ngay** — chứ không phải "trông có vẻ đúng nhưng lúc dev thử mới phát hiện sai". Nếu lần thử đầu bị lỗi, hệ thống tự đọc lỗi, sửa lại bản mô tả, thử lại vài lần. Nó chỉ báo "hoàn tất" khi đã xuất được SQL sạch.

Giống như đầu bếp không chỉ nhìn công thức rồi bảo "chắc ngon", mà **nấu thử một mẻ** để chắc chắn công thức chạy được trước khi giao cho bếp chính.

Một điều `/dbdiagram` **không** làm: nó không có kiểu "sửa tới sửa lui nhiều vòng ngay trong khung chat" — vì bản mô tả không hiện thành hình trong chat. Bạn xem hình bằng cách dán file `.dbml` lên dbdiagram.io. Muốn chỉnh, bạn gọi lại lệnh với yêu cầu thay đổi — hệ thống tự hiểu là đang sửa bản cũ, cho bạn xem phần thay đổi rồi ghi lại + xuất SQL mới.

---

## 6. Ba anh em cùng vẽ "bức tranh dữ liệu" — chọn cái nào?

`/dbdiagram` là một trong ba lệnh cùng mô tả dữ liệu của một tính năng. Chúng khác nhau ở **ai xem và dùng để làm gì** — đây là cách phân biệt cho dễ nhớ:

Cả ba vẽ **cùng một loại nội dung** (bảng + liên hệ) — khác nhau ở **vẽ bằng kiểu nào** và **chi tiết tới mức nào**.

| Lệnh | Khác biệt chính | Ai xem / dùng làm gì |
|---|---|---|
| **`/erd`** | Kiểu vẽ Mermaid — **nhúng thẳng vào tài liệu**, tự hiện khi mở, không cần cài công cụ | BA/stakeholder đọc trong tài liệu |
| **`/d2-erd`** | **Cùng nội dung như `/erd`, chỉ khác kiểu vẽ** (công cụ D2 thay Mermaid) — cho ra một file hình riêng | ai thích style vẽ này hơn, hoặc cần file hình tách khỏi tài liệu |
| **`/dbdiagram`** (lệnh này) | Đi **sâu hơn về kỹ thuật** — kiểu database thật, danh sách lựa chọn, quy tắc chống trùng, **xuất ra mã SQL** để dev dựng database; xem/chia sẻ trên dbdiagram.io | dev / kỹ sư database triển khai |

Cách chọn nhanh:

- Chỉ cần thấy nhanh dữ liệu liên hệ ra sao trong tài liệu → `/erd` (hoặc `/d2-erd` nếu bạn thích kiểu vẽ đó hơn — hai cái chỉ khác style vẽ, không cái nào hơn cái nào).
- Cần **bàn giao cho dev, xuất SQL, hoặc chia sẻ sơ đồ trên web** (nhất là khi dữ liệu có nhiều danh sách lựa chọn / quy tắc chống trùng) → dùng `/dbdiagram` (lệnh này) — đây là khác biệt về *độ chi tiết*, không phải kiểu vẽ.

**Một lưu ý trung thực:** `/dbdiagram` không phải "cái xịn nhất phải luôn dùng". Với tính năng nhỏ chỉ có 2-3 bảng và bạn chỉ muốn thấy nhanh chúng liên hệ ra sao, thì `/erd` là đủ và nhẹ hơn. `/dbdiagram` chỉ thật sự phát huy khi bạn cần **bàn giao dev, xuất SQL, hoặc mô tả dữ liệu phức tạp** (nhiều danh sách lựa chọn, quy tắc chống trùng, giá trị mặc định) mà hai lệnh kia không diễn tả được. Chọn theo đúng nhu cầu, đừng chọn theo "cái nào chi tiết nhất".

---

## 7. Ví dụ thực tế

Anh **Minh**, một BA phụ trách tính năng "flashcard" (thẻ ghi nhớ) của một app học tiếng Anh, vừa hoàn thiện phần mô tả nghiệp vụ và cần **bàn giao cấu trúc dữ liệu cho đội dev** để họ bắt đầu dựng database. Anh muốn đưa cho dev thứ import chạy được ngay, đồng thời có một sơ đồ trên web để cả team cùng xem.

Anh Minh mở terminal, gõ:

```
/dbdiagram --feature flashcard
```

1. Hệ thống kiểm tra trước: công cụ cần thiết đã cài trên máy chưa? Có rồi — đi tiếp. (Nếu chưa, nó đã dừng ngay và đưa anh Minh một dòng lệnh cài đặt.)

2. Hệ thống nhận ra đây là tính năng `flashcard`, và tìm thấy trước đó anh đã vẽ một sơ đồ dữ liệu bằng `/erd`. Nó đọc lại bản đó và **nâng cấp lên mức database thật** — không bắt anh mô tả lại từ đầu. Trong lúc đọc, nó thấy tính năng có "kết quả ôn thẻ" chỉ được là một trong ba giá trị (quên / mơ hồ / đã nhớ), nên chuẩn bị tạo một danh sách lựa chọn cố định cho nó.

3. Hệ thống mô tả bằng lời thường: *"Em sẽ tạo schema database cho flashcard: 4 bảng (người dùng, bộ thẻ, thẻ, lượt ôn thẻ); 3 liên hệ chính; 1 danh sách lựa chọn cho kết quả ôn (quên / mơ hồ / đã nhớ); 1 quy tắc tra nhanh theo thẻ + thời gian ôn. Apply?"* Anh Minh gõ `Y`.

4. Hệ thống viết file mô tả (DBML), rồi thử biến nó thành file SQL để kiểm. Lần đầu bị lỗi nhỏ (danh sách lựa chọn "kết quả ôn" chưa được khai báo trước khi dùng) — hệ thống tự đọc lỗi, sửa lại, thử lại. Lần này xuất ra file SQL sạch, nghĩa là mô tả hợp lệ.

5. Hệ thống báo xong, đưa anh Minh hai file: `docs/flashcard/dbdiagram/flashcard.dbml` (bản mô tả) và `flashcard.sql` (mã lệnh tạo bảng). Anh Minh mở trang dbdiagram.io, dán nội dung file `.dbml` vào — sơ đồ hiện ra ngay, anh copy link chia sẻ cho cả team xem. Còn file `.sql` anh gửi thẳng cho dev; dev chạy nó là dựng xong cấu trúc database, khớp 100% với tài liệu.

Vài hôm sau, nghiệp vụ thêm tính năng "gắn nhãn cho bộ thẻ". Anh Minh chỉ cần gõ lại `/dbdiagram --feature flashcard` và nói thêm bảng "Nhãn" — hệ thống tự hiểu là đang cập nhật bản cũ, cho anh xem trước phần thay đổi, ghi lại và xuất file SQL mới.

---

## Xem thêm

Tài liệu này chỉ giải thích ý tưởng và luồng chạy ở mức dễ hiểu. Muốn xem đầy đủ chi tiết kỹ thuật (công thức viết DBML, cách xuất SQL, các trường hợp đặc biệt), đọc file gốc: `.claude/skills/dbdiagram/SKILL.md`.

Các lệnh cùng họ mô tả dữ liệu:

- `explain-skills/erd.md` — vẽ sơ đồ dữ liệu **nhúng thẳng vào tài liệu** để GitHub/Obsidian tự hiện (nhẹ, cho BA đọc).
- `explain-skills/d2-erd.md` — **cùng nội dung như `/erd`, chỉ khác kiểu vẽ** (dùng công cụ D2 thay Mermaid), cho ra một file hình riêng.

Các lệnh vẽ sơ đồ khác trong cùng bộ công cụ:

- `explain-skills/sequence.md` — vẽ **cuộc trao đổi giữa nhiều bên theo thời gian**.
- `explain-skills/state.md` — vẽ **vòng đời trạng thái** của một đối tượng.

Chọn loại sơ đồ:

- `explain-skills/erd-family.md` — so sánh nhanh cả 3 lệnh vẽ dữ liệu (`/erd`, `/d2-erd`, `/dbdiagram`), giúp chọn đúng cái cần.
- `explain-skills/diagram-selection.md` — bàn chỉ đường cho **mọi loại sơ đồ** (khi chưa biết cần loại nào).
- Quy tắc gốc (bản kỹ thuật, cho máy): `.claude/rules/diagram-selection.md`.
