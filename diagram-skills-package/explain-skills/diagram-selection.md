---
type: skill-explainer
skill: diagram-selection
updated: 2026-07-14
---

# Chọn sơ đồ nào? — bàn chỉ đường cho mọi loại sơ đồ

> Tài liệu này là **điểm bắt đầu** khi bạn biết mình cần "vẽ một cái gì đó" nhưng **chưa biết nên vẽ loại sơ đồ nào**. Nó chỉ đường tới đúng lệnh — rồi bạn đọc file explainer riêng của lệnh đó (hoặc file "so sánh trong họ") để hiểu sâu. Nói cách khác: đây là *tấm bản đồ tổng*, các file kia là *đường đi chi tiết*.

## 1. Vì sao cần một tài liệu chỉ đường riêng?

Bộ công cụ này có **rất nhiều lệnh vẽ sơ đồ** — mỗi lệnh mạnh ở một loại. Vấn đề thường gặp không phải "lệnh này chạy thế nào" (cái đó đã có explainer riêng), mà là câu hỏi *đứng trước* đó: **"Việc tôi đang cần mô tả thì nên vẽ bằng loại sơ đồ nào?"**

Chọn nhầm loại sơ đồ thì mất công vẽ lại từ đầu — ví dụ bạn muốn cho thấy "một đối tượng đi qua các trạng thái nào" mà lại đi vẽ sơ đồ trao đổi giữa các bên, thì hình ra sẽ không trả lời đúng câu hỏi bạn cần.

Tài liệu này giải bài toán đó: bạn mô tả **tình huống nghiệp vụ** của mình, nó chỉ cho bạn **loại sơ đồ đúng** và **lệnh tương ứng**.

> Một điều cần phân biệt ngay: có một file khác tên gần giống — `.claude/rules/diagram-selection.md`. File đó là **quy tắc cho máy** (giúp hệ thống tự chọn engine lúc chạy), viết bằng ngôn ngữ kỹ thuật. File bạn đang đọc là **bản dành cho người**, giải thích cùng chuyện đó bằng lời thường.

---

## 2. Sáu câu hỏi để chọn đúng loại sơ đồ

Cách nhanh nhất: hỏi **"cái tôi muốn cho người khác thấy là gì?"** rồi so với sáu nhóm dưới đây. Mỗi nhóm trả lời một *kiểu câu hỏi nghiệp vụ* khác nhau.

| Cái bạn muốn cho thấy | Ví dụ | Loại sơ đồ | Lệnh |
|---|---|---|---|
| Nhiều bên trao đổi qua lại **theo thứ tự thời gian** — ai gọi ai trước, trả về gì, rồi tới bước nào | đăng nhập, thanh toán, gọi dịch vụ ngoài | Sơ đồ trình tự | `/sequence` |
| Một đối tượng đi qua các **trạng thái** nào, và chuyển từ trạng thái này sang kia khi nào | Tài khoản: chưa xác thực → đã xác thực → bị khóa | Sơ đồ trạng thái | `/state` |
| Một **quy trình** chạy thế nào — có những bước gì, ai làm bước nào, rẽ nhánh ra sao | duyệt hoàn tiền, onboarding nhiều cấp | Sơ đồ quy trình | xem **họ activity** (mục 3) |
| **Toàn cảnh** tính năng — có những ai (vai trò) và họ làm được những việc gì trong hệ thống | bức tranh phạm vi lúc kickoff với stakeholder | Sơ đồ ca sử dụng | `/usecase-diagram` |
| Tính năng **lưu** những loại thông tin gì, và chúng gắn với nhau ra sao | Khách hàng — Đơn hàng — Giao dịch | Sơ đồ dữ liệu | xem **họ ERD** (mục 4) |
| Bức tranh **kiến trúc** — các thành phần / dịch vụ / kho dữ liệu của hệ thống lồng vào nhau thế nào | app gọi những dịch vụ nào, dữ liệu nằm ở đâu | Sơ đồ kiến trúc | `/d2-architect` |

Một câu để nhớ: **thời gian → trình tự; trạng thái → state; quy trình → activity; phạm vi → ca sử dụng; dữ liệu → ERD; kiến trúc → architecture.**

Hai trong sáu nhóm — **quy trình** và **dữ liệu** — mỗi nhóm lại có **nhiều lệnh** (cùng vẽ một loại nhưng bằng công cụ/độ chi tiết khác nhau). Với hai nhóm này, sau khi biết mình cần loại nào, bạn đọc tiếp mục 3 (họ activity) hoặc mục 4 (họ ERD) để chọn đúng lệnh trong họ.

---

## 3. Nhóm "quy trình" có bốn lựa chọn — chọn thế nào

Khi bạn đã biết mình cần **sơ đồ quy trình** (các bước, ai làm bước nào, rẽ nhánh), thì có ba lệnh cùng vẽ được (`/activity`, `/activity-swimlane`, `/d2-activity`) cộng một lựa chọn chuyên biệt (`/bpmn`) — chọn theo bảng nhanh này:

| Bạn cần | Chọn |
|---|---|
| Quy trình **gọn, 1-2 vai trò**, muốn hình **nhúng thẳng vào tài liệu** (mở GitHub/Obsidian là hiện) | `/activity` |
| Quy trình **nhiều vai trò**, nhiều qua lại giữa các bên, cần thấy rõ **"ai làm bước nào"** (phân làn thật) ⭐ mặc định | `/activity-swimlane` |
| Quy trình **nhiều nhánh** nhưng ít giao cắt, cần một **file ảnh riêng** đẹp để dán slide / xuất ra | `/d2-activity` |
| Quy trình cần **chuẩn quốc tế (OMG)** hoặc mở bằng phần mềm quản lý quy trình (Camunda, Bizagi) | `/bpmn` |

Ranh giới quan trọng nhất trong họ này: **số vai trò tham gia**. Nhiều vai trò giao cắt → `/activity-swimlane` (nó giữ mỗi vai một "làn" thẳng cột). Muốn hiểu vì sao và xem so sánh đầy đủ, đọc `explain-skills/activity-family.md`.

---

## 4. Nhóm "dữ liệu" có ba lệnh — chọn thế nào

Khi bạn đã biết mình cần **sơ đồ dữ liệu** (bảng thông tin + liên hệ), có ba lệnh cùng vẽ — khác nhau ở **kiểu vẽ** và **độ chi tiết**:

| Bạn cần | Chọn |
|---|---|
| Hình **nhúng thẳng vào tài liệu** để BA/stakeholder đọc (nhẹ, không cần cài công cụ) | `/erd` |
| **Cùng nội dung như `/erd`, chỉ khác kiểu vẽ** — một **file hình riêng** (cần cài công cụ D2) | `/d2-erd` |
| **Bàn giao cho dev**: kiểu database thật, danh sách lựa chọn, **xuất ra mã SQL**, chia sẻ trên web dbdiagram.io | `/dbdiagram` |

Ranh giới quan trọng: `/erd` và `/d2-erd` chỉ khác **kiểu vẽ** (không cái nào "đẹp hơn"); còn `/dbdiagram` khác về **độ chi tiết** (gần dev nhất). Muốn hiểu sâu và xem so sánh đầy đủ, đọc `explain-skills/erd-family.md`.

---

## 5. Bảng "tình huống thật → nên vẽ gì"

Đôi khi dễ chọn hơn nếu nhìn tình huống cụ thể. Vài ví dụ hay gặp:

| Tình huống bạn đang gặp | Nên vẽ | Lệnh |
|---|---|---|
| "Muốn ghi lại luồng đăng nhập bằng Google: người dùng bấm nút → hệ thống gọi Google → Google trả về → hệ thống tạo phiên" | Sơ đồ trình tự (nhiều bên, theo thời gian) | `/sequence` |
| "Muốn ghi lại một đơn hàng đi qua những trạng thái nào: chờ → đã trả → đã giao → đã huỷ" | Sơ đồ trạng thái | `/state` |
| "Muốn mô tả quy trình duyệt hoàn tiền qua tay Khách, Hệ thống, Nhân viên, Quản lý" | Sơ đồ quy trình phân làn (nhiều vai trò) | `/activity-swimlane` |
| "Muốn mô tả quy trình đổi mật khẩu — chỉ người dùng và hệ thống, rất gọn, để nhúng vào tài liệu" | Sơ đồ quy trình gọn, nhúng thẳng | `/activity` |
| "Muốn một hình tổng cho stakeholder xem lúc kickoff: có những ai và làm được gì trong tính năng" | Sơ đồ ca sử dụng | `/usecase-diagram` |
| "Muốn ghi lại tính năng thanh toán lưu những loại thông tin gì và chúng liên hệ ra sao, để dev đọc trong tài liệu" | Sơ đồ dữ liệu nhúng | `/erd` |
| "Muốn bàn giao cấu trúc dữ liệu cho dev dựng database, kèm file chạy được ngay" | Sơ đồ dữ liệu gần dev, xuất SQL | `/dbdiagram` |
| "Muốn một bức tranh kiến trúc: app gọi những dịch vụ nào, dữ liệu nằm ở đâu" | Sơ đồ kiến trúc | `/d2-architect` |

Nếu tình huống của bạn không khớp hàng nào, quay lại **sáu câu hỏi ở mục 2** — trong phạm vi bộ lệnh này, hầu hết tình huống thực tế đều rơi vào một (đôi khi vài) trong sáu nhóm đó.

---

## 6. Hai nguyên tắc chung — đọc trước khi vẽ

**Vẽ để giao tiếp, không phải để khoe.** Đừng vẽ sơ đồ cho *mọi* thứ chỉ vì vẽ được. Một sơ đồ chỉ đáng vẽ khi nó **giúp ai đó hiểu nhanh hơn** so với đọc chữ. Quy trình đơn giản chỉ vài bước tuyến tính thì viết vài dòng đánh số là đủ — không cần một sơ đồ quy trình cầu kỳ. Bảng hai trạng thái (bật/tắt) thì một câu là xong — không cần sơ đồ trạng thái.

**Một tính năng phức tạp thường cần NHIỀU sơ đồ bổ trợ nhau, không phải chọn một.** Các loại sơ đồ trả lời các câu hỏi khác nhau, nên chúng **không loại trừ nhau**. Ví dụ một tính năng thanh toán đầy đủ có thể cần: một sơ đồ ca sử dụng (toàn cảnh) + vài sơ đồ trình tự (mỗi luồng) + một sơ đồ quy trình phân làn (luồng hoàn tiền) + một sơ đồ trạng thái (vòng đời đơn hàng) + một sơ đồ dữ liệu (Đơn hàng / Giao dịch / Hoàn tiền). Câu hỏi không phải "chọn cái nào" mà "cần những cái nào cho đủ để mọi người hiểu".

| Tính năng ví dụ | Bộ sơ đồ thường dùng |
|---|---|
| Đăng nhập / đăng ký (có OAuth, xác thực email) | Ca sử dụng (tổng quan) + Trình tự (mỗi luồng) + Trạng thái (vòng đời Tài khoản) |
| Thanh toán / đặt hàng | Ca sử dụng + Trình tự (luồng trả tiền) + Quy trình phân làn (hoàn tiền) + Trạng thái (đơn hàng) + Dữ liệu |
| Quy trình duyệt nhiều cấp | Ca sử dụng + Quy trình phân làn (duyệt) + Trạng thái (yêu cầu) |

---

## 7. Ví dụ thực tế — dùng bàn chỉ đường này

Chị **Hà**, một BA mới nhận tính năng "đặt lịch học" cho app học tiếng Anh, ngồi trước màn hình với một mớ ghi chú nghiệp vụ và không biết bắt đầu vẽ từ đâu. Chị mở tài liệu này và đi theo **sáu câu hỏi ở mục 2**:

1. Chị có một luồng "học viên đặt lịch → hệ thống kiểm lịch trống của giáo viên → gửi xác nhận qua email". Đây là **nhiều bên trao đổi theo thời gian** → chị chọn `/sequence`.

2. Chị nhận ra một buổi học đi qua các trạng thái: *đã đặt → đã xác nhận → đã diễn ra → đã huỷ*. Đây là **vòng đời trạng thái** → chị chọn `/state`.

3. Chị có quy trình "xin đổi lịch" qua tay Học viên, Hệ thống, và Giáo viên (giáo viên phải đồng ý). Đây là **quy trình nhiều vai trò** → chị mở mục 3, thấy "nhiều vai trò → `/activity-swimlane`", và chọn nó.

4. Chị cần một hình tổng cho buổi họp kickoff với trưởng nhóm sản phẩm: có những ai (Học viên, Giáo viên, Quản trị) làm được gì. Đây là **toàn cảnh phạm vi** → chị chọn `/usecase-diagram`.

5. Cuối cùng chị cần ghi lại tính năng lưu những gì (Buổi học, Lịch trống, Học viên, Giáo viên) để dev đọc. Đây là **dữ liệu**; vì chị chỉ cần dev đọc trong tài liệu, chị mở mục 4 và chọn `/erd` (chưa cần tới `/dbdiagram` vì chưa tới lúc bàn giao dựng database).

Kết quả: chị Hà không vẽ bừa. Chị có đúng năm sơ đồ, mỗi cái trả lời một câu hỏi khác nhau, bổ trợ nhau — chứ không phải năm cách vẽ cùng một thứ. Và chị chọn được chúng chỉ bằng cách so tình huống của mình với sáu nhóm, không cần biết gì về công cụ vẽ bên dưới.

---

## Xem thêm

Sau khi bàn chỉ đường này giúp bạn chọn **loại** sơ đồ, đọc tiếp để hiểu sâu từng lệnh:

**Các file "so sánh trong họ" (khi một nhóm có nhiều lệnh):**

- `explain-skills/activity-family.md` — chọn giữa `/activity`, `/activity-swimlane`, `/d2-activity` (+ `/bpmn`) cho **sơ đồ quy trình**.
- `explain-skills/usecase-family.md` — phân biệt `/usecase`, `/usecase-diagram`, `/userstory` (kịch bản chữ / toàn cảnh hình / chia việc backlog).
- `explain-skills/erd-family.md` — chọn giữa `/erd`, `/d2-erd`, `/dbdiagram` cho **sơ đồ dữ liệu**.

**Các explainer từng lệnh (nhóm chỉ có một lệnh):**

- `explain-skills/sequence.md` — `/sequence` (trao đổi nhiều bên theo thời gian).
- `explain-skills/state.md` — `/state` (vòng đời trạng thái của một đối tượng).
- `explain-skills/usecase-diagram.md` — `/usecase-diagram` (bức tranh tổng actor + ca sử dụng).
- `explain-skills/d2-architect.md` — `/d2-architect` (sơ đồ kiến trúc hệ thống).
- `explain-skills/bpmn.md` — `/bpmn` (chuẩn quốc tế BPMN, mở bằng phần mềm quản lý quy trình).

**Quy tắc gốc (dành cho máy / người muốn chi tiết kỹ thuật):**

- `.claude/rules/diagram-selection.md` — bảng chọn engine đầy đủ + lưu ý cú pháp Mermaid an toàn. Đây là bản kỹ thuật; file bạn vừa đọc là bản diễn giải cho người.
