# Báo Cáo Phân Tích Hệ Thống Skill System Design: `proyecto26/system-design-skills`

- **Tên kho lưu trữ**: `proyecto26/system-design-skills`
- **Định dạng**: Modular Plugin Ecosystem / Wiki of 22 Composable Building-Block Skills + HTML/SVG Diagramming Engine + Python Sizing Tool + Evals Benchmark Suite
- **Giấy phép**: MIT License
- **Đường dẫn phân tích**: [system-design-skills](file:///E:/gemini/agent_setup/system-design-skills)
- **Tệp mục tiêu so sánh**: [.agents/skills/system-design/SKILL.md](file:///E:/gemini/agent_setup/.agents/skills/system-design/SKILL.md)

---

## 1. Tổng Quan & Triết Lý Cốt Lõi (Core Philosophy)

### 1.1. Triết lý "Reasoning Over Memorization" (Tư Duy Suy Luận Thay Vì Học Vẹt Sơ Đồ)
Tài liệu định hướng cốt lõi [`docs/GUIDE.md`](file:///E:/gemini/agent_setup/system-design-skills/docs/GUIDE.md) của repo chỉ ra một thực tế nhức nhối trong ngành kỹ nghệ phần mềm:
> **"System Design exercises contain a counterintuitive trap: the more you rely on memorized architectures and patterns, the more likely you are to fail. Strong engineers often get rejected not because their design was wrong, but because they optimized for the wrong signals."**  
> *(Các bài toán System Design chứa đựng một cái bẫy phi trực giác: bạn càng dựa dẫm vào những sơ đồ và mẫu thiết kế học vẹt, bạn càng dễ thất bại. Những kỹ sư giỏi thường bị trượt không phải vì thiết kế sai, mà vì họ tối ưu hóa sai các tín hiệu).*

Repo đưa ra quan điểm mang tính cách mạng: **Kiến trúc chỉ là một giả thuyết (Hypothesis)** được sinh ra để thỏa mãn một tập hợp các ràng buộc nhất định. Khi ràng buộc thay đổi (ví dụ: người dùng tăng 10x, yêu cầu tính nhất quán tức thời, mất kết nối liên vùng), một kiến trúc học vẹt sẽ sụp đổ hoàn toàn; trong khi một kỹ sư thực thụ sẽ bình tĩnh điều chỉnh các khối tương ứng.

### 1.2. Bộ Khung Phòng Vệ 10 "Mùi Thất Bại" (10 Failure Modes & Antidotes)
Repo đúc kết 10 sai lầm phổ biến nhất của kỹ sư khi thiết kế hệ thống và đưa ra các cơ chế phòng vệ tương ứng:

| Mã | Tên Failure Mode | Biểu hiện sai lầm | Biện pháp phòng vệ bắt buộc (Antidote) |
| :---: | :--- | :--- | :--- |
| **#1** | **Inadequate Fundamentals** | Không nắm vững bản chất CAP, PACELC, Quorum, Replication lag, Consensus. | Quay về nền tảng: Luôn xác định hệ thống ưu tiên C hay A khi xảy ra đứt mạng (Network partition). |
| **#2** | **Opaque Primitives** | Coi component như hộp đen; chỉ biết gọi tên công nghệ mà không hiểu cách nó hoạt động khi tải cao. | Phải giải thích được cơ chế bên trong: Eviction policy của Cache, Backpressure của Queue, Connection pool của DB. |
| **#3** | **Rushing Without Clarifying** | Vừa nghe đề bài đã lao vào vẽ sơ đồ hộp; không làm rõ bài toán. | Bắt buộc chia yêu cầu thành: Functional, Non-functional (kèm số), và Out-of-Scope trước khi vẽ. |
| **#4** | **Weak Trade-Off Articulation** | Nhắc đến công nghệ như một "chuẩn mực ngành" (Industry standard) mà không nêu đánh đổi. | Áp dụng công thức 3 câu hỏi cho mọi công nghệ: **Solves / Worsens / When to change**. |
| **#5** | **No Sense of Scale or Numbers** | Dùng từ ngữ định tính mơ hồ ("High traffic", "Big data", "Fast"). | Định lượng hóa bằng Back-of-the-envelope: Tính QPS đỉnh, dung lượng lưu trữ/ngày, băng thông, số server. |
| **#6** | **Ignoring Failure Modes** | Thiết kế giả định mạng luôn thông, server không bao giờ chết; chỉ biết dùng "Retry". | Thiết kế suy thoái êm dịu (Graceful degradation): Circuit breaker, Fallback cache, Dead-letter queue. |
| **#7** | **Over-Indexing on "Correct" Diagram** | Cố gắng vẽ ra sơ đồ "chuẩn sách giáo khoa", sợ thay đổi khi có yêu cầu mới. | Xem kiến trúc là giả thuyết linh hoạt; sẵn sàng xóa bỏ một hộp nếu ràng buộc đầu vào thay đổi. |
| **#8** | **Weak API & Data-Model Thinking** | Chỉ vẽ hộp ở mức hạ tầng, không viết nổi payload JSON, HTTP method hay khóa phân vùng (Partition key). | Làm rõ hợp đồng giao tiếp: Endpoint, Method, Request/Response body, Partition key, Sort key. |
| **#9** | **Presentation Instead of Collaboration** | Độc thoại một mình, coi câu hỏi phản biện của đồng nghiệp/người phỏng vấn như một sự công kích. | Biến buổi thiết kế thành phiên làm việc cộng tác (Working session); lắng nghe gợi ý và thích ứng. |
| **#10** | **Inability to Course-Correct** | Tâm lý bảo thủ (Sunk Cost Fallacy); cố chấp bám lấy giải pháp ban đầu dù ràng buộc đã bị phá vỡ. | Kiểm toán giả định (Audit assumptions): Chỉ ra chính xác giả định nào bị vô hiệu hóa và thiết kế lại phần đó. |

---

## 2. Kiến Trúc Phân Tầng 8 Cấp Độ & Hệ Sinh Thái 22 Skills

`proyecto26` tiếp cận bài toán theo tư duy **Chia để trị (Divide and Conquer)**. Thay vì một tài liệu khổng lồ, repo chia hệ thống thành **22 skills độc lập** được sắp xếp theo cấu trúc tô-pô từ đáy lên đỉnh (Bottom-Up), trong đó mỗi tầng chỉ phụ thuộc vào các tầng bên dưới:

```
L7 Growth      scaling-evolution                                           (Thay đổi gì khi tải tăng 10x / 100x)
L6 Ops         resilience-failure · observability · distributed-logging    (Suy thoái, quan sát, sống sót qua sự cố)
L5 Correctness consistency-coordination                                   (CAP, Thứ tự, Quorum, Đồng thuận Paxos/Raft)
L4 Async       messaging-streaming · task-scheduling                       (Tách rời, lập lịch, hấp thụ xung đột ghi)
L3 State       data-storage · caching · blob-store · sequencer ·
               sharded-counters · distributed-search                       (Lưu trữ dữ liệu, đọc/ghi siêu tốc)
L2 Services   api-design · service-decomposition                         (Ranh giới dịch vụ & Hợp đồng giao tiếp)
L1 Edge       dns · load-balancing · content-delivery                     (Đón traffic ở rìa mạng, phân phối gần user)
L0 Frame      requirements-scoping · back-of-the-envelope                 (Xác định LÀM CÁI GÌ và QUY MÔ BAO LỚN)
   Render     architecture-diagram                                        (Engine sinh sơ đồ HTML+SVG độc lập)
   Meta       system-design                                               (Orchestrator điều phối toàn bộ chu trình)
```

### Danh Mục 22 Skills & Trách Nhiệm Chi Tiết

| Tầng | Tên Skill | Câu hỏi cốt lõi giải quyết | Tài liệu tham chiếu đi kèm |
| :--- | :--- | :--- | :--- |
| **L0** | [`requirements-scoping`](file:///E:/gemini/agent_setup/system-design-skills/skills/requirements-scoping) | Làm cái gì? Cái gì trong scope, cái gì out-of-scope? Ràng buộc SLA là gì? | `clarifying-question-catalog.md` |
| **L0** | [`back-of-the-envelope`](file:///E:/gemini/agent_setup/system-design-skills/skills/back-of-the-envelope) | Bao nhiêu QPS? Bao nhiêu TB lưu trữ? Cần bao nhiêu server? | `estimation-recipes.md`, `numbers-to-remember.md`, `botec.py` |
| **L1** | [`dns`](file:///E:/gemini/agent_setup/system-design-skills/skills/dns) | Client phân giải dịch vụ ra sao? Geo/Latency routing? Failover DNS? | `deep-dive.md`, providers (AWS, Azure, GCP, Generic) |
| **L1** | [`load-balancing`](file:///E:/gemini/agent_setup/system-design-skills/skills/load-balancing) | Phân phối lưu lượng thế nào? L4 vs L7? Tránh DDoS khi phục hồi? | `deep-dive.md`, providers (AWS, Azure, GCP, Generic) |
| **L1** | [`content-delivery`](file:///E:/gemini/agent_setup/system-design-skills/skills/content-delivery) | Phân phối file tĩnh/media ở Edge thế nào? CDN Push vs Pull? | `deep-dive.md`, providers (AWS, Azure, GCP, Generic) |
| **L2** | [`api-design`](file:///E:/gemini/agent_setup/system-design-skills/skills/api-design) | REST, gRPC hay GraphQL? Request/Response shape? Pagination, Idempotency? | `deep-dive.md`, providers (AWS, Azure, GCP, Generic) |
| **L2** | [`service-decomposition`](file:///E:/gemini/agent_setup/system-design-skills/skills/service-decomposition) | Monolith hay Microservices? Ranh giới tách service theo domain hay scale? | `deep-dive.md`, providers (AWS, Azure, GCP, Generic) |
| **L3** | [`data-storage`](file:///E:/gemini/agent_setup/system-design-skills/skills/data-storage) | SQL hay NoSQL? Chọn Shard key? Replication lag xử lý ra sao? | `deep-dive.md`, providers (AWS, Azure, GCP, Generic) |
| **L3** | [`caching`](file:///E:/gemini/agent_setup/system-design-skills/skills/caching) | Cache cái gì? Chiến lược Cache-aside hay Write-through? Hot-key mitigation? | `deep-dive.md`, providers (AWS, Azure, GCP, Generic) |
| **L3** | [`blob-store`](file:///E:/gemini/agent_setup/system-design-skills/skills/blob-store) | Lưu file dung lượng lớn ở đâu? Chunking, Signed URLs, Phân tầng lưu trữ? | `deep-dive.md`, providers (AWS, Azure, GCP, Generic) |
| **L3** | [`sequencer`](file:///E:/gemini/agent_setup/system-design-skills/skills/sequencer) | Sinh ID duy nhất phân tán thế nào? Snowflake, UUIDv7 hay Ticket server? | `deep-dive.md`, providers (AWS, GCP, Generic) |
| **L3** | [`sharded-counters`](file:///E:/gemini/agent_setup/system-design-skills/skills/sharded-counters) | Đếm view/like triệu lượt ghi/giây mà không nghẽn row? HyperLogLog? | `deep-dive.md`, providers (AWS, Azure, GCP, Generic) |
| **L3** | [`distributed-search`](file:///E:/gemini/agent_setup/system-design-skills/skills/distributed-search) | Tìm kiếm toàn văn (Full-text search), Inverted Index, Phân mảnh Search? | `deep-dive.md`, providers (AWS, Azure, GCP, Generic) |
| **L4** | [`messaging-streaming`](file:///E:/gemini/agent_setup/system-design-skills/skills/messaging-streaming) | Queue vs Stream? Xử lý trùng lặp tin nhắn? Thứ tự message (Ordering)? | `deep-dive.md`, providers (AWS, Azure, GCP, Generic, Temporal) |
| **L4** | [`task-scheduling`](file:///E:/gemini/agent_setup/system-design-skills/skills/task-scheduling) | Lập lịch tác vụ nền, Worker leasing, Phân tán cron job, Retry & Dedup? | `deep-dive.md`, providers (AWS, Azure, GCP, Generic, Temporal) |
| **L5** | [`consistency-coordination`](file:///E:/gemini/agent_setup/system-design-skills/skills/consistency-coordination) | Mạnh hay Eventual? Quorum $W+R>N$, Đồng thuận Raft/Paxos, Distributed Lock? | `deep-dive.md`, providers (AWS, Azure, GCP, Generic) |
| **L6** | [`resilience-failure`](file:///E:/gemini/agent_setup/system-design-skills/skills/resilience-failure) | Điểm chết đơn lẻ (SPOF)? Circuit Breaker, Bulkhead, Throttling, Rate Limiter? | `deep-dive.md`, providers (AWS, Azure, GCP, Generic, Temporal) |
| **L6** | [`observability`](file:///E:/gemini/agent_setup/system-design-skills/skills/observability) | Theo dõi cái gì? Metrics, Distributed Tracing, SLI/SLO, Alert thresholds? | `deep-dive.md`, providers (AWS, Azure, GCP, Generic) |
| **L6** | [`distributed-logging`](file:///E:/gemini/agent_setup/system-design-skills/skills/distributed-logging) | Thu thập log hàng tỷ sự kiện/ngày? Buffering, Shipping, Retention, Trace ID? | `deep-dive.md`, providers (AWS, Azure, GCP, Generic) |
| **L7** | [`scaling-evolution`](file:///E:/gemini/agent_setup/system-design-skills/skills/scaling-evolution) | Thang bậc mở rộng (Scaling ladder): Thay đổi gì ở mốc 10k, 100k, 1M, 10M DAU? | `scaling-ladder.md` |
| **Render**| [`architecture-diagram`](file:///E:/gemini/agent_setup/system-design-skills/skills/architecture-diagram) | Render sơ đồ Dark-theme HTML + SVG độc lập, có summary card và export PNG/PDF | `template.html`, `interactive-template.html`, `design-system.md` |
| **Meta** | [`system-design`](file:///E:/gemini/agent_setup/system-design-skills/skills/system-design) | Điều phối quy trình suy luận 6 bước, liên kết các blocks, sinh tài liệu | `reasoning-loop.md`, `tradeoff-framework.md`, `failure-modes.md` |

---

## 3. Hệ Thống Chuẩn Hóa: Skill Contract & Tính Đa Đám Mây (Provider Modularity)

### 3.1. Hợp đồng kỹ thuật bắt buộc ([`meta/SKILL-CONTRACT.md`](file:///E:/gemini/agent_setup/system-design-skills/meta/SKILL-CONTRACT.md))
Tất cả các skill trong repo đều phải tuân thủ nghiêm ngặt theo hợp đồng cấu trúc:
1. **Phân loại 2 Archetype**:
   - **Component Block** (các khối thành phần hạ tầng: DB, Cache, Queue...): Bắt buộc phải có `The options`, bảng `Trade-offs`, phân tích `Behavior under stress`, và thư mục con `references/providers/` (`generic.md` bắt buộc, `aws.md`, `azure.md`, `gcp.md`, `temporal.md`).
   - **Method Block** (phương pháp luận: Scoping, BOTEC, Scaling evolution): Tập trung vào các bước thực hiện, công thức, và các cạm bẫy thường gặp (`Pitfalls`).
2. **Khung Trade-Off 4 Cột Chuẩn**:
   Mọi component đều bắt buộc phải liệt kê các phương án theo cấu trúc:
   ```markdown
   | Option | What it solves | What it worsens | Change it when |
   ```
   *Nghiêm cấm lý do "chuẩn công nghiệp" hoặc "mở rộng tốt" mà không chỉ ra nhược điểm và ngưỡng phá vỡ (breaking point).*
3. **Phần "Behavior under stress" (Hành vi khi chịu áp lực)**:
   Mỗi skill phân tích chính xác điều gì xảy ra khi hệ thống bị nghẽn: lệch tải (hot-shard skew), bão cache miss (stampede), bão retry, tràn bộ nhớ, mất kết nối, và đưa ra biện pháp giảm thiểu.

### 3.2. Tính module hóa nhà cung cấp đám mây (Provider Modularity)
Mỗi block đều ưu tiên giải pháp **Vendor-Neutral (Generic)** làm mặc định (ví dụ: PostgreSQL, Redis, Kafka, Nginx). Tuy nhiên, khi người dùng hoặc hệ thống yêu cầu triển khai trên một cloud cụ thể, block sẽ tra cứu trực tiếp các file mapping:
- **AWS**: Route 53, ALB/NLB, CloudFront, DynamoDB/Aurora, ElastiCache, S3, SQS/SNS/Kinesis, EventBridge, CloudWatch/X-Ray.
- **GCP**: Cloud DNS, Cloud Load Balancing, Cloud CDN, Cloud Spanner/Firestore/Cloud SQL, Memorystore, Cloud Storage, Pub/Sub, Cloud Tasks, Cloud Monitoring/Trace.
- **Azure**: Azure DNS, Azure Front Door/App Gateway, Azure CDN, Cosmos DB/Azure SQL, Azure Cache for Redis, Blob Storage, Service Bus/Event Hubs, Event Grid, Monitor/App Insights.
- **Temporal**: Sử dụng cho các kịch bản cần Workflow dài hạn, Sagas điều phối phân tán có trạng thái (Durable Workflows) trong các block `messaging-streaming`, `task-scheduling`, `resilience-failure`.

---

## 4. Công Cụ & Tự Động Hóa Độc Đáo (Tooling & Assets)

### 4.1. Công cụ tính nhẩm tự động ([`botec.py`](file:///E:/gemini/agent_setup/system-design-skills/skills/back-of-the-envelope/scripts/botec.py))
Repo trang bị một script Python thuần (không cần external dependency) giúp chuyển đổi các giả định người dùng thành các con số kỹ thuật chính xác:
```bash
python botec.py --dau 150e6 --actions 2 --peak 2 --obj-bytes 1e6 --media-frac 0.10 --retention-days 1825 --server-qps 1000 --json
```
Script tự động tính toán:
- QPS trung bình và QPS đỉnh (Peak QPS).
- Dung lượng lưu trữ mỗi ngày và tổng dung lượng tích lũy theo năm.
- Băng thông mạng đỉnh (Peak Bandwidth B/s).
- Ước lượng số lượng server tối thiểu cần thiết để gánh tải.

### 4.2. Bộ Engine sinh sơ đồ kiến trúc chuyên nghiệp ([`architecture-diagram`](file:///E:/gemini/agent_setup/system-design-skills/skills/architecture-diagram))
Thay vì chỉ sinh Mermaid hay ASCII, repo cung cấp một giải pháp trực quan hóa cực kỳ mạnh mẽ:
- Xuất ra tệp **HTML + SVG độc lập** với giao diện Dark-theme hiện đại, chạy offline 100%.
- Sử dụng **hệ thống màu ngữ nghĩa (Semantic Palette)** chuẩn hóa:
  - *Client / Edge*: Cyan (`#22d3ee`)
  - *Backend / Service*: Emerald (`#34d399`)
  - *Database / Store*: Purple (`#a78bfa`)
  - *Cache*: Sky Blue (`#38bdf8`)
  - *Message Bus / Queue*: Orange (`#fb923c`)
  - *Managed / Cloud*: Amber (`#fbbf24`)
  - *Security / Auth*: Rose (`#fb7185`)
- Tích hợp sẵn Summary Cards (tóm tắt các quyết định quan trọng ngay dưới sơ đồ) và hỗ trợ xuất ảnh PNG/PDF chất lượng cao thông qua các script thư viện được ghim mã băm SRI an toàn.

### 4.3. Các Mẫu Tài Liệu Thiết Kế Có Cổng Kiểm Soát (Validation Gates)
- **`requirements-template.md`**: Bắt buộc phải có ít nhất 1 mục Out-of-scope; mọi tiêu chí phi chức năng phải có con số cụ thể (cấm ghi "nhanh" hay "cao"); các giả định phải được ghi lại rõ ràng.
- **`design-doc-template.md`**: Thiết lập 9 phần chuẩn mực, có checklist Validation Gate cuối file: kiểm tra xem mọi quyết định kiến trúc có chỉ ra mặt trái ("Worsens") và ngưỡng phá vỡ không; kiểm tra xem mọi hộp trong sơ đồ có nguồn gốc từ số liệu hay yêu cầu không.

---

## 5. Bảng So Sánh Chi Tiết: `proyecto26` vs `wondelai` vs Skill Hiện Tại

| Khía cạnh | Skill hiện tại (`.agents/skills/system-design`) | `wondelai/skills/system-design` | `proyecto26/system-design-skills` |
| :--- | :--- | :--- | :--- |
| **Quy mô & Cấu trúc** | 1 file `SKILL.md` (224 dòng, ~10 KB) | 1 skill gồm 7 file (~75 KB) | **22 skills phân tầng** (hơn 100 tệp tin, ~350 KB tri thức) |
| **Cách thức tiếp cận** | Quy trình chung, khái niệm cơ bản | Hướng theo 8 bài toán lớn kinh điển (Interview & Case study) | **Hướng khối xây dựng (Composable Building Blocks)** ghép nối theo nhu cầu |
| **Tư duy thiết kế** | Tĩnh, liệt kê định nghĩa | 4 bước có timebox, thang điểm 10/10 | **Reasoning Loop 6 bước**, coi kiến trúc là giả thuyết, chống 10 Failure Modes |
| **Đánh đổi (Trade-offs)** | Liệt kê pros/cons ngắn | Bảng phân tích ưu/nhược điểm từng linh kiện | Bắt buộc bảng 4 cột: **Solves / Worsens / Change it when** |
| **Ánh xạ Cloud Provider** | Không có | Không có (chỉ Generic) | **Đầy đủ 4 provider**: AWS, Azure, GCP, Temporal + Generic |
| **Hành vi khi sự cố (Stress)** | Nhắc lướt qua failover | Hướng dẫn Health checks, Liveness/Readiness, DR | **Phân tích Behavior under stress** cho từng thành phần cụ thể |
| **Công cụ & Tự động hóa** | Không có | Không có | **Script `botec.py`** tính toán tải + **Engine `architecture-diagram`** HTML/SVG |
| **Sơ đồ kiến trúc** | Vẽ tay hoặc Mermaid | Vẽ tay hoặc Mermaid | **Engine HTML + SVG Dark Theme**, có semantic colors & PNG/PDF export |
| **Kiểm định chất lượng** | Không có | Quick Diagnostic 8 hàng | Evals suite tự động (`run_checks.py`, benchmarks, golden fixtures) |

---

## 6. Điểm Mạnh, Điểm Yếu & Đánh Giá Tổng Thể

### 6.1. Điểm mạnh vượt bậc
1. **Kiến trúc phân tầng & Module hóa tối đa**: Việc chia nhỏ thành 22 skill cho phép Agent có thể được triệu hồi chuyên biệt (ví dụ: chỉ hỏi về `sharded-counters` hoặc `blob-store`) mà không làm bùng nổ context window với những thông tin không liên quan.
2. **Khung lý luận "Solves / Worsens / Change it when"**: Buộc Agent phải suy nghĩ như một Senior/Principal Architect, tuyệt đối không được đưa ra giải pháp theo kiểu "chuẩn ngành" mà không nhìn nhận chi phí vận hành hay độ phức tạp kèm theo.
3. **Phân tích hành vi chịu tải (`Behavior under stress`)**: Giúp Agent lường trước các thảm họa vận hành thực tế như Cache Stampede, Hot-shard skew, Retry amplification, Broken quorum.
4. **Hỗ trợ Cloud Provider thực tế**: Giúp chuyển đổi ngay lập tức bản thiết kế lý thuyết sang hạ tầng thực thi trên AWS, GCP hoặc Azure.
5. **Công cụ hỗ trợ trực quan & tính toán**: Script `botec.py` và engine vẽ sơ đồ `architecture-diagram` là vũ khí cực mạnh cho các Artifacts của Antigravity.

### 6.2. Hạn chế & Thách thức khi tích hợp
1. **Số lượng skill quá lớn (22 skills)**: Nếu nạp toàn bộ 22 skills vào thư mục `.agents/skills/`, danh sách skills của workspace sẽ bị phình to đáng kể, có thể gây nhiễu cho cơ chế Tool Selection của Agent nếu không có cơ chế định tuyến (Router) chặt chẽ.
2. **Thiếu vắng các bản thiết kế tổng thể từ đầu đến cuối (End-to-End Case Studies)**: Khác với `wondelai` (có sẵn 8 case study hoàn chỉnh như Twitter, Uber, Chat, Crawler), `proyecto26` tập trung vào từng linh kiện rời rạc, đòi hỏi Agent phải tự ghép nối tốt từ đầu.

---

## 7. Đề Xuất Tiếp Thu Cho Kế Hoạch Nâng Cấp Hệ Thống Skill

Để tạo ra một **Skill System Design "Vô Địch" (Ultimate System Design Skill)** cho dự án, chúng ta nên kết hợp sức mạnh bổ trợ của cả 2 kho lưu trữ:

1. **Lấy Khung Quy Trình & Triết Lý của `proyecto26` làm Xương Sống**:
   - Sử dụng Reasoning Loop 6 bước (Clarify $\rightarrow$ Estimate $\rightarrow$ Design $\rightarrow$ Trade-offs $\rightarrow$ Failure Modes $\rightarrow$ Iterate).
   - Áp dụng nguyên tắc chống 10 Failure Modes và bảng Trade-off 4 cột (Solves / Worsens / Change it when).
   - Tích hợp script `botec.py` để tự động hóa khâu tính toán Back-of-the-Envelope.
   - Kế thừa engine `architecture-diagram` để sinh Artifacts sơ đồ kiến trúc HTML+SVG đẳng cấp cao.
2. **Lấy Kho Dữ Liệu Thực Chiến của `wondelai` làm Thịt và Máu**:
   - Tích hợp bảng hằng số độ trễ của Jeff Dean và bảng tính toán SLA nines vào tài liệu tra cứu.
   - Đưa 8 Case Study kinh điển của `wondelai` vào làm thư viện mẫu tham khảo nhanh (Reference Architecture Bank).
   - Sử dụng thang điểm 10/10 và 8 tiêu chí Quick Diagnostic của `wondelai` làm cổng đánh giá nghiệm thu sản phẩm.
3. **Chiến Lược Tích Hợp Thông Minh (Smart Hybrid Integration)**:
   - Thay vì rải phẳng cả 22 skill làm loãng danh mục workspace, ta có thể xây dựng một **Master System Design Skill** tại `.agents/skills/system-design/` đóng vai trò Orchestrator, bên trong chứa các thư mục con `references/building-blocks/` (tổng hợp 20 khối của proyecto26 kèm mapping cloud), `references/patterns/` (8 mẫu của wondelai), `scripts/` (`botec.py`) và `render/` (`architecture-diagram`).
   - Cung cấp cơ chế routing rõ ràng, giúp Agent vừa có thể bao quát toàn cục vừa có thể đi sâu vào từng ngóc ngách kỹ thuật phức tạp nhất.
