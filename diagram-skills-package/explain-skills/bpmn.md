---
type: skill-explainer
skill: bpmn
updated: 2026-07-14
---

# `/bpmn` là gì và nó chạy như thế nào?

## 1. Dùng để làm gì, khi nào nên gõ lệnh này

`/bpmn` là lệnh vẽ sơ đồ quy trình theo **một chuẩn quốc tế tên BPMN** (viết tắt của "Business Process Model and Notation" — mô hình hoá quy trình nghiệp vụ). So với các lệnh vẽ quy trình khác, `/bpmn` không phải "cao cấp hơn" — nó phục vụ **một nhu cầu khác**: khi bạn không chỉ cần một hình để xem, mà cần một bản đúng chuẩn để đưa vào phần mềm quản lý quy trình chuyên nghiệp.

"BPMN là chuẩn quốc tế" nghĩa là gì? Nghĩa là nó có một **bộ ký hiệu thống nhất mà giới làm quy trình khắp thế giới đều đọc được giống nhau** — hình tròn là điểm bắt đầu/kết thúc, hình thoi là ngã rẽ (gateway), hình chữ nhật bo góc là một bước việc, các "làn" phân theo vai trò. Giống như biển báo giao thông: dù ở nước nào, người ta nhìn là hiểu, không cần giải thích lại.

Vài tình huống điển hình nên dùng `/bpmn`:

- Quy trình nghiệp vụ (Business) **phức tạp, nhiều bước, nhiều vai trò** (duyệt nhiều cấp, tiếp nhận khách/nhân viên mới, hoàn tiền qua nhiều phòng ban) — cần vẽ thật bài bản.
- Bạn cần một file **mở được bằng phần mềm quản lý quy trình chuyên nghiệp** (Camunda, Bizagi, draw.io) để đội kỹ thuật đưa vào hệ thống chạy quy trình thật, hoặc để **kéo-thả chỉnh sửa** tiếp.
- Bạn làm việc với đối tác/khách hàng đã quen đọc sơ đồ BPMN và mong nhận đúng loại đó.

Gõ lệnh đơn giản như:

```
/bpmn "khách gửi yêu cầu hoàn tiền, nhân viên xem xét, quản lý duyệt, hệ thống chuyển tiền" --feature payment
```

> **Một câu để nhớ:** `/bpmn` vẽ quy trình theo **chuẩn quốc tế**, ra file **mở được bằng phần mềm quản lý quy trình + kéo-thả sửa** — dùng cho luồng nghiệp vụ phức tạp cần làm bài bản.

---

## 2. Lệnh này khác gì `/activity-swimlane`? (đọc trước để khỏi chọn nhầm)

Đây là câu hỏi quan trọng nhất, vì `/bpmn` và `/activity-swimlane` **rất giống nhau** — cả hai đều vẽ quy trình nhiều vai trò với các "làn" phân theo người phụ trách. Chọn nhầm sẽ mất công.

Cách phân biệt: hãy nghĩ tới **mục đích cuối cùng của cái sơ đồ**.

- **`/activity-swimlane`** cho ra một **hình để đọc** — nhúng vào tài liệu BA, mọi người xem để hiểu quy trình. Nhẹ, nhanh, đủ dùng cho phần lớn trường hợp mô tả nghiệp vụ hằng ngày.
- **`/bpmn`** cho ra một **file quy trình đúng chuẩn để "chạy" hoặc chỉnh sửa tiếp** — không chỉ để xem, mà để đội kỹ thuật nhập vào phần mềm quản lý quy trình, hoặc để bạn kéo-thả sửa như dùng một công cụ vẽ chuyên nghiệp.

Ví von: `/activity-swimlane` giống như **bản vẽ tay đẹp** dán lên tường cho cả nhóm nhìn; còn `/bpmn` giống như **bản vẽ kỹ thuật đúng tiêu chuẩn** nộp cho nhà thầu để thi công thật.

Quy tắc chọn:
- Chỉ cần **mô tả quy trình trong tài liệu** cho người đọc hiểu → dùng `/activity-swimlane` (nhẹ hơn).
- Luồng nghiệp vụ **phức tạp cần làm bài bản**, hoặc cần **chuẩn quốc tế / nhập vào phần mềm quy trình / kéo-thả sửa** → mới lên `/bpmn`.

---

## 3. Toàn bộ luồng chạy — sơ đồ

Điểm đặc biệt nhất của `/bpmn` nằm ở cách nó vẽ: **AI không tự vẽ hình, mà chỉ mô tả nghiệp vụ; một "máy vẽ" riêng lo phần hình.** Và trước khi vẽ, có một bước **tự kiểm tra tính hợp lý của quy trình**. Hai điều này được giải thích kỹ ở Mục 4 và 5.

```
 BẠN GÕ LỆNH
 /bpmn "mo ta quy trinh" --feature X
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ GIAI ĐOẠN 1 — Tìm tính năng + hiểu quy trình          │
 │  Đoán bạn đang nói về tính năng nào; đọc tài liệu đã  │
 │  có (use case, đặc tả) để lấy các bước, vai trò, ngã  │
 │  rẽ. Thiếu thông tin → HỎI bạn (bằng ngôn ngữ nghiệp  │
 │  vụ, không hỏi kỹ thuật).                             │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ GIAI ĐOẠN 2 — Ghi lại "bản mô tả có cấu trúc"         │
 │  AI KHÔNG vẽ hình. Nó chỉ ghi ra một bản mô tả gọn    │
 │  gàng: có những vai trò nào, bước nào, ngã rẽ nào,    │
 │  kết cục nào. (Bản này gọi là "IR" — xem Mục 4.)     │
 │  Kèm một bản "đối chiếu" liệt kê vai trò/nhánh/lỗi    │
 │  rút ra từ tài liệu gốc, để lát nữa kiểm lại.        │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ GIAI ĐOẠN 3 — Xem trước rồi mới ghi (xin phép)        │
 │  Tóm tắt bằng lời: mấy vai trò, mấy bước, mấy ngã rẽ, │
 │  mấy kết cục, phủ đủ nghiệp vụ từ tài liệu nào.       │
 │  Bạn gõ Y (đồng ý) mới làm tiếp.                      │
 └──────────────────────────────────────────────────────┘
        │  (chỉ đi tiếp khi bạn gõ Y)
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ GIAI ĐOẠN 4 — MÁY TỰ KIỂM tính hợp lý (semcheck)      │
 │  Trước khi vẽ, máy soi bản mô tả: có điểm bắt đầu và  │
 │  điểm kết thúc không? mọi bước có đường đi tới đích   │
 │  không (không có bước "mồ côi")? mỗi ngã rẽ có đủ ít  │
 │  nhất 2 hướng không? Sai logic → dừng, sửa lại.      │
 │  (Vì sao quan trọng: xem Mục 5.)                     │
 └──────────────────────────────────────────────────────┘
        │  (hợp lý → đi tiếp)
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ GIAI ĐOẠN 5 — "Máy vẽ" dựng hình đúng chuẩn           │
 │  Một công cụ riêng (engine) đọc bản mô tả rồi tự tính │
 │  vị trí từng ô, kẻ đường, sắp làn — ra file sơ đồ     │
 │  BPMN đúng chuẩn. AI KHÔNG đụng vào việc này.        │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ GIAI ĐOẠN 6 — Kiểm lần cuối + báo hoàn tất            │
 │  Chạy kiểm tra lại lần nữa cho chắc (logic sạch, hình │
 │  không đè). Tạo kèm một trang HTML để bạn KÉO-THẢ sửa │
 │  sơ đồ như dùng công cụ chuyên nghiệp. Báo bạn:      │
 │  mở trang đó để xem/sửa, hoặc nhập file vào Camunda.  │
 └──────────────────────────────────────────────────────┘
        │
        ▼
   HOÀN TẤT — có sơ đồ BPMN chuẩn + trang kéo-thả để sửa
```

---

## 4. Điểm cốt lõi: "AI mô tả nghiệp vụ, máy lo vẽ hình"

Đây là thiết kế thông minh nhất của `/bpmn`, và cũng là lý do nó đáng tin. Cần giải thích kỹ.

Với các lệnh vẽ khác, AI vừa hiểu nghiệp vụ vừa viết luôn ra hình. Nhưng `/bpmn` **tách hẳn hai việc đó ra**:

1. **AI chỉ làm phần nó giỏi: hiểu nghiệp vụ.** Nó đọc tài liệu, rồi ghi ra một "bản mô tả có cấu trúc" — liệt kê: quy trình này có những vai trò nào, những bước nào, mỗi bước ai làm, có những ngã rẽ nào, dẫn tới những kết cục nào. Bản này **chỉ có nội dung nghiệp vụ, không có một toạ độ hay đường kẻ nào cả.** (Trong tài liệu kỹ thuật, bản mô tả này gọi tắt là "IR" — bạn không cần nhớ tên.)

2. **Một "máy vẽ" riêng làm phần còn lại: dựng hình.** Máy này (gọi là *engine*) đọc bản mô tả rồi tự tính vị trí từng ô, tự kẻ đường sao cho không đè nhau, tự sắp các làn cho thẳng. AI **không hề đụng vào việc tính vị trí.**

Vì sao tách ra? Vì đây là **hai loại việc rất khác nhau, và AI chỉ giỏi một loại.** AI hiểu nghiệp vụ rất tốt, nhưng nếu bắt nó tự tính "ô này đặt ở toạ độ x=120, y=340" thì rất dễ sai — hình ra sẽ đè lên nhau, đường kẻ chồng chéo. Ngược lại, "máy vẽ" thì tính toạ độ cực chuẩn nhưng không hiểu nghiệp vụ. Ghép đúng người đúng việc: AI lo ý nghĩa, máy lo hình thức.

Một lợi ích thực tế: khi bạn muốn sửa quy trình sau này, AI chỉ cần **sửa lại bản mô tả nghiệp vụ** (thêm một bước, đổi một ngã rẽ), rồi máy tự vẽ lại hình mới — không phải vẽ tay lại từ đầu.

---

## 5. Bước "tự kiểm tính hợp lý" (semcheck) làm gì?

Trước khi cho vẽ, `/bpmn` chạy một bước kiểm tra đặc biệt mà các lệnh khác không có ở mức này — kiểm xem **quy trình được mô tả có hợp lý về mặt logic không.** Đây không phải kiểm chính tả, mà kiểm "cái quy trình này có chạy được không".

Nó soi mấy điều cơ bản mà một quy trình đúng đắn phải có:

- **Có điểm bắt đầu và điểm kết thúc rõ ràng không?** Một quy trình phải biết bắt đầu từ đâu và kết thúc ở đâu.
- **Mọi bước có đường đi tới đích không?** Không được có bước nào "mồ côi" — tức là vẽ ra đó nhưng không có đường nào dẫn tới, hoặc đi vào rồi tắc, không ra tới kết thúc.
- **Mỗi ngã rẽ có đủ ít nhất hai hướng không?** Một điểm rẽ nhánh (ví dụ "duyệt hay không?") mà chỉ có một hướng đi ra thì vô nghĩa — nó phải có ít nhất hai (duyệt → hướng này, từ chối → hướng kia).

Nếu quy trình vi phạm những điều này, hệ thống **dừng lại và sửa** trước khi vẽ, chứ không vẽ ra một sơ đồ sai logic.

Ngoài ra còn một lớp kiểm nữa gọi là **"đối chiếu độ phủ"**: hệ thống so bản mô tả với tài liệu gốc xem có **bỏ sót** gì không — ví dụ tài liệu nhắc tới 4 vai trò mà bản mô tả chỉ có 3, hay có một trường hợp lỗi trong tài liệu chưa được thể hiện. Nếu thấy lệch, nó cảnh báo để người viết rà lại. Đây là cách đảm bảo sơ đồ vẽ ra **khớp với nghiệp vụ thật**, không thiếu không thừa.

---

## 6. Kết quả gồm gì — đặc biệt là "trang kéo-thả để sửa"

`/bpmn` không chỉ tạo một hình, mà tạo một bộ file. Hai thứ đáng chú ý nhất với bạn:

- **File sơ đồ BPMN chuẩn** — đây là file đúng chuẩn quốc tế, **nhập được vào các phần mềm quản lý quy trình** (Camunda, Bizagi, draw.io). Đội kỹ thuật lấy file này đưa vào hệ thống để chạy quy trình thật, hoặc mở ra chỉnh tiếp.

- **Một trang HTML để kéo-thả chỉnh sửa** — đây là điểm rất tiện: mở trang này bằng trình duyệt, bạn được một **công cụ vẽ giống bpmn.io** (một công cụ vẽ BPMN nổi tiếng) ngay trong trình duyệt. Bạn có thể **kéo-thả các ô, sửa nhãn, thêm bước** trực tiếp bằng chuột, rồi tải file đã sửa về. Nghĩa là sau khi hệ thống vẽ xong, bạn vẫn chủ động chỉnh tay được nếu muốn, không bị "khoá cứng".

(Cùng với đó là vài file phụ trợ: bản mô tả nghiệp vụ ở Mục 4 để sửa lại về sau, và một file danh mục liệt kê các quy trình đã vẽ cho tính năng.)

Một lưu ý nhỏ: trang kéo-thả này cần **kết nối internet lần đầu** để tải công cụ vẽ về (giống nhiều trang web hiện đại). Sau đó dùng bình thường.

---

## 7. Ví dụ thực tế

Chị **Lan**, một BA phụ trách tính năng "payment" (thanh toán), được giao vẽ quy trình **hoàn tiền** — nhưng lần này đội kỹ thuật muốn một bản BPMN chuẩn để đưa vào phần mềm quản lý quy trình của công ty, chứ không chỉ một hình để xem. Vì vậy chị chọn `/bpmn`.

Chị Lan gõ:

```
/bpmn "khách gửi yêu cầu hoàn tiền, hệ thống kiểm tra đơn, nhân viên xem xét, quản lý duyệt nếu số tiền lớn, hệ thống chuyển tiền" --feature payment
```

1. Hệ thống nhận ra tính năng `payment`, đọc các tài liệu đã có (use case hoàn tiền) để lấy các bước, vai trò và các ngã rẽ.

2. Nó ghi ra "bản mô tả có cấu trúc": 4 vai trò (Khách, Hệ thống, Nhân viên, Quản lý), 7 bước, 2 ngã rẽ ("Đơn có hợp lệ?", "Số tiền có vượt hạn mức cần quản lý duyệt?"), 2 kết cục (chuyển tiền thành công / từ chối). Kèm bản đối chiếu rút từ tài liệu gốc.

3. Hệ thống tóm tắt cho chị Lan bằng lời: *"Em sẽ tạo BPMN quy trình hoàn tiền: 4 vai trò, 7 bước, 2 ngã rẽ, 2 kết cục — phủ đủ 4 vai trò và cả 2 nhánh từ use case. Đồng ý?"* Chị Lan gõ `Y`.

4. Trước khi vẽ, máy tự kiểm tính hợp lý: có điểm bắt đầu (khách gửi yêu cầu) và kết thúc (2 kết cục) rõ ràng; mọi bước đều có đường tới đích; cả 2 ngã rẽ đều đủ hai hướng. Logic sạch. Phần đối chiếu cũng khớp — không sót vai trò hay nhánh nào so với tài liệu.

5. "Máy vẽ" đọc bản mô tả và tự dựng hình: tính vị trí từng ô, kẻ đường không đè, sắp các làn thẳng — ra file BPMN chuẩn. Chị Lan không phải canh chỉnh gì.

6. Hệ thống kiểm lần cuối (sạch), rồi báo chị Lan: *"BPMN hoàn tiền đã xong. Mở file `payment-bpmn-editor.html` để xem và kéo-thả sửa; hoặc kéo file `.bpmn` vào Camunda để nhập vào hệ thống."*

7. Chị Lan mở trang kéo-thả, thấy sơ đồ đúng chuẩn với 4 làn rõ ràng. Chị muốn đổi tên một bước cho sát nghiệp vụ hơn, nên kéo-thả sửa trực tiếp bằng chuột rồi tải về. Sau đó chị gửi file `.bpmn` cho đội kỹ thuật nhập vào phần mềm quy trình.

Toàn bộ quá trình, chị Lan chỉ mô tả nghiệp vụ và xác nhận một lần — phần vẽ đúng chuẩn và kiểm logic đã có hệ thống lo, và chị vẫn chủ động chỉnh tay được ở bước cuối.

---

## Xem thêm

Tài liệu này chỉ giải thích ý tưởng và luồng chạy ở mức dễ hiểu. Muốn xem đầy đủ chi tiết kỹ thuật (kiến trúc 2 lớp, cách máy vẽ dựng làn, các trường hợp đặc biệt), đọc file gốc: `.claude/skills/bpmn/SKILL.md`.

`/bpmn` là một trong nhóm lệnh cùng vẽ quy trình — mỗi lệnh hợp một nhu cầu khác nhau (không phải cái nào "cao cấp" hơn cái nào):

- `explain-skills/activity-swimlane.md` — `/activity-swimlane`: cũng phân làn theo vai trò nhưng **nhẹ hơn**, để mô tả nghiệp vụ trong tài liệu (không cần chuẩn OMG / phần mềm quy trình). Đây là lựa chọn mặc định cho quy trình đa vai trò thường ngày.
- `explain-skills/activity.md` — `/activity`: vẽ nhanh bằng Mermaid, nhúng thẳng vào tài liệu, hợp quy trình gọn.
- `explain-skills/d2-activity.md` — `/d2-activity`: cách vẽ thứ ba, dàn gọn hơn Mermaid khi nhiều nhánh, cho file ảnh đứng riêng.
- `explain-skills/activity-family.md` — bảng so sánh tổng hợp, giúp chọn đúng lệnh cho từng tình huống.
