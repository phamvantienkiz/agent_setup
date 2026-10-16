# 05. Lộ Trình Triển Khai & Kế Hoạch Nghiệm Thu (Roadmap & Verification)

> **Mục tiêu**: Kế hoạch thực thi và kiểm thử chất lượng cho trang web `agent_setup` by Hi Jin.

---

## 1. Các Hạng Mục Thực Thi

1. **Chuẩn hóa Design Tokens & CSS**:
   - Tông màu Xanh Đen (OLED Black, Dark Navy, Emerald Mint).
   - Typography `Inter` và `JetBrains Mono`.
   - Layout 2 cột cho Hero Section (Headline bên trái, Showcase Motion Card bên phải).
2. **Xây dựng Hero Showcase Motion Card**:
   - Lấy cảm hứng từ bố cục thẻ card và phân đoạn trực quan trong `docs/plan/reference/`.
   - 5 phân cảnh tự động lướt (Story bar progress mỏng trên đỉnh).
   - Tuyệt đối không có nút điều khiển video (no play/pause, no timeline scrub, no countdown screen).
3. **Thư viện 50+ Kỹ năng (Skills Explorer)**:
   - Dữ liệu chuẩn xác của repository `agent_setup`.
   - 100% SVG icons cho mọi danh mục và nút hành động.
   - Tìm kiếm tức thì, lọc danh mục, copy prompt 1-click và modal xem chi tiết.
4. **Kiểm thử chất lượng**:
   - Cú pháp JavaScript hợp lệ (`node -c`).
   - Đạt chuẩn tương phản WCAG 2.2 AA.
   - Thao tác mượt mà trên mọi kích thước màn hình.

---

## 2. Tiêu Chí Nghiệm Thu

- [ ] Tên sản phẩm là `agent_setup` dành cho Antigravity CLI, tác giả là Hi Jin.
- [ ] Không chứa bất kỳ nội dung lạc đề nào (xóa sạch 200Lab, xóa bỏ "0đ phí github").
- [ ] Thành phần Hero là Showcase Card chuyển động tự nhiên, không có nút bấm video player.
- [ ] Sử dụng 100% SVG icons chuyên nghiệp, không dùng emoji làm icon.
- [ ] Hoàn toàn tĩnh, tải nhanh, sẵn sàng triển khai GitHub Pages.
