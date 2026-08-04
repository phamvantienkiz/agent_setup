---
type: skill-explainer
skill: sequence
updated: 2026-07-14
---

# `/sequence` là gì và nó chạy như thế nào?

## 1. Dùng để làm gì, khi nào nên gõ lệnh này

`/sequence` là lệnh vẽ **sơ đồ tuần tự** (sequence diagram) — một loại hình mô tả **ai nói chuyện với ai, theo thứ tự thời gian nào** trong một luồng nghiệp vụ.

Hãy hình dung nó giống như **kịch bản một cuộc trao đổi**: có mấy "nhân vật" đứng thành cột dọc trên đầu hình (ví dụ: Khách, Màn hình, Hệ thống, Cổng thanh toán Momo), rồi từng mũi tên ngang chỉ ra "người này gửi gì cho người kia" — đọc từ trên xuống dưới đúng theo thứ tự việc xảy ra. Ai gọi trước, ai trả lời sau, chỗ nào rẽ nhánh (thành công thì thế này, lỗi thì thế kia) — tất cả hiện rõ theo trục thời gian.

Vài tình huống điển hình nên dùng `/sequence`:

- Bạn muốn mô tả một luồng **có nhiều bên trao đổi qua lại** — ví dụ luồng đăng nhập (Khách → Màn hình → Hệ thống → kiểm tra rồi trả kết quả về), luồng thanh toán (có thêm cổng thanh toán bên ngoài), luồng nhận thông báo từ đối tác (webhook).
- Luồng có **thứ tự rõ ràng theo thời gian** và bạn muốn người đọc thấy được "bước nào xảy ra trước, bước nào sau".
- Luồng có **nhánh rẽ khi lỗi** — ví dụ "nếu thanh toán thành công thì hiện trang cảm ơn, nếu thất bại/hết giờ thì hiện thông báo lỗi".

Gõ lệnh đơn giản như:

```
/sequence "khách bấm thanh toán, hệ thống gọi cổng Momo, Momo báo kết quả về" --feature payment
```

Phần trong ngoặc kép là **mô tả luồng bằng lời thường** của bạn. Phần `--feature payment` cho hệ thống biết luồng này thuộc tính năng nào (nếu bạn không ghi, và trong dự án chỉ có một tính năng đang làm dở, hệ thống sẽ tự đoán ra).

**Một câu để nhớ:** `/sequence` vẽ **cuộc trao đổi giữa nhiều bên theo trục thời gian** — hợp nhất khi bạn cần thấy rõ "ai gọi ai, trả về gì, theo thứ tự nào, và rẽ nhánh ra sao khi có lỗi".

---

## 2. Toàn bộ luồng chạy — sơ đồ

Điều cần nhớ về `/sequence`: hình nó vẽ ra là dạng **mã chữ** (Mermaid) nhúng thẳng vào tài liệu — nghĩa là bạn không nhìn thấy hình ngay trong khung chat, mà mở tài liệu ra (trong công cụ đọc tài liệu như VS Code / Obsidian / GitHub) thì hình mới hiện. Vì vậy hệ thống có một bước **tự vẽ thử ra ảnh để kiểm tra** trước khi báo xong — đảm bảo hình không bị lỗi khi bạn mở lên.

```
 BẠN GÕ LỆNH
 /sequence "mo ta luong" --feature X
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 1 — Xác định luồng này thuộc tính năng nào        │
 │  Đọc mô tả, đoán tính năng. Không chắc → hỏi bạn.     │
 │  Tính năng chưa có → tự đặt tên rồi tạo mới (không    │
 │  bắt bạn phải chuẩn bị gì trước).                     │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 2 — Hiểu luồng cho đúng                           │
 │  Đọc tài liệu sẵn có của tính năng (use case, đặc     │
 │  tả...) để lấy: có những "nhân vật" nào, họ trao đổi  │
 │  gì theo thứ tự nào, có nhánh lỗi nào.                │
 │  Mô tả còn mơ hồ → HỎI bạn (ai tham gia? có nhánh     │
 │  lỗi/hết giờ/hủy nào không?) — KHÔNG tự bịa.          │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 3 — Lập "danh sách cần có" để tự chấm sau         │
 │  Trước khi vẽ, hệ thống tự liệt kê ra 3 thứ:           │
 │   • các nhân vật sẽ xuất hiện                          │
 │   • các bước chính theo thứ tự                         │
 │   • các nhánh rẽ (lỗi/hết giờ/hủy), đánh số riêng      │
 │  Danh sách này để cuối buổi ĐỐI CHIẾU xem vẽ đủ chưa.  │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 4 — Xem trước rồi mới ghi (xin phép)              │
 │  Hệ thống mô tả bằng lời: "sẽ thêm luồng X vào tài     │
 │  liệu, có N nhân vật, M bước, K nhánh rẽ". Bạn gật    │
 │  (Y) mới ghi vào file.                                │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 5 — Ghi sơ đồ vào tài liệu chung của tính năng    │
 │  Thêm một mục mới vào file "các luồng" của tính năng  │
 │  (không tạo file rời rạc, gom chung một chỗ dễ tra).  │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 6 — Tự vẽ thử ra ảnh, kiểm lỗi cú pháp            │
 │  Vì hình không hiện trong chat, hệ thống tự "vẽ thử"  │
 │  ra ảnh để chắc chắn nó vẽ được. Lỗi → tự sửa, thử    │
 │  lại (vài lần). Chỉ đi tiếp khi vẽ ra được hình.      │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 7 — Đối chiếu: vẽ ĐỦ nội dung chưa?               │
 │  So hình vừa vẽ với "danh sách cần có" ở Bước 3:       │
 │   • đủ nhân vật chưa?                                  │
 │   • đủ các bước chính chưa?                            │
 │   • đủ các nhánh lỗi chưa, nhãn có đúng không?         │
 │  Thiếu → tự bổ sung rồi vẽ lại. (Vẽ được hình ≠ vẽ    │
 │  đủ ý — đây là 2 việc khác nhau.)                     │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 8 — Nhờ "người soát sơ đồ" (chỉ khi luồng PHỨC   │
 │          TẠP)                                          │
 │  Nếu luồng nhiều nhánh / nhiều nhân vật / có gọi lại  │
 │  (webhook, hết giờ), hệ thống mời một trợ lý chuyên   │
 │  rà sơ đồ kỹ thuật soát lại. Luồng đơn giản → bỏ qua. │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 9 — Báo hoàn tất                                  │
 │  Cho biết đã thêm luồng vào file nào, hình vẽ được,   │
 │  đã kiểm đủ nội dung. Ghi lại vào sổ theo dõi.        │
 └──────────────────────────────────────────────────────┘
        │
        ▼
     HOÀN TẤT — mở tài liệu trong công cụ đọc là thấy hình
```

---

## 3. "Nhân vật" và "mũi tên" trong sơ đồ nghĩa là gì?

Đây là phần giúp bạn **đọc hiểu** một sơ đồ tuần tự, kể cả khi bạn không phải người kỹ thuật.

**Các nhân vật (đứng thành cột dọc trên đầu hình).** Mỗi cột là một bên tham gia vào luồng. Có hai loại:

- **Người thật** — ví dụ "Khách", "Nhân viên duyệt". Trong hình thường có ký hiệu hình người.
- **Hệ thống / bộ phận** — ví dụ "Màn hình", "Hệ thống", "Cổng thanh toán Momo". Trong hình là một ô chữ nhật.

Một điểm nhỏ: nếu mô tả của bạn nhắc tên người cụ thể (ví dụ "chị Lan bấm nút"), hệ thống sẽ **đổi thành vai chung là "Khách"/"Người dùng"** — vì sơ đồ mô tả vai trò, không phải một cá nhân.

**Các mũi tên (kẻ ngang giữa các cột).** Mỗi mũi tên là "một bên gửi gì đó cho bên kia", đọc từ trên xuống theo thứ tự thời gian. Trong bộ tài liệu này có một **quy ước để đọc cho dễ**:

- **Mũi tên nét liền** = một bên **yêu cầu / gọi** bên kia làm gì đó (ví dụ Khách bấm "Thanh toán" gửi tới Màn hình).
- **Mũi tên nét đứt** = **kết quả trả về** (ví dụ Hệ thống trả về "thành công" cho Màn hình).

> **Một chỗ hay bị hiểu nhầm, nói rõ luôn:** nét liền / nét đứt ở đây **chỉ để phân biệt "gọi đi" và "trả về"** cho dễ đọc — nó **không** mang ý nghĩa kỹ thuật "đồng bộ / bất đồng bộ" như một số người quen đọc sơ đồ UML có thể nghĩ. Đây là quy ước của team để tài liệu dễ hiểu, không phải thuật ngữ chuyên môn.

**Các khối rẽ nhánh.** Khi luồng có nhiều khả năng xảy ra, hình sẽ có một khung bao quanh, chia làm mấy phần — ví dụ: *"Nếu thanh toán thành công"* làm một phần, *"Nếu khách hủy hoặc hết giờ"* làm phần khác. Nhờ vậy người đọc thấy được cả đường đi bình thường lẫn đường đi khi có sự cố.

---

## 4. Vì sao phải "tự vẽ thử ra ảnh" và "đối chiếu lại" (Bước 6 và 7)?

Đây là hai bước tự-kiểm-tra quan trọng, làm nên sự khác biệt giữa "báo xong nhưng hình lỗi" và "báo xong là dùng được".

**Vì sao phải tự vẽ thử ra ảnh (Bước 6)?**
Sơ đồ tuần tự được lưu dưới dạng **mã chữ** — tức là một đoạn văn bản theo cú pháp riêng, để công cụ đọc tài liệu tự biến thành hình khi bạn mở lên. Vấn đề là: đoạn mã chữ đó có thể viết sai cú pháp một chỗ nhỏ (thiếu một ký tự, một dấu ngoặc lệch), khiến khi bạn mở tài liệu ra thì **cả khối hình báo lỗi, không hiện gì cả**. Và vì hình không hiện được trong khung chat, nếu hệ thống không tự kiểm, bạn sẽ chỉ phát hiện lỗi khi tự mở file lên — lúc đó đã mất công. Nên hệ thống **tự vẽ thử ra một ảnh** ngay sau khi ghi; nếu vẽ không ra thì tự đọc lỗi, sửa lại, thử lại vài lần — chỉ báo xong khi chắc chắn hình vẽ được.

**Vì sao phải đối chiếu lại nội dung (Bước 7)?**
Đây là một điểm tinh tế: **hình vẽ ra được (đúng cú pháp) không có nghĩa là hình vẽ đủ ý.** Ví dụ, mô tả của bạn có nói tới nhánh "nếu thanh toán hết giờ thì báo lỗi", nhưng khi vẽ, hệ thống có thể vô tình bỏ sót nhánh đó — mà hình vẫn hiện ra bình thường, không báo lỗi gì. Nếu không có ai đối chiếu, bạn sẽ nhận một sơ đồ trông ổn nhưng thiếu mất một tình huống quan trọng.

Vì vậy hệ thống dùng lại "danh sách cần có" đã lập ở Bước 3 (đủ những nhân vật nào, những bước nào, những nhánh rẽ nào) để **soi lại từng mục xem hình vẽ có đủ không**. Thiếu chỗ nào thì tự bổ sung rồi vẽ lại. Giống như viết xong một bài rồi rà lại dàn ý xem đã nói đủ các ý đã định chưa, chứ không chỉ kiểm tra "câu chữ có đúng ngữ pháp không".

---

## 5. Ai "soát" sơ đồ khi luồng phức tạp? (Bước 8)

Với những luồng **đơn giản** (ít nhân vật, đi thẳng một mạch), hai bước tự-kiểm ở trên là đủ — hệ thống không mời thêm ai để tránh làm chậm.

Nhưng khi luồng **phức tạp** — có nhiều nhánh rẽ (từ 3 nhánh lỗi trở lên), hoặc nhiều bên tham gia (từ 4 nhân vật trở lên), hoặc có nhánh lồng trong nhánh, hoặc có kiểu "gọi lại sau" (webhook, chờ hết giờ) — thì hệ thống mời một **trợ lý chuyên rà soát sơ đồ kỹ thuật** (bạn có thể hình dung như một đồng nghiệp giỏi đọc sơ đồ, được mời soi lại giúp).

Trợ lý này chuyên bắt những lỗi mà việc tự-kiểm dễ bỏ qua: một nhân vật bị thiếu, một nhánh lỗi trong mô tả nhưng chưa được vẽ, một đường đi tới đó rồi "cụt" không dẫn đi đâu, một chỗ rẽ nhánh nhưng thiếu mất một khả năng. Nếu trợ lý phát hiện thiếu sót nghiêm trọng, hệ thống tự bổ sung rồi vẽ lại, tối đa vài vòng.

Cách này giúp cân bằng: **luồng đơn giản thì làm nhanh, luồng phức tạp thì soát kỹ** — không bắt mọi luồng đều qua quy trình rà soát nặng nề như nhau.

---

## 6. Sơ đồ này được lưu ở đâu, và nó khác các loại sơ đồ khác thế nào?

`/sequence` **không tạo file rời rạc** cho từng luồng. Thay vào đó, nó gom tất cả các luồng của cùng một tính năng vào **một tài liệu chung** (file "các luồng" của tính năng đó). Mỗi lần bạn vẽ thêm một luồng, nó thêm một mục mới vào cuối tài liệu này — nhờ vậy tất cả luồng của một tính năng nằm chung một chỗ, dễ tra cứu.

Một quy tắc quan trọng: **sơ đồ tuần tự KHÔNG được nhét vào tài liệu Use Case.** Lý do là hai loại tài liệu này ở "độ cao" khác nhau:

- **Use Case** mô tả nghiệp vụ theo góc nhìn của người dùng ("khách muốn đạt được gì, kết quả mong đợi là gì") — đọc là hiểu, không dính chi tiết kỹ thuật.
- **Sơ đồ tuần tự** đi vào chi tiết "bên nào gọi bên nào" — gần với cách hệ thống vận hành hơn.

Trộn hai thứ này vào nhau sẽ khiến người đọc nghiệp vụ bị lạc vào chi tiết kỹ thuật, mà người kỹ thuật thì vẫn phải nhảy qua file khác để đọc cho đủ. Nên chúng được để riêng: Use Case ở một chỗ, sơ đồ tuần tự ở tài liệu "các luồng". Nếu bạn yêu cầu "vẽ sequence vào trong use case", hệ thống sẽ từ chối và giải thích lý do này.

Còn về việc chọn đúng loại sơ đồ: `/sequence` là một trong nhiều lệnh vẽ sơ đồ. Nói ngắn gọn cách phân biệt:

| Bạn cần thể hiện... | Nên dùng |
|---|---|
| Nhiều bên **trao đổi qua lại theo thời gian** (gọi đi, trả về) | `/sequence` (lệnh này) |
| Một quy trình **từng bước một, có rẽ nhánh** (ai làm bước nào) | nhóm lệnh vẽ quy trình (`/activity`, `/activity-swimlane`...) |
| **Vòng đời trạng thái** của một đối tượng (đơn hàng: chờ → đã trả → đã giao) | `/state` |
| **Bức tranh dữ liệu** (có những bảng dữ liệu nào, liên hệ ra sao) | `/erd`, `/d2-erd` |

---

## 7. Vì sao lệnh này KHÔNG "vẽ đi vẽ lại nhiều vòng trong chat"?

Một số lệnh vẽ (ví dụ lệnh vẽ khung màn hình bằng ký tự) cho phép bạn xem kết quả ngay trong khung chat rồi bảo "sửa chỗ này, sửa chỗ kia" nhiều vòng liên tục. `/sequence` **cố tình không làm vậy**, và có lý do chính đáng:

Sơ đồ tuần tự được lưu dưới dạng mã chữ, mà **mã chữ đó không hiện thành hình trong khung chat** — chat chỉ in ra đoạn mã thô, nhìn vào một đống ký tự bạn cũng khó mà "duyệt" được hình đẹp hay xấu, đủ hay thiếu. Cho bạn "sửa nhiều vòng" trên một thứ bạn không nhìn thấy hình là vô nghĩa.

Thay vào đó, cách làm hợp lý hơn là: hệ thống ghi hình vào tài liệu, tự kiểm cho vẽ được và đủ ý, rồi bạn **mở tài liệu trong công cụ đọc** (VS Code / Obsidian / GitHub) để xem hình thật. Muốn sửa, bạn **gọi lại lệnh** và nói cần đổi gì — hệ thống tự hiểu là đang sửa luồng cũ (không tạo trùng), cho bạn xem phần thay đổi "trước/sau" rồi mới ghi đè.

Nói cách khác: bạn review từ **hình thật trong tài liệu**, không phải từ mã chữ trong chat — nên vòng lặp sửa diễn ra qua việc gọi lại lệnh, chứ không phải sửa tại chỗ trong chat.

---

## 8. Ví dụ thực tế

Chị **Lan**, một BA phụ trách tính năng "payment" (thanh toán), cần mô tả rõ luồng khách thanh toán qua Momo cho dev hiểu — đặc biệt là phải thấy rõ chuyện gì xảy ra khi thanh toán **thất bại hoặc hết giờ**, chứ không chỉ đường đi thuận lợi.

Chị Lan mở terminal, gõ:

```
/sequence "khách bấm thanh toán, hệ thống tạo yêu cầu rồi chuyển sang Momo, Momo báo kết quả về qua webhook; xử lý cả trường hợp thành công, thất bại và hết giờ" --feature payment
```

1. Hệ thống nhận ra đây là tính năng `payment` (chị Lan ghi rõ) — không cần hỏi lại.

2. Hệ thống đọc các tài liệu sẵn có của `payment` để hiểu đúng luồng: có những bên nào tham gia, thứ tự trao đổi ra sao, có những nhánh lỗi nào.

3. Trước khi vẽ, hệ thống tự lập "danh sách cần có": 4 nhân vật (Khách, Màn hình, Hệ thống, Momo); các bước chính (bấm thanh toán → tạo yêu cầu → chuyển Momo → Momo báo về); và 3 nhánh rẽ (thành công / thất bại / hết giờ), đánh số riêng từng nhánh.

4. Hệ thống mô tả bằng lời: *"Em sẽ thêm luồng 'Thanh toán qua Momo' vào tài liệu các luồng của payment: 4 nhân vật, khoảng 8 bước, 3 nhánh rẽ (thành công / thất bại / hết giờ). Apply?"* Chị Lan gõ `Y`.

5. Hệ thống thêm một mục mới vào file `docs/payment/srs/payment-flows.md` — nơi gom mọi luồng của tính năng payment.

6. Hệ thống tự vẽ thử ra ảnh để kiểm cú pháp. Lần đầu có một lỗi nhỏ, hệ thống tự đọc lỗi, sửa lại, vẽ lại — lần này ra hình hoàn chỉnh.

7. Hệ thống đối chiếu lại với "danh sách cần có": đủ 4 nhân vật chưa? — đủ. Đủ các bước chính chưa? — đủ. Đủ 3 nhánh chưa? — kiểm thấy nhánh "hết giờ" có nhãn hơi mờ, hệ thống chỉnh lại cho khớp mô tả rồi vẽ lại lần nữa.

8. Vì luồng này có 4 nhân vật, 3 nhánh rẽ và có webhook (gọi lại sau), hệ thống mời **trợ lý rà soát sơ đồ** soi lại. Trợ lý xác nhận không có nhánh nào bị cụt, không thiếu bên nào — ổn.

9. Hệ thống báo xong: đã thêm luồng "Thanh toán qua Momo" vào file `payment-flows.md`, hình vẽ được, đã kiểm đủ 4 nhân vật / các bước chính / 3 nhánh rẽ. Chị Lan mở file trong VS Code, thấy sơ đồ hiện ra rõ ràng — cả đường thanh toán thuận lợi lẫn hai nhánh sự cố. Chị gửi cho dev, dev đọc hiểu ngay phải xử lý gì khi Momo báo thất bại hoặc không phản hồi.

Vài hôm sau, nghiệp vụ đổi: cần thêm bước "gửi email biên nhận cho khách sau khi thanh toán thành công". Chị Lan chỉ cần gõ lại lệnh với yêu cầu thay đổi đó — hệ thống tự hiểu là đang sửa luồng cũ, cho chị xem phần chỉnh "trước/sau" rồi mới ghi đè, không tạo ra luồng trùng.

---

## Xem thêm

Tài liệu này chỉ giải thích ý tưởng và luồng chạy ở mức dễ hiểu. Muốn xem đầy đủ chi tiết kỹ thuật (cú pháp Mermaid, cách kiểm tra hình, các bước 1-10, các trường hợp đặc biệt), đọc file gốc: `.claude/skills/sequence/SKILL.md`.

Các lệnh vẽ sơ đồ khác trong cùng bộ công cụ:

- `explain-skills/state.md` — vẽ **vòng đời trạng thái** của một đối tượng (đơn hàng: chờ → đã trả → đã giao). Khác `/sequence`: sơ đồ trạng thái vẽ *một đối tượng đi qua các trạng thái nào*, còn `/sequence` vẽ *nhiều bên trao đổi với nhau theo thời gian*.
- `explain-skills/activity-family.md` — nhóm lệnh vẽ **sơ đồ quy trình** (từng bước một việc chạy thế nào, ai làm bước nào).
- Quy tắc chọn loại sơ đồ đầy đủ (khi nào dùng sơ đồ tuần tự, khi nào dùng loại khác) nằm ở file gốc: `.claude/rules/diagram-selection.md`.
