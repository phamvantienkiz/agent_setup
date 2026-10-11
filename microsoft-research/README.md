# MICROSOFT RESEARCH SKILLS SUITE (HITL EDITION)

> **Bộ Kỹ năng Nghiên cứu Khoa học Tinh hoa từ Microsoft Research & AI-Nuts**  
> *Được chuẩn hóa cho AI Coding Agent (Antigravity CLI / Claude Code / Codex)*  
> *Mô hình cộng tác: Con người là trung tâm (Human-in-the-Loop) — Không tự hành đóng kín*  
> *Môi trường: Cô lập 100% trong `.venv` — Chạy mượt mà trên laptop thông thường (CPU/GPU onboard/Apple Silicon)*

---

## 1. TỔNG QUAN

Thư mục `microsoft-research` là kho kỹ năng gốc được trích xuất, tối ưu hóa và chuẩn hóa từ dự án **ResearchStudio** của Microsoft Research (arXiv:2607.04439 & 2607.04438).

Thay vì để AI "chạy một mạch tự động" từ đầu đến cuối như phiên bản thử nghiệm của Microsoft, bộ kỹ năng này được thiết kế lại theo mô hình **Cộng tác Từng bước (Step-by-Step Collaboration)**:
- AI hỗ trợ tìm kiếm tài liệu, phân tích đối chiếu, gợi ý mẫu hình sáng tạo và phác thảo giải pháp.
- Người nghiên cứu (bạn) đóng vai trò thẩm định, chốt điểm nghẽn, lựa chọn cơ chế và định hướng thực nghiệm.
- Mỗi chặng nghiên cứu đều dừng lại xin ý kiến và xuất báo cáo kiểm chứng vào `docs/ai/`.

---

## 2. DANH MỤC 11 KỸ NĂNG TRÍCH XUẤT

Bộ kỹ năng gồm 2 phân hệ đối xứng tương ứng với hai đầu mút của chu trình nghiên cứu:

### Phân hệ 1: Tiền bài báo (The First Mile — Ý tưởng & Tính mới)
| Tên Thư mục Skill | Tên Kỹ năng | Mô tả chức năng | Điểm dừng Human Gate |
| :--- | :--- | :--- | :--- |
| `rs-paper-search/` | `rs-paper-search` | Tìm kiếm tài liệu đồng thời trên 6 nguồn (arXiv, OpenReview, Semantic Scholar, OpenAlex, DBLP, Crossref), tự động lọc trùng và chấm điểm tương quan. | Bạn duyệt danh sách và chọn ra các bài báo then chốt nhất. |
| `rs-bottleneck-diagnosis/` | `rs-bottleneck-diagnosis` | Bóc tách điểm nghẽn thực sự của SOTA từ toàn văn bài báo, phân biệt điểm nghẽn thật vs điểm nghẽn dễ làm để tránh soft target. | Bạn thảo luận và chốt điểm nghẽn trọng tâm muốn tấn công. |
| `rs-pattern-ideator/` | `rs-pattern-ideator` | Ánh xạ bài toán vào kho **15 Ideation Patterns** và **31 Sub-patterns** đúc kết từ 1,947 bài báo Oral ICLR/NeurIPS, đề xuất 2–3 phương án cơ chế giải pháp. | Bạn phản biện bản chất toán học/thuật toán và chọn phương án tối ưu. |
| `rs-scoop-check/` | `rs-scoop-check` | Thẩm định tính mới qua 4 trục (*Problem framing, Core mechanism, Key insight, Application domain*) với các công trình gần nhất, cảnh báo nguy cơ bị trùng lặp. | Thống nhất "Delta Statement" (Điểm khác biệt độc nhất) trước khi làm thí nghiệm. |
| `rs-idea-quality/` | `rs-idea-quality` | Chấm điểm chất lượng ý tưởng 3 trục (*Problem position, Method quality, Problem-fit*) trên thang điểm 0–100 chỉ từ bản thảo ý tưởng, không cần chạy code. | Thẩm định độc lập tính khả thi lý thuyết. |
| `rs-idea-spark/` | `rs-idea-spark` | Nhạc trưởng điều phối chu trình sinh đề cương nghiên cứu hoàn chỉnh (Title · Motivation · Method · Kế hoạch phản nghiệm) ở chế độ cộng tác. | Từng giai đoạn đều dừng lại lấy phản hồi. |

### Phân hệ 2: Hậu bài báo (The Last Mile — Ấn phẩm & Lan tỏa)
| Tên Thư mục Skill | Tên Kỹ năng | Mô tả chức năng | Điểm dừng Human Gate |
| :--- | :--- | :--- | :--- |
| `rs-paper2assets/` | `rs-paper2assets` | Bóc tách toàn văn PDF bài báo (dùng PyMuPDF thuần), cắt đồ thị độ nét cao 432 dpi, bóc metadata và tạo bảng `paper_spec.md` 9 phần. | Kiểm tra độ nét của hình ảnh và tính chính xác của số liệu. |
| `rs-paper2poster/` | `rs-paper2poster` | Tạo poster khổ ngang (NeurIPS/ICML) hoặc khổ dọc (ACL), kiểm tra canh lề tự động, in PDF/PNG và **xuất file PowerPoint native `poster.pptx` có thể sửa được từng chữ**. | Duyệt bố cục và chỉnh sửa nội dung trên PowerPoint. |
| `rs-paper2blog/` | `rs-paper2blog` | Viết bài blog khoa học song ngữ: `blog_en.docx` (phong cách học thuật phương Tây) và `blog_zh.docx` (phong cách truyền thông WeChat). | Duyệt văn phong và duyệt vị trí hình ảnh minh họa. |
| `rs-paper2video/` | `rs-paper2video` | Tạo video thuyết trình 1080p có phụ đề và con trỏ laser, lồng tiếng Edge-TTS đồng bộ chính xác từng mili-giây hiệu ứng slide PPTX. | Nghe thử giọng đọc và duyệt thời lượng video. |
| `rs-paper2reel/` | `rs-paper2reel` | Đóng gói toàn bộ poster, slide, video và blog vào giao diện web tương tác `reel.html`, bấm vào từng phần trên poster sẽ mở video và slide tương ứng. | Trải nghiệm giao diện web trước khi release công khai. |

---

## 3. CÁCH CÀI ĐẶT MÔI TRƯỜNG CÔ LẬP TRONG `.venv`

Tất cả các thư viện và công cụ đều được đóng gói gọn gàng, **tuyệt đối không cài đặt bất kỳ thứ gì vào môi trường hệ điều hành**:

```powershell
# 1. Di chuyển vào thư mục dự án nghiên cứu của bạn
cd E:\research\my-nckh-project

# 2. Khởi tạo môi trường ảo Python 3.10+ (Khuyến nghị dùng uv)
uv venv --python 3.10
.venv\Scripts\activate   # Trên Windows
# source .venv/bin/activate  # Trên macOS/Linux

# 3. Cài đặt các thư viện từ pyproject.toml
uv pip install -e E:\gemini\agent_setup\microsoft-research

# 4. Tải trình duyệt Chromium cục bộ cho Playwright (dùng để in poster PDF)
uv run python -m playwright install chromium
```

> **Ghi chú về FFmpeg và pdftotext:**  
> - Đã tích hợp thư viện `imageio-ffmpeg` trong `.venv` (tự kèm binary ffmpeg), bạn **không cần cài ffmpeg vào Windows/macOS**.  
> - Đã tích hợp `pymupdf` thuần Python trong `.venv`, bạn **không cần cài Poppler vào hệ thống**.

---

## 4. HƯỚNG DẪN COPY KỸ NĂNG SANG BẤT KỲ REPO NCKH NÀO

Khi bạn làm một đề tài nghiên cứu mới (ví dụ: `E:\research\graph-reasoning`), bạn chỉ cần copy các folder kỹ năng bạn muốn dùng vào thư mục `.agents/skills/` của repo đó:

### Cách 1: Copy thủ công bằng chuột hoặc lệnh
```powershell
# Tạo thư mục .agents/skills nếu chưa có
mkdir -p E:\research\graph-reasoning\.agents\skills

# Copy kỹ năng tìm bài báo và kiểm tra tính mới:
Copy-Item -Recurse E:\gemini\agent_setup\microsoft-research\rs-paper-search E:\research\graph-reasoning\.agents\skills\
Copy-Item -Recurse E:\gemini\agent_setup\microsoft-research\rs-scoop-check E:\research\graph-reasoning\.agents\skills\
Copy-Item -Recurse E:\gemini\agent_setup\microsoft-research\rs-pattern-ideator E:\research\graph-reasoning\.agents\skills\
```

### Cách 2: Tạo Symbolic Link (Tiết kiệm dung lượng, cập nhật tự động)
```powershell
# Mở PowerShell với quyền User thông thường (hoặc Developer Mode):
New-Item -ItemType SymbolicLink -Path "E:\research\graph-reasoning\.agents\skills\rs-paper-search" -Target "E:\gemini\agent_setup\microsoft-research\rs-paper-search"
```

Khi copy vào `.agents/skills/`, AI Agent (Antigravity CLI / Claude Code / Codex) sẽ **tự động nhận diện** kỹ năng thông qua file `SKILL.md` và sẵn sàng phục vụ bạn!

---

## 5. KỊCH BẢN CỘNG TÁC THỰC TẾ (WORKFLOW)

### Kịch bản A: Phát triển ý tưởng nghiên cứu mới từ đầu
1. **Bạn:** *"Tôi muốn làm đề tài về nén KV Cache cho LLM ngữ cảnh dài. Dùng `rs-paper-search` tìm cho tôi 10 bài báo nổi bật nhất 2024–2026."*
2. **AI:** Quét arXiv và Semantic Scholar, xuất bảng tổng hợp vào `docs/ai/01-kv-cache-survey.md`.
3. **Bạn & AI:** Thảo luận và chốt điểm nghẽn chính qua `rs-bottleneck-diagnosis`.
4. **AI:** Dùng `rs-pattern-ideator` gợi ý 2 hướng: (1) Thay thế toán tử chú ý, (2) Nới lỏng phân cụm rời rạc.
5. **Bạn:** *"Tôi chọn hướng 1 vì tôi có kinh nghiệm về giải tích ma trận. Hãy dùng `rs-scoop-check` kiểm tra xem hướng này đã bị ai làm chưa."*
6. **AI:** Phân tích 4 trục, xác nhận mức độ mới lạ Level 4 (rất mới) và cùng bạn soạn Delta Statement.

### Kịch bản B: Sau khi bài báo được chấp nhận (Làm Poster & Video)
1. **Bạn:** *"Bài báo `papers/my_paper.pdf` của tôi vừa được accept vào CVPR. Hãy dùng `rs-paper2poster` tạo poster khổ ngang và file PowerPoint sửa được."*
2. **AI:** Dùng `rs-paper2assets` bóc tách hình ảnh, cân chỉnh bố cục và tạo ra `poster.html`, `poster.pdf`, cùng file native PowerPoint `poster.pptx`.
3. **Bạn:** Mở `poster.pptx` trên máy tính bằng Microsoft PowerPoint để chỉnh sửa chữ hoặc đổi màu theo ý thích cá nhân.
