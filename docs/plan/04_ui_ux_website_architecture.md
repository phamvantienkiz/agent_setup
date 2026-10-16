# 04. Kiến Trúc Giao Diện & Trải Nghiệm Người Dùng (UI/UX Architecture)

> **Mục tiêu**: Xây dựng landing page đẳng cấp lập trình viên (Developer-Grade) cho `agent_setup` by Hi Jin. Đầy đủ các tiêu chuẩn từ `ui-ux-pro-max`, 100% SVG icons, bố cục chặt chẽ và tương tác mượt mà.

---

## 1. Bố Cục Trang Web Toàn Diện (Page Structure)

```
+=======================================================================+
| [NAVBAR] agent_setup · by Hi Jin | Triết lý | Skills | Cài đặt | [GitHub ↗]|
+=======================================================================+
|                                                                       |
|  [HERO SECTION: 2 CỘT CÂN ĐỐI]                                        |
|  +-------------------------------+ +--------------------------------+ |
|  | CỘT TRÁI:                     | | CỘT PHẢI:                      | |
|  | - Tag: Antigravity Skills     | | - [HERO SHOWCASE MOTION CARD]  | |
|  | - Title: Dạy Nghề Cho AI      | |   (5 phân đoạn tự động lướt,   | |
|  | - Subtitle súc tích           | |    thanh story progress trên   | |
|  | - CTA: [Khám phá 50+ Skills]  | |    đỉnh, không có nút video    | |
|  | - Quick Terminal snippet      | |    player thô kệch)            | |
|  +-------------------------------+ +--------------------------------+ |
|                                                                       |
+=======================================================================+
|  [PHILOSOPHY: BỐN NGUYÊN TẮC BẤT BIẾN]                                |
|  1. Think Before Coding  2. Simplicity First  3. Surgical  4. Isolated|
+=======================================================================+
|                                                                       |
|  [INTERACTIVE SKILLS EXPLORER]                                        |
|  - Ô tìm kiếm SVG tức thì (Ctrl+K)                                    |
|  - Tabs lọc 7 trụ cột (SVG icons: Code, BA, Design, 3D...)            |
|  - Lưới hiển thị thẻ kỹ năng (Cards Grid)                             |
|  - Nút Copy Prompt 1-Click (SVG icon) & Modal chi tiết                |
|                                                                       |
+=======================================================================+
|                                                                       |
|  [QUICK SETUP & INTEGRATION]                                          |
|  - Cấu hình AGENTS.md & .agents/ trong 10 giây                        |
|                                                                       |
+=======================================================================+
|  [FOOTER] agent_setup · by Hi Jin · Giấy phép MIT · GitHub SVG icon   |
+=======================================================================+
```

---

## 2. Tiêu Chuẩn Icon & Thẩm Mỹ (SVG-First Standard)

- **100% SVG Vector**:
  - Logo GitHub: SVG chính thức của GitHub.
  - Icon Tìm kiếm: SVG Search.
  - Icon Sao chép: SVG Clipboard / Checkmark.
  - Icon Danh mục: SVG Terminal, Layers, Palette, Box3D, FileText, Cpu, Flask.
  - Tuyệt đối không dùng emoji thay cho icon giao diện.
- **Micro-interactions**:
  - Hover thẻ card: Đẩy nhẹ 2px, viền phát quang xanh ngọc `rgba(110, 231, 183, 0.3)`.
  - Nút sao chép: Chuyển icon sang dấu tích xanh `✓` trong 2 giây rồi hồi phục.
  - Phím tắt: `Ctrl + K` đưa con trỏ vào ô tìm kiếm, `Esc` đóng modal.
