# Hướng dẫn Biên dịch, Nạp Code và Chạy Test

Tài liệu này hướng dẫn chi tiết các bước thực hiện trên STM32CubeIDE sau khi bạn đã cấu hình xong phần cứng và cập nhật xong file `main.c`.

---

## 1. Biên dịch và Nạp chương trình (Build & Debug)

1. **Biên dịch (Build):**
   * Nhấn biểu tượng cây búa (🔨 **Build**) trên thanh công cụ, hoặc ấn phím tắt `Ctrl + B`.
   * Chờ ở góc dưới cùng (Console) hiện dòng chữ `Build Finished. 0 errors, 0 warnings`.
2. **Nạp và Gỡ lỗi (Debug):**
   * Đảm bảo cáp USB đã cắm từ máy tính vào cổng **ST-LINK** trên bo mạch.
   * Nhấn biểu tượng con bọ (🐛 **Debug**) trên thanh công cụ, hoặc phím `F11`.
   * Hộp thoại "Edit Configuration" (nếu có) hiện ra, cứ để mặc định và nhấn **OK**.
   * Trình biên dịch sẽ nạp code vào chip. Khi nạp xong, IDE sẽ tự động chuyển sang giao diện Debug (Perspective) và dừng lại ở dòng lệnh đầu tiên của hàm `main()`.
3. **Chạy chương trình (Resume):**
   * Nhấn biểu tượng nút Play màu xanh lá/vàng (▶️ **Resume**), hoặc phím `F8` để MCU chạy tự do. Lúc này mã nguồn của bạn đã chính thức được thực thi.

---

## 2. Công cụ Giám sát (IDE Views)

*(Agent: Chỉ thêm phần này nếu task cần dùng UART Console, Live Expressions, hoặc SFRs)*

### Mở Serial Terminal (Nếu dùng UART)
1. Ở nửa dưới màn hình, chọn tab **Console**.
2. Phía bên phải của tab Console, bấm vào mũi tên trỏ xuống 🔽 ngay cạnh biểu tượng **Màn hình máy tính có dấu cộng màu xanh (Open Console)**.
3. Chọn **3 Command Shell Console**.
4. **Connection Type:** Chọn `Serial Port`.
5. Nhấn nút **New...** để tạo kết nối mới:
   - **Name:** Gõ tên bất kỳ (Ví dụ: `STLINK VCP`).
   - **Serial Port:** Chọn cổng COM của ST-LINK.
   - **Baud Rate:** [Điền Baudrate cấu hình, VD: 115200]
   - Nhấn **Finish** và **OK**.

### Xem Biến Trực tiếp (Live Expressions)
1. Vào menu **Window > Show View > Live Expressions**.
2. Bấm vào nút dấu cộng `+` (Add new expression).
3. Gõ tên biến bạn muốn xem (VD: `rx_buffer` hoặc `led_active`) và ấn Enter.

---

## 3. Các bước Test chức năng (Test Scenarios)

### Test 1: Khởi động và trạng thái ban đầu
* **Hành động:** Nhấn nút Reset màu đen trên bo mạch (hoặc tắt đi bật lại kết nối Console).
* **Kỳ vọng:** [Mô tả trạng thái hệ thống, VD: đèn LED tắt, terminal in ra thông báo Welcome].

### Test 2: [Tên kịch bản test 2]
* **Hành động:** [Mô tả hành động của người dùng, VD: Gõ lệnh `LED_GREEN` và ấn Enter].
* **Kỳ vọng:** [Mô tả phản hồi của hệ thống].

*(Thêm các kịch bản test khác phù hợp với yêu cầu bài toán...)*

---

## 4. Xử lý sự cố thường gặp (Troubleshooting)

*(Agent: Đưa ra các lỗi phổ biến cụ thể với task này, dựa vào playbook hoặc kinh nghiệm thực tế. Dưới đây là các ví dụ, hãy thay đổi cho phù hợp).*

1. **[Hiện tượng lỗi 1, VD: Không thấy hiện chữ khi gõ]**
   * [Cách khắc phục, VD: Terminal của IDE không có Local Echo. Hãy kiểm tra xem đã tích chọn gửi ký tự `\r\n` (CR LF) chưa. Nếu dùng Hercules, hãy tích 2 ô CR và LF ở góc dưới].
2. **[Hiện tượng lỗi 2, VD: Mạch đơ ngay lúc khởi động]**
   * [Cách khắc phục, VD: Bấm phím Resume (F8) để chắc chắn debugger không tạm dừng chip. Nếu dừng trong Error_Handler, kiểm tra cấu hình Clock (HSE Bypass vs Crystal)].
3. **[Hiện tượng lỗi 3, VD: Không tìm thấy cổng COM]**
   * [Cách khắc phục, VD: Đảm bảo đã cài driver ST-LINK. Nâng cấp ST-LINK Firmware qua menu Help > ST-LINK Upgrade].
