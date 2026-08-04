---
type: skill-explainer
skill: erd-family
updated: 2026-07-14
---

# Ba lệnh vẽ "sơ đồ dữ liệu" — chọn cái nào?

> Tài liệu này giải thích **mối liên quan** giữa ba lệnh cùng vẽ sơ đồ dữ liệu: `/erd`, `/d2-erd`, `/dbdiagram`. Muốn hiểu sâu từng lệnh, đọc file explainer riêng của nó (liệt kê ở cuối).

## 1. Vì sao lại có tận ba lệnh cho cùng một việc?

Cả ba lệnh đều trả lời cùng một câu hỏi nghiệp vụ: **"tính năng này cần lưu những loại thông tin gì, và các loại thông tin đó gắn với nhau ra sao?"** Kết quả đều là một **sơ đồ dữ liệu** (tên chuyên môn: ERD): mỗi ô là một "bảng" thông tin (Khách hàng, Đơn hàng, Giao dịch...), bên trong liệt kê các mẩu thông tin của bảng đó, và các đường nối cho biết mối liên hệ ("một Khách hàng đặt nhiều Đơn hàng").

Vậy tại sao không gộp làm một? Vì cùng một bức tranh dữ liệu có thể cần **cho ra theo ba cách phục vụ ba nhu cầu khác nhau** — giống như cùng một ngôi nhà, bạn có thể cần bản phác nhanh để bàn với chủ nhà, bản in đẹp để đóng khung, hay bản kỹ thuật chi tiết để giao thợ xây. Mỗi lệnh mạnh ở một chỗ:

- **`/erd`** — vẽ nhanh, **nhúng thẳng vào tài liệu**, tự hiện khi mở (không cần cài công cụ). Cho BA và stakeholder đọc.
- **`/d2-erd`** — **cùng nội dung như `/erd`, chỉ khác kiểu vẽ** (dùng công cụ D2), cho ra một **file ảnh riêng**.
- **`/dbdiagram`** — đi **sâu hơn về kỹ thuật**: kiểu database thật, danh sách lựa chọn, **xuất ra mã SQL** cho dev dựng database.

Điểm cần nhớ ngay: khác biệt giữa ba lệnh nằm ở **hai trục** — **kiểu vẽ** (Mermaid hay D2) và **độ chi tiết** (nghiệp vụ hay gần dev) — chứ **không phải cái nào "đẹp hơn" hay "xịn hơn"**.

---

## 2. Bảng chọn nhanh

Nếu chỉ đọc một phần, đọc bảng này:

```
 CÂU HỎI                                          → CHỌN LỆNH

 Muốn hình dữ liệu HIỆN NGAY trong tài liệu
 (mở trên GitHub / Obsidian là thấy hình luôn,
 không cần cài gì)?                               → /erd  (Mermaid)

 Muốn cùng nội dung đó nhưng là một FILE ẢNH
 RIÊNG (dán slide / gửi email), hoặc muốn thử
 một kiểu vẽ khác cho hợp mắt?                    → /d2-erd  (D2)

 Cần BÀN GIAO cho dev dựng database: kiểu dữ
 liệu thật, danh sách lựa chọn, quy tắc chống
 trùng, và một file SQL chạy được ngay?          → /dbdiagram  (DBML → SQL)
```

Một câu để nhớ: **đọc-trong-tài-liệu → `/erd`; file-ảnh-riêng → `/d2-erd`; bàn-giao-dev-xuất-SQL → `/dbdiagram`.**

---

## 3. So sánh ba lệnh cạnh nhau

Cả ba vẽ **cùng một loại nội dung** (bảng + liên hệ) — khác nhau ở hai chuyện: **vẽ bằng kiểu nào** và **chi tiết tới mức nào**.

| | `/erd` | `/d2-erd` | `/dbdiagram` |
|---|---|---|---|
| **Công cụ vẽ** | Mermaid | D2 | DBML (ngôn ngữ mô tả database) |
| **Khác biệt chính** | Nhúng thẳng vào tài liệu, tự hiện khi mở | Cùng nội dung `/erd`, chỉ khác kiểu vẽ | Đi sâu hơn về kỹ thuật, xuất được SQL |
| **Độ chi tiết** | Mức nghiệp vụ (kiểu gọn: chữ/số/ngày) | Mức nghiệp vụ (như `/erd`) | Gần dev (kiểu database thật, danh sách lựa chọn cố định, quy tắc chống trùng) |
| **Cần cài công cụ?** | Không | Có (công cụ D2) | Có (một công cụ nhỏ để xuất SQL) |
| **Kết quả để ở đâu** | Nhúng trong file dữ liệu của tính năng | File ảnh `.svg` đứng riêng | File `.dbml` (dán lên dbdiagram.io) + file `.sql` cho dev |
| **Ai xem / dùng làm gì** | BA/stakeholder đọc trong tài liệu | Ai thích style này, hoặc cần file ảnh rời | Dev / kỹ sư database triển khai |

> Note: `/dbdiagram` đặt tên theo trang web **dbdiagram.io** (nơi dán file để xem sơ đồ), nhưng file sinh ra có đuôi `.dbml` — vì "DBML" là tên *ngôn ngữ*, còn "dbdiagram.io" là tên *công cụ xem*. Đừng tìm file đuôi `.dbdiagram` — không có.

---

## 4. Hai ranh giới quan trọng — hiểu đúng để chọn không nhầm

Trong họ này có hai chỗ hay bị hiểu sai. Nắm được hai chỗ này là chọn đúng gần như mọi lúc.

**Ranh giới thứ nhất: `/erd` và `/d2-erd` chỉ khác KIỂU VẼ, không cái nào đẹp hơn.** Hai lệnh này cho ra **cùng một nội dung** (cùng các bảng, cùng các liên hệ, cùng độ chi tiết nghiệp vụ) — chỉ khác công cụ vẽ bên dưới (Mermaid với `/erd`, D2 với `/d2-erd`) và **nơi kết quả nằm** (nhúng trong tài liệu với `/erd`, file ảnh riêng với `/d2-erd`). Vì thế đừng chọn `/d2-erd` vì nghĩ "nó xịn hơn" — nó không xịn hơn, chỉ là **một style vẽ khác** để bạn có thêm lựa chọn. Chọn theo: muốn nhúng thẳng, không cài gì → `/erd`; muốn file ảnh rời hoặc thử dàn hình khác → `/d2-erd`.

**Ranh giới thứ hai: `/dbdiagram` khác về ĐỘ CHI TIẾT, không phải kiểu vẽ.** `/dbdiagram` không đơn thuần là "một cách vẽ khác" — nó **đi sâu hơn hẳn**: dùng đúng kiểu dữ liệu thật của database, thêm được danh sách lựa chọn cố định (ví dụ trạng thái đơn chỉ được là "chờ / đã trả / đã huỷ"), quy tắc chống trùng, giá trị mặc định — những thứ `/erd` và `/d2-erd` cố tình không diễn tả. Và nó xuất kèm một file **SQL** để dev dựng database chạy được ngay. Đây là lệnh **gần dev nhất** trong ba anh em.

Từ hai ranh giới đó suy ra một điều quan trọng: **`/dbdiagram` không phải "cái tốt nhất phải luôn dùng".** Với một tính năng nhỏ chỉ có 2-3 bảng mà bạn chỉ muốn thấy nhanh chúng liên hệ ra sao, thì `/erd` là đủ và nhẹ hơn nhiều. `/dbdiagram` chỉ thật sự phát huy khi bạn cần **bàn giao dev, xuất SQL, hoặc mô tả dữ liệu phức tạp**. Chọn theo đúng nhu cầu, đừng chọn theo "cái nào chi tiết nhất".

---

## 5. Ba điểm giống nhau ở cả ba lệnh

Dù khác công cụ và độ chi tiết, cả ba vận hành theo cùng vài nguyên tắc:

1. **Không có nguồn thì không bịa.** Cả ba đều ưu tiên đọc tài liệu sẵn có của tính năng (đặc tả, hoặc sơ đồ dữ liệu đã vẽ trước đó) để rút ra các bảng. Thiếu thông tin → **hỏi bạn** ("có những loại thông tin nào, mỗi loại lưu gì, liên hệ với nhau ra sao"), chứ không tự nghĩ ra bảng hay tự đoán liên hệ. `/d2-erd` và `/dbdiagram` còn tận dụng luôn bản `/erd` đã vẽ trước đó (nếu có) làm nguồn — không bắt bạn mô tả lại từ đầu.

2. **Bạn mô tả nghĩa nghiệp vụ, máy lo phần còn lại.** Cả ba đều **không** hỏi bạn những câu kỹ thuật của dân database ("cột này kiểu gì", "dài bao nhiêu ký tự", "có đánh chỉ mục không"). Bạn chỉ mô tả nghĩa nghiệp vụ ("email là địa chỉ liên hệ", "số tiền là giá đơn"). Ngay cả `/dbdiagram` — dù *tạo ra* thứ chi tiết cho dev — cũng **không bắt bạn phải nghĩ như dev**; nó tự chọn kiểu dữ liệu phù hợp.

3. **Xem trước rồi mới ghi, và tự kiểm trước khi báo xong.** Trước khi ghi, cả ba đều mô tả bằng lời sẽ vẽ gì và chờ bạn gật đầu (file đã có thì cho xem phần thay đổi trước/sau). Sau khi ghi, cả ba đều **tự kiểm**: `/erd` và `/d2-erd` tự vẽ thử ra ảnh (và `/erd` còn tự mở ảnh soi lại để bắt lỗi *vẽ ngược chiều liên hệ* — lỗi mà máy kiểm cú pháp không thấy); còn `/dbdiagram` tự **thử biến bản mô tả thành file SQL** — xuất được SQL sạch nghĩa là mô tả chắc chắn hợp lệ, dev import được ngay.

Một điểm chung nữa: **không xem-và-sửa nhiều vòng trong khung chat.** Cả ba đều dùng "mã chữ" không hiện thành hình trong chat, nên bạn xem hình từ file/web đã xuất ra, thấy cần đổi thì gọi lại lệnh và nói cần sửa gì — hệ thống tự hiểu là đang sửa bản cũ (không tạo trùng).

---

## 6. Ví dụ thực tế — cùng một dữ liệu, ba cách dùng

Anh **Minh**, một BA phụ trách tính năng "flashcard" (thẻ ghi nhớ) của một app học tiếng Anh, trong vòng đời của tính năng gặp ba nhu cầu khác nhau về sơ đồ dữ liệu — và mỗi lần anh chọn một lệnh khác nhau theo đúng nhu cầu:

1. **Lúc viết đặc tả** — anh muốn ghi lại "tính năng lưu những gì" ngay trong tài liệu để dev đọc tài liệu là thấy, không phải mở file ảnh riêng. Anh dùng `/erd`: hình nhúng thẳng vào tài liệu, mở trong VS Code là hiện ra ngay giữa trang, không cần cài gì.

2. **Lúc chuẩn bị họp với ban giám đốc** — anh cần một **file ảnh riêng** để dán vào slide, và muốn thử một kiểu vẽ khác xem có gọn mắt hơn không. Anh dùng `/d2-erd`: nó đọc lại bản `/erd` đã có (không bắt mô tả lại), vẽ ra một file ảnh `.svg` đứng riêng, anh dán thẳng vào slide.

3. **Lúc bàn giao cho dev dựng database** — anh cần đưa cho dev thứ chạy được ngay, và dữ liệu có một danh sách lựa chọn cố định (kết quả ôn thẻ chỉ được là "quên / mơ hồ / đã nhớ"). Anh dùng `/dbdiagram`: nó nâng cấp bản dữ liệu lên mức database thật, xuất ra một file `.dbml` (anh dán lên dbdiagram.io để cả team xem) và một file `.sql` được sinh trực tiếp từ cùng bản `.dbml` (anh gửi thẳng cho dev chạy dựng database, khỏi phải gõ lại theo tài liệu — vừa mất công vừa dễ sai lệch).

Điểm mấu chốt: anh Minh **không** vẽ cùng một thứ ba lần cho phí công. Ba lần dùng ba lệnh là vì ba nhu cầu thật khác nhau — đọc trong tài liệu, dán slide, và bàn giao dev — và ba lệnh phục vụ đúng ba nhu cầu đó. Nhiều bản của cùng một dữ liệu có thể tồn tại song song, không cái nào xoá cái nào.

---

## Xem thêm

Muốn hiểu sâu từng lệnh, đọc file explainer riêng:

- `explain-skills/erd.md` — `/erd` (Mermaid, nhúng thẳng vào tài liệu, cho BA/stakeholder đọc).
- `explain-skills/d2-erd.md` — `/d2-erd` (D2, cùng nội dung `/erd` nhưng khác kiểu vẽ, file ảnh riêng).
- `explain-skills/dbdiagram.md` — `/dbdiagram` (DBML, gần dev nhất, xuất SQL, chia sẻ trên dbdiagram.io).

Quy tắc chọn diagram đầy đủ (cho mọi loại sơ đồ, không chỉ dữ liệu) nằm ở:

- `explain-skills/diagram-selection.md` — bàn chỉ đường chọn loại sơ đồ (bản cho người).
- `.claude/rules/diagram-selection.md` — quy tắc gốc (bản kỹ thuật, cho máy).
