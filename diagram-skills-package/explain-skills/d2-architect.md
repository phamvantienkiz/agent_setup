---
type: skill-explainer
skill: d2-architect
updated: 2026-07-14
---

# `/d2-architect` là gì và nó chạy như thế nào?

## 1. Dùng để làm gì, khi nào nên gõ lệnh này

`/d2-architect` vẽ ra **bức tranh tổng thể của một hệ thống** — kiểu sơ đồ cho người ta nhìn phát là hiểu "hệ thống này gồm những khối gì, mỗi khối chứa cái gì bên trong, nó gọi ra những dịch vụ bên ngoài nào, và dữ liệu chạy qua lại giữa chúng ra sao". Trong nghề gọi là *sơ đồ kiến trúc* (architecture diagram).

Hình dung nó giống **bản đồ một khu phố nhìn từ trên cao**: bạn thấy các toà nhà (các khối lớn: phần giao diện người dùng, phần xử lý phía sau, kho dữ liệu), thấy bên trong mỗi toà có những phòng gì (các bộ phận con), và thấy các con đường nối giữa chúng (dữ liệu đi từ đâu tới đâu). Nó **không** vẽ chi tiết từng viên gạch — mục tiêu là để cả người nghiệp vụ lẫn dev cùng nhìn và hiểu **bối cảnh chung**, chứ không phải bản thiết kế thi công.

Chữ "d2" trong tên lệnh là tên công cụ vẽ mà lệnh này dùng. Điểm khiến D2 hợp với loại sơ đồ này: nó vẽ được các **khối lồng trong khối** rất gọn — một "toà nhà Backend" bên trong có "phòng Auth", "phòng Xử lý chính", "kho Dữ liệu"... tất cả nằm ngăn nắp trong một khung lớn. Đây chính là chỗ mà công cụ Mermaid (dùng ở nhiều lệnh vẽ khác) làm không đẹp — nên với riêng loại sơ đồ kiến trúc, D2 là lựa chọn hợp lý hơn.

Vài tình huống điển hình nên dùng `/d2-architect`:

- Bạn cần một **hình tổng quan hệ thống** để đưa vào tài liệu, dùng lúc kickoff dự án, hoặc giải thích cho người mới "hệ thống mình gồm những phần nào, nối với nhau ra sao".
- Bạn muốn cho thấy rõ **hệ thống gọi ra những dịch vụ bên ngoài nào** (đăng nhập Google, cổng thanh toán, dịch vụ gửi email...) và mỗi cái dùng để làm gì.

Gõ lệnh đơn giản như:

```
/d2-architect --feature auth
```

hoặc mô tả cả hệ thống tổng thể (không gắn vào một tính năng cụ thể):

```
/d2-architect "hệ thống học tiếng Anh: web/mobile, backend, kho dữ liệu, gọi Google đăng nhập và AI chấm phát âm"
```

**Một câu để nhớ:** `/d2-architect` vẽ **bản đồ tổng thể của hệ thống** ở tầm dễ hiểu — có những khối gì, lồng nhau ra sao, gọi dịch vụ ngoài nào — để mọi người cùng nắm bối cảnh. Nó vẽ *bối cảnh*, không vẽ *bản thiết kế thi công*.

---

## 2. Toàn bộ luồng chạy — sơ đồ

```
 BẠN GÕ LỆNH
 /d2-architect --feature auth   (hoặc mô tả cả hệ thống)
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 0 — Kiểm tra công cụ vẽ đã cài chưa               │
 │  Cần công cụ "D2" cài sẵn trên máy mới vẽ được. Chưa  │
 │  có → DỪNG ngay, chỉ bạn 1 dòng lệnh cài. KHÔNG vẽ    │
 │  nửa vời, không tạo file rỗng.                        │
 └──────────────────────────────────────────────────────┘
        │  (đã có công cụ → đi tiếp)
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 1 — Xác định vẽ cho ai                            │
 │  Vẽ cho 1 tính năng cụ thể? → để trong thư mục tính   │
 │  năng đó. Vẽ cả hệ thống tổng? → để vào thư mục dùng  │
 │  chung. Tính năng chưa có → tự đặt tên rồi tạo mới.   │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 2 — Hiểu hệ thống cho đúng                        │
 │  Đọc tài liệu "tổng quan hệ thống" nếu có (nguồn tốt  │
 │  nhất), hoặc bản đặc tả tính năng. Thiếu / mập mờ →   │
 │  HỎI bạn, KHÔNG tự bịa ra khối hay dịch vụ không có.  │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 3 — Bóc tách thành khối                           │
 │  Chia ra: các khối lớn (Giao diện / Backend / ...),   │
 │  bộ phận con bên trong mỗi khối, các dịch vụ ngoài,   │
 │  và các luồng dữ liệu nối chúng.                      │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 4 — Xem trước rồi mới vẽ (xin phép)               │
 │  Mô tả bằng lời: "sẽ vẽ K khối, N bộ phận, M dịch vụ  │
 │  ngoài, các luồng chính là...". Bạn gật (Y) mới làm.  │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 5 — Vẽ + kiểm tra ra được ảnh                     │
 │  Viết mô tả sơ đồ, rồi nhờ công cụ D2 "vẽ thật" ra    │
 │  file ảnh. Vẽ lỗi → tự sửa, vẽ lại. Chỉ báo XONG khi  │
 │  đã ra được ảnh hoàn chỉnh.                           │
 └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │ BƯỚC 6 — Báo hoàn tất                                  │
 │  Cho bạn đường dẫn file ảnh (.svg) để mở xem. Ghi vào │
 │  sổ theo dõi các sơ đồ kiến trúc.                     │
 └──────────────────────────────────────────────────────┘
        │
        ▼
     HOÀN TẤT — có 1 file ảnh sơ đồ kiến trúc đứng riêng
```

---

## 3. Điểm cốt lõi: vẽ ở "tầm bối cảnh", KHÔNG vẽ chi tiết thi công

Đây là chỗ dễ hiểu nhầm nhất, nên nói kỹ. `/d2-architect` phục vụ người phân tích nghiệp vụ (BA), **không phải kỹ sư hệ thống (architect)**. Nghĩa là nó vẽ ở mức **"hệ thống gồm khối gì, gọi dịch vụ ngoài nào, dữ liệu chính chạy ra sao"** — đủ để stakeholder và dev cùng hiểu bối cảnh, và dừng ở đó.

**Nó CÓ vẽ:**

- Các khối logic lớn: phần Giao diện (web/mobile), phần Backend (xử lý phía sau), kho Dữ liệu.
- Các bộ phận con theo chức năng nghiệp vụ: bộ phận đăng nhập, bộ phận xử lý chính, bộ phận nhập liệu...
- Các dịch vụ bên ngoài theo **tên thật + mục đích**: "Google — để đăng nhập", "cổng thanh toán", "dịch vụ gửi email".
- Các luồng dữ liệu chính, có nhãn dễ hiểu: "Giao diện gọi Backend", "Backend gọi Google để đăng nhập".

**Nó KHÔNG vẽ** những thứ thuộc về chi tiết vận hành kỹ thuật — số máy chủ chạy song song, bộ cân bằng tải, cấu hình mạng, số cổng kết nối, phiên bản phần mềm nền... Những cái đó là việc của kỹ sư hệ thống khi thực sự bắt tay xây, nằm ngoài phạm vi của một sơ đồ nghiệp vụ. Nếu bạn cần tới mức đó, đây không phải công cụ đúng.

Lý do giữ nguyên tắc này: một sơ đồ kiến trúc để **giao tiếp và thống nhất bối cảnh** thì càng gọn càng tốt. Nhồi chi tiết thi công vào chỉ làm hình rối và làm loãng thứ mà stakeholder cần thấy. Cũng vì vậy, `/d2-architect` **sẽ không hỏi bạn** những câu kiểu "chạy mấy máy chủ, mở cổng nào" — nó chỉ hỏi về khối, bộ phận, dịch vụ ngoài và luồng dữ liệu bằng ngôn ngữ nghiệp vụ.

---

## 4. Vì sao dùng D2 chứ không phải Mermaid? (nói thật, không tô vẽ)

Trong bộ công cụ này có nhiều lệnh vẽ sơ đồ, phần lớn dùng Mermaid. Riêng `/d2-architect` dùng D2 vì một lý do cụ thể, và cũng cần nói cho rõ để tránh hiểu nhầm.

Loại sơ đồ kiến trúc có một đặc thù: nó cần vẽ **khối lồng trong khối** — một khung "Backend" lớn, bên trong chứa mấy ô nhỏ (Auth, Xử lý chính, kho Dữ liệu), và các ô nhỏ đó lại nối ra ngoài. Mermaid vẽ kiểu lồng nhau này ra **không gọn, dễ rối**. D2 thì xử lý chuyện lồng khối này ngăn nắp hơn hẳn — đó là lý do thật sự để chọn nó cho riêng loại sơ đồ này.

> **Một chỗ cần nói thẳng để khỏi hiểu lầm:** D2 hợp với sơ đồ kiến trúc **không có nghĩa nó "đẹp hơn" hay "xịn hơn" mọi công cụ khác ở mọi loại hình.** Nó chỉ là **một cách vẽ khác, mạnh đúng ở khoản khối-lồng-khối này.** Với các loại sơ đồ khác (quy trình nhiều vai trò chẳng hạn), công cụ khác lại làm tốt hơn. Nói cách khác: chọn `/d2-architect` vì bạn cần **vẽ kiến trúc hệ thống**, chứ không phải vì nghĩ "D2 là đẹp nhất".

Ngoài chuyện lồng khối, D2 còn giúp vài thứ nhỏ cho dễ đọc: kho dữ liệu được vẽ thành hình trụ (giống biểu tượng ổ cứng quen thuộc), người dùng vẽ thành hình người, và cụm dịch vụ bên ngoài được **khoanh bằng khung viền đứt nét** để thấy ngay "cái này nằm ngoài tầm kiểm soát của mình".

---

## 5. Kết quả để ở đâu? Vẽ cho 1 tính năng hay cho cả hệ thống?

`/d2-architect` linh hoạt ở chỗ nó vẽ được cả **kiến trúc của một tính năng cụ thể** lẫn **kiến trúc tổng thể của cả sản phẩm** — và để kết quả ở hai chỗ khác nhau tuỳ theo:

- Nếu bạn vẽ cho **một tính năng** (ví dụ tính năng đăng nhập), kết quả nằm trong thư mục riêng của tính năng đó.
- Nếu bạn vẽ **bức tranh cả hệ thống** (không thuộc riêng tính năng nào), kết quả nằm trong một thư mục **dùng chung** của cả dự án — vì nó là tài sản chung, không nên nhét vào một tính năng lẻ.

Dù ở đâu, mỗi lần vẽ đều cho ra:

- Một file "bản gốc" (đuôi `.d2`) — chứa phần mô tả bằng chữ, để sau này sửa lại được.
- Một file ảnh (đuôi `.svg`) — chính là hình đã vẽ xong, mở bằng trình duyệt hoặc phần mềm xem tài liệu là thấy ngay, không cần cài thêm gì.
- Một dòng ghi vào "sổ theo dõi" — liệt kê các sơ đồ kiến trúc đã vẽ, để dễ tra.

Nếu vẽ lại cho một sơ đồ **đã có sẵn**, hệ thống tự hiểu là đang **cập nhật bản cũ** — cho bạn xem trước phần thay đổi rồi mới ghi đè, và **không đụng chạm** tới các sơ đồ khác.

> **Một nguồn nên có trước để vẽ đúng:** dự án có thể có sẵn một tài liệu "tổng quan hệ thống" mô tả các khối và cách chúng nối nhau. Nếu có, đây là nguồn tốt nhất để `/d2-architect` vẽ chính xác. Chưa có thì hệ thống sẽ hỏi bạn để dựng — hoặc bạn có thể tạo tài liệu tổng quan đó trước rồi vẽ sẽ nhàn hơn.

---

## 6. Vì sao phải kiểm tra công cụ và "vẽ ra được ảnh mới báo xong"?

Hai chi tiết trong cách chạy giúp bạn yên tâm về kết quả — giống hệt các lệnh cùng họ D2.

**Kiểm tra công cụ trước tiên.** Khác với nhiều lệnh chạy hoàn toàn bên trong hệ thống, `/d2-architect` cần công cụ "D2" được cài sẵn trên máy tính của bạn thì mới vẽ được. Vì vậy việc đầu tiên nó làm là kiểm tra: công cụ này có chưa? Chưa có thì nó **dừng lại ngay và chỉ cho bạn đúng một dòng lệnh để cài** — chứ không cố vẽ nửa vời rồi tạo ra file hỏng.

**Vẽ ra được ảnh mới báo xong.** Sau khi viết xong phần mô tả sơ đồ, hệ thống nhờ D2 "vẽ thật" ra file ảnh. Nếu phần mô tả có lỗi khiến vẽ không ra (lỗi thường gặp: một cái tên có ký tự đặc biệt chưa xử lý), nó **tự đọc lỗi, sửa lại, vẽ lại** (thử vài lần). Chỉ báo "hoàn tất" khi đã có file ảnh đàng hoàng — chứ không báo xong khi ảnh còn hỏng hoặc mở ra trắng trơn.

Một điều `/d2-architect` **không** làm: nó không có kiểu "vẽ ra rồi sửa tới sửa lui nhiều vòng ngay trong khung chat". Bản mô tả sơ đồ không hiện thành hình trong chat, nên bạn xem hình từ chính file ảnh. Muốn chỉnh, gọi lại lệnh với yêu cầu thay đổi — hệ thống tự hiểu là đang sửa bản cũ.

---

## 7. Ví dụ thực tế

Anh **Tuấn**, một BA, chuẩn bị buổi kickoff cho dự án học tiếng Anh và cần một **hình tổng quan hệ thống** để mở đầu — cho cả nhóm (gồm cả người không rành kỹ thuật) cùng nhìn và hiểu "sản phẩm mình gồm những phần nào, nối với nhau ra sao, gọi ra những dịch vụ ngoài nào".

Anh Tuấn mở terminal, gõ:

```
/d2-architect "hệ thống học tiếng Anh: web và mobile, backend xử lý bài học, kho dữ liệu, gọi Google để đăng nhập và một dịch vụ AI để chấm phát âm"
```

1. Hệ thống kiểm tra trước: công cụ D2 đã cài trên máy chưa? Có rồi — đi tiếp. (Nếu chưa, nó đã dừng ngay và đưa anh một dòng lệnh cài đặt.)

2. Vì đây là mô tả **cả hệ thống tổng thể** (không gắn riêng tính năng nào), hệ thống quyết định để kết quả vào thư mục dùng chung của dự án.

3. Nó tìm tài liệu "tổng quan hệ thống" — chưa có, nên **hỏi lại** anh Tuấn vài câu để hiểu đúng: *"Phần Backend gồm những bộ phận con nào? Dịch vụ AI chấm phát âm là dịch vụ ngoài hay tự làm trong hệ thống?"* Anh trả lời bằng ngôn ngữ nghiệp vụ, không phải bận tâm chuyện máy chủ hay cổng kết nối.

4. Hệ thống mô tả bằng lời: *"Em sẽ vẽ sơ đồ kiến trúc: 3 khối lớn (Giao diện web/mobile, Backend, Dịch vụ ngoài), trong Backend có 3 bộ phận (Đăng nhập, Xử lý bài học, Kho dữ liệu), 2 dịch vụ ngoài (Google đăng nhập, AI chấm phát âm). Luồng chính: Giao diện gọi Backend, Backend gọi Google và AI. Apply?"* Anh Tuấn gõ `Y`.

5. Hệ thống viết phần mô tả sơ đồ rồi nhờ D2 vẽ thật. Lần đầu bị lỗi nhỏ (tên "AI (chấm phát âm)" có dấu ngoặc chưa xử lý) — nó tự sửa, vẽ lại. Lần này ra ảnh hoàn chỉnh.

6. Hệ thống báo xong, đưa đường dẫn file ảnh. Anh Tuấn mở bằng trình duyệt: thấy một sơ đồ gọn — khối Backend lớn lồng ba ô con bên trong, kho dữ liệu vẽ hình trụ, cụm dịch vụ ngoài (Google, AI) khoanh khung viền đứt nét cho biết "nằm ngoài tầm kiểm soát", các mũi tên có nhãn rõ ràng.

7. Anh Tuấn đưa hình này lên slide mở đầu buổi kickoff. Cả nhóm — kể cả người không rành kỹ thuật — nhìn phát nắm được bức tranh chung của hệ thống, buổi họp đỡ mất thời gian giải thích.

Vài tuần sau, dự án thêm dịch vụ gửi email nhắc học. Anh Tuấn chỉ cần gõ lại lệnh và nói thêm dịch vụ đó — hệ thống tự hiểu là đang cập nhật bản cũ, cho anh xem trước phần chỉnh rồi vẽ lại hình mới.

---

## Xem thêm

Tài liệu này chỉ giải thích ý tưởng và luồng chạy ở mức dễ hiểu. Muốn xem đầy đủ chi tiết kỹ thuật (công thức viết sơ đồ, cách render, các trường hợp đặc biệt), đọc file gốc: `.claude/skills/d2-architect/SKILL.md`.

Các lệnh cùng dùng công cụ D2 (họ D2):

- `explain-skills/d2-activity.md` — `/d2-activity`, vẽ **sơ đồ quy trình** bằng D2 (dàn gọn khi nhiều nhánh, file đứng riêng).
- `/d2-erd` — vẽ **sơ đồ dữ liệu** (các bảng dữ liệu và quan hệ giữa chúng) bằng D2. Cả ba lệnh D2 dùng chung một "máy vẽ" phía sau.
- Quy tắc chọn loại sơ đồ đầy đủ (khi nào dùng sơ đồ kiến trúc, khi nào dùng loại khác) nằm ở file gốc: `.claude/rules/diagram-selection.md`.
