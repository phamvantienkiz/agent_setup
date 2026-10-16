# Kế hoạch Thiết kế & Phát triển Website "Level Up Your AI Skills · 200Lab"

> **Mục tiêu**: Xây dựng trang web tĩnh giới thiệu toàn diện kho tri thức Agent Setup & Skills, tích hợp bộ diễn hoạt Intro Cinematic (60s @ 30fps) bằng HTML/CSS/JS, chuẩn Design Tokens tông Xanh Đen (`#000000` / `#0d1725` / `#6ee7b7`), sẵn sàng triển khai GitHub Pages.

---

## 📑 Danh mục Tài liệu Kế hoạch (docs/plan/)

| STT | Tài liệu | Nội dung chính |
|---|---|---|
| 01 | [01_requirements_and_brand.md](./01_requirements_and_brand.md) | Phân tích chi tiết yêu cầu bài toán, Brand "Level Up Your AI Skills · 200Lab", hệ thống Design Tokens (Màu sắc, Typography, Spacing, WCAG 2.2 AA). |
| 02 | [02_cinematic_intro_animation.md](./02_cinematic_intro_animation.md) | Thiết kế kiến trúc bộ diễn hoạt Cinematic Hero Intro 60 giây (30fps) bằng Canvas/DOM JS Timeline, Storyboard 4 màn, tính năng Skip & Controls. |
| 03 | [03_skills_catalog_structure.md](./03_skills_catalog_structure.md) | Danh mục & cấu trúc phân loại toàn diện các Skills trong repository (BA, UI/UX, Diagram, Docs, System Design, Coding, Research, MCP). |
| 04 | [04_ui_ux_website_architecture.md](./04_ui_ux_website_architecture.md) | Cấu trúc trang web tĩnh, Component Anatomy, tương tác bàn phím/chuột, bộ lọc tìm kiếm Skills, Dialog chi tiết. |
| 05 | [05_implementation_roadmap.md](./05_implementation_roadmap.md) | Lộ trình thực thi chi tiết theo từng giai đoạn, kế hoạch kiểm thử tự động/thủ công, và định hướng CI/CD GitHub Pages. |

---

## 🎯 Tóm tắt Định hướng Triển khai

1. **Kiến trúc Kỹ thuật**:
   - Sử dụng **Vanilla Web hiện đại (HTML5, CSS Custom Properties, ES Modules)** không phụ thuộc build tooling nặng nề, đảm bảo trang load tức thì (<0.5s), không tốn chi phí băng thông, tương thích 100% với **GitHub Pages miễn phí**.
   - Bộ diễn hoạt Intro 60s được render qua HTML5 Canvas + Web Animations API / `requestAnimationFrame` chính xác 30 khung hình/giây, không dùng video MP4 cồng kềnh (tiết kiệm 99% dung lượng).
2. **Phong cách Thị giác**:
   - Tông màu chủ đạo: **Xanh đen / Emerald Cybernetic** (`#000000`, `#0d1725`, `#6ee7b7`, `#ffffff`).
   - Font: `Inter` kết hợp font monospace lập trình (`JetBrains Mono` / `Fira Code` / `ui-monospace`) cho code/skills.
   - Đạt chuẩn tương phản **WCAG 2.2 AA**, hỗ trợ đầy đủ `focus-visible` và điều hướng bàn phím.
3. **Quy trình Thực hiện**:
   - **Bước 1**: Phê duyệt kế hoạch tổng thể & chi tiết trong `docs/plan/`.
   - **Bước 2**: Xây dựng mockup / prototype khung sườn web và hệ thống tokens.
   - **Bước 3**: Hoàn thiện kịch bản animation 60s Canvas Intro engine.
   - **Bước 4**: Tích hợp danh mục Skills tương tác (tìm kiếm, lọc tag, xem prompt, copy command).
   - **Bước 5**: Tối ưu hiệu năng, audit accessibility & chuẩn bị workflow GitHub Actions CI/CD.
