# Hướng Dẫn Cấu Hình CubeMX & Tích Hợp Thư Viện LCD (Zero-Error SOP)

Tài liệu này là quy chuẩn bắt buộc (SOP) để khởi tạo một Project có sử dụng màn hình LCD trên bo mạch STM32F429I-DISC1.

---

## PHẦN 1: TẠO VÀ CẤU HÌNH TRONG STM32CUBEMX

### 1. Khởi tạo Project & Tắt cấu hình mặc định (CỰC KỲ QUAN TRỌNG)

1. Mở STM32CubeIDE -> **File -> New -> STM32 Project**.
2. Chọn tab **Board Selector**, gõ `STM32F429I-DISC1` và chọn bo mạch. Bấm **Next**.
3. Đặt tên Project (vd: `my-lcd-project`) -> Bấm **Finish**.
4. **⚠️ BƯỚC QUYẾT ĐỊNH**: Khi có bảng thông báo _"Initialize all peripherals with their default Mode?"_, **BẮT BUỘC CHỌN "NO"**.
   _(Lý do: Nếu chọn Yes, CubeMX sẽ sinh code khởi tạo LCD, SPI, I2C, FMC... trùng lặp với code của thư viện BSP, gây lỗi `Multiple Definition` không thể cứu vãn)._

### 2. Cấu hình System Core

- Vào **System Core** -> **RCC**:
  - `High Speed Clock (HSE)`: Chọn **BYPASS Clock Source**.
- Vào **System Core** -> **SYS**:
  - `Debug`: Chọn **Serial Wire**.
  - `Timebase Source`: Chọn **SysTick**.

### 3. Cấu hình Clock Tree (180 MHz)

1. Chuyển sang tab **Clock Configuration**.
2. Tại **Input frequency**, nhập **8** (MHz).
3. Tại **PLL Source Mux**, chọn **HSE**.
4. Tại ô **HCLK (MHz)**, gõ **180** và nhấn **Enter**.
5. CubeMX sẽ tự động giải quyết các thông số nhân/chia (M, N, P, Q) để đạt 180MHz.

### 4. Thiết lập Project Manager & Sinh Code

1. Chuyển sang tab **Project Manager**.
2. Tại mục **Code Generator**: Chọn **Copy only the necessary library files**.
3. Nhấn **Ctrl + S** (hoặc nút Save) hoặc nhấn phím **Alt+K** để sinh code (Generate Code).

---

## PHẦN 2: TÍCH HỢP THƯ VIỆN THỦ CÔNG VÀO CUBEIDE

Vì chúng ta nhường quyền khởi tạo LCD cho thư viện BSP của ST (để viết code ngắn gọn), CubeMX sẽ không copy các file thư viện liên quan. Chúng ta phải tự copy chúng từ gói Firmware Repository.

### 1. Xác định vị trí Firmware Repository trên máy

- Đường dẫn mặc định: `C:\Users\ADMIN\STM32Cube\Repository\STM32Cube_FW_F4_V1.28.3` (phiên bản V1.xx.x có thể khác tùy máy).

### 2. Tạo cấu trúc thư mục trong Project CubeIDE

Trong **Project Explorer** của CubeIDE, click chuột phải vào Project của bạn, chọn **New -> Folder** và tạo cây thư mục như sau:

```text
my-lcd-project/
├── Drivers/
│   ├── BSP/
│   │   ├── STM32F429I-Discovery/
│   │   ├── Components/
│   │   │   ├── ili9341/
│   │   │   ├── Common/
├── Utilities/
│   ├── Fonts/
```

### 3. Copy các file BSP (Board Support Package)

Truy cập vào đường dẫn Firmware Repository (Phần 2.1), tìm và **copy** các file sau thả vào thư mục tương ứng vừa tạo trong CubeIDE:

1. Vào `Drivers\BSP\STM32F429I-Discovery\` copy thả vào `STM32F429I-Discovery/`:
   - `stm32f429i_discovery.c` và `.h`
   - `stm32f429i_discovery_lcd.c` và `.h`
   - `stm32f429i_discovery_sdram.c` và `.h`
2. Vào `Drivers\BSP\Components\ili9341\` copy thả vào `ili9341/`:
   - `ili9341.c` và `.h`
3. Vào `Drivers\BSP\Components\Common\` copy thả vào `Common/`:
   - **`lcd.h`** _(Thiếu file này sẽ bị lỗi fatal error)_
4. Vào `Utilities\Fonts\` copy thả vào `Fonts/`:
   - `font8.c`, `font12.c`, `font16.c`, `font20.c`, `font24.c` và `fonts.h`

### 4. Copy các file HAL Driver bị thiếu

Tiếp tục trong Firmware Repository, tìm và copy các file thư viện chuẩn:

1. Vào `Drivers\STM32F4xx_HAL_Driver\Src\`, copy thả vào `Drivers/STM32F4xx_HAL_Driver/Src/` của Project:
   - `stm32f4xx_hal_spi.c`
   - `stm32f4xx_hal_i2c.c` và `stm32f4xx_hal_i2c_ex.c`
   - `stm32f4xx_hal_ltdc.c` và `stm32f4xx_hal_ltdc_ex.c`
   - `stm32f4xx_hal_sdram.c`
   - `stm32f4xx_ll_fmc.c`
   - `stm32f4xx_hal_dma2d.c`
2. Vào `Drivers\STM32F4xx_HAL_Driver\Inc\`, copy thả vào `Drivers/STM32F4xx_HAL_Driver/Inc/` của Project:
   - Tất cả các file `.h` tương ứng với các file `.c` ở bước trên (`...hal_spi.h`, `...ll_fmc.h`, v.v.)

### 5. Kích hoạt Macro thư viện trong Code

1. Mở file `Core/Inc/stm32f4xx_hal_conf.h`.
2. Tìm và xóa dấu comment `/*` và `*/` ở 5 dòng sau:

```c
#define HAL_DMA2D_MODULE_ENABLED
#define HAL_SDRAM_MODULE_ENABLED
#define HAL_I2C_MODULE_ENABLED
#define HAL_LTDC_MODULE_ENABLED
#define HAL_SPI_MODULE_ENABLED
```

### 6. Trỏ đường dẫn Include Paths (Quyết định việc biên dịch)

1. Chuột phải vào Project -> **Properties**.
2. Cây menu trái: **C/C++ Build** -> **Settings**.
3. Tab **Tool Settings**, chọn **MCU GCC Compiler** -> **Include paths**.
4. Bấm biểu tượng **Thêm (Add)** (Màu xanh lá) -> Chọn **Workspace...** và thêm 3 đường dẫn:
   - `/Drivers/BSP/STM32F429I-Discovery`
   - `/Drivers/BSP/Components/ili9341`
   - `/Utilities/Fonts`
5. Nhấn **Apply and Close**.

🎉 **HOÀN TẤT SETUP!** Bây giờ bạn có thể dùng file `skeleton-main.c` để bắt đầu code giao diện mà không lo gặp bất kỳ lỗi biên dịch nào.
