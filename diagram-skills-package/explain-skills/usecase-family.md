---
type: skill-explainer
skill: usecase-family
updated: 2026-07-14
---

# `/usecase`, `/usecase-diagram`, `/userstory` — chúng liên quan với nhau thế nào?

> Tài liệu này giải thích **mối liên quan** giữa ba lệnh cùng làm việc với "kịch bản người dùng" và "backlog": `/usecase`, `/usecase-diagram`, `/userstory`. Muốn hiểu sâu từng lệnh, đọc file explainer riêng của nó (liệt kê ở cuối).

## 1. Ba lệnh này KHÔNG phải ba cách làm cùng một việc

Khác với ba lệnh vẽ sơ đồ quy trình (ở đó `/activity`, `/activity-swimlane`, `/d2-activity` là **ba cách vẽ khác nhau cho cùng một thứ**), ba lệnh ở đây làm **ba việc khác nhau, bổ trợ cho nhau**. Chúng không thay thế nhau — mỗi cái cho ra một loại đầu ra riêng, và bạn dùng cái nào tùy nhu cầu (không bắt buộc phải chạy đủ cả ba, cũng không bắt buộc theo đúng thứ tự).

Hãy hình dung bạn đang xây một tính năng. Sau khi có bản đặc tả kỹ thuật (SRS — nơi liệt kê các yêu cầu chức năng, gọi tắt là FR), bạn thường có ba việc để làm:

- **`/usecase`** — viết ra **từng kịch bản người dùng** bằng lời: ai muốn đạt điều gì, đi qua các bước nào, gặp tình huống lỗi thì sao. Đây là phần **chữ**, mô tả chi tiết.
- **`/usecase-diagram`** — vẽ **một bức tranh tổng** cho thấy toàn cảnh: có những ai (actor) và họ làm được những việc gì trong hệ thống. Đây là phần **hình**, nhìn phát thấy "phạm vi" của tính năng.
- **`/userstory`** — cắt công việc thành các **mẩu nhỏ đưa vào backlog** để đội phát triển nhận về làm từng sprint. Đây là phần **chia việc để giao**.

Nói ngắn gọn: **`/usecase` mô tả (chữ), `/usecase-diagram` vẽ toàn cảnh (hình), `/userstory` chia nhỏ để giao việc.** Ba đầu ra bổ trợ nhau, không phải ba lựa chọn loại trừ nhau.

---

## 2. Bức tranh dòng chảy — cái gì đến trước, cái gì sinh ra cái gì

```
                    ┌───────────────────────┐
                    │   /srs  (đặc tả SRS)   │
                    │   → các yêu cầu FR      │
                    │   ("nguồn sự thật")     │
                    └───────────┬───────────┘
                                │  (/userstory cần SRS mới chạy. /usecase-
                                │   diagram cần use case HOẶC SRS. Riêng
                                │   /usecase chạy được cả TRƯỚC SRS — xem ▼)
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
    ┌──────────────────┐  ┌───────────────┐  ┌──────────────────┐
    │   /usecase       │  │/usecase-diagram│ │   /userstory     │
    │  KỊCH BẢN (chữ)  │  │  TOÀN CẢNH (hình)│ │  BACKLOG (mẩu nhỏ)│
    │  từng use case   │  │  ai làm được gì │  │  chia để giao việc│
    │  chi tiết        │  │  trong hệ thống │  │                  │
    └────────┬─────────┘  └───────┬───────┘  └────────┬─────────┘
             │                    │                    │
             │ use case là nguồn  │                    │ story là nguồn
             │ tốt cho 2 lệnh kia │                    │ cho bước tiếp
             ▼                    ▼                    ▼
      (diagram đọc lại      (file .puml + ảnh     ┌──────────────────┐
       danh mục use case      .svg + bảng nhúng    │   /ac            │
       để biết vẽ ai/gì)      vào cùng 1 file      │  tiêu chí chấp   │
                              index với use case)  │  nhận (test được)│
                                                    └──────────────────┘
```

Hai điều quan trọng đọc từ sơ đồ này:

1. **Đều bám nguồn sự thật, nhưng điều kiện khác nhau.** `/userstory` **bắt buộc phải có SRS** mới chạy (chưa có thì từ chối, chỉ bạn viết `/srs` trước). `/usecase-diagram` cần **danh mục use case HOẶC SRS** (thiếu cả hai mới từ chối). Riêng **`/usecase` chạy được cả khi CHƯA có SRS** — vì viết use case là một cách *khám phá* nghiệp vụ, thường làm sớm rồi từ đó mới ra SRS (xem Mục 4). Điểm chung: không lệnh nào tự bịa nội dung từ con số không — thiếu thì hỏi hoặc đánh dấu câu hỏi mở.

2. **Chúng dùng chung một "sổ cái".** `/usecase` và `/usecase-diagram` cùng ghi vào **một file duy nhất** — `{feature}-usecase-index.md`: use case đóng góp bảng ma trận truy vết (use case ↔ FR ↔ màn hình ↔ mã lỗi), còn diagram đóng góp cái hình + bảng actor. Nhờ chung một chỗ nên chúng không đá nhau.

---

## 3. Bảng phân biệt nhanh

Nếu chỉ đọc một phần, đọc bảng này:

| | `/usecase` | `/usecase-diagram` | `/userstory` |
|---|---|---|---|
| **Cho ra cái gì** | Văn bản chi tiết từng kịch bản người dùng | Một bức hình tổng quan (scope) | Các mẩu công việc nhỏ cho backlog |
| **Trả lời câu hỏi** | "Kịch bản này chạy ra sao, đảm bảo gì?" | "Ai làm được những gì trong hệ thống?" | "Cắt thế nào để giao đội dev làm từng đợt?" |
| **Dạng** | Chữ (mô tả nghiệp vụ) | Hình (một sơ đồ xuất ra file ảnh) | Chữ ngắn + tiêu chí + bảng backlog |
| **Đọc để làm gì** | Dev/QA hiểu chính xác hành vi mong đợi | Stakeholder xem toàn cảnh lúc kickoff | Đội dev nhận việc, ước lượng, làm |
| **Cần có trước** | Không bắt buộc: chưa có SRS → chế độ khám phá; có SRS → chế độ diễn giải | ≥1 trong: danh mục use case HOẶC SRS | SRS (FR) — dùng cả use case nếu có |
| **Kết quả để ở đâu** | `uc-*.md` + bảng trong file index | Ảnh + bảng nhúng vào cùng file index | Bảng index + mỗi story 1 file `us-NNN.md` |

Một câu để nhớ: **use case = kịch bản (chữ); use case diagram = toàn cảnh (hình); user story = chia việc (backlog).**

---

## 4. Thứ tự chạy điển hình (và vì sao)

Không bắt buộc phải chạy đủ cả ba, nhưng thứ tự thường gặp là:

**`/usecase` có thể là bước sớm nhất — trước cả SRS.** Vì viết use case là một cách khám phá nghiệp vụ, nhiều nhóm dựng use case *trước* để làm rõ "người dùng cần làm gì", rồi mới chạy `/srs` để rút ra các yêu cầu chính thức từ chính các use case đó. `/usecase` tự nhận biết: chưa có SRS thì nó hỏi bạn (chế độ khám phá); đã có SRS thì nó đọc các yêu cầu FR (chế độ diễn giải). Cả hai đều hợp lệ.

**`/usecase` trước, rồi `/usecase-diagram`.** Vì khi đã có danh mục use case rõ ràng, diagram có sẵn nguồn để "đọc lại" — biết chính xác có những use case nào, ai là actor — nên bức tranh tổng khớp với thực tế hơn. (Diagram vẫn chạy được khi mới chỉ có SRS, chỉ là phải tự suy actor/use case từ FR.) Nói cách khác: **viết kịch bản chi tiết xong rồi mới vẽ tấm bản đồ tổng** thì tấm bản đồ đối chiếu được với những gì đã viết.

**`/userstory` có thể chạy song song hoặc sau.** User story cũng đọc SRS làm nguồn, và nếu đã có use case thì nó tận dụng luôn (use case gợi ý ranh giới "một việc trọn vẹn"). Nhưng nó **không bắt buộc** phải có use case trước — chỉ cần SRS là đủ.

**Sau `/userstory` thường là `/ac`** (acceptance criteria — tiêu chí chấp nhận): biến mỗi story thành các điều kiện kiểm thử pass/fail rõ ràng. `/userstory` còn hỏi bạn có muốn chạy `/ac` luôn không ngay sau khi tạo story.

Điểm mấu chốt: đây là **một dây chuyền từ mô tả → toàn cảnh → chia việc → tiêu chí kiểm thử**, mỗi bước làm rõ thêm một tầng, đi từ "hiểu nghiệp vụ" xuống dần "sẵn sàng giao dev".

---

## 5. Ranh giới dễ nhầm — ba chỗ hay lẫn

**Use case (chữ) ≠ use case diagram (hình).** Đây là chỗ lẫn phổ biến nhất vì tên gần giống. `/usecase` cho ra **văn bản chi tiết** từng kịch bản (đọc để hiểu chính xác hành vi); `/usecase-diagram` cho ra **một bức hình tổng** (nhìn để nắm phạm vi). Một bên là đọc kỹ, một bên là nhìn tổng — bổ trợ nhau, không thay nhau. Vì thế cái hình và cái bảng use case được để **chung một file** cho tiện tra.

**Use case ≠ user story.** Use case mô tả **đầy đủ một kịch bản** (đường chuẩn + mọi nhánh lỗi + đảm bảo khi thành công/thất bại) — thiên về "hiểu cho đúng và đủ". User story là **một mẩu việc nhỏ để giao dev** — thiên về "cắt sao cho làm được trong một đợt sprint và tạo ra giá trị quan sát được". Một use case (ví dụ "Đặt hàng") có thể được cắt thành nhiều user story nhỏ.

**Một use case ≠ một FR, và một story ≠ một FR.** Cả hai lệnh đều **không** máy móc "một yêu cầu FR = một use case/story". Một mục tiêu người dùng thường gom nhiều FR; ngược lại một FR đôi khi chỉ là một quy tắc nằm trong use case lớn hơn. Chia theo **giá trị nghiệp vụ trọn vẹn**, không theo đếm số FR.

---

## 6. Ba điểm giống nhau ở cả ba lệnh

Dù làm ba việc khác nhau, cả ba vận hành theo cùng vài nguyên tắc:

1. **Không có nguồn thì không bịa.** Mỗi lệnh bám nguồn sự thật theo cách của nó: `/userstory` đọc SRS; `/usecase-diagram` đọc danh mục use case (hoặc SRS); `/usecase` đọc SRS nếu có, còn chưa có thì hỏi bạn (chế độ khám phá). Thiếu nguồn bắt buộc → **từ chối và chỉ đường** chạy lệnh tạo nguồn trước, chứ không tự nghĩ ra nội dung. Gặp chỗ nghiệp vụ còn thiếu (một con số, một quy tắc) → đánh dấu **câu hỏi mở** (open question) trả lại để làm rõ, không "đoán đại".

2. **Xem trước rồi mới ghi.** Trước khi ghi file, cả ba đều cho bạn xem trước kế hoạch (sẽ tạo/sửa những gì) và chờ bạn gật đầu. Nếu file đã có sẵn, chúng cho bạn xem phần thay đổi (dạng so sánh trước/sau) rồi mới ghi đè.

3. **Gom vào một file index chung cho mỗi loại.** Thay vì rải metadata khắp nơi, mỗi loại có một "sổ cái": use case + diagram chung `{feature}-usecase-index.md`, còn story dùng `{feature}-story-index.md`. Nhìn một chỗ là thấy toàn bộ trạng thái.

---

## 7. Ví dụ thực tế — đi qua cả ba

Chị **Lan**, một BA phụ trách tính năng "hoàn tiền" (`refund`), vừa hoàn tất bản đặc tả SRS (đã có các yêu cầu FR). Giờ chị cần chuyển từ "đặc tả" sang "sẵn sàng giao dev". Chị đi qua ba lệnh:

1. **`/usecase refund`** — chị viết ra các kịch bản người dùng chi tiết. Hệ thống đọc SRS, gợi ý các mục tiêu ở "mức mặt biển": *"Gửi yêu cầu hoàn tiền"* (của Khách) và *"Duyệt hoàn tiền"* (của Nhân viên). Nó **không** tách "Kiểm chứng từ" thành use case riêng — đó chỉ là một bước bên trong. Mỗi use case ghi rõ: đường chuẩn, các nhánh lỗi (yêu cầu quá hạn, thiếu chứng từ), và đảm bảo khi thành công/thất bại. Kết quả: hai file `uc-*.md` + một bảng ma trận trong file index.

2. **`/usecase-diagram --feature refund`** — chị vẽ bức tranh tổng. Hệ thống **đọc lại** hai use case vừa tạo, nhận ra hai actor (Khách, Nhân viên) và vẽ một hình gọn: khung "System: refund" với hai use case bên trong, hai actor bên ngoài nối vào. Nó không tự thêm quan hệ include/extend vì không có bằng chứng rõ. Ảnh `.svg` được nhúng thẳng vào **cùng file index** với bảng use case ở bước 1.

3. **`/userstory refund`** — chị chia việc cho backlog. Hệ thống cắt theo **kết quả nghiệp vụ nhỏ nhất**: story *"Khách gửi yêu cầu hoàn tiền"*, story *"Nhân viên duyệt/từ chối yêu cầu"*... Một FR mô tả ngưỡng thời hạn hoàn tiền còn mơ hồ (không nói rõ bao nhiêu ngày) → hệ thống **không bịa** mà sinh story nháp + đánh **câu hỏi mở** "thời hạn hoàn tiền là bao nhiêu ngày?" để chị làm rõ với PO. Xong, nó hỏi chị: *"Tạo tiêu chí chấp nhận (AC) luôn không?"* — chị gõ `Y`, và `/ac` chạy tiếp.

Cuối chặng, chị Lan có: kịch bản chi tiết (đọc để hiểu), một bức tranh tổng (nhìn để nắm phạm vi), và một backlog các story kèm tiêu chí kiểm thử (giao được cho dev) — tất cả truy vết ngược về đúng các yêu cầu FR ban đầu.

---

## Xem thêm

Muốn hiểu sâu từng lệnh, đọc file explainer riêng:

- `explain-skills/usecase.md` — `/usecase` (viết kịch bản người dùng chi tiết, chuẩn Cockburn).
- `explain-skills/usecase-diagram.md` — `/usecase-diagram` (vẽ bức tranh tổng quan actor + use case).
- `explain-skills/userstory.md` — `/userstory` (chia công việc thành user story cho backlog).

Các lệnh liên quan ở hai đầu dây chuyền:

- `.claude/skills/srs/SKILL.md` — `/srs` sinh ra SRS (FR). `/userstory` luôn đọc SRS; `/usecase-diagram` đọc SRS hoặc danh mục use case; `/usecase` đọc SRS khi ở chế độ diễn giải, còn chế độ khám phá thì chạy trước cả SRS (và giúp dựng nên SRS).
- Sau `/userstory` thường là `/ac` (tiêu chí chấp nhận) — biến story thành điều kiện kiểm thử pass/fail.
