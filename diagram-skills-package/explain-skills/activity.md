---
type: skill-explainer
skill: activity
updated: 2026-07-14
---

# `/activity` là gì và nó chạy như thế nào?

## 1. Dùng để làm gì, khi nào nên gõ lệnh này

`/activity` là lệnh bạn gõ khi muốn **vẽ một sơ đồ quy trình** (hay *sơ đồ luồng công việc*) — tức là cái hình có các ô vuông nối bằng mũi tên, thể hiện "làm bước này xong thì tới bước kia, nếu đúng thì rẽ hướng này, nếu sai thì rẽ hướng kia". Dân trong nghề gọi loại hình này là *activity diagram* (sơ đồ hoạt động). Nó trông na ná lưu đồ (flowchart) quen thuộc, nhưng là một loại bài bản hơn — thêm được phần chia làn theo vai trò và một vài cấu trúc khác mà lưu đồ cơ bản không có; nói ngắn gọn thì đừng đánh đồng hai thứ.

Điểm đặc biệt của `/activity`: nó vẽ bằng một công cụ tên là **mermaid**. Bạn không cần biết mermaid là gì để dùng lệnh, nhưng hiểu qua thì tiện. Mermaid là **một cách viết sơ đồ bằng chữ** — thay vì kéo-thả từng ô như vẽ tay trong PowerPoint, bạn (hay ở đây là hệ thống) chỉ cần viết vài dòng chữ mô tả "ô A nối tới ô B", rồi có công cụ tự đọc mấy dòng chữ đó và **biến chúng thành hình vẽ** khi bạn mở file lên xem.

Vài tình huống điển hình nên dùng `/activity`:

- Bạn cần minh hoạ một quy trình duyệt đơn giản: "user gửi yêu cầu → hệ thống kiểm tra → hợp lệ thì xử lý, không hợp lệ thì báo lỗi".
- Bạn muốn vẽ một luồng nghiệp vụ gọn (1-2 người/bộ phận tham gia) và muốn hình đó **hiện ngay trong file tài liệu** khi mở trên GitHub hoặc Obsidian, không phải chèn thêm file ảnh riêng.
- Bạn đang viết SRS (tài liệu đặc tả) và muốn kèm một sơ đồ có vài điểm rẽ nhánh "nếu... thì...".

Gõ lệnh đơn giản như:

```
/activity "user gửi yêu cầu hoàn tiền, hệ thống kiểm tra điều kiện, đủ thì hoàn, không đủ thì báo từ chối" --feature payment
```

Phần `--feature payment` chỉ là để nói cho hệ thống biết sơ đồ này thuộc tính năng nào (ở đây là "payment" — thanh toán). Nếu bạn quên ghi, hệ thống sẽ tự đoán từ ngữ cảnh, mơ hồ quá thì mới hỏi lại.

**Một câu để nhớ:** `/activity` vẽ sơ đồ quy trình bằng chữ và **nhúng thẳng vào file tài liệu**, nên hình tự hiện lên khi mở file — hợp nhất với quy trình gọn, ít vai trò.

---

## 2. Toàn bộ luồng chạy — sơ đồ

```
 BẠN GÕ LỆNH
 /activity "mo ta quy trinh" --feature <ten>
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ GIAI ĐOẠN 1 — Hiểu quy trình + gom thông tin          │
 │  Hệ thống đọc mô tả của bạn. Nếu tính năng đã có       │
 │  tài liệu (use case, SRS) thì đọc để lấy các bước.    │
 │  Chỗ nào mô tả còn thiếu/mơ hồ → HỎI BẠN (các bước    │
 │  là gì, có điểm quyết định nào, mấy vai trò tham gia). │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ GIAI ĐOẠN 2 — Chốt danh sách "ai tham gia"            │
 │  NẾU quy trình có nhiều vai trò: hệ thống quét mô tả  │
 │  đoán ra rồi HỎI LẠI BẠN "phát hiện N vai trò: ...    │
 │  đủ chưa?" và chờ bạn gật/bổ sung mới vẽ (xem Mục 4). │
 │  Quy trình chỉ 1 vai trò → bỏ qua bước này.           │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │  Nhiều vai trò + tương tác qua lại chằng chịt?        │
 │  → Hệ thống ĐỀ XUẤT chuyển sang /activity-swimlane    │
 │    (vẽ đẹp hơn cho loại này). Bạn có quyền ở lại       │
 │    mermaid nếu vẫn muốn nhúng inline.                 │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ GIAI ĐOẠN 3 — Xem trước rồi mới ghi (chờ bạn gật)     │
 │  Hệ thống tóm tắt "sẽ vẽ sơ đồ gì, mấy điểm quyết      │
 │  định, mấy vai trò, ghi vào file nào" và CHỜ bạn      │
 │  đồng ý (Y) trước khi động vào file.                  │
 └──────────────────────────────────────────────────────┘
        │
        │  (chỉ đi tiếp khi bạn gõ Y)
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ GIAI ĐOẠN 4 — Vẽ + ghi vào file tài liệu              │
 │  Hệ thống viết đoạn sơ đồ (bằng chữ mermaid) và thêm  │
 │  vào cuối file docs/<tính năng>/srs/<tính năng>-flows.md │
 │  (cùng file với các sơ đồ khác của tính năng đó).     │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ GIAI ĐOẠN 5 — TỰ KIỂM bằng máy, 2 lần                 │
 │  (a) Kiểm CÚ PHÁP: chạy máy thử "dịch" đoạn chữ thành │
 │      hình xem có lỗi không (như bật chính tả).        │
 │  (b) Kiểm NỘI DUNG: đối chiếu lại xem mọi điểm quyết  │
 │      định / vai trò có mặt đủ chưa, có "nhánh cụt"     │
 │      (đường đi rồi tắc, không dẫn tới đâu) không.      │
 │  Lỗi → tự sửa (tối đa 2 lần) rồi kiểm lại.             │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ GIAI ĐOẠN 5.5 — Mời "trợ lý soát sơ đồ" (nếu phức tạp)│
 │  Chỉ khi sơ đồ rắc rối (nhiều vai / nhiều quyết định  │
 │  / có vòng lặp) mới mời thêm 1 trợ lý chuyên rà        │
 │  (agent diagram-reviewer). Sơ đồ gọn thì bỏ qua.      │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ GIAI ĐOẠN 6 — Báo cáo hoàn tất                         │
 │  In tóm tắt: đã ghi sơ đồ vào file nào, mấy điểm       │
 │  quyết định, mấy vai trò, kiểm cú pháp OK, và nhắc     │
 │  bạn mở file trong IDE/Obsidian/GitHub để xem hình.   │
 └──────────────────────────────────────────────────────┘
        │
        ▼
   HOÀN TẤT — muốn sửa thì gọi lại /activity, hệ thống
   tự nhận ra sơ đồ cũ và vào chế độ cập nhật
```

---

## 3. Điểm mạnh riêng: hình tự hiện trong file, không cần ảnh rời

Đây là lý do chính để chọn `/activity` thay vì các cách vẽ sơ đồ khác, nên đáng giải thích kỹ.

Hãy tưởng tượng bạn viết một bản Word có kèm sơ đồ. Cách thông thường: bạn vẽ sơ đồ ở đâu đó, xuất ra một file ảnh (.png), rồi dán ảnh vào Word. Nhược điểm: khi quy trình đổi, bạn phải vẽ lại, xuất ảnh mới, dán đè lại — và nếu ai đó chỉ đọc bản chữ mà quên gửi kèm ảnh thì họ không thấy hình.

`/activity` làm khác. Nó không tạo file ảnh. Nó **viết đoạn mô tả sơ đồ bằng chữ ngay trong lòng file tài liệu**. Các công cụ đọc tài liệu phổ biến như **GitHub** (nơi lưu trữ tài liệu) và **Obsidian** (phần mềm ghi chú) đều **tự hiểu đoạn chữ mermaid đó và hiện thành hình** mỗi khi có người mở file lên. Nghĩa là:

- Hình và chữ đi liền một khối, không bao giờ lạc mất nhau.
- Sửa quy trình chỉ cần sửa vài dòng chữ, hình tự cập nhật theo — không phải vẽ lại rồi xuất ảnh.
- Người đọc chỉ cần mở đúng file là thấy hình, không phải xin thêm file đính kèm.

Đổi lại, cách này có một giới hạn: nó chỉ đẹp khi quy trình **gọn**. Đó là lý do có Mục 4 dưới đây.

---

## 4. Vì sao hệ thống hỏi lại "danh sách vai trò" trước khi vẽ?

Trong một quy trình, "vai trò" là những bên tham gia — ví dụ *khách hàng*, *hệ thống*, *nhân viên chăm sóc*, *bộ phận tài chính*. Mỗi vai trò làm một số bước riêng.

Vấn đề: khi bạn mô tả quy trình bằng câu văn tự nhiên, đôi khi một vai trò **bị ẩn** trong câu chữ mà không được gọi tên rõ ràng. Ví dụ câu "sau khi duyệt xong thì tiền được chuyển đi" — ai chuyển tiền? Có thể là bộ phận tài chính, nhưng câu văn không nói thẳng. Máy quét tự động rất dễ **bỏ sót** một vai trò như vậy, và nếu bỏ sót thì cả một phần của sơ đồ sẽ thiếu mà không ai để ý.

Vì vậy, **khi phát hiện quy trình có nhiều vai trò**, `/activity` không tự tin quét xong là vẽ luôn. Nó **quét ra danh sách vai trò rồi hỏi lại bạn**: *"Phát hiện 2 vai trò tham gia: Khách hàng, Hệ thống. Đủ chưa, hay còn ai khác?"* — và chờ bạn xác nhận hoặc bổ sung. (Nếu quy trình chỉ có một vai trò duy nhất, không có "làn" nào để chia, thì bỏ qua bước hỏi này.) Đây là một nguyên tắc chung của cả bộ công cụ: những quyết định quan trọng thì hỏi con người, không tự đoán im lặng.

**Khi nào nó khuyên bạn đổi công cụ khác?** Nếu quy trình có từ 3 vai trò trở lên và các bước cứ nhảy qua nhảy lại giữa các vai trò liên tục, thì cách vẽ của mermaid sẽ **bị xô lệch, rối mắt** — các "làn" của từng vai trò không thẳng hàng, mũi tên đè chồng lên nhau. Lúc đó `/activity` sẽ chủ động gợi ý: *"Quy trình này nhiều vai trò, nên chuyển sang `/activity-swimlane` cho đẹp"* (một công cụ anh em vẽ được "phân làn" thẳng cột cho từng vai trò). Bạn vẫn có quyền chọn ở lại `/activity` nếu điều quan trọng với bạn là hình phải nhúng thẳng trong file.

---

## 5. Vì sao có bước "tự kiểm tra bằng máy 2 lần"?

Vì mermaid viết sơ đồ bằng chữ, nên có một rủi ro: viết sai một dấu ngoặc, một ký tự lạ, thì cả sơ đồ **không hiện được** khi mở file — chỉ ra một khối chữ khó hiểu. Tệ hơn, không như nhiều lệnh khác, `/activity` **không thể cho bạn xem trước hình ngay trong cửa sổ chat** (khung chat không biết cách hiện hình mermaid — nó chỉ hiện được đoạn chữ thô). Nghĩa là nếu viết sai, bạn sẽ chỉ phát hiện ra khi tự mở file lên và thấy hình vỡ.

Để tránh cảnh đó, sau khi ghi sơ đồ vào file, `/activity` **tự chạy máy kiểm tra 2 lần, hai loại khác nhau**:

1. **Kiểm cú pháp (compile):** máy thử "dịch" đoạn chữ thành hình để xem có lỗi viết sai không — giống như bật chức năng kiểm tra chính tả trước khi gửi email. Nếu lỗi, hệ thống tự sửa (tối đa 2 lần) rồi thử lại. Nếu sửa 2 lần vẫn không được, nó báo bạn rõ lỗi ở đâu chứ không âm thầm để file hỏng mà vẫn báo "xong".

2. **Kiểm nội dung (phủ đủ):** đây là loại kiểm khác — không phải xem viết đúng chữ chưa, mà xem **có vẽ thiếu gì không**. Cụ thể: mọi điểm quyết định bạn nói (mỗi chỗ "nếu... thì...") có xuất hiện trong hình chưa; mọi vai trò đã chốt ở Mục 4 có mặt chưa; và quan trọng là không có **"nhánh cụt"** — tức là không có đường đi nào chạy được nửa chừng rồi tắc, không dẫn tới điểm kết thúc.

Điểm cần nhớ: **"viết đúng cú pháp" chưa chắc là "vẽ đủ nội dung".** Một sơ đồ có thể hiện hình đẹp mà vẫn thiếu mất một vai trò, hoặc có một nhánh "từ chối" vẽ dở dang rồi bỏ lửng. Đó là lý do phải kiểm cả hai.

---

## 6. Khi nào mời thêm "trợ lý soát sơ đồ"?

Với sơ đồ gọn, hai lần tự kiểm bằng máy ở trên đã đủ. Nhưng khi sơ đồ **rắc rối** — nhiều vai trò, nhiều điểm quyết định, hoặc có vòng lặp (kiểu "làm lại, thử lại") — thì `/activity` mời thêm một **trợ lý chuyên soát sơ đồ** (một agent tên *diagram-reviewer*, bạn có thể hình dung như một đồng nghiệp chuyên đi rà lại hình vẽ giúp bạn).

Trợ lý này đọc sơ đồ vừa vẽ và đối chiếu với danh sách những thứ đáng lẽ phải có, để bắt các lỗi tinh vi mà máy dễ bỏ qua: một vai trò bị thiếu làn, một nhánh rẽ quên vẽ, một điểm quyết định thiếu mất một hướng đi. Nếu trợ lý phát hiện lỗi nghiêm trọng, hệ thống tự bổ sung rồi kiểm lại, tối đa vài vòng.

Trợ lý này **chỉ được mời khi sơ đồ vượt ngưỡng phức tạp** (đại khái: từ 3 vai trò trở lên, hoặc từ 5 điểm quyết định trở lên, hoặc có quyết định lồng nhiều tầng, hoặc có vòng lặp). Sơ đồ đơn giản thì bỏ qua bước này cho nhanh.

---

## 7. Không có bước "sửa tới sửa lui ngay trong chat"

Một số lệnh vẽ khác cho bạn xem thử ngay trong khung chat rồi sửa nhiều vòng cho tới khi ưng. `/activity` **cố tình không làm vậy**, và lý do rất đơn giản: như đã nói ở Mục 5, khung chat không hiện được hình mermaid — nó chỉ hiện đoạn chữ thô, mà nhìn chữ thô thì bạn không thể đánh giá hình đẹp hay xấu, đúng hay sai.

Nên quy trình đúng là: hệ thống ghi sơ đồ vào file → bạn **mở file lên (trong IDE, Obsidian, hoặc GitHub) để xem hình thật** → nếu muốn đổi gì, bạn **gọi lại `/activity`** và nói cần sửa. Khi bạn gọi lại đúng quy trình đó, hệ thống nhận ra "à, sơ đồ này đã có rồi", tự vào chế độ cập nhật và cho bạn xem phần thay đổi (trước/sau) trước khi ghi đè.

---

## 8. Ví dụ thực tế

Chị **Mai**, một BA phụ trách tính năng "payment" (thanh toán), cần vẽ sơ đồ cho quy trình hoàn tiền để đưa vào tài liệu SRS. Chị mở terminal, gõ:

```
/activity "khách gửi yêu cầu hoàn tiền, hệ thống kiểm tra đơn còn trong hạn hoàn không, còn hạn thì hoàn tiền và gửi email xác nhận, hết hạn thì báo từ chối" --feature payment
```

1. Hệ thống đọc mô tả, nhận ra tính năng là `payment`. Nó thấy quy trình đã đủ rõ nên không cần hỏi thêm nhiều về các bước.

2. Hệ thống quét ra 2 vai trò — *Khách* và *Hệ thống* — rồi hỏi lại chị Mai: *"Phát hiện 2 vai trò tham gia: Khách, Hệ thống. Đủ chưa, hay còn ai khác (ví dụ bộ phận tài chính duyệt tay)?"* Chị Mai trả lời: "đủ rồi, hệ thống tự hoàn không cần duyệt tay."

3. Vì chỉ 2 vai trò và tương tác đơn giản, hệ thống **không** đề xuất chuyển sang công cụ khác — `/activity` là lựa chọn hợp lý.

4. Hệ thống tóm tắt cho chị Mai: *"Em sẽ thêm sơ đồ quy trình hoàn tiền vào file docs/payment/srs/payment-flows.md, gồm 1 điểm quyết định (còn hạn hoàn hay không) và 2 vai trò. Đồng ý? (Y / sửa)"* Chị Mai gõ `Y`.

5. Hệ thống viết đoạn sơ đồ và ghi vào cuối file flows.md.

6. Ngay sau đó, máy tự kiểm 2 lần: kiểm cú pháp — dịch thử đoạn chữ thành hình, không lỗi (báo "compile OK"). Kiểm nội dung — điểm quyết định "còn hạn?" có đủ 2 nhánh "còn/hết", cả hai nhánh đều dẫn tới điểm kết thúc, không có nhánh cụt. Đủ.

7. Sơ đồ này gọn (chỉ 1 điểm quyết định, 2 vai trò) nên hệ thống không cần mời trợ lý soát sơ đồ.

8. Hệ thống in báo cáo: *"Đã thêm sơ đồ hoàn tiền vào payment-flows.md. 1 điểm quyết định, 2 vai trò, kiểm cú pháp OK, không nhánh cụt. Mở file trong IDE/Obsidian/GitHub để xem hình. Cần sửa thì gọi lại /activity."*

9. Chị Mai mở file trên GitHub, hình hiện lên ngay trong tài liệu — không cần file ảnh nào rời. Chị thấy thiếu một bước "ghi log giao dịch" nên gõ lại `/activity` với mô tả bổ sung; hệ thống nhận ra sơ đồ cũ, cho chị xem phần thêm mới (trước/sau) rồi mới ghi đè.

Toàn bộ quá trình, chị Mai chưa từng bị hệ thống tự ý vẽ sai rồi ghi bừa vào file — mỗi lần ghi đều có bước xác nhận, và hình luôn được máy kiểm tra trước khi báo xong.

---

## Xem thêm

Tài liệu này chỉ giải thích ý tưởng và luồng chạy ở mức dễ hiểu. Muốn xem đầy đủ chi tiết kỹ thuật (từng bước, format lệnh, các trường hợp đặc biệt), đọc file gốc: `.claude/skills/activity/SKILL.md`.

`/activity` có 2 người anh em cùng "họ activity" — cùng vẽ sơ đồ quy trình nhưng bằng công cụ khác, hợp với tình huống khác:

- **`explain-skills/activity-swimlane.md`** — vẽ "phân làn" thẳng cột cho từng vai trò, là lựa chọn tốt hơn khi quy trình có nhiều vai trò tương tác chằng chịt (chính là chỗ `/activity` bị xô lệch).
- **`explain-skills/d2-activity.md`** — vẽ sơ đồ ĐẸP đứng riêng (thành file ảnh) để đưa cho sếp/khách hàng xem hoặc xuất báo cáo, khi không cần nhúng thẳng trong tài liệu.
- **`explain-skills/activity-family.md`** — bảng so sánh cả 3 công cụ trên, giúp bạn chọn nhanh nên dùng cái nào.
