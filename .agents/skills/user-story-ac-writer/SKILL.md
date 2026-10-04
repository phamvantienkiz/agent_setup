---
name: user-story-ac-writer
description: Sinh User Story và Acceptance Criteria chuẩn INVEST + Given-When-Then (Gherkin) cho Senior IT-BA & Product Owner, tích hợp chặt chẽ với Hệ thống Kiến trúc Tài liệu 3 Tầng (docs/implementation/{release}/backlog/). Tích hợp kỹ thuật bóc tách kịch bản từ sơ đồ luồng (Sequence/Activity Diagram), kiểm tra độ bao phủ nhánh lỗi (Fact-list Coverage Check), truy vết nguồn gốc (Traceability), quản lý câu hỏi mở (OQ) và đặc biệt thiết lập Architecture Guardrails để ngăn chặn AI Coding Agent phá hủy hệ thống.
---

# User Story & Acceptance Criteria Writer (Agent-Safe & 3-Layer Edition)

## 1. Mục đích & Vai trò

Skill này biến một Senior IT-BA thành chuyên gia chuyển đổi yêu cầu nghiệp vụ cấp cao (PRD/Use Cases/Sơ đồ luồng) thành các **User Story độc lập, có thể ước lượng và nghiệm thu rõ ràng (chuẩn INVEST)**, kèm theo **Acceptance Criteria (AC) bao phủ 100% các nhánh rẽ và tình huống lỗi**.

Đặc biệt, skill này tuân thủ tuyệt đối cấu trúc tài liệu của skill [`documentation`](../documentation/SKILL.md) và thiết lập **"Rào chắn kiến trúc (Architecture Guardrails)"** bên trong từng Story để triệt tiêu hoàn toàn hiện tượng **"Agent Amnesia" (Coding Agent bị quên kiến trúc, tự tiện sinh code phá vỡ hệ thống)**.

### Nguyên tắc vàng của BA thực thụ:
1. **Lưu đúng Tầng Implementation**: Toàn bộ Sổ cái và User Stories phải nằm trong `docs/implementation/{release}/backlog/`. Không tạo thư mục tùy tiện.
2. **Rào chắn kiến trúc (Architecture Guardrails)**: Mỗi User Story bắt buộc phải trích dẫn các ràng buộc bất biến từ `docs/architecture/` (Data schema, Security RBAC, Design principles) để buộc Coding Agent phải tuân thủ trước khi viết code.
3. **Bóc tách từ Sơ đồ (Diagram-driven AC)**: AC không được viết bằng cảm tính. Phải đối chiếu trực tiếp với các nhánh rẽ (`alt`/`opt` trong Sequence Diagram, ngã rẽ hình thoi trong Activity Diagram ở `technical-design.md`) để bóc tách các kịch bản ngoại lệ.
4. **Fact-list Coverage Check**: Đảm bảo mọi Actor, mọi điều kiện biên và mọi nhánh lỗi xuất hiện trong sơ đồ/PRD đều có ít nhất 1 scenario AC tương ứng.
5. **No-guessing & Open Questions (OQ)**: Tuyệt đối không tự bịa số liệu nghiệp vụ. Nếu thiếu, đánh mã `[OQ]` yêu cầu PO chốt.
6. **Approval Gate (L1/L2)**: Xem trước kế hoạch (L1) và xem diff (L2) trước khi ghi file.

---

## 2. Quy trình làm việc (BA Story & AC Workflow)

```
[docs/implementation/{release}/prd.md & technical-design.md]
        │
        ▼
Bước 1: Xác định Mode, Release Target & Đọc Nguồn sự thật
        │
        ▼
Bước 2: Trích xuất Fact-list Nghiệp vụ (Actors, Decision Points, Alt/Error Paths)
        │
        ▼
Bước 3: Cắt lát User Story theo chuẩn INVEST (Split nếu quá to)
        │
        ▼
Bước 4: Bóc tách Acceptance Criteria theo Given-When-Then (từ Fact-list)
        │
        ▼
Bước 5: Thiết lập Architecture Guardrails (Chống Coding Agent phá vỡ hệ thống)
        │
        ▼
Bước 6: Fact-list Coverage Check & Quản lý OQ
        │
        ▼
Bước 7: Approval Gate L1/L2 ──► Xuất Sổ cái Backlog & File Story
```

---

### Bước 1: Xác định Mode, Release Target & Đọc Nguồn sự thật

1. **Xác định Release đích:** Xác định rõ story này thuộc đợt phát hành nào (`release-1`, `release-2`...).
2. **Đọc Nguồn sự thật (No-re-ask):**
   - Đọc PRD đợt phát hành: `docs/implementation/{release}/prd.md`.
   - Đọc thiết kế kỹ thuật/sơ đồ luồng: `docs/implementation/{release}/technical-design.md` (hoặc các sơ đồ sequence/activity vừa vẽ).
   - Đọc các tài liệu kiến trúc liên quan tại `docs/architecture/`:
     - Database schema: `05-data-architecture.md`
     - Security/Auth: `07-security-architecture.md`
     - Design Patterns: `09-design-principles.md`

---

### Bước 2: Trích xuất Fact-list Nghiệp vụ (Fact-list Extraction)

Trước khi viết, BA tự động lập bảng **Fact-list** từ tài liệu và sơ đồ luồng:

- **Actors/Participants:** Ai tham gia trực tiếp? (vd: Khách hàng, Quản trị viên, Cổng Momo...).
- **Main Success Steps (Happy path):** Các bước theo trình tự chuẩn khi mọi thứ suôn sẻ.
- **Decision Points & Alternative Paths (Nhánh phụ):** Các ngã rẽ điều kiện (vd: thanh toán bằng thẻ vs ví điện tử; khách đăng nhập vs khách vãng lai).
- **Error & Failure Paths (Nhánh lỗi):** Bóc tách từ các khối `alt/opt` hoặc rẽ nhánh thất bại (vd: sai OTP > 3 lần, cổng thanh toán timeout, không đủ số dư, hủy ngang).
- **Business Constraints:** Các quy tắc số liệu bắt buộc (vd: link hết hạn sau 24h, hoàn tiền trong 7 ngày).

---

### Bước 3: Cắt lát User Story theo chuẩn INVEST

Format chuẩn của User Story:
```markdown
**US-[RELEASE]-[FEATURE]-[NNN]**: [Động từ + Đối tượng nghiệp vụ cụ thể]
**Traceability**: Map to [FR-xxx] trong `docs/implementation/{release}/prd.md`
**Priority**: P0 (Must) / P1 (Should) / P2 (Could)

**As a** [persona cụ thể, có ngữ cảnh; không dùng "user" chung chung]
**I want to** [hành động nghiệp vụ cụ thể, mang lại kết quả quan sát được]
**So that** [giá trị kinh doanh thực tế, không lặp lại hành động]
```

#### Đánh giá Checklist INVEST trước khi chốt Story:
- **I (Independent)**: Có thể bàn giao và triển khai độc lập không bị kẹt phụ thuộc cứng không?
- **N (Negotiable)**: Để không gian trao đổi về giải pháp triển khai; không trói buộc chi tiết công nghệ (không ghi gọi API nào, dùng class gì).
- **V (Valuable)**: Mang lại giá trị trực tiếp cho người dùng hoặc nghiệp vụ.
- **E (Estimable)**: Dev có thể ước lượng được độ phức tạp (1-3 ngày làm việc).
- **S (Small)**: Hoàn thành gọn trong 1 sprint. Nếu story quá lớn (chứa chữ "VÀ", chứa cả cụm CRUD, có > 7 AC) $\rightarrow$ **Bắt buộc Split (Cắt nhỏ)**.
- **T (Testable)**: QA có thể dựng kịch bản kiểm thử pass/fail rõ ràng thông qua Acceptance Criteria.

---

### Bước 4: Bóc tách Acceptance Criteria theo Given-When-Then

Mỗi User Story bắt buộc phải có **tối thiểu 3-5 AC**, bao quát đủ 3 nhóm kịch bản:

```markdown
### AC1: [Tên kịch bản - Happy Path / Thành công chuẩn]
- **Given** [Tiền điều kiện cụ thể: trạng thái tài khoản, dữ liệu đã có sẵn]
- **When** [Hành động người dùng thực hiện kích hoạt]
- **Then** [Kết quả nghiệp vụ mong đợi quan sát được]
- **And** [Kết quả phụ: cập nhật trạng thái, ghi nhận lịch sử, gửi thông báo]

### AC2: [Tên kịch bản - Validation & Điều kiện biên (Edge Case)]
- **Given** [Tiền điều kiện biên: vượt hạn mức, dữ liệu cận trên/cận dưới]
- **When** [Người dùng thực hiện hành động]
- **Then** [Hệ thống ngăn chặn và hiển thị thông báo nghiệp vụ rõ ràng]

### AC3: [Tên kịch bản - Negative Path / Lỗi từ bên thứ ba hoặc ngoại lệ]
- **Given** [Tiền điều kiện: cổng thanh toán phản hồi lỗi / timeout giao dịch]
- **When** [Giao dịch được xử lý]
- **Then** [Hệ thống hủy giao dịch an toàn, hoàn lại trạng thái trước đó]
- **And** [Gợi ý cho người dùng giải pháp thay thế]
```

---

### Bước 5: Thiết lập Rào chắn Kiến trúc (Architecture Guardrails for Coding Agents)

> 🛡️ **Đây là bước quan trọng nhất để chống "Agent Amnesia"**: 
> Mỗi User Story bắt buộc phải có một mục **Architecture Guardrails** trích dẫn chính xác các tài liệu bất biến từ `docs/architecture/`. Khi bàn giao Story cho Coding Agent, các liên kết này buộc Agent phải nạp ngữ cảnh kiến trúc trước khi sinh code.

BA điền đầy đủ 4 rào chắn:
1. **Data Model Invariant**: Trích dẫn `docs/architecture/05-data-architecture.md` (Quy định rõ bảng nào được phép insert/update, cấm tự tiện đổi kiểu dữ liệu cột sẵn có).
2. **Security & RBAC Guardrail**: Trích dẫn `docs/architecture/07-security-architecture.md` (Bắt buộc dùng Auth Guard hiện có, không bypass permission).
3. **Integration & API Contract**: Trích dẫn `docs/architecture/08-integration-architecture.md` (Quy ước gọi webhook/API bên ngoài).
4. **Design Principles & Repository Layout**: Trích dẫn `docs/architecture/09-design-principles.md` và `10-folder-structure.md` (Code theo pattern Repository/Service, đặt file đúng thư mục).

---

### Bước 6: Kiểm tra độ bao phủ (Coverage Check) & Quản lý OQ

Trước khi xuất tài liệu, BA thực hiện:
1. **Fact-list Coverage Check:**
   - Đối chiếu AC với Fact-list trích xuất từ sơ đồ `technical-design.md`.
   - Đảm bảo 100% các nhánh rẽ và tình huống lỗi đều có kịch bản AC.
2. **Quy tắc No-guessing & OQ:**
   - Nếu phát hiện thông số chưa rõ, tuyệt đối không tự bịa con số.
   - Đánh dấu ngay trong AC: `- And Thời gian hiệu lực là [OQ-01: Cần PO chốt thời hạn]`.

---

### Bước 7: Phê duyệt (Approval Gate L1/L2) & Xuất Sổ cái Backlog

1. **L1 Plan Preview:**
   In bản kế hoạch trước khi tạo file:
   ```markdown
   [user-story-ac-writer] Kế hoạch xuất tài liệu đợt phát hành {release}:
   - Sổ cái Backlog: docs/implementation/{release}/backlog/{feature}-story-index.md (tổng hợp N stories)
   - Chi tiết Story: docs/implementation/{release}/backlog/stories/US-001.md, US-002.md...
   - Rào chắn kiến trúc: Đã gắn Guardrails trích dẫn docs/architecture/ (05-data, 07-security, 09-principles)
   - Độ bao phủ: {X} AC Happy Path, {Y} AC Edge Cases, {Z} AC Negative Paths.
   
   Xác nhận tạo các file trên vào tầng Implementation? (Y / Sửa / Hủy)
   ```
2. **L2 Diff:** Nếu cập nhật story đã có sẵn, hiển thị diff trước khi ghi.

---

## 3. Cấu trúc Tài liệu Xuất chuẩn

### 3.1. File Sổ cái Backlog: `docs/implementation/{release}/backlog/{feature}-story-index.md`

```markdown
# Backlog Sổ cái: [Tên Feature / Release]

**Tầng tài liệu**: Implementation Layer  
**Release**: [release-1 / release-2...]  
**Nguồn tham chiếu**: PRD `docs/implementation/{release}/prd.md`  
**Sơ đồ luồng**: Sơ đồ Sequence tại `docs/implementation/{release}/technical-design.md`  
**Ngày cập nhật**: [YYYY-MM-DD]  

## 1. Ma trận phân bổ Story & Traceability

| Mã Story | Tiêu đề User Story | Persona | Ưu tiên | PRD FR Ref | Số AC | Architecture Guardrails | Trạng thái |
|---|---|---|---|---|---|---|---|
| **US-001** | Đăng ký tài khoản qua số điện thoại | Khách hàng | P0 (Must) | FR-01 | 4 ACs | 05-data, 07-security | Ready for Dev |
| **US-002** | Xác thực mã OTP kích hoạt tài khoản | Khách hàng | P0 (Must) | FR-01 | 5 ACs | 07-security, 08-integ | Ready for Dev |
| **US-003** | Khóa tạm thời khi nhập sai OTP quá 5 lần | Hệ thống | P1 (Should) | FR-01 | 3 ACs | 07-security | Pending PO (1 OQ) |

## 2. Danh sách Câu hỏi mở (Open Questions cần PO chốt)
- `[ ] OQ-01 (US-003)`: Thời gian khóa tài khoản tạm thời là 15 phút hay 30 phút?
```

### 3.2. File Chi tiết từng Story: `docs/implementation/{release}/backlog/stories/{us-id}.md`

```markdown
# User Story: [US-ID] - [Tiêu đề]

**Tầng tài liệu**: Implementation Layer  
**Release**: [release-1 / release-2...]  
**Traceability**: Map to [FR-xxx] trong `docs/implementation/{release}/prd.md`  
**Priority**: P0 (Must)  
**Estimable Effort**: ~2 Story Points  

---

## 1. User Story Statement

**As a** [Persona có ngữ cảnh cụ thể]  
**I want to** [Hành động nghiệp vụ rõ ràng]  
**So that** [Lợi ích nghiệp vụ thiết thực]  

---

## 2. Acceptance Criteria (Given-When-Then)

### AC1: [Happy path - Đăng ký thành công]
- **Given** Khách hàng chưa có tài khoản trên hệ thống và đang ở màn hình Đăng ký
- **When** Khách hàng nhập số điện thoại hợp lệ và bấm "Tiếp tục"
- **Then** Hệ thống gửi mã OTP 6 số qua tin nhắn SMS
- **And** Chuyển hướng người dùng sang màn hình xác thực OTP kèm đếm ngược 60 giây

### AC2: [Validation - Số điện thoại đã tồn tại]
- **Given** Số điện thoại đã được đăng ký và xác thực trước đó
- **When** Khách hàng bấm "Tiếp tục"
- **Then** Hệ thống hiển thị thông báo "Số điện thoại đã tồn tại" và hiển thị nút "Đăng nhập ngay"

### AC3: [Negative path - Cổng gửi tin SMS bị lỗi]
- **Given** Cổng SMS trung gian mất kết nối hoặc phản hồi mã lỗi
- **When** Khách hàng yêu cầu gửi OTP
- **Then** Hệ thống hiển thị thông báo: "Hệ thống đang bận, vui lòng thử lại sau ít phút"
- **And** Không trừ lượt gửi OTP của người dùng trong phiên này

---

## 3. Architecture Guardrails for Coding Agents (BẮT BUỘC ĐỌC TRƯỚC KHI CODE)

> ⛔ **Cảnh báo cho AI Coding Agent**: Trước khi sinh hoặc sửa code cho User Story này, Agent BẮT BUỘC phải đọc và tuân thủ các tài liệu kiến trúc bất biến sau để không làm phá vỡ hệ thống:

1. **Data Model Guardrails** (`docs/architecture/05-data-architecture.md`):
   - Bảng thao tác: `users`, `otp_verifications`.
   - Ràng buộc: Tuyệt đối không xóa hoặc thay đổi kiểu dữ liệu các cột hiện có. Sử dụng migration script đúng chuẩn.
2. **Security & Auth Guardrails** (`docs/architecture/07-security-architecture.md`):
   - Áp dụng cơ chế Rate Limiting: tối đa 3 lần gửi OTP / 1 phút.
   - Tuyệt đối không log plain-text OTP hoặc thông tin nhạy cảm vào system logs.
3. **Design Principles & Patterns** (`docs/architecture/09-design-principles.md`):
   - Tách biệt rõ ràng Repository Layer (truy vấn DB) và Service Layer (nghiệp vụ OTP).
   - Đặt file mới đúng quy hoạch tại `docs/architecture/10-folder-structure.md`.

---

## 4. Fact-list & Coverage Verification
- [x] Happy Path: Đã có AC1
- [x] Input Validation: Đã có AC2
- [x] External Service Failure: Đã có AC3
- [x] Đã đối chiếu với sơ đồ Sequence tại `technical-design.md`: Không có nhánh lỗi nào bị bỏ sót
```

---

## 4. Tiêu chí hoàn thành (Checklist)

- [ ] Lưu đúng vị trí trong tầng Implementation: `docs/implementation/{release}/backlog/`.
- [ ] Mọi Story đều thỏa mãn 6 tiêu chí INVEST.
- [ ] Bóc tách AC chuẩn Given-When-Then, bao quát đủ Happy Path, Edge Cases, và Negative Paths từ sơ đồ luồng.
- [ ] **Mọi Story đều có mục `Architecture Guardrails for Coding Agents`** trích dẫn rõ các file trong `docs/architecture/`.
- [ ] Kiểm tra Coverage: 100% các nhánh lỗi trong sơ đồ/PRD đều có AC tương ứng.
- [ ] Không tự bịa thông số nghiệp vụ; đánh mã `[OQ]` cho các giá trị chưa rõ.
- [ ] Đã qua bước **Approval Gate L1** trước khi xuất file.
- [ ] Tạo đầy đủ file Sổ cái `{feature}-story-index.md` và các file chi tiết story.
