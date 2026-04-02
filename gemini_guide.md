# Gemini CLI — Personal Usage Guide

> Ghi chú cá nhân về cách sử dụng Gemini CLI hiệu quả trong phát triển phần mềm.
> Viết cho người mới bắt đầu, tổng hợp từ workflow thực chiến và best practices cộng đồng.

---

## Tư duy nền tảng (Đọc trước khi làm gì khác)

Gemini CLI **không phải là chatbot**. Nó là một **engineer làm việc trong terminal của bạn** — có khả năng đọc toàn bộ codebase, chạy lệnh shell, và tìm kiếm web.

Điểm khác biệt lớn nhất so với Claude Code:

> Gemini có **context window cực lớn** — đây vừa là lợi thế, vừa là bẫy nếu dùng sai.

Dùng đúng: load cả module/codebase để hiểu toàn cảnh, phân tích sâu.
Dùng sai: để context phình ra vô kiểm soát → chất lượng giảm, tốc độ chậm.

---

## Phần 1 — Thiết lập ban đầu (Làm 1 lần)

### Bước 1: Cài đặt Gemini CLI

```bash
npm install -g @google/gemini-cli
```

Đăng nhập:

```bash
gemini auth login
```

Kiểm tra hoạt động:

```bash
gemini --version
```

### Bước 2: Tạo file GEMINI.md

Đây là file quan trọng nhất. Gemini CLI đọc file này mỗi khi bắt đầu session trong thư mục project.

```bash
# Tạo ở root của project
touch GEMINI.md
```

Dùng file `GEMINI.md` đi kèm — điền vào phần **Project Context** với thông tin thật của project bạn.

**Quan trọng**: Càng cụ thể càng tốt. Ví dụ:

```markdown
## Project Context

- Project name: E-commerce API
- Stack: Node.js, Express, TypeScript, PostgreSQL, Redis
- Current goal: Implement order management module
- Active branch: feat/order-management
- Run command: npm run dev
- Test command: npm run test:watch
- Build command: npm run build
- Log locations: /logs/app.log, /logs/error.log
```

### Bước 3: Tạo thư mục tasks/

```bash
mkdir tasks
touch tasks/todo.md
touch tasks/lessons.md
```

- `todo.md` → kế hoạch và progress của task hiện tại
- `lessons.md` → Gemini tự cập nhật sau mỗi lần bạn correct nó

### Bước 4: Tạo thư mục docs/ai/

```bash
mkdir -p docs/ai
```

Mọi file markdown Gemini tạo ra → lưu vào đây. Giữ repo sạch sẽ.

### Bước 5: Tạo file .geminiignore (Tùy chọn)

Giống `.gitignore`, ngăn Gemini đọc những file không cần thiết:

```
node_modules/
.env
.env.local
dist/
build/
coverage/
*.log
```

---

## Phần 2 — Khởi động Gemini CLI

### Cách khởi động cơ bản

```bash
# Vào thư mục project
cd your-project

# Khởi động Gemini CLI (đọc GEMINI.md tự động)
gemini
```

### Chọn model ngay từ đầu

```bash
# Dùng Flash cho task nhanh
gemini --model gemini-2.0-flash

# Dùng Pro cho task phức tạp
gemini --model gemini-2.5-pro
```

Hoặc đổi model trong session:

```
/model gemini-2.5-pro
```

---

## Phần 3 — Workflow hàng ngày

### Bắt đầu một feature mới — Quan trọng nhất

**KHÔNG bao giờ gõ "Build this..." ngay lập tức.**

**Bước 1: Lập kế hoạch trước**

```
Analyze this repository and create a step-by-step implementation plan for adding [feature].
Do not modify any files yet. Output the plan to tasks/todo.md.
```

**Bước 2: Review kế hoạch**

Đọc `tasks/todo.md`, chỉnh sửa nếu cần. Sau đó:

```
The plan looks good. Now proceed with implementation, starting from step 1.
Mark each step complete in tasks/todo.md as you go.
```

---

### Tận dụng context window lớn — Gemini's Superpower

Đây là thứ Gemini làm tốt hơn hầu hết AI khác. Dùng nó cho:

**Phân tích toàn bộ codebase:**

```
Load all files in src/ and give me a comprehensive architectural overview.
Write the summary to docs/ai/architecture-review.md
```

**Phân tích dependency giữa các module:**

```
Load @src/auth/ and @src/users/ together.
Explain how they interact and identify any coupling issues.
```

**Review toàn bộ PR diff:**

```
Here is the full git diff: !git diff main...feat/my-feature
Review this as a senior engineer. What concerns do you have?
```

**Cảnh báo**: Dù context window lớn, đừng lạm dụng. Load file khi cần thiết, không load hết codebase mỗi lần hỏi câu đơn giản.

---

### Chạy shell commands trong Gemini

Một trong những điểm mạnh của Gemini CLI — có thể chạy lệnh shell trực tiếp:

```
# Trong chat với Gemini
Run the tests and tell me what's failing:
!npm test

Check the current git status:
!git status

Find all TODO comments in the codebase:
!grep -r "TODO" src/
```

Gemini sẽ đọc output và phân tích cho bạn.

---

### Debug lỗi

```bash
# Cách 1: Pipe log vào
cat error.log | gemini "Explain this error and suggest a fix"

# Cách 2: Reference file trong chat
```

```
Here is the error log: @logs/error.log
Here is the relevant source: @src/services/payment.ts
Trace the root cause and propose the minimal fix.
```

---

### Phân loại task: Tự chạy vs Theo dõi sát

| Để Gemini tự chạy          | Theo dõi từng bước                  |
| -------------------------- | ----------------------------------- |
| Phân tích codebase lớn     | Core business logic                 |
| Viết unit tests            | Authentication / Security / Payment |
| Tạo documentation          | Database migrations                 |
| Refactor nhỏ, rõ ràng      | Tích hợp third-party service        |
| Convert code giữa ngôn ngữ | API contract changes                |

---

### Tìm kiếm web trong Gemini

Gemini có thể search web khi cần:

```
Search for the latest best practices for JWT refresh token rotation in 2025
and suggest how to apply them to @src/auth/token.service.ts
```

```
This error: "Cannot read property 'map' of undefined" appears in React 18.
Search for the most common causes and apply the fix to @src/components/UserList.tsx
```

---

## Phần 4 — Quản lý Context

### Vấn đề với context window lớn

Lợi thế của context lớn có thể trở thành vấn đề nếu:

- Session kéo dài nhiều giờ, nhiều task khác nhau
- Context chứa nhiều output cũ của shell commands
- Gemini bắt đầu "nhớ" quyết định sai từ sớm trong session

### Dấu hiệu cần reset context

- Output bắt đầu mâu thuẫn với những gì đã thống nhất
- Gemini không nhớ quyết định architecture từ đầu session
- Chất lượng code giảm rõ rệt sau nhiều task

### Giải pháp

```bash
# Nén context (giữ tóm tắt)
/compress

# Reset hoàn toàn
/clear

# Cách tốt nhất: commit checkpoint trước khi reset
!git add -A && git commit -m "checkpoint: before context reset"
/clear
```

### Rule đơn giản

- **Task ngắn, độc lập** → 1 session
- **Task lớn nhiều giờ** → commit checkpoint thường xuyên
- **Mỗi ngày mới** → thường nên `/clear` và bắt đầu fresh

---

## Phần 5 — Các Lệnh Trong Session

### Slash Commands Quan Trọng

| Lệnh                  | Tác dụng                        |
| --------------------- | ------------------------------- |
| `/help`               | Xem tất cả lệnh có sẵn          |
| `/clear`              | Reset context hoàn toàn         |
| `/compress`           | Nén context, giữ tóm tắt        |
| `/model [name]`       | Đổi model (flash/pro/ultra)     |
| `/tools`              | Xem các tool Gemini có thể dùng |
| `/quit` hoặc `Ctrl+C` | Thoát                           |

### Shell Commands Trong Session

```bash
# Prefix ! để chạy shell command trực tiếp
!git status
!npm test
!ls src/
!cat error.log
```

### Reference Files

```
# Dùng @ để reference file
@src/auth/middleware.ts
@package.json
@tasks/todo.md
```

---

## Phần 6 — Cấu Trúc Prompt Hiệu Quả

### Prompt tốt = Input tốt → Output tốt

**Không tốt:**

```
Fix the bug
```

**Tốt:**

```
# Context
File: @src/api/orders.ts
Error: !npm test 2>&1 | tail -30

# Problem
The createOrder function fails when payment method is "bank_transfer".
It works for "credit_card" and "e_wallet".

# Request
Find the root cause in the createOrder function and fix it.
The fix should not affect other payment methods.
Write tests for the bank_transfer case.
```

### Dùng Markdown để cấu trúc

```markdown
# Goal

Refactor the authentication module

## Current state

@src/auth/auth.service.ts — monolithic, 800 lines

## Requirements

- Split into: TokenService, SessionService, PasswordService
- Maintain all existing public APIs
- No behavior changes

## Constraints

- Cannot change the database schema
- Must stay compatible with existing middleware
```

---

## Phần 7 — So Sánh Gemini CLI vs Claude Code

Hiểu điểm mạnh của từng tool để dùng đúng lúc:

|                             | Gemini CLI           | Claude Code      |
| --------------------------- | -------------------- | ---------------- |
| **Context window**          | Rất lớn (1M+ tokens) | Lớn, quản lý tốt |
| **Whole-codebase analysis** | ⭐⭐⭐⭐⭐           | ⭐⭐⭐⭐         |
| **Web search tích hợp**     | ✅ Native            | Cần tool bổ sung |
| **Shell integration**       | ✅ `!command`        | ✅ Native        |
| **Ecosystem & plugins**     | Đang phát triển      | Trưởng thành hơn |
| **Custom slash commands**   | Giới hạn             | Phong phú        |
| **GEMINI.md / CLAUDE.md**   | `GEMINI.md`          | `CLAUDE.md`      |

**Kết luận thực tế**: Hai tool complement nhau tốt. Nhiều developer dùng cả hai — Gemini cho phân tích codebase lớn, Claude Code cho coding workflow hàng ngày.

---

## Phần 8 — Tình Huống Thường Gặp

### Gemini đọc sai file?

```
# Specify rõ hơn
Load ONLY @src/auth/auth.service.ts — do not load other files.
```

### Output quá dài, khó đọc?

```
Give me a summary in bullet points, max 10 points.
Then write the full analysis to docs/ai/analysis.md
```

### Gemini đang overcomplicate giải pháp?

```
Stop. This solution is too complex.
What is the simplest possible approach to solve this specific problem?
```

### Muốn Gemini làm nhiều task song song?

Mở nhiều terminal window, mỗi window một instance Gemini trong context riêng.

### Gemini lặp lại cùng một lỗi?

```
Update tasks/lessons.md with this rule: [mô tả pattern cụ thể]
Reference this rule at the start of future sessions.
```

---

## Phần 9 — Checklist Hàng Ngày

### Bắt đầu ngày làm việc

- [ ] `cd your-project`
- [ ] `gemini` (đọc GEMINI.md tự động)
- [ ] Đọc summary từ `tasks/todo.md` và `tasks/lessons.md`
- [ ] Xác nhận active branch: `!git branch`
- [ ] Git state sạch? `!git status`

### Trước khi bắt đầu task mới

- [ ] Đã lập kế hoạch chưa? (plan to `tasks/todo.md`)
- [ ] Task này để Gemini tự chạy hay cần theo dõi sát?
- [ ] Đã commit checkpoint chưa? `!git add -A && !git commit -m "checkpoint"`
- [ ] Context còn phù hợp không? (nếu cần: `/compress` hoặc `/clear`)

### Trước khi commit / tạo PR

- [ ] Build pass: `!npm run build`
- [ ] Tests pass: `!npm test`
- [ ] Không còn debug code: `!grep -r "console.log" src/`
- [ ] Không còn temp files
- [ ] Commit message rõ ràng, conventional format
- [ ] `tasks/todo.md` và `tasks/lessons.md` đã cập nhật

---

## Quick Reference Card

```
Khởi động:        gemini
Đổi model:        /model gemini-2.5-pro
Chạy shell:       !npm test
Reference file:   @src/module.ts
Nén context:      /compress
Reset context:    /clear
Thoát:            /quit hoặc Ctrl+C

Commit checkpoint trước khi làm gì phức tạp:
!git add -A && git commit -m "checkpoint: [mô tả]"
```

---

## Ghi Nhớ Cuối Cùng

**Ba thứ tạo ra 80% kết quả:**

1. **GEMINI.md tốt** — Viết context project đầy đủ, rõ ràng. Làm 1 lần, hưởng lợi mãi.
2. **Plan trước khi build** — Không bao giờ để Gemini code ngay khi chưa có kế hoạch.
3. **Commit thường xuyên** — Checkpoint trước mỗi task lớn. Rollback nếu cần, không sợ mất gì.

> Gemini CLI mạnh nhất khi bạn cho nó **toàn cảnh** — nhưng với **mục tiêu rõ ràng**. Đó là sự khác biệt giữa dùng AI như công cụ và dùng AI như đồng đội.

---

PROMPT ĐÁNH GIÁ CODE TOÀN DIỆN
Đảm bảo chất lượng code

---

Đánh giá đoạn code sau về các thực tiễn tốt nhất, hiệu suất, bảo mật và khả năng bảo trì:
[DÁN CODE CỦA BẠN]
Ngôn ngữ/Framework: [ví dụ: Python/Django, JavaScript/React]
Cung cấp:

1. Các lỗ hổng bảo mật
2. Các điểm nghẽn hiệu suất
3. Phát hiện mã lỗi
4. Vi phạm thực tiễn tốt nhất
5. Đề xuất tái cấu trúc
6. Xếp hạng (1-10) kèm lý do
