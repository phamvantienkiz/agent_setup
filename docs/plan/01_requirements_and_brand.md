# 01. Phân Tích Yêu Cầu & Nhận Diện `agent_setup` (by Hi Jin)

> **Sản phẩm**: **`agent_setup`**  
> **Mục tiêu**: Bộ cấu hình và thư viện kỹ năng (skills) chuyên sâu dành cho **Antigravity CLI** (hỗ trợ cả Gemini CLI, Claude Code, Cursor) cho developer sử dụng.  
> **Tác giả**: **Hi Jin**

---

## 1. Bản Chất Sản Phẩm (`agent_setup`)

- **Tên repository / sản phẩm**: `agent_setup`
- **Tác giả**: Hi Jin (nhắc đến tinh tế 1-2 lần ở header và footer `agent_setup · by Hi Jin`).
- **Mục đích**: 
  - Cung cấp cấu hình chuẩn mực (`AGENTS.md`, `.agents/`, `tasks/`) biến AI Coding CLI (trọng tâm là **Antigravity**) thành trợ lý kỹ sư kỷ luật và tự chủ.
  - Thư viện hơn 50+ kỹ năng (Skills) thực tế bao phủ toàn diện chu trình phần mềm:
    - **BA & Requirements**: `product-requirements`, `user-story-ac-writer` (BRD, PRD, User Story chuẩn INVEST & Gherkin).
    - **Design & UI/UX**: `ui-ux-pro-max`, `ui-styling`, `design-system`, `design-artifact`, `banner-design`, `brand`.
    - **Diagram & 3D**: `diagram-design`, `html-diagram`, `3dviz-pro-max`, `lecture-visualizer` (Architecture diagram, C4, Sequence, Three.js).
    - **Documentation & Plans**: `documentation`, `html-plan`, `html-wireframe`, `html-prototype`, `slides` (Kiến trúc tài liệu 3 tầng, Single Source of Truth).
    - **System Design & Harness**: `system-design`, `agent-harness`, `api-design-patterns` (Kiến trúc phân tán, Caching, CAP, Agent Loop bền bỉ).
    - **Engineering & Clean Code**: `clean-code` (66 quy tắc Clean Code của Robert C. Martin, Boy Scout Rule), `python-fastapi-code`, `fastapi-backend-scaffold`, `nvidia-cuda`, `stm32-embedded-workflow`.
    - **Research**: `cs-research-skills/*`, `microsoft-research/*`, `rag-architect`, `prompt-engineer`, `langchain-skills`, literature search (ArXiv, OpenAlex...).

---

## 2. Bốn Nguyên Tắc Kỹ Thuật Bất Biến (Core Philosophy)

Được đúc kết từ thực chiến và các bài học của Andrej Karpathy về lỗi của LLM:
1. **Think Before Coding**: Không giả định bừa, làm rõ yêu cầu và nêu rõ đánh đổi (trade-offs) trước khi viết mã.
2. **Simplicity First**: Viết lượng code tối thiểu, không suy đoán tương lai, không over-engineering.
3. **Surgical Changes**: Sửa đúng phạm vi, diff sạch, giữ nguyên coding style, mọi dòng code đều truy vết được về yêu cầu.
4. **Strict Isolation**: Mọi cài đặt dependencies phải cô lập tuyệt đối trong workspace (`.venv`), nghiêm cấm làm bẩn hệ thống global.

---

## 3. Hệ Thống Thẩm Mỹ & Design Tokens

Áp dụng chuyên môn từ `ui-ux-pro-max` và `design-system`:
- **Chủ đạo**: Tông **Xanh Đen / Emerald Cybernetic** (nền đen sâu `#030712`, xanh đêm `#0b1329`, điểm nhấn ngọc lục bảo `#10b981` / `#6ee7b7`, chữ trắng `#ffffff` và xám `#94a3b8`).
- **Typography**: `Inter` cho văn bản thông thường, `JetBrains Mono` cho mã nguồn và kỹ năng.
- **Iconography**: **100% SVG vector chuẩn** (GitHub official mark, Terminal, Search, Copy, Check, External Link). Tuyệt đối không dùng emoji thay cho icon.
- **Không có các chi tiết lạc đề**: Loại bỏ hoàn toàn mọi tham chiếu 200Lab, không có e-commerce, không dùng khẩu hiệu "0đ phí github".
