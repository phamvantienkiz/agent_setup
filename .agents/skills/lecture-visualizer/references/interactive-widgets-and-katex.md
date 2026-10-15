# Cấu Hình KaTeX & Bộ Widget Tương Tác Sư Phạm (Interactive Widgets & KaTeX)

Tài liệu này cung cấp code mẫu và cơ chế hoạt động cho hệ thống kết xuất toán học KaTeX cùng 4 loại Widget tương tác mẫu mực.

---

## 1. Cấu Hình KaTeX Render Toán Học Không Lỗi

Để toàn bộ công thức toán học hiển thị chuẩn xác (chuẩn LaTeX của các tạp chí khoa học ACM/IEEE) mà không để lộ text raw dạng `$\sigma$` hay `$$...$$`:

### 1.1 Khai Báo CDN Tại Header:
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"></script>
```

### 1.2 Khởi Tạo Script Render Tự Động:
```javascript
document.addEventListener("DOMContentLoaded", function() {
    renderMathInElement(document.body, {
        delimiters: [
            {left: '$$', right: '$$', display: true},
            {left: '$', right: '$', display: false},
            {left: '\\[', right: '\\]', display: true},
            {left: '\\(', right: '\\)', display: false}
        ],
        throwOnError: false
    });
});
```

> **Quy tắc quan trọng:** Bất kỳ khi nào một widget JavaScript tiêm (inject) HTML mới chứa công thức toán vào DOM (như khi nhấn nút slider hay chuyển bước simulator), **bắt buộc phải gọi lại `renderMathInElement`** trên container đó:
> ```javascript
> if (window.renderMathInElement) {
>     renderMathInElement(targetContainer, {
>         delimiters: [{left: '$', right: '$', display: false}],
>         throwOnError: false
>     });
> }
> ```

---

## 2. Widget 1: Thanh Trượt Trực Quan Hóa Bùng Nổ Tổ Hợp (Combinatorial Slider)

Giúp người học "cảm nhận" được sự bùng nổ cấp số nhân của không gian trạng thái $2^M$ hoặc độ phức tạp $O(N^2), O(2^N)$ một cách trực quan:

```html
<div class="interactive-card">
    <h4>🧮 Trực Quan Hóa: Thảm Họa Bùng Nổ Tổ Hợp $2^{|I|}$</h4>
    <p class="subtitle">Kéo thanh trượt để quan sát sự tăng trưởng cấp số nhân của không gian tìm kiếm khi số lượng mặt hàng $m$ tăng lên:</p>
    <div style="display: flex; align-items: center; gap: 16px; margin: 12px 0;">
        <label for="item-slider" style="font-weight: 600;">Số lượng mục ($m$):</label>
        <input type="range" id="item-slider" min="5" max="60" value="20" style="flex: 1; max-width: 300px;">
        <span id="slider-val" style="font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #2563eb;">20 mục</span>
    </div>
    <div id="calc-result" style="background: #ffffff; padding: 14px 18px; border-radius: 6px; border: 1px solid #cbd5e1; font-family: 'JetBrains Mono', monospace; font-size: 0.92rem;">
        <!-- Kết quả tính toán tiêm qua JS -->
    </div>
</div>
```

```javascript
function initSlider() {
    const slider = document.getElementById('item-slider');
    const valLabel = document.getElementById('slider-val');
    const resultBox = document.getElementById('calc-result');

    function update() {
        const m = parseInt(slider.value);
        valLabel.innerText = m + ' mục';
        const total = Math.pow(2, m);
        const pairs = (m * (m - 1)) / 2;
        
        let timeStr = "";
        if (m <= 25) timeStr = "< 1 mili-giây (siêu nhanh)";
        else if (m <= 35) timeStr = "~ vài giây đến 1 phút";
        else if (m <= 45) timeStr = "~ nhiều ngày tính toán";
        else timeStr = "> hàng tỷ năm nếu duyệt vét cạn!";

        resultBox.innerHTML = `
            <div>• Kích thước không gian tìm kiếm $2^{${m}}$: <strong>${total.toLocaleString('vi-VN')}</strong> tập mục</div>
            <div>• Số cặp ứng viên tầng 2 ($C_2 = \\binom{${m}}{2}$): <strong>${pairs.toLocaleString('vi-VN')}</strong> cặp</div>
            <div style="margin-top: 6px; color: #dc2626;">• Thời gian duyệt vét cạn (1 tỷ mục/giây): <strong>${timeStr}</strong></div>
        `;
        if (window.renderMathInElement) {
            renderMathInElement(resultBox, {
                delimiters: [{left: '$', right: '$', display: false}],
                throwOnError: false
            });
        }
    }
    slider.addEventListener('input', update);
    update();
}
```

---

## 3. Widget 2: Trình Mô Phỏng Cây / Trạng Thái Từng Bước (Step-by-Step Simulator)

Hiển thị một chuỗi các nút bấm bước 0, 1, 2, 3... Khi học viên nhấn từng nút, sơ đồ cây hoặc đồ thị biến đổi tương ứng, làm nổi bật (highlight) nhánh mới được thêm vào và giải thích bằng lời văn:

```html
<div class="interactive-card">
    <h4>🌳 Trình Mô Phỏng Xây Dựng Cấu Trúc Dữ Liệu Từng Bước</h4>
    <p class="subtitle">Nhấn từng nút để quan sát thao tác chèn giao dịch và cơ chế chia sẻ tiền tố:</p>
    
    <div class="btn-group">
        <button class="interactive-btn active" onclick="setStep(0)">0. Khởi Tạo</button>
        <button class="interactive-btn" onclick="setStep(1)">1. Chèn Giao Dịch 1</button>
        <button class="interactive-btn" onclick="setStep(2)">2. Chèn Giao Dịch 2</button>
        <!-- Thêm các bước kế tiếp -->
    </div>

    <div class="sim-view" id="step-sim-view">
        <!-- JS render sơ đồ và giải thích -->
    </div>
</div>
```

---

## 4. Widget 3: Trình Khám Phá Trạng Thái / Hậu Tố (State Explorer)

Dành cho các thuật toán chia để trị, quy hoạch động hoặc duyệt đồ thị: Cho phép học viên nhấp vào từng đối tượng (ví dụ: từng hậu tố $p, m, b, a, c, f$) để xem:
- Các đường dẫn tiền tố liên quan.
- Bài toán con điều kiện thu nhỏ.
- Kết quả trung gian sinh ra.

---

## 5. Widget 4: Bộ 15 Câu Hỏi Phản Biện Bảo Vệ Đề Tài (Defense Q&A Accordion)

Tập hợp 15 câu hỏi xoáy sâu vào bản chất toán học, trường hợp biên (worst case), so sánh đối thủ, và xử lý Big Data.

```html
<div id="qa-container">
    <!-- JS render danh sách câu hỏi đóng/mở -->
</div>
```

```javascript
const qaList = [
    {
        q: "1. Tại sao thuật toán này lại tối ưu hơn thuật toán cũ?",
        a: "Phân tích 3 lý do kỹ thuật: Chi phí I/O đĩa cứng, dung lượng bộ nhớ RAM và số chu kỳ CPU..."
    },
    // Các câu hỏi tiếp theo
];

function initQA() {
    const container = document.getElementById('qa-container');
    container.innerHTML = qaList.map((item, idx) => `
        <div class="qa-card" id="qa-${idx}">
            <div class="qa-question" onclick="toggleQA(${idx})">${item.q}</div>
            <div class="qa-answer">${item.a}</div>
        </div>
    `).join('');
    if (window.renderMathInElement) {
        renderMathInElement(container, {
            delimiters: [{left: '$', right: '$', display: false}],
            throwOnError: false
        });
    }
}

function toggleQA(idx) {
    const card = document.getElementById(`qa-${idx}`);
    card.classList.toggle('open');
}
```
