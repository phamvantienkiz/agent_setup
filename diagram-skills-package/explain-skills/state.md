---
type: skill-explainer
skill: state
updated: 2026-07-14
---

# `/state` là gì và nó chạy như thế nào?

## 1. Dùng để làm gì, khi nào nên gõ lệnh này

`/state` vẽ ra **sơ đồ trạng thái** cho một "đối tượng" trong hệ thống của bạn — thứ mà trong nghề gọi là *state diagram*. Nghe hơi lạ, nhưng ý tưởng rất đời thường: nhiều thứ trong phần mềm **đi qua nhiều giai đoạn (trạng thái) khác nhau trong vòng đời của nó**, và sơ đồ trạng thái vẽ ra đủ các giai đoạn đó cùng với việc "đi từ giai đoạn này sang giai đoạn kia thì cần chuyện gì xảy ra".

Ví dụ cho dễ hình dung:

- Một **tài khoản** người dùng: mới đăng ký thì *chưa xác thực* → bấm link xác thực email thì thành *đã xác thực* → nhập sai mật khẩu 5 lần thì bị *khoá* → sau 24 giờ tự *mở khoá*. Mỗi cụm chữ nghiêng đó là một trạng thái.
- Một **đơn hàng**: *chờ thanh toán* → *đã thanh toán* → *đang giao* → *đã giao* → (hoặc) *đã huỷ*.
- Một **gói cước**: *dùng thử* → *đang hoạt động* → *hết hạn* → *gia hạn*.

Điểm hay của việc vẽ sơ đồ này: nó **ép bạn (và cả nhóm) phải nghĩ cho hết** — đối tượng này có tất cả bao nhiêu trạng thái, đi từ trạng thái nào sang trạng thái nào được, **cái gì kích hoạt** mỗi lần chuyển (bấm nút? hết giờ? admin duyệt?), và quan trọng nhất là **những đường chuyển KHÔNG được phép** (ví dụ đơn *đã thanh toán* thì tuyệt đối không được tự quay về *chờ thanh toán*). Những đường cấm này rất hay bị bỏ sót khi chỉ mô tả bằng lời — vẽ ra thì lộ ngay.

Vài tình huống điển hình nên dùng `/state`:

- Bạn có một đối tượng (tài khoản, đơn hàng, phiếu yêu cầu, gói cước, phiên đăng nhập...) đi qua **từ 3 trạng thái trở lên**. (Nếu chỉ có 2 trạng thái kiểu bật/tắt thì một câu chữ là đủ, không cần vẽ.)
- Bạn muốn ghi rõ **quy tắc chuyển trạng thái** để dev và tester không hiểu sai (khi nào được chuyển, khi nào cấm).

Gõ lệnh đơn giản như:

```
/state Account --feature auth
```

(nghĩa là: vẽ sơ đồ trạng thái cho đối tượng "Account" — tài khoản — thuộc tính năng "auth").

**Một câu để nhớ:** `/state` vẽ **vòng đời của một đối tượng** — nó đi qua những trạng thái nào, chuyển giữa các trạng thái nhờ chuyện gì, và đường nào bị cấm — để cả nhóm nghĩ cho hết và không hiểu sai.

---

## 2. Toàn bộ luồng chạy — sơ đồ

```
 BẠN GÕ LỆNH
 /state Account --feature auth
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 1 — Xác định đối tượng + tính năng                │
 │  Hiểu bạn đang vẽ cho đối tượng nào (Account),        │
 │  thuộc tính năng nào (auth). Tính năng chưa có →       │
 │  tự đặt tên rồi tạo mới, không bắt làm bước gì trước. │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 2 — Gom thông tin trạng thái                      │
 │  Đọc tài liệu sẵn có của tính năng (ghi chú ý tưởng,  │
 │  bản đặc tả) để lấy sẵn các trạng thái + quy tắc.     │
 │  Thiếu hoặc mô tả mập mờ → HỎI bạn, KHÔNG tự bịa.     │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 3 — Kiểm tra "có đáng vẽ không"                   │
 │  Dưới 3 trạng thái → nhắc "bảng chữ có khi đủ rồi,    │
 │  vẫn muốn vẽ chứ?" — chờ bạn quyết.                   │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 4 — Xem trước rồi mới vẽ (xin phép)               │
 │  Mô tả bằng lời: "sẽ vẽ N trạng thái, M đường         │
 │  chuyển, K đường cấm". Bạn gật (Y) mới làm tiếp.      │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 5 — Ghi sơ đồ vào tài liệu                        │
 │  Thêm một mục mới cho đối tượng này vào file trạng     │
 │  thái chung của tính năng. Kèm một bảng riêng liệt kê │
 │  các đường chuyển bị CẤM.                             │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 6 — Tự soi lại hình + đối chiếu cho đủ            │
 │  Vẽ thử ra ảnh, TỰ MỞ ẢNH RA XEM (mũi tên đúng chiều  │
 │  chưa? trạng thái nào bị lơ lửng không?), rồi đối     │
 │  chiếu lại: đủ trạng thái + đủ đường chuyển chưa?     │
 │  Thiếu/sai → tự sửa, làm lại. Chỉ báo xong khi ổn.    │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 7 — Báo hoàn tất                                  │
 │  Cho biết đã thêm sơ đồ vào file nào, mở bằng trình   │
 │  soạn tài liệu (IDE/Obsidian/GitHub) là thấy hình.    │
 └──────────────────────────────────────────────────────┘
        │
        ▼
     HOÀN TẤT — file trạng thái có thêm một sơ đồ mới
```

---

## 3. Ba thứ quan trọng nhất mà sơ đồ này bắt bạn nghĩ cho hết

Đây là lý do thật sự khiến `/state` đáng dùng — không phải để có cái hình cho vui, mà để **không bỏ sót**.

**Thứ nhất — đủ trạng thái chưa?** Rất hay có chuyện: khi mô tả bằng lời, người ta chỉ kể vài trạng thái "chính" (chờ, xong) mà quên các trạng thái "phụ" nhưng quan trọng (đang xử lý, bị từ chối, hết hạn). Vẽ ra thành sơ đồ thì những khoảng trống lộ ngay — "ủa, từ *đang giao* mà giao thất bại thì đơn về đâu?".

**Thứ hai — cái gì kích hoạt mỗi lần chuyển?** Mỗi mũi tên trong sơ đồ đều có một cái nhãn ghi rõ **chuyện gì làm nó chuyển**: người dùng bấm nút, hệ thống hết giờ chờ, admin duyệt, thanh toán thành công... Bắt buộc phải điền nhãn này nghĩa là bắt bạn trả lời câu "tại sao lại chuyển", chứ không để mập mờ.

**Thứ ba — đường nào bị CẤM?** Đây là phần nhiều công cụ khác bỏ qua nhưng `/state` làm hẳn **một bảng riêng**. Nó liệt kê những đường chuyển **không được phép xảy ra** và lý do — ví dụ "đơn *đã thanh toán* → *chờ thanh toán*: không được, vì đã trả tiền rồi không thể lùi về chưa trả". Những quy tắc cấm này chính là chỗ hệ thống hay bị lỗi nếu dev không biết — ghi rõ ra là để phòng ngừa.

> **Vì sao đường cấm để riêng thành bảng, không vẽ vào hình?** Vì nếu vẽ cả đường được-phép lẫn đường-bị-cấm vào cùng một hình thì rối và dễ đọc nhầm (tưởng đường cấm là đường đi được). Nên hình chỉ vẽ đường được phép; đường cấm nằm gọn trong một bảng bên dưới, đọc rõ ràng.

---

## 4. Kết quả để ở đâu? Vì sao gom chung một file?

`/state` **không tạo file mới lẻ tẻ cho mỗi đối tượng.** Thay vào đó, mọi sơ đồ trạng thái của cùng một tính năng được **gom hết vào một file chung** (tên có dạng `...-states.md`), mỗi đối tượng là một mục riêng trong file đó.

Ví dụ tính năng "auth" có thể có sơ đồ trạng thái cho *Account* (tài khoản) và cho *VerifyLink* (link xác thực) — cả hai nằm chung một file, mỗi cái một mục. Lần sau bạn vẽ thêm một đối tượng nữa, nó lại thêm một mục vào đúng file đó.

Lý do gom chung: các sơ đồ trạng thái của một tính năng thường liên quan nhau, để chung một chỗ thì dễ đọc cả bộ, dễ tìm, không phải mở chục file rời rạc. Nếu bạn vẽ lại cho một đối tượng **đã có sẵn** trong file, hệ thống tự hiểu là đang **cập nhật mục cũ** — nó sẽ cho bạn xem trước phần thay đổi (dạng so sánh trước/sau) rồi mới ghi đè.

Hình được vẽ bằng một công cụ tên **Mermaid**. Điểm tiện: loại hình này **hiện thẳng ra khi bạn mở file** trên các công cụ phổ biến (trình soạn code, Obsidian, GitHub) — không cần cài thêm gì, không cần xuất file ảnh riêng.

---

## 5. Vì sao "tự mở ảnh ra soi" và "đối chiếu cho đủ"?

Hai bước kiểm tra ở cuối là phần khiến bạn yên tâm rằng "báo xong" nghĩa là thật sự ổn, chứ không phải xong nửa vời.

**Tự mở ảnh ra soi.** Sau khi ghi sơ đồ, hệ thống **tự vẽ thử ra ảnh và tự mở ảnh đó ra nhìn** — kiểm những lỗi mà chỉ nhìn hình mới thấy: có trạng thái nào bị **lơ lửng** (không có đường nào dẫn vào hoặc dẫn ra) không? mũi tên có **đúng chiều** không (vẽ *Khoá → Đã xác thực* trong khi ý là ngược lại là sai)? các nhãn có bị **đè lên nhau, mất chữ** không? Thấy lỗi thì tự sửa rồi vẽ lại. Lý do phải làm vậy: loại hình này không hiện được trong khung chat, nên nếu không tự soi thì lỗi sẽ để lại cho bạn tự phát hiện lúc mở file — trễ và mất công.

**Đối chiếu cho đủ.** Đây là một bước kiểm tra **khác** với việc soi ảnh: trước khi vẽ, hệ thống đã lập sẵn một danh sách "phải có những trạng thái này, những đường chuyển này". Sau khi vẽ xong, nó **soát lại từng cái** — mỗi trạng thái trong danh sách có xuất hiện thành một ô chưa? mỗi đường chuyển có đủ nhãn kích hoạt chưa? Thiếu cái nào thì bổ sung. Vì một sơ đồ có thể "vẽ ra không lỗi" nhưng vẫn **thiếu một trạng thái** so với ý ban đầu — soi ảnh không bắt được lỗi thiếu này, nên cần bước đối chiếu riêng.

Một điều `/state` **không** làm: nó không có kiểu "vẽ ra rồi sửa tới sửa lui nhiều vòng ngay trong khung chat". Bản mô tả không hiện thành hình trong chat, nên bạn xem hình từ file. Muốn chỉnh, gọi lại lệnh và nói cần đổi gì — hệ thống tự hiểu là đang sửa bản cũ.

---

## 6. Điều `/state` sẽ KHÔNG hỏi bạn (và vì sao)

`/state` phục vụ người phân tích nghiệp vụ (BA), không phải lập trình viên. Nên khi cần thêm thông tin, nó chỉ hỏi bằng **ngôn ngữ nghiệp vụ**:

- Đối tượng này đi qua **những trạng thái nào**?
- **Chuyện gì** làm nó chuyển từ trạng thái này sang trạng thái kia?
- Có đường chuyển nào **bị cấm** không?

Nó **sẽ không hỏi** những thứ thuộc về kỹ thuật lưu trữ hay lập trình — ví dụ trạng thái lưu vào cột nào trong cơ sở dữ liệu, kiểu dữ liệu gì, tên hàm xử lý ra sao. Đó là việc của bước đặc tả kỹ thuật và của dev, không phải việc bạn phải bận tâm khi vẽ sơ đồ trạng thái. Bạn chỉ cần trả lời được "vòng đời nghiệp vụ" là đủ.

Một quy tắc nhỏ nhưng hữu ích: nếu bạn bảo "vẽ sơ đồ trạng thái này nhét luôn vào use case X đi", hệ thống sẽ **từ chối khéo** và giải thích — vì một đối tượng (như tài khoản) thường được dùng chung ở nhiều chỗ, nên sơ đồ trạng thái của nó phải để ở file trạng thái chung, không nhét riêng vào một use case.

---

## 7. Ví dụ thực tế

Chị **Lan**, một BA phụ trách tính năng đăng nhập (`auth`), vừa họp xong và nhận ra: đối tượng "tài khoản" trong hệ thống thực ra phức tạp hơn chị tưởng — nó có tới mấy trạng thái và vài quy tắc cấm mà nếu không ghi rõ, dev rất dễ làm sai. Chị quyết định vẽ một sơ đồ trạng thái cho nó.

Chị Lan mở terminal, gõ:

```
/state Account --feature auth
```

1. Hệ thống hiểu chị đang vẽ cho đối tượng "Account" thuộc tính năng "auth". Tính năng này đã có tài liệu sẵn, nên nó đọc qua để lấy thông tin.

2. Từ ghi chú ý tưởng, hệ thống thấy nhắc tới các trạng thái *chưa xác thực*, *đã xác thực*, *bị khoá* — nhưng phần "khi nào tự mở khoá" thì mô tả mập mờ. Nó **hỏi lại**: *"Tài khoản bị khoá thì mở lại bằng cách nào — admin mở tay hay tự mở sau một khoảng thời gian?"* Chị Lan trả lời: *"Tự mở sau 24 giờ, không cần admin."* — nhờ hỏi mà không bịa sai.

3. Đối tượng này có 3 trạng thái, đủ để vẽ (không bị nhắc "bảng chữ có khi đủ rồi").

4. Hệ thống mô tả bằng lời: *"Em sẽ thêm sơ đồ trạng thái cho Account: 3 trạng thái (Chưa xác thực, Đã xác thực, Bị khoá), 4 đường chuyển, 1 đường cấm (đã xác thực không được quay về chưa xác thực). Apply?"* Chị Lan gõ `Y`.

5. Hệ thống thêm một mục mới "Account" vào file trạng thái chung của tính năng auth, kèm một bảng liệt kê đường cấm.

6. Nó tự vẽ thử ra ảnh và **tự mở ra soi**: mũi tên *Bị khoá → Đã xác thực* (tự mở khoá sau 24h) đúng chiều chưa? có trạng thái nào lơ lửng không? — ổn. Rồi nó **đối chiếu lại danh sách**: đủ 3 trạng thái, đủ 4 đường chuyển, mỗi đường có nhãn kích hoạt. Đủ cả.

7. Hệ thống báo xong, cho biết đã thêm sơ đồ vào file `docs/auth/srs/auth-states.md`, mục "Account". Chị Lan mở file trong trình soạn tài liệu, thấy sơ đồ hiện ra rõ ràng — kèm bảng đường cấm bên dưới. Chị gửi cho dev, dev đọc hiểu ngay quy tắc "tài khoản đã xác thực không được lùi về chưa xác thực", không cần hỏi lại.

Tuần sau, hệ thống bổ sung tính năng "tạm ngưng tài khoản". Chị Lan chỉ cần gõ lại `/state Account --feature auth` và nói thêm trạng thái mới — hệ thống tự hiểu là đang cập nhật sơ đồ cũ, cho chị xem trước phần thay đổi rồi mới ghi.

---

## Xem thêm

Tài liệu này chỉ giải thích ý tưởng và luồng chạy ở mức dễ hiểu. Muốn xem đầy đủ chi tiết kỹ thuật (cú pháp Mermaid, cách kiểm tra hình, các trường hợp đặc biệt), đọc file gốc: `.claude/skills/state/SKILL.md`.

Các lệnh vẽ sơ đồ khác trong cùng bộ công cụ:

- `explain-skills/activity-family.md` — nhóm lệnh vẽ **sơ đồ quy trình** (từng bước một việc chạy thế nào). Khác `/state`: sơ đồ quy trình vẽ *dòng chảy công việc*, còn `/state` vẽ *vòng đời trạng thái của một đối tượng*.
- Quy tắc chọn loại sơ đồ đầy đủ (khi nào dùng sơ đồ trạng thái, khi nào dùng loại khác) nằm ở file gốc: `.claude/rules/diagram-selection.md`.
