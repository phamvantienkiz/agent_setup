# STM32F429I-DISC1 LCD Skeleton Template

Bộ khung (Skeleton) này được đúc kết từ kinh nghiệm thực chiến xử lý các xung đột phần cứng khi làm việc với màn hình LCD trên bo mạch **STM32F429I-DISC1**. 

Mục tiêu của bộ khung này là cung cấp một **Quy trình chuẩn hóa (Standard Operating Procedure - SOP)** giúp bạn khởi tạo nhanh chóng bất kỳ dự án nào liên quan đến màn hình LCD trong tương lai, cam kết **0 lỗi biên dịch (Zero Compile Errors)** và bỏ qua mọi xung đột khó chịu của STM32CubeMX.

## 📦 Thành phần của bộ Skeleton
Bộ khung này bao gồm 3 tài liệu chính:

1. **[01-cubemx-and-ide-setup.md](./01-cubemx-and-ide-setup.md)**
   - Hướng dẫn "từng cú click chuột" để cấu hình Clock và Project trong CubeMX.
   - Danh sách chính xác 100% các file BSP và HAL Driver cần copy thủ công.
   - Hướng dẫn cấu hình STM32CubeIDE (Include Paths, Macro ENABLE).
   - *Sử dụng file này mỗi khi bạn bấm nút "New STM32 Project".*

2. **[02-architecture-and-theory.md](./02-architecture-and-theory.md)**
   - Trình bày kiến trúc phần cứng của màn hình (LTDC, SDRAM, DMA2D).
   - Giải thích lý do cốt lõi tại sao phải cấu hình thủ công (Xung đột `MspInit` giữa CubeMX và ST BSP).
   - Kỹ thuật "Padding" xử lý nháy màn hình (Flickering) khi cập nhật dữ liệu liên tục.
   - *Dành cho Developer đọc để hiểu bản chất hệ thống trước khi code.*

3. **[skeleton-main.c](./skeleton-main.c)**
   - File mã nguồn C mẫu chuẩn mực.
   - Chứa sẵn cấu trúc khởi tạo LCD, cấu hình Layer, và vòng lặp `while(1)` cập nhật giao diện không bị nháy.
   - *Copy thẳng vào `Core/Src/main.c` của Project mới làm điểm xuất phát.*

## 🚀 Hướng dẫn sử dụng nhanh
1. Mở STM32CubeIDE và tạo Project mới cho board `STM32F429I-DISC1`.
2. Mở file **`01-cubemx-and-ide-setup.md`** và làm theo đúng từng bước.
3. Thay thế toàn bộ nội dung file `main.c` sinh ra bằng nội dung của **`skeleton-main.c`**.
4. Bấm Build (F5) và nạp code. Màn hình sẽ sáng lên ngay lập tức!
5. Bắt đầu phát triển tính năng riêng của bạn dựa trên nền tảng LCD đã hoạt động.
