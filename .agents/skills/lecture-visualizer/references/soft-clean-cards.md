# Design System — "Soft Clean Cards"

> Phong cách: sáng, thoáng, bo tròn lớn, đổ bóng rất nhẹ, một con số/tiêu đề lớn làm điểm nhấn, màu sắc chỉ xuất hiện ở **dữ liệu** (chart, trạng thái), còn lại gần như đơn sắc.

File này là nguồn sự thật (source of truth) cho mọi thiết kế UI. Khi dùng với AI (Claude, Cursor, v.v.), hãy đính kèm file này và yêu cầu: _"Tuân thủ nghiêm ngặt DESIGN_SYSTEM.md."_

---

## 1. Triết lý thiết kế

1. **Một thẻ = một nhiệm vụ.** Mỗi card trả lời đúng một câu hỏi (nhịp tim bao nhiêu? tuần này tốn bao nhiêu token? đang phát bài gì?).
2. **Con số/tiêu đề là nhân vật chính.** Một phần tử lớn, mọi thứ còn lại nhỏ và im lặng.
3. **Màu là thông tin, không phải trang trí.** UI nền trắng–xám; màu chỉ dùng cho dữ liệu, nút chính, và trạng thái.
4. **Khoảng trắng hào phóng.** Thà thừa khoảng trống còn hơn nhồi nhét.
5. **Phân cấp bằng cỡ chữ và độ xám**, không bằng viền đậm, không bằng nhiều màu.
6. **Bo tròn nhất quán, đổ bóng mờ, không viền cứng.**

---

## 2. Design Tokens

### 2.1 Màu sắc

#### Neutral (chiếm ~95% giao diện)

| Token               | Hex       | Dùng cho                                                     |
| ------------------- | --------- | ------------------------------------------------------------ |
| `--bg-page`         | `#F5F5F7` | Nền trang (có thể chuyển nhẹ sang xám đậm hơn ở đáy)         |
| `--bg-card`         | `#FFFFFF` | Nền card                                                     |
| `--bg-subtle`       | `#F4F4F6` | Nền phụ trong card: vùng chart, segmented control, nút ghost |
| `--bg-subtle-hover` | `#ECECEF` | Hover của vùng phụ                                           |
| `--border-hairline` | `#EFEFF2` | Đường kẻ rất mờ, divider, grid chart                         |
| `--border-card`     | `#E9E9EE` | Viền ngoài card (rất mờ, 1px)                                |
| `--text-primary`    | `#0B0B0F` | Tiêu đề, số lớn, giá trị                                     |
| `--text-secondary`  | `#6B6B76` | Nhãn, phụ đề, đơn vị                                         |
| `--text-tertiary`   | `#9A9AA5` | Trục chart, timestamp, placeholder                           |
| `--ink`             | `#111114` | Nút chính (nút Play đen)                                     |

#### Data palette (chỉ dùng cho chart/trạng thái)

Bốn màu bão hòa, đủ khác biệt khi xếp chồng, dùng theo đúng thứ tự từ dưới lên:

| Token                | Hex       | Ghi chú                     |
| -------------------- | --------- | --------------------------- |
| `--data-1` (blue)    | `#1F5FFF` | Series chính, nằm dưới cùng |
| `--data-2` (purple)  | `#B13BF0` |                             |
| `--data-3` (orange)  | `#FF8A1F` |                             |
| `--data-4` (green)   | `#1FA63A` | Nằm trên cùng               |
| `--data-alert` (red) | `#E5483D` | Đường ECG, cảnh báo, lỗi    |

#### Pastel (ảnh bìa, avatar, minh họa)

`#FFD9E8` hồng · `#D9E8FF` xanh nhạt · `#FFF1C9` vàng · `#D8F3E4` mint · `#E6DDFB` tím nhạt

Quy tắc:

- Không dùng quá **4 màu data** trong một chart.
- Không dùng gradient làm trang trí. Chỉ cho phép gradient cực nhẹ ở nền trang (trắng → xám `#EDEDF0`).
- Text trên nền màu phải đạt tương phản WCAG AA (4.5:1).

### 2.2 Typography

**Font:** sans-serif hình học, hiện đại, dễ đọc. Ưu tiên `Inter`; thay thế `Geist`, `SF Pro`, `system-ui`.

```css
font-family:
  "Inter",
  "Geist",
  -apple-system,
  BlinkMacSystemFont,
  "Segoe UI",
  sans-serif;
font-feature-settings:
  "tnum" 1,
  "cv11" 1; /* số có độ rộng cố định */
```

| Vai trò    | Size / Line-height | Weight | Màu       | Ví dụ                             |
| ---------- | ------------------ | ------ | --------- | --------------------------------- |
| `display`  | 64 / 1             | 400    | primary   | `77` (số lớn)                     |
| `title-lg` | 28 / 1.15          | 500    | primary   | "Token spend", "Deep Current"     |
| `title-md` | 18 / 1.25          | 600    | primary   | "Core strength"                   |
| `value`    | 15 / 1.3           | 500    | primary   | `1.6`, `640K`                     |
| `body`     | 14 / 1.4           | 400    | primary   | Tên mục trong legend              |
| `label`    | 13 / 1.3           | 400    | secondary | "Current", "Average", "Jul 1 – 7" |
| `caption`  | 12 / 1.3           | 400    | tertiary  | Nhãn trục, thời lượng 0:00        |

Quy tắc:

- Số lớn đi kèm **đơn vị nhỏ, màu xám, căn theo baseline** (`77` + `bpm`).
- **Sentence case** cho mọi nhãn. Không viết HOA toàn bộ, không letter-spacing rộng.
- Letter-spacing nhẹ âm (`-0.02em`) cho `display` và `title-lg`.
- Luôn bật `tabular-nums` cho số trong bảng, legend, chart.
- Không quá hai weight trong một card (thường là 400 và 500).

### 2.3 Spacing (lưới 4px)

`4 · 8 · 12 · 16 · 20 · 24 · 32 · 40 · 48`

- Padding card: **24px** (mobile: 20px)
- Khoảng cách giữa các block trong card: **20–24px**
- Khoảng cách giữa label và value: **4px**
- Khoảng cách giữa các hàng legend: **12px**
- Khoảng cách giữa các card: **24–32px**

### 2.4 Bo góc

| Token           | Giá trị | Dùng cho                                  |
| --------------- | ------- | ----------------------------------------- |
| `--radius-xs`   | 4px     | Đoạn cột trong chart                      |
| `--radius-sm`   | 8px     | Chip nhỏ, tooltip                         |
| `--radius-md`   | 12px    | Nút ghost full-width, ảnh bìa, vùng chart |
| `--radius-lg`   | 16px    | Segmented control (khung)                 |
| `--radius-xl`   | 28px    | **Card**                                  |
| `--radius-full` | 999px   | Nút tròn, pill, avatar                    |

Quy tắc lồng nhau: bo góc phần tử bên trong = bo góc phần tử cha − padding (xấp xỉ), để các góc trông song song.

### 2.5 Đổ bóng và viền

```css
--shadow-card:
  0 1px 2px rgba(16, 16, 24, 0.04), 0 8px 24px rgba(16, 16, 24, 0.06);

--shadow-control:   /* nút tròn nhỏ, tab đang chọn */
  0 1px 2px rgba(16, 16, 24, 0.08), 0 0 0 1px rgba(16, 16, 24, 0.04);

--shadow-primary:   /* nút Play */ 0 6px 16px rgba(16, 16, 24, 0.22);
```

- Card luôn có `--shadow-card` + viền 1px `--border-card`. Bóng phải _mờ và rộng_, không bao giờ đen đậm.
- Không chồng nhiều tầng bóng khác nhau lên cùng một phần tử.

---

## 3. Layout

- Canvas nền `--bg-page`, các card đặt cách đều, **căn giữa theo chiều ngang**.
- Chiều rộng card tham chiếu: 320–340px (card đơn), có thể mở rộng trên desktop theo grid.
- Grid: 12 cột, gutter 24px. Dashboard: 1 cột (mobile), 2 cột (tablet), 3 cột (desktop).
- **Căn lề trái** cho nội dung văn bản và chart; **căn giữa** chỉ cho con số hero (như `77 bpm`) và cụm điều khiển media.
- Mỗi card theo cấu trúc dọc:

```
┌──────────────────────────────┐
│ Header (tiêu đề / hành động) │
│                              │
│ Hero (số lớn hoặc visual)    │
│                              │
│ Vùng dữ liệu (chart/ảnh)     │
│                              │
│ Chi tiết (3 cột / legend)    │
│ Footer (nút ghost / social)  │
└──────────────────────────────┘
```

---

## 4. Components

### 4.1 Card

```css
.card {
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: 28px;
  padding: 24px;
  box-shadow: var(--shadow-card);
  display: flex;
  flex-direction: column;
  gap: 20px;
}
```

Không đặt card trong card. Dùng `--bg-subtle` để tạo vùng phụ bên trong.

### 4.2 Nút tròn nhỏ (icon button)

Dùng cho "quay lại", "thêm tùy chọn (···)", trái tim.

- Kích thước 32×32 (touch target thực tế ≥ 44px nhờ padding vô hình)
- Nền trắng, `--shadow-control`, `border-radius: 999px`
- Icon 16px, nét 1.5px, màu `--text-primary`
- Hover: nền `--bg-subtle`; Active: `scale(0.96)`

### 4.3 Nút chính tròn (Play)

- 52×52, nền `--ink`, icon trắng đặc 20px, `--shadow-primary`
- Hai nút phụ hai bên (tua lại/tới): chỉ có icon đen, **không nền**, cách nút chính 32–40px
- Là phần tử duy nhất có nền tối đặc trong card, nên mắt tự động dồn vào đó

### 4.4 Segmented control (Week / Month / Year)

```css
.segmented {
  background: var(--bg-subtle);
  border-radius: 16px;
  padding: 4px;
  display: inline-flex;
}
.segmented button {
  padding: 6px 14px;
  border-radius: 12px;
  font-size: 13px;
  color: var(--text-secondary);
}
.segmented button[aria-selected="true"] {
  background: #fff;
  color: var(--text-primary);
  font-weight: 500;
  box-shadow: var(--shadow-control);
}
```

Chuyển tab: nền trắng trượt sang vị trí mới trong 200ms.

### 4.5 Nút ghost full-width ("Details")

- Nền `--bg-subtle`, radius 12, cao 44, padding ngang 16
- Chữ `label` trái, chevron phải (16px, màu secondary)
- Hover: `--bg-subtle-hover`; chevron xoay 180° khi mở rộng

### 4.6 Hàng chỉ số (metric row)

Ba cột đều nhau, mỗi cột gồm nhãn trên, giá trị dưới:

```
Current        Average        Max
1.6 sec/sqt    2.2 sec/sqt    4.2 sec/sqt
```

- Nhãn: `label`, secondary
- Giá trị: `value` (primary), đơn vị: `label` (secondary), cách giá trị 4px
- Không có divider giữa các cột; khoảng trắng đã đủ phân tách

### 4.7 Legend (chú giải dạng danh sách)

Mỗi hàng: chấm màu 8px → tên (`body`) → giá trị căn phải (`value`, tabular-nums).
Không dùng viền, không dùng nền xen kẽ. Khoảng cách hàng 12px.

### 4.8 Thanh tiến trình (media)

- Track cao 2px, `--border-hairline`; phần đã chạy `--text-primary`
- Mốc thời gian `caption` hai đầu (trái `0:00`, phải `4:05`)

### 4.9 Avatar stack + "likes"

- Avatar 28px tròn, nền pastel, chữ viết tắt 10px, chồng lên nhau −6px, viền trắng 2px
- Theo sau là text `body` ("9 likes") và chevron mở rộng ở cuối hàng
- Phía trên là divider `1px --border-hairline`

### 4.10 Ảnh bìa / thumbnail

- Vuông, 104px (trong card), radius 12, `object-fit: cover`
- Nền pastel, chủ thể rõ ràng, ít chi tiết

---

## 5. Data visualization

### 5.1 Stacked bar chart

- Mỗi cột rộng ~32px, khoảng cách giữa các cột ~16–20px (cột : khe ≈ 1 : 0.6)
- Đoạn xếp chồng cách nhau **2px**, mỗi đoạn `border-radius: 4px`
- Thứ tự màu: `data-1` ở đáy → `data-4` ở đỉnh, giống nhau ở mọi cột
- **Không có trục Y, không có gridline.** Chiều cao cột đã đủ nói lên giá trị
- Nhãn trục X: `caption`, secondary, căn giữa dưới cột (Mon, Tue, …)
- Tổng giá trị đặt phía trên chart: `1.7M` (`title-md`) + `Tokens` (`label`, secondary)
- Hover: làm mờ các cột khác về 40% opacity, hiện tooltip trắng, radius 8, `--shadow-control`

### 5.2 Biểu đồ nhịp tim / line chart

- Nằm trong vùng `--bg-subtle`, radius 12, cao ~96px
- Grid: đường kẻ dọc/ngang 1px `--border-hairline`, bước 24px
- Đường dữ liệu: 1.5–2px, `--data-alert`, `stroke-linejoin: round`
- Không điểm đánh dấu, không fill dưới đường

### 5.3 Quy tắc chung

- Tối đa 4 series, luôn có legend dạng danh sách (mục 4.7) có kèm giá trị
- Không dùng 3D, không đổ bóng cho chart, không viền quanh cột
- Màu không là kênh thông tin duy nhất: legend luôn có nhãn chữ

---

## 6. Iconography

- Bộ icon nét mảnh: **Lucide** hoặc **Phosphor (Regular)**
- Nét 1.5px, góc bo tròn, kích thước 16 / 20 / 24
- Màu kế thừa `currentColor`
- Icon điều khiển media (play, prev, next) dùng dạng **đặc**; icon điều hướng dùng dạng **nét**

---

## 7. Motion

Chuyển động chỉ để phản hồi hành động của người dùng:

| Tương tác                  | Thời lượng | Easing                             |
| -------------------------- | ---------- | ---------------------------------- |
| Hover/nhấn nút             | 120ms      | `ease-out`                         |
| Chuyển tab segmented       | 200ms      | `cubic-bezier(0.32, 0.72, 0, 1)`   |
| Mở rộng (chevron, Details) | 240ms      | `cubic-bezier(0.32, 0.72, 0, 1)`   |
| Cột chart đổi dữ liệu      | 400ms      | `ease-in-out` (cao độ chuyển mượt) |

- Không animation tự chạy lặp vô hạn, không hiệu ứng "bay vào" cho từng card
- Tôn trọng `prefers-reduced-motion: reduce` (tắt hoặc giảm còn fade)

---

## 8. Nội dung và giọng văn

- Ngắn, rõ, danh từ cụ thể: "Token spend", "Core strength", "Details"
- Sentence case, không dấu chấm cuối nhãn
- Khoảng ngày viết gọn: `Jul 1 – 7`
- Số lớn đi cùng đơn vị: `1.7M Tokens`, `77 bpm`, `4:05`
- Nút hành động nói đúng việc sẽ xảy ra ("Save changes", không phải "Submit")

---

## 9. Accessibility

- Tương phản chữ thường ≥ 4.5:1 (đặc biệt `--text-tertiary` trên trắng: chỉ dùng cho caption không thiết yếu, hoặc tối đi thành `#7C7C88`)
- Vùng chạm tối thiểu 44×44px
- Focus ring rõ ràng: `outline: 2px solid #1F5FFF; outline-offset: 2px`
- Chart có `aria-label` mô tả tóm tắt + bảng dữ liệu thay thế cho screen reader
- Segmented control dùng `role="tablist"` / `role="tab"` và `aria-selected`

---

## 10. CSS variables (copy dùng ngay)

```css
:root {
  /* neutral */
  --bg-page: #f5f5f7;
  --bg-card: #ffffff;
  --bg-subtle: #f4f4f6;
  --bg-subtle-hover: #ececef;
  --border-hairline: #efeff2;
  --border-card: #e9e9ee;
  --text-primary: #0b0b0f;
  --text-secondary: #6b6b76;
  --text-tertiary: #9a9aa5;
  --ink: #111114;

  /* data */
  --data-1: #1f5fff;
  --data-2: #b13bf0;
  --data-3: #ff8a1f;
  --data-4: #1fa63a;
  --data-alert: #e5483d;

  /* radius */
  --radius-xs: 4px;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 28px;
  --radius-full: 999px;

  /* shadow */
  --shadow-card:
    0 1px 2px rgba(16, 16, 24, 0.04), 0 8px 24px rgba(16, 16, 24, 0.06);
  --shadow-control:
    0 1px 2px rgba(16, 16, 24, 0.08), 0 0 0 1px rgba(16, 16, 24, 0.04);
  --shadow-primary: 0 6px 16px rgba(16, 16, 24, 0.22);

  /* spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
}

body {
  background: linear-gradient(180deg, var(--bg-page) 70%, #ededf0 100%);
  color: var(--text-primary);
  font-family:
    "Inter",
    "Geist",
    -apple-system,
    "Segoe UI",
    sans-serif;
  font-variant-numeric: tabular-nums;
  -webkit-font-smoothing: antialiased;
}
```

### Tailwind (`tailwind.config.js`)

```js
export default {
  theme: {
    extend: {
      colors: {
        page: "#F5F5F7",
        subtle: "#F4F4F6",
        ink: "#111114",
        muted: { DEFAULT: "#6B6B76", soft: "#9A9AA5" },
        data: {
          1: "#1F5FFF",
          2: "#B13BF0",
          3: "#FF8A1F",
          4: "#1FA63A",
          alert: "#E5483D",
        },
      },
      borderRadius: { card: "28px" },
      boxShadow: {
        card: "0 1px 2px rgba(16,16,24,.04), 0 8px 24px rgba(16,16,24,.06)",
        control: "0 1px 2px rgba(16,16,24,.08), 0 0 0 1px rgba(16,16,24,.04)",
      },
      fontFamily: { sans: ["Inter", "Geist", "system-ui", "sans-serif"] },
    },
  },
};
```

Ví dụ card:

```html
<div
  class="bg-white rounded-card shadow-card border border-black/5 p-6 flex flex-col gap-5"
>
  <h2 class="text-[28px] font-medium tracking-tight">Token spend</h2>
  <p class="text-[13px] text-muted">Jul 1 – 7</p>
</div>
```

---

## 11. Nên và không nên

**Nên**

- Dùng một nhân vật chính mỗi card (số lớn, ảnh bìa, hoặc chart)
- Giữ nền trắng + chữ đen/xám, để màu dành cho dữ liệu
- Bo góc lớn, bóng mờ, khoảng trắng rộng
- Căn chỉnh theo lưới 4px

**Không nên**

- Viền đậm, viền màu quanh card
- Gradient rực rỡ hoặc nền màu loang làm trang trí
- Chữ HOA + letter-spacing rộng cho nhãn
- Nhiều hơn 2 weight chữ trong một card
- Trục, gridline, 3D, hiệu ứng thừa trong chart
- Nhiều nút chính (nền đen/đặc) trong cùng một card
- Đặt card trong card, hoặc bóng đen/đậm

---

## 12. Checklist trước khi giao

- [ ] Mỗi card có đúng một điểm nhấn chính?
- [ ] Màu rực chỉ xuất hiện ở dữ liệu và nút chính?
- [ ] Mọi bo góc/khoảng cách nằm trong token ở mục 2?
- [ ] Số dùng `tabular-nums`, đơn vị nhỏ và xám?
- [ ] Nhãn dùng sentence case?
- [ ] Bóng mờ, không có viền cứng?
- [ ] Đạt tương phản và vùng chạm 44px?
- [ ] Hoạt động tốt ở 360px, tôn trọng `prefers-reduced-motion`?

---

## 13. Prompt mẫu để giao việc cho AI

```
Hãy thiết kế [màn hình/component] cho [sản phẩm].
Tuân thủ nghiêm ngặt DESIGN_SYSTEM.md đính kèm:
- Card trắng, radius 28px, padding 24px, shadow-card
- Một nhân vật chính trong mỗi card (số lớn hoặc chart hoặc ảnh)
- Font Inter, sentence case, số tabular, đơn vị nhỏ màu xám
- Màu rực chỉ dùng cho dữ liệu (data-1..4) và nút chính màu ink
- Không gradient trang trí, không viền đậm, không chữ HOA
Nội dung thực: [dán dữ liệu thật vào đây].
```
