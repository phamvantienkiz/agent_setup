# Hệ Thống Thiết Kế Giao Diện HTML & Bố Cục Full-Width (HTML Design System)

Tài liệu này định nghĩa kiến trúc giao diện cho các trang bài giảng Single-File HTML (`index.html`) được xây dựng bởi kỹ năng `lecture-visualizer`.

---

## 1. Triết Lý Bố Cục: Tối Ưu Hóa 100% Không Gian Ngang (Full-Width Utilization)

Trong các tài liệu khoa học máy tính cao học:
- **Vấn đề của layout truyền thống**: Sử dụng `max-width: 800px` hoặc `960px` ở giữa màn hình khiến 35-40% diện tích màn hình lớn bị bỏ phí thành khoảng trắng vô nghĩa. Hậu quả là các bảng dữ liệu nhiều cột (Trace table, Paradigm comparison matrix) bị co ép, chữ nhảy dòng liên tục và công thức toán LaTeX bị tràn ngang (overflow).
- **Quy tắc bố cục của `lecture-visualizer`**:
  - Sidebar cố định bên trái: Chiều rộng chuẩn `var(--sidebar-width) = 280px` (hoặc `300px`).
  - Toàn bộ phần nội dung chính `main.content` chiếm **100% không gian còn lại**:
    ```css
    :root {
        --sidebar-width: 290px;
    }
    main.content {
        margin-left: var(--sidebar-width);
        width: calc(100% - var(--sidebar-width));
        padding: 40px 48px;
        box-sizing: border-box;
    }
    ```
  - Giúp các bảng trace 5-6 cột và các cây phân cấp hiển thị thoáng đãng, sang trọng, mang lại trải nghiệm đọc như một ấn phẩm nghiên cứu cao cấp.

---

## 2. Thanh Điều Hướng Sidebar Tối Giản Kiểu Word / Notion (Sticky ScrollSpy)

Sidebar được thiết kế theo phong cách văn bản tối giản (Text-only, không icon cồng kềnh, không màu mè rối mắt):
1. **Phân cấp nhóm chuyên đề**: Dùng `<span class="nav-group-title">` để gom nhóm các chuyên đề lớn (Chuyên đề 01, 02, 03...).
2. **Đường dẫn mục con**: Các link `<a class="nav-item sub-item">` thụt lề nhẹ 14px.
3. **Chỉ thị vị trí cuộn trang (Active State)**:
   - Khi người dùng cuộn đến section nào, liên kết tương ứng trên sidebar tự động sáng đèn:
     ```css
     .nav-item.active {
         background: #eff6ff;
         color: #1d4ed8;
         font-weight: 600;
         border-left: 3px solid #2563eb;
         padding-left: 13px; /* bù trừ cho border-left */
     }
     ```
4. **Thanh tiến trình đọc ở đỉnh màn hình (Reading Progress Bar)**:
   - Một thanh chỉ báo mảnh 3px màu xanh dương `#2563eb` cố định ở đỉnh màn hình, tự động chạy từ 0% đến 100% theo độ cuộn của trang.

---

## 3. Hệ Thống Khối Hộp Thông Tin (Semantic Callout System)

Bộ thẻ hộp thoại trực quan chuẩn mực giúp phân tách rõ ràng các loại thông tin:

| Loại Callout | Class CSS | Màu Viền & Nền | Biểu Tượng & Mục Đích Sử Dụng |
|:---|:---|:---|:---|
| **Định Nghĩa Chuẩn** | `.callout.def` | Viền xanh dương `#2563eb`, nền `#f0f7ff` | 📚 Dùng cho các định nghĩa học thuật, phát biểu bài toán FIM, khái niệm chính quy. |
| **Góc Người Học Chậm** | `.callout.intuition` | Viền xanh lá ngọc `#059669`, nền `#ecfdf5` | 🌱 Dùng giải thích bản chất đời thực, ví dụ trực quan, phép ẩn dụ siêu thị. |
| **Mẹo & Chú Ý** | `.callout.tip` | Viền tím nhạt `#7c3aed`, nền `#f5f3ff` | 💡 Các mẹo ghi nhớ, giải thích lý do vì sao thuật toán lại chọn thiết kế đó. |
| **Cảnh Báo & Cổ Chai** | `.callout.warn` | Viền đỏ cam `#dc2626`, nền `#fef2f2` | ⚠️ Cảnh báo bùng nổ tổ hợp, nút thắt I/O đĩa cứng, giới hạn bộ nhớ RAM. |
| **Định Lý & Bổ Đề** | `.callout.theorem` | Viền chàm `#4338ca`, nền `#eef2ff` | 📜 Phát biểu định lý toán học, bổ đề Han et al., công thức đường dẫn đơn. |

---

## 4. Bảng Dữ Liệu Chống Tràn Ngang (Responsive Table Containers)

Mọi bảng biểu số học hoặc ma trận so sánh bắt buộc phải được bọc trong container chống tràn:

```html
<div class="table-container">
    <table>
        <thead>
            <tr>
                <th style="width: 15%;">Cột 1</th>
                <th style="width: 45%;">Cột 2</th>
                <th style="width: 40%;">Cột 3</th>
            </tr>
        </thead>
        <tbody>
            <tr><td>...</td><td>...</td><td>...</td></tr>
        </tbody>
    </table>
</div>
```

```css
.table-container {
    width: 100%;
    overflow-x: auto;
    margin: 20px 0 28px 0;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    background: #ffffff;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.92rem;
    text-align: left;
}
th {
    background: #f8fafc;
    color: #1e293b;
    font-weight: 600;
    padding: 12px 16px;
    border-bottom: 1px solid #cbd5e1;
}
td {
    padding: 12px 16px;
    border-bottom: 1px solid #e2e8f0;
    vertical-align: middle;
}
tr:hover td {
    background: #f8fafc;
}
```

---

## 5. Typography & Font Chữ Chuẩn Mực

- **Font chữ chính (Body & Heading)**: Sử dụng font `Inter` hoặc hệ thống Sans-serif hiện đại (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto...`) cho cảm giác đọc sắc nét, không mỏi mắt.
- **Font chữ Mã nguồn & Số liệu (Code & Monospace)**: Sử dụng `'JetBrains Mono', 'Fira Code', Consolas, monospace` cho các mã giao dịch (TID 1, TID 2), công thức tính toán, danh sách ứng viên ($C_k, F_k$).
- **Khoảng cách dòng (Line Height)**: Tối thiểu `1.7` đến `1.85` đối với các đoạn văn giải thích để người học chậm không bị hoa mắt khi đọc các đoạn dài.

---

## 6. Tiêu Chuẩn Thẻ Card "Soft Clean Cards" (Bắt Buộc Cho Mọi Card)

Mọi card trong bài giảng (từ thẻ widget mô phỏng, thẻ tính toán, thẻ chỉ số metric đến thẻ câu hỏi Q&A) bắt buộc phải tuân thủ nghiêm ngặt **Design System 'Soft Clean Cards'** (chi tiết tại [`soft-clean-cards.md`](soft-clean-cards.md)):

```css
/* Card CSS Token Chuẩn */
:root {
    --bg-page: #F5F5F7;
    --bg-card: #FFFFFF;
    --bg-subtle: #F4F4F6;
    --bg-subtle-hover: #ECECEF;
    --border-hairline: #EFEFF2;
    --border-card: #E9E9EE;
    --text-primary: #0B0B0F;
    --text-secondary: #6B6B76;
    --text-tertiary: #9A9AA5;
    --ink: #111114;

    /* Bo góc chuẩn */
    --radius-xs: 4px;
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 28px;      /* Card chính luôn là 28px */
    --radius-full: 999px;

    /* Bóng mờ siêu nhẹ */
    --shadow-card: 0 1px 2px rgba(16, 16, 24, 0.04), 0 8px 24px rgba(16, 16, 24, 0.06);
    --shadow-control: 0 1px 2px rgba(16, 16, 24, 0.08), 0 0 0 1px rgba(16, 16, 24, 0.04);
}

/* Base Card Class */
.card, .interactive-card {
    background: var(--bg-card);
    border: 1px solid var(--border-card);
    border-radius: var(--radius-xl); /* 28px bo tròn lớn */
    padding: 24px 28px;
    box-shadow: var(--shadow-card);
    margin: 28px 0;
    display: flex;
    flex-direction: column;
    gap: 18px;
}
```

### 4 Quy Tắc Cốt Lõi Khi Lập Trình Card:
1. **Một card = một nhiệm vụ / một nhân vật chính**: Luôn có một điểm nhấn nổi bật (một con số display lớn hoặc một widget/chart tương tác trung tâm).
2. **Không viền cứng, không bóng đen**: Viền card chỉ 1px mờ `#E9E9EE`, bóng mờ rộng và nhẹ.
3. **Màu sắc chỉ dùng cho dữ liệu**: Không dùng nền gradient rực rỡ hay viền màu bao quanh card. Nền luôn là trắng tinh trên nền trang xám `#F5F5F7`.
4. **Vùng con dùng `--bg-subtle`**: Không lồng card trong card; các vùng phụ bên trong (bảng nhỏ, đồ thị, khung nhập liệu) dùng nền `--bg-subtle: #F4F4F6` với bo góc `--radius-md: 12px`.

