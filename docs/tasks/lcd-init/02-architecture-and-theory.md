# Kiến Trúc Màn Hình & Lý Thuyết Cốt Lõi (STM32F429I-DISC1)

Hiểu rõ kiến trúc bên dưới sẽ giúp bạn làm chủ LCD và tự tin gỡ lỗi (debug) thay vì chỉ học vẹt các bước copy/paste code.

## 1. Tại Sao Không Dùng CubeMX Khởi Tạo LCD? (Cuộc Chiến MspInit)

Nếu bạn tick chọn khởi tạo SPI5, LTDC, FMC (SDRAM), I2C3 trong CubeMX, CubeMX sẽ tự động sinh ra các hàm khởi tạo cấu hình chân cắm, xung nhịp (gọi là `HAL_XXX_MspInit`) bên trong file `stm32f4xx_hal_msp.c`.

Đồng thời, bộ thư viện **BSP (Board Support Package)** của hãng ST cũng được viết sẵn để chứa các hàm `HAL_XXX_MspInit` này nhằm mục đích đóng gói toàn bộ cấu hình phần cứng thành các hàm siêu ngắn ngọn như `BSP_LCD_Init()`.

**Hậu quả:** Trình biên dịch sẽ báo lỗi `Multiple Definition` (Định nghĩa nhiều lần) do tồn tại 2 hàm trùng tên `MspInit` trong toàn bộ Project. 
-> **Giải pháp chuẩn:** Không cấu hình ngoại vi trong CubeMX, tự copy các file `.c`, `.h` của HAL Driver và để BSP toàn quyền khởi tạo. Đó là lý do ra đời tài liệu `01-cubemx-and-ide-setup.md`.

## 2. Kiến Trúc 3 Tầng Điều Khiển LCD
Trên bo STM32F429I-DISC1, LCD không hoạt động độc lập mà là sự phối hợp của 3 thành phần phần cứng mạnh mẽ:
1. **LTDC (LCD-TFT Display Controller):** Khối ngoại vi phần cứng của STM32, chịu trách nhiệm bắn liên tục tín hiệu màu (RGB) và tín hiệu đồng bộ (H-Sync, V-Sync) ra panel màn hình (Chip ILI9341).
2. **FMC (Flexible Memory Controller) & SDRAM:** LTDC cần một vùng nhớ khổng lồ để chứa dữ liệu hình ảnh (Frame Buffer). Chip STM32F429 không đủ RAM nội (chỉ có 256KB), do đó nó dùng bộ nhớ RAM ngoài (SDRAM 8MByte) giao tiếp qua FMC.
3. **DMA2D (Chrom-Art Accelerator):** Con chip "Đồ họa" chuyên dụng của STM32, giúp copy/vẽ hình khối/chuyển đổi hệ màu siêu tốc từ RAM ra Frame Buffer mà không cần CPU nhúng tay vào.

**Flow dữ liệu:** CPU tính toán màu sắc -> Gửi cho DMA2D -> DMA2D vẽ vào SDRAM (Frame Buffer) -> LTDC tự động đọc liên tục từ SDRAM đẩy ra màn hình ILI9341.

## 3. Quản Lý Layer
LTDC hỗ trợ 2 Layer (Lớp hình ảnh) chồng lên nhau (Background và Foreground).
- `BSP_LCD_LayerDefaultInit(LayerIndex, FrameBufferAddress)`: Hàm này cấp phát 1 vùng nhớ trong SDRAM cho Layer.
- `BSP_LCD_SelectLayer(LayerIndex)`: Trước khi vẽ bất cứ thứ gì, bạn phải gọi hàm này để chọn xem mình sẽ vẽ lên Layer nào.

## 4. Kỹ Thuật "Padding" (Đệm Xóa) Khi Cập Nhật Text
Vấn đề kinh điển khi vẽ chữ lên LCD liên tục (ví dụ: vẽ thời gian, vẽ tọa độ Gyro) là **nháy chữ (flickering)** hoặc **chữ cái đè lên nhau nát bét**.

**Lý do:** Hàm `BSP_LCD_DisplayStringAt()` khi vẽ chữ mới, nó không xóa hết nền đằng sau chữ cũ.
**Giải pháp sai lầm phổ biến:** Dùng `BSP_LCD_Clear()` trước khi in. Màn hình chớp nháy liên tục vì tốc độ xóa/vẽ không đồng bộ với tần số quét.
**Giải pháp chuẩn xác (Padding):** Thêm khoảng trắng (dấu cách) vào cuối chuỗi `sprintf` để đảm bảo độ dài chuỗi luôn cố định. Các khoảng trắng này sẽ "tô đè" lên các ký tự thừa của chuỗi cũ mà không cần xóa nguyên cả màn hình.

**Ví dụ:**
```c
char str[50];
// Chuỗi cũ: "Value: -123" (11 ký tự)
// Chuỗi mới: "Value: 4" (8 ký tự)
// NẾU KHÔNG CÓ PADDING -> Màn hình hiện: "Value: 4123" (bị dính số đuôi)

// DÙNG PADDING (15 khoảng trống):
sprintf(str, "Value: %d               ", 4);
// Màn hình in ra chuỗi mới đè kín 15 ký tự, "cạo" sạch các số rác ở đuôi.
BSP_LCD_DisplayStringAt(10, 50, (uint8_t*)str, LEFT_MODE);
```
