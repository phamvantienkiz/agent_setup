# COMPUTER SCIENCE & ACADEMIC RESEARCH SKILLS PACK
## Bộ Kỹ Năng Nghiên Cứu Khoa Học Máy Tính & Xuất Bản Học Thuật Dành Cho AI Agents

> **Phiên bản:** 1.0 (Trích xuất từ `scientific-agent-skills`, tối ưu hóa cho ngành Computer Science)  
> **Tổng số kỹ năng:** 46 skills chuyên sâu  
> **Mục đích sử dụng:** Phục vụ nghiên cứu cao học (Master/PhD), làm đồ án tốt nghiệp, đề tài NCKH, viết và định dạng bài báo nộp các hội nghị A* (NeurIPS, ICML, ICLR, CVPR, ACL, CHI, KDD, IEEE/ACM).

---

## 1. HƯỚNG DẪN QUẢN LÝ VÀ SỬ DỤNG THỦ CÔNG

Kho kỹ năng này được thiết kế theo dạng **Module độc lập**, hoàn toàn tương thích với chuẩn `.agents/skills` của Antigravity CLI và các Agentic Coding Assistants.

### Khi làm dự án Cao học / Nghiên cứu khoa học CS:
1. Mở thư mục dự án nghiên cứu của bạn.
2. Kiểm tra hoặc tạo thư mục `.agents/skills/` tại gốc của dự án.
3. **Sao chép (Copy)** toàn bộ 46 thư mục kỹ năng (hoặc chỉ những kỹ năng cụ thể bạn cần cho đề tài) từ `cs-research-skills/` vào thư mục `.agents/skills/` của dự án nghiên cứu đó.
4. Agent sẽ tự động nhận diện các kỹ năng nghiên cứu khoa học ngay khi bạn mở dự án.

### Khi làm dự án Lập trình / Phát triển phần mềm thông thường:
1. Giữ nguyên thư mục `.agents/skills/` của dự án thông thường (chỉ chứa các kỹ năng phát triển phần mềm như `clean-code`, `python-fastapi-code`, `system-design`,...).
2. **Không copy** thư mục `cs-research-skills/` sang. Việc này giúp giữ cho System Prompt của Agent luôn nhẹ, phản hồi nhanh và không bị loãng ngữ cảnh.
3. Nếu bạn đã lỡ copy vào một dự án thường, chỉ cần chọn và **Xóa (Delete)** các thư mục kỹ năng nghiên cứu khoa học khỏi `.agents/skills/`.

---

## 2. DANH MỤC 46 KỸ NĂNG ĐƯỢC PHÂN THEO CHUYÊN NGÀNH

### Nhóm 1: Trí tuệ nhân tạo, Học sâu & Khoa học dữ liệu (12 skills)
*   **`transformers`**: Tinh chỉnh (fine-tuning) và đánh giá các mô hình nền tảng (LLMs, Vision Transformers, Multimodal), quản lý checkpoint, pipeline inference và rà soát rò rỉ dữ liệu.
*   **`pytorch-lightning`**: Chuẩn hóa mã nguồn Deep Learning, cấu hình huấn luyện phân tán đa GPU/TPU (DDP, FSDP, DeepSpeed), callbacks và logging thí nghiệm.
*   **`torch-geometric`**: Nghiên cứu Graph Neural Networks (GNNs), message passing (GCN, GAT, GraphSAGE, GIN), phân loại nút, cạnh và đồ thị không đồng nhất.
*   **`stable-baselines3`**: Nghiên cứu Học tăng cường (Reinforcement Learning) đơn tác nhân với các thuật toán chuẩn (PPO, SAC, DQN, TD3), custom Gymnasium environments.
*   **`pufferlib`**: Nghiên cứu RL hiệu năng siêu cao: vector hóa môi trường hàng loạt bằng C/CUDA, tối ưu hóa thông lượng mẫu (sample throughput).
*   **`scikit-learn`**: Các thuật toán Machine Learning kinh điển (SVM, Random Forest, GBDT, K-Means), tiền xử lý đặc trưng, pipeline đóng gói và baseline benchmarks.
*   **`shap`**: Nghiên cứu Trí tuệ nhân tạo có thể giải thích (Explainable AI - XAI), phân tích đóng góp đặc trưng (feature attribution), đánh giá độ công bằng mô hình.
*   **`umap-learn`**: Giảm chiều phi tuyến tính (nonlinear dimensionality reduction), trực quan hóa không gian tiềm ẩn (latent embeddings) 2D/3D.
*   **`aeon`**: Khai phá và học máy cho chuỗi thời gian: phân loại chuỗi thời gian, phân cụm, phát hiện bất thường và phân đoạn chuỗi.
*   **`timesfm-forecasting`**: Dự báo chuỗi thời gian zero-shot với Time-Series Foundation Model của Google Research (TimesFM).
*   **`pymc`**: Học máy xác suất (Probabilistic ML), suy diễn Bayes, lấy mẫu MCMC (NUTS), định lượng độ bất định (uncertainty quantification).
*   **`hugging-science`**: Khám phá, đánh giá và đối chuẩn (benchmark) các mô hình, bộ dữ liệu mở và Gradio Spaces trên Hugging Face.

### Nhóm 2: Tính toán hiệu năng cao (HPC), Hệ thống & Kỹ thuật dữ liệu (7 skills)
*   **`optimize-for-gpu`**: Profiling CUDA/GPU NVIDIA, tối ưu hóa băng thông bộ nhớ và gia tốc tính toán Python (CuPy, cuDF, cuML, Numba-CUDA).
*   **`modal`**: Điện toán đám mây không máy chủ (Serverless Cloud Computing): mở rộng quy mô tính toán lên hàng nghìn container, cấp phát GPU H100/H200/B200 theo nhu cầu.
*   **`dask`**: Tính toán phân tán và xử lý song song vượt giới hạn RAM (out-of-core computing), lập lịch đồ thị tác vụ động trên cụm máy chủ.
*   **`polars`**: Xử lý dữ liệu dạng cột (Columnar Data Processing) hiệu năng cao, tối ưu hóa câu truy vấn lười biếng (lazy query optimization).
*   **`vaex`**: Phân tích tập dữ liệu dạng bảng hàng tỷ dòng bằng kỹ thuật ánh xạ bộ nhớ (memory mapping - mmap), không tốn RAM sao chép.
*   **`zarr-python`**: Lưu trữ và truy xuất mảng đa chiều nén theo khối (chunked, compressed N-D arrays), hỗ trợ lưu trữ đám mây phân tán.
*   **`get-available-resources`**: Thăm dò cấu hình phần cứng thời gian thực (CPU, RAM, GPU VRAM, cgroups) để lập lịch thuật toán thích ứng tài nguyên.

### Nhóm 3: Lý thuyết đồ thị, Toán rời rạc & Mô phỏng hệ thống (4 skills)
*   **`networkx`**: Phân tích mạng phức tạp (Complex Networks), cài đặt giải thuật đồ thị (đường đi ngắn nhất, độ trung tâm, phát hiện cộng đồng).
*   **`simpy`**: Mô phỏng sự kiện rời rạc hướng tiến trình: nghiên cứu lý thuyết hàng đợi (queueing theory), lập lịch CPU, định tuyến gói tin mạng.
*   **`pymoo`**: Tối ưu hóa đa mục tiêu và siêu đa mục tiêu (Multi- & Many-objective Optimization) sử dụng giải thuật tiến hóa (NSGA-II, NSGA-III, MOEA/D).
*   **`sympy`**: Hệ đại số máy tính (Computer Algebra System - CAS): tính toán ký hiệu chính xác, giải phương trình, kiểm chứng hình thức và sinh mã tự động.

### Nhóm 4: Tính toán lượng tử & Khoa học thông tin lượng tử (3 skills)
*   **`qiskit`**: IBM Quantum SDK: thiết kế và biên dịch mạch lượng tử, thuật toán lượng tử, giảm thiểu lỗi và chạy trên QPU IBM thực tế.
*   **`cirq`**: Khung tính toán lượng tử của Google Quantum AI: thiết kế mạch lượng tử nhận biết nhiễu và thuật toán NISQ.
*   **`pennylane`**: Học máy lượng tử (Quantum Machine Learning - QML): đạo hàm tự động cho mạch lượng tử biến phân, thuật toán lai VQE/QAOA.

### Nhóm 5: Hệ thống tác nhân tự trị & Lập luận đa tác nhân (4 skills)
*   **`pi-agent`**: Nền tảng xây dựng AI coding agent, điều phối subagent, định tuyến LLM cục bộ (`llama.cpp router`) và tích hợp MCP server.
*   **`arbor`**: Cấu trúc cây giả thuyết tự động tối ưu hóa thí nghiệm (Hypothesis Tree Refinement), cô lập thử nghiệm qua Git worktrees.
*   **`autoskill`**: Khai phá quy trình làm việc (workflow mining), tự động tổng hợp kỹ năng mới cho agent từ nhật ký hoạt động.
*   **`consciousness-council`**: Cơ chế suy luận đa tác nhân (Multi-agent debate / Devil's advocate) để phản biện và ra quyết định kiến trúc hệ thống.

### Nhóm 6: Xử lý tài liệu, NLP & Sơ đồ kiến trúc (3 skills)
*   **`markitdown`**: Chuyển đổi tài liệu không đồng nhất (PDF, Word, PPTX, HTML, Excel) sang Markdown cho pipeline RAG và NLP.
*   **`liteparse`**: Trích xuất văn bản nhận biết bố cục không gian (spatial bounding boxes) và OCR cho Document AI đa phương thức.
*   **`scientific-schematics`**: Tự động thiết kế bản vẽ trực quan kiến trúc mạng nơ-ron, sơ đồ khối hệ thống máy tính đạt chuẩn bài báo hội nghị.

### Nhóm 7: Phương pháp luận thực nghiệm & Đánh giá Benchmark (4 skills)
*   **`experimental-design`**: Thiết kế thí nghiệm (DOE): phân nhóm ngẫu nhiên, chặn khối, thử nghiệm nhân tố, A/B testing cho thuật toán.
*   **`statistical-analysis`**: Lựa chọn kiểm định thống kê chuẩn xác (t-test, ANOVA, Wilcoxon, Mann-Whitney U, Friedman), tính effect size và báo cáo chuẩn APA.
*   **`statistical-power`**: Tính toán cỡ mẫu tối thiểu và công suất thống kê (power analysis) đảm bảo benchmark có ý nghĩa thực chất.
*   **`exploratory-data-analysis`**: Khảo sát phân bố dữ liệu benchmark, phát hiện rò rỉ dữ liệu (data leakage) giữa tập train/test.

### Nhóm 8: Xuất bản bài báo, Tra cứu arXiv & Soạn thảo LaTeX (9 skills)
*   **`venue-templates`**: Cung cấp template LaTeX và cẩm nang chi tiết cho các hội nghị hàng đầu: **NeurIPS, ICML, ICLR, CVPR, ACL ARR, ACM CHI, KDD, IEEE**. Kiểm tra số trang, ẩn danh (double-blind) và font PDF.
*   **`paper-lookup`**: Truy vấn đồng thời 18 API học thuật: **arXiv**, Semantic Scholar, Crossref, OpenAlex, PubMed; tải PDF Open Access.
*   **`citation-management`**: Tự động chuyển đổi DOI/arXiv ID thành bản ghi BibTeX chuẩn xác phục vụ biên soạn bài báo bằng LaTeX/Overleaf.
*   **`scientific-writing`**: Soạn thảo các phần của bài báo CS (Abstract, Methodology, Experimental Setup, Results), viết bản phản hồi phản biện (Rebuttal).
*   **`peer-review`**: Soạn thảo nhận xét phản biện mang tính xây dựng theo đúng tiêu chuẩn các hội nghị lớn.
*   **`literature-review`**: Thực hiện tổng quan tài liệu có hệ thống (Systematic Literature Review - SLR) trong khoa học máy tính.
*   **`scientific-visualization`**: Thiết kế biểu đồ khoa học chuẩn mực xuất bản: tương phản thân thiện mắt, hiển thị error bars, lưu trữ vector PDF/SVG.
*   **`latex-posters`**: Thiết kế poster báo cáo hội nghị bằng mã nguồn LaTeX (`tikzposter`, `beamerposter`).
*   **`scientific-slides`**: Thiết kế slide thuyết trình bảo vệ luận án / báo cáo hội nghị bằng LaTeX Beamer hoặc PowerPoint.

---

## 3. TÓM TẮT MA TRẬN TRA CỨU NHANH

| Nhóm Nhu Cầu | Các Kỹ Năng Khuyên Dùng |
| :--- | :--- |
| **Làm mô hình NLP / LLM / Thị giác máy tính** | `transformers`, `pytorch-lightning`, `optimize-for-gpu`, `shap`, `modal` |
| **Nghiên cứu Thuật toán Đồ thị / Mạng** | `networkx`, `torch-geometric`, `simpy`, `pymoo` |
| **Nghiên cứu Học tăng cường (RL)** | `stable-baselines3`, `pufferlib`, `simpy` |
| **Nghiên cứu Tính toán lượng tử (QIS)** | `qiskit`, `pennylane`, `cirq` |
| **Nghiên cứu Agentic AI / LLM Agents** | `pi-agent`, `arbor`, `autoskill`, `consciousness-council` |
| **Khảo sát tài liệu liên quan (Related Work)** | `paper-lookup`, `literature-review`, `citation-management` |
| **Chạy thực nghiệm & So sánh Benchmark** | `experimental-design`, `statistical-analysis`, `statistical-power`, `exploratory-data-analysis` |
| **Viết bài báo nộp hội nghị (Paper Writing)** | `venue-templates`, `scientific-schematics`, `scientific-visualization`, `scientific-writing`, `peer-review` |
| **Bảo vệ luận văn / Báo cáo poster** | `scientific-slides`, `latex-posters` |
