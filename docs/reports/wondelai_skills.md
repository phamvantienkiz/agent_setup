# Báo Cáo Phân Tích Hệ Thống Skill System Design: `wondelai/skills/system-design`

- **Tên kho lưu trữ**: `wondelai/skills/system-design` (Phiên bản: 1.4.1)
- **Tác giả / Dòng tư tưởng**: wondelai (Kế thừa phương pháp luận Alex Xu - *ByteByteGo / System Design Interview* & Martin Kleppmann - *DDIA*)
- **Định dạng**: Monolithic Agent Skill kết hợp Reference Knowledge Base (1 `SKILL.md` + 6 tệp tài liệu tham chiếu chuyên sâu)
- **Giấy phép**: MIT License
- **Đường dẫn phân tích**: [skills/system-design](file:///E:/gemini/agent_setup/skills/system-design)
- **Tệp mục tiêu so sánh**: [.agents/skills/system-design/SKILL.md](file:///E:/gemini/agent_setup/.agents/skills/system-design/SKILL.md)

---

## 1. Tổng Quan & Triết Lý Cốt Lõi (Core Philosophy)

### 1.1. Triết lý "Start with Requirements, Not Solutions"
Kho lưu trữ `wondelai/skills/system-design` đặt nền tảng trên một nguyên lý bất biến trong kỹ nghệ phần mềm quy mô lớn:
> **"Start with requirements, not solutions. Jumping to architecture before understanding constraints produces over- or under-engineered systems."**  
> *(Bắt đầu từ yêu cầu, không bắt đầu từ giải pháp. Nhảy bổ vào vẽ kiến trúc trước khi nắm vững ràng buộc chỉ tạo ra những hệ thống hoặc thừa thãi, hoặc non nớt).*

Hệ thống phân tán có thể mở rộng được cấu thành từ các khối xây dựng đã được kiểm chứng (load balancers, caches, queues, databases, CDNs). Trình độ của một kỹ sư kiến trúc không nằm ở việc nhớ nhiều công nghệ hào nhoáng, mà nằm ở:
1. **Lựa chọn đúng khối xây dựng** phù hợp với bài toán.
2. **Định lượng quy mô (Sizing)** bằng các phép tính nhẩm Back-of-the-Envelope thực tế.
3. **Thấu hiểu và làm chủ các đánh đổi (Trade-offs)** mà mỗi quyết định đưa vào hệ thống.

### 1.2. Thang Đo Chất Lượng 10/10 (The 10/10 Diagnostic Score)
Khác với các tài liệu hướng dẫn định tính chung chung, skill của wondelai thiết lập một thước đo chất lượng nghiêm ngặt dựa trên **8 tiêu chuẩn chẩn đoán nhanh (Quick Diagnostic Rows)**:
$$\text{Score} = \text{round}\left(\frac{\text{Passed Rows}}{8} \times 10\right)$$

- **9 – 10 điểm (Xuất sắc)**: Đạt hầu hết/toàn bộ 8 tiêu chí — yêu cầu tường minh, số liệu tính toán dung lượng cụ thể, kiến trúc có tính dự phòng (redundancy), chiến lược mở rộng database & cache rõ ràng, xử lý bất đồng bộ qua queue, giám sát observability đầy đủ, kế hoạch triển khai zero-downtime, và mọi đánh đổi đều được nêu tên.
- **5 – 6 điểm (Trung bình)**: Kiến trúc chạy được nhưng bỏ qua khâu ước lượng quy mô, thiếu dự phòng SPOF hoặc bỏ quên khâu vận hành.
- **$\le$ 3 điểm (Thất bại)**: Đề xuất công nghệ và vẽ sơ đồ trước khi phân tích yêu cầu và tính toán tải.

---

## 2. Cấu Trúc Kho Lưu Trữ & Bản Đồ Tri Thức (Repository Architecture)

Toàn bộ kho lưu trữ gồm 7 tệp với tổng dung lượng ~75 KB tri thức cô đọng:

```
skills/system-design/
├── SKILL.md                              # Khung điều phối chính, quy tắc chấm điểm 10/10, bảng sai lầm thường gặp
└── references/
    ├── four-step-process.md              # Khung quy trình 4 bước thiết kế chuẩn (45-60 phút)
    ├── estimation-numbers.md             # Bộ số liệu tính nhẩm (Latency Jeff Dean, SLA Nines, QPS, Storage)
    ├── building-blocks.md                # 8 khối xây dựng nền tảng (DNS, CDN, LB, Cache, MQ, Consistent Hashing)
    ├── database-scaling.md               # Chiến lược mở rộng CSDL (Replication, Sharding, Shard Key, Hotspots)
    ├── common-designs.md                 # 8 thiết kế mẫu kinh điển (URL Shortener, Rate Limiter, Feed, Chat, v.v.)
    └── reliability-operations.md         # Vận hành tin cậy (Health checks Liveness/Readiness, RED/USE, DR, Autoscaling)
```

---

## 3. Phân Tích Chi Tiết Từng Trụ Cột Tri Thức

### 3.1. Quy trình 4 bước kinh điển ([`four-step-process.md`](file:///E:/gemini/agent_setup/skills/system-design/references/four-step-process.md))
Quy trình được timebox chặt chẽ cho một phiên thiết kế kiến trúc chuẩn mực (45 – 60 phút):
1. **Bước 1: Hiểu bài toán & Thiết lập phạm vi (5 – 10 phút)**:
   - Đặt tối thiểu 5 câu hỏi làm rõ (Clarifying Questions) về Use Cases, Actors, Inputs/Outputs, và các tính năng ngoài phạm vi (Out-of-scope).
   - Tách bạch yêu cầu chức năng (Functional) và phi chức năng (Non-Functional: Scale DAU/QPS, Latency SLAs P50/P95/P99, Availability nines, Consistency model, Durability RPO).
   - Tính toán nhẩm quy mô sơ bộ để định hướng quyết định.
2. **Bước 2: Đề xuất thiết kế mức cao & Đạt đồng thuận (15 – 20 phút)**:
   - Vẽ sơ đồ khung: Clients, API Gateway / Load Balancers, Application Services, Data Stores, Message Queues, CDN.
   - Định nghĩa API Contract cốt lõi (Endpoint, Method, Request/Response, Error codes).
   - Thiết lập Data Model mức logic và lựa chọn loại hình lưu trữ (Relational, Key-Value, Document, Wide-Column).
   - Hỏi ý kiến người phản biện để chốt 2-3 thành phần trọng yếu cần đào sâu.
3. **Bước 3: Đào sâu vào thành phần then chốt (Deep Dive) (15 – 20 phút)**:
   - Tập trung vào các thành phần khó mở rộng nhất, nhạy cảm nhất về tính đúng đắn (Consistency, Payment, Rate Limit), hoặc mang tính đặc thù cao nhất của hệ thống.
   - Với mỗi thành phần, bắt buộc đưa ra **tối thiểu 2 phương án** kèm bảng so sánh ưu/nhược điểm trước khi chốt giải pháp.
4. **Bước 4: Tổng kết & Đánh giá (Wrap-up) (5 phút)**:
   - Tóm tắt kiến trúc trong 1 đoạn văn.
   - Thừa nhận các đánh đổi (Acknowledged Trade-offs) và điểm nghẽn tiềm ẩn (Bottlenecks) khi quy mô tăng gấp 10x/100x.
   - Đề xuất lộ trình cải tiến tương lai và phương án xử lý lỗi biên.

---

### 3.2. Bộ số liệu định lượng Back-of-the-Envelope ([`estimation-numbers.md`](file:///E:/gemini/agent_setup/skills/system-design/references/estimation-numbers.md))
Repo cung cấp đầy đủ các hằng số vật lý và công thức vàng:
- **Lũy thừa của 2 & Quy đổi chuẩn**:
  - $2^{10} \approx 1\text{ KB} = 10^3\text{ B}$; $2^{20} \approx 1\text{ MB} = 10^6\text{ B}$; $2^{30} \approx 1\text{ GB} = 10^9\text{ B}$; $2^{40} \approx 1\text{ TB} = 10^{12}\text{ B}$.
  - 1 ngày = $86,400\text{ giây} \approx 10^5\text{ giây}$; 1 tháng $\approx 2.5 \times 10^6\text{ giây}$; 1 năm $\approx 3.15 \times 10^7\text{ giây}$.
- **Bảng độ trễ kinh điển của Jeff Dean (Latency Numbers Every Programmer Should Know)**:
  - Đọc L1 cache: 0.5 ns; Đọc RAM: 100 ns; Đọc ngẫu nhiên SSD: 150 µs; Đọc tuần tự 1 MB từ RAM: 250 µs; Round-trip cùng Data Center: 500 µs; Đọc tuần tự 1 MB SSD: 1 ms; HDD Seek: 10 ms; Round-trip liên lục địa (CA $\rightarrow$ Netherlands): 150 ms.
  - *Ý nghĩa kiến trúc*: Nếu yêu cầu độ trễ $< 1\text{ ms}$ bắt buộc phải nằm trên RAM (Cache); $< 100\text{ ms}$ có thể truy vấn DB có index; $> 1\text{ s}$ bắt buộc phải xử lý bất đồng bộ.
- **Quy luật khả dụng (Availability Nines & SLA Composition)**:
  - 99.9% (3 số 9) = 8.77 giờ downtime/năm; 99.99% (4 số 9) = 52.6 phút downtime/năm.
  - **Luật nhân phụ thuộc tuần tự**: 3 service phụ thuộc nhau, mỗi service đạt 99.9% $\rightarrow$ SLA tổng thể chỉ còn $99.9\% \times 99.9\% \times 99.9\% \approx 99.7\%$ (tụt gần một bậc 9).
  - **Dự phòng song song**: 2 instance chạy song song, mỗi instance đạt 99% $\rightarrow$ SLA tổng thể: $1 - (0.01 \times 0.01) = 99.99\%$.

---

### 3.3. Các khối xây dựng hạ tầng ([`building-blocks.md`](file:///E:/gemini/agent_setup/skills/system-design/references/building-blocks.md))
- **DNS**: A, AAAA, CNAME, NS, TTL trade-offs, GeoDNS, Round-robin DNS.
- **CDN**: Push CDN (tải chủ động, nội dung tĩnh ít đổi) vs Pull CDN (kéo theo nhu cầu, tự động cache), chiến lược vô hiệu hóa cache (TTL, Versioned URLs, Purge API).
- **Load Balancers & Reverse Proxy**:
  - L4 (Transport layer, TCP/UDP, siêu nhanh, pass-through) vs L7 (Application layer, HTTP/HTTPS, định tuyến theo path/header/cookie, SSL Termination).
  - 5 thuật toán cân bằng tải: Round Robin, Weighted Round Robin, Least Connections, IP Hash, Consistent Hashing.
  - Phân biệt Active Health Check (`/health`) và Passive Health Check (theo dõi lỗi 5xx thực tế).
- **Caching**:
  - 5 tầng cache: Client $\rightarrow$ CDN $\rightarrow$ Web Server $\rightarrow$ Application (Redis/Memcached) $\rightarrow$ DB Buffer Pool.
  - 5 chiến lược đọc/ghi: Cache-aside, Read-through, Write-through (đồng bộ), Write-behind (bất đồng bộ), Refresh-ahead.
  - Chính sách xóa (Eviction): LRU, LFU, FIFO, Random.
  - Xử lý 4 bài toán kinh điển: **Cache Stampede** (dùng Mutex lock / Request coalescing), **Hot Key** (nhân bản key trên nhiều node), **Cache Penetration** (lưu Null result kèm short TTL + Bloom Filter), **Cache Warming** (tải trước dữ liệu khi khởi động).
- **Message Queues**: Point-to-point Queue vs Pub/Sub, so sánh Kafka vs RabbitMQ vs SQS vs Redis Streams, 3 cấp độ bảo đảm phân phối (At-most-once, At-least-once, Exactly-once).
- **Consistent Hashing**: Nguyên lý vòng băm (Hash Ring), giải quyết triệt để bài toán thêm/bớt node làm dịch chuyển toàn bộ key ($1/N$ keys di chuyển thay vì $100\%$), kỹ thuật Virtual Nodes (100-200 vnodes/server) chống lệch tải.

---

### 3.4. Thiết kế & Mở rộng cơ sở dữ liệu ([`database-scaling.md`](file:///E:/gemini/agent_setup/skills/system-design/references/database-scaling.md))
- **Cây quyết định SQL vs NoSQL**: Phân tích khi nào cần ACID, Complex Joins, Structured Schema (SQL) vs High Write Throughput, Horizontal Scaling, Flexible Schema (NoSQL: Key-Value, Document, Wide-Column, Graph). Nhấn mạnh triết lý **Polyglot Persistence**.
- **Replication**: Leader-Follower (WAL replication, giải quyết replication lag bằng cơ chế Read-your-writes), Multi-Leader (xử lý xung đột ghi: LWW, App-merge, CRDTs), Leaderless (Quorum: $W + R > N$).
- **Sharding (Phân mảnh ngang)**:
  - 3 chiến lược: Hash-based, Range-based, Directory-based.
  - Tiêu chí vàng chọn Shard Key: High cardinality, Phân phối đều (Even distribution), Trùng khớp truy vấn chính (tránh Scatter-Gather).
  - Xử lý bài toán **Celebrity / Hotspot**: Shard riêng cho thực thể VIP, thứ cấp phân vùng (secondary partitioning), cache đệm phía trước.
  - Giải quyết các thao tác liên shard (Cross-shard operations): Denormalization thay cho Cross-shard Join, Distributed Saga thay cho 2PC/XA transaction.

---

### 3.5. Bộ sưu tập 8 thiết kế mẫu kinh điển ([`common-designs.md`](file:///E:/gemini/agent_setup/skills/system-design/references/common-designs.md))
Mỗi thiết kế đều bao gồm Requirements, Key Components, Trade-offs, và Số liệu tính toán cụ thể:
1. **URL Shortener**: Base62 encoding, 301 (Permanent - cache tốt) vs 302 (Temporary - bắt được analytics), Key-Value store.
2. **Rate Limiter**: So sánh 5 thuật toán (Token Bucket, Leaky Bucket, Fixed Window, Sliding Window Log, Sliding Window Counter), lưu trữ Redis cluster, HTTP headers (`X-RateLimit-*`, `Retry-After`).
3. **Notification System**: Tách riêng worker/queue cho Push, SMS, Email; Exponential Backoff retry; Idempotency key chống gửi trùng; Priority levels.
4. **News Feed (Social Network)**: Phân tích sâu bài toán **Fanout-on-write (Push)** vs **Fanout-on-read (Pull)** và kiến trúc **Hybrid Model** (Tài khoản thường $< 10\text{k}$ followers dùng Push vào Redis Sorted Set, Người nổi tiếng dùng Pull khi đọc).
5. **Chat System**: WebSocket kết nối 2 chiều trạng thái (stateful), Monotonic ID đánh số thứ tự tin nhắn theo hội thoại, Presence service dùng heartbeat 30 giây.
6. **Search Autocomplete**: Cấu trúc dữ liệu Trie (Prefix Tree), tiền tính toán top-k offline theo batch, phân mảnh Trie theo ký tự đầu.
7. **Web Crawler**: URL Frontier (hàng đợi ưu tiên BFS), cơ chế lịch sự (Politeness - robots.txt, giới hạn tần suất theo domain), Deduplication (băm nội dung HTML chống trang trùng lặp).
8. **Unique ID Generator**: Cấu trúc **Snowflake ID 64-bit** (1 bit sign, 41 bit timestamp, 5 bit datacenter, 5 bit machine, 12 bit sequence $\rightarrow$ 4 triệu ID/giây trên toàn hệ thống), cơ chế xử lý clock drift qua NTP.

---

### 3.6. Vận hành & Độ tin cậy sản xuất ([`reliability-operations.md`](file:///E:/gemini/agent_setup/skills/system-design/references/reliability-operations.md))
- **Health Checks**: Phân biệt rạch ròi **Liveness probe** (`/healthz` - tiến trình có sống không? nếu chết thì restart container) và **Readiness probe** (`/readyz` - có nhận được traffic không? nếu DB lag hoặc chưa load cache thì tạm gỡ khỏi load balancer).
- **3 Trụ cột Observability**:
  - **Four Golden Signals** (Google SRE): Latency (P50/P95/P99), Traffic (QPS), Errors (5xx rate), Saturation (CPU, RAM, Queue depth).
  - **RED Method** cho dịch vụ hướng request: Rate, Errors, Duration.
  - **USE Method** cho tài nguyên: Utilization, Saturation, Errors.
- **Chiến lược triển khai (Deployment Strategies)**: Rolling Update, Blue-Green Deployment, Canary Release (5% traffic ban đầu, tự động rollback nếu metric bất thường).
- **Kế hoạch phục hồi thảm họa (Disaster Recovery)**: Định nghĩa RPO (Recovery Point Objective - mức độ mất dữ liệu chấp nhận được) và RTO (Recovery Time Objective - thời gian hệ thống được phép ngừng hoạt động).
- **Quy tắc Autoscaling**: Luôn thiết lập Min/Max bounds, đặt Cooldown period chống hiện tượng dao động bật/tắt liên tục (thrashing).

---

## 4. Bảng So Sánh Chi Tiết: `wondelai` vs Hiện Tại (`.agents/skills/system-design`)

| Tiêu chí | Skill hiện tại (`.agents/skills/system-design`) | Skill `wondelai/skills/system-design` | Nhận xét & Đánh giá |
| :--- | :--- | :--- | :--- |
| **Quy mô tệp tin** | 1 tệp duy nhất (`SKILL.md`, 224 dòng, ~10 KB) | 1 tệp `SKILL.md` (208 dòng) + 6 tệp tham chiếu chuyên sâu (~75 KB) | `wondelai` sâu sắc hơn gấp 7 lần về khối lượng tri thức kỹ thuật. |
| **Quy trình thiết kế** | 5 bước chung chung (Analyze, Plan, Design, Validate, Document) | 4 bước chuẩn mực có timebox cụ thể (Scope, High-Level, Deep-Dive, Wrap-up) | `wondelai` rõ ràng về vai trò từng bước, thời lượng, và tiêu chí bàn giao (deliverables). |
| **Tính toán định lượng** | Không có công thức, chỉ nhắc "Latency, Throughput" | Đầy đủ công thức QPS, Storage, Bandwidth, Jeff Dean latency numbers, SLA nines | Skill hiện tại hoàn toàn thiếu hụt công cụ định lượng kích thước hệ thống. |
| **Cơ sở dữ liệu** | So sánh cơ bản SQL vs NoSQL 10 dòng | Hướng dẫn chọn CSDL, 3 kiểu Replication, 3 chiến lược Sharding, bài toán Hotspot | `wondelai` giải quyết được các bài toán thực tế khi DB đạt ngưỡng hàng triệu bản ghi. |
| **Kiến trúc mẫu** | Không có kiến trúc mẫu nào | 8 kiến trúc mẫu kinh điển kèm số liệu và cấu trúc dữ liệu cụ thể | `wondelai` cung cấp kho tài liệu tham khảo phong phú để suy luận theo mẫu. |
| **Khâu vận hành (Ops)** | Nhắc lướt qua "cần có monitoring" | Hướng dẫn chi tiết Liveness vs Readiness, Four Golden Signals, Blue-Green/Canary, DR (RPO/RTO) | `wondelai` biến khâu vận hành thành một phần không thể tách rời của bản thiết kế. |
| **Đánh giá chất lượng** | Không có tiêu chí đánh giá cụ thể | Thang điểm 10/10 với 8 tiêu chí kiểm tra nhanh (Quick Diagnostic) | Giúp Agent tự chấm điểm và biết chính xác mình đang thiếu sót phần nào. |

---

## 5. Điểm Mạnh, Điểm Yếu & Đánh Giá Tổng Thể

### 5.1. Điểm mạnh nổi bật
1. **Tính sư phạm & Cấu trúc chuẩn hóa cao**: Phù hợp tối đa với các chuẩn mực phỏng vấn kiến trúc tại các tập đoàn lớn (FAANG/Big Tech) và các tài liệu thiết kế tiêu chuẩn trong doanh nghiệp.
2. **Số liệu định lượng thực tế**: Bảng tra cứu độ trễ của Jeff Dean và công thức tính dung lượng/băng thông giúp agent không bị rơi vào bẫy "nói chung chung" (nói "hệ thống tải cao" thay vì "50,000 QPS").
3. **8 Case study kinh điển**: Cung cấp mẫu hình chuẩn mực cho những bài toán phổ biến nhất (URL shortener, rate limiter, chat, feed, unique id, v.v.).
4. **Cơ chế tự kiểm tra 10/10**: Bảng Quick Diagnostic 8 hàng là công cụ cực kỳ hữu hiệu để đưa vào checklist nghiệm thu của Agent.

### 5.2. Hạn chế & Khoảng trống kỹ thuật
1. **Thiếu tính module hóa ở mức Agent**: Toàn bộ kiến trúc vẫn gom trong 1 skill đơn lẻ (`system-design`). Khi Agent cần giải quyết một bài toán hẹp (như chỉ hỏi về Sharded Counter hoặc thiết kế API contract), việc đọc toàn bộ reference có thể gây lãng phí context window.
2. **Thiếu ánh xạ nhà cung cấp đám mây (Cloud Providers)**: Các hướng dẫn hoàn toàn ở mức khái niệm trung lập (Generic/Vendor-neutral), chưa có bảng ánh xạ tương đương sang AWS (ALB, DynamoDB, SQS, Kinesis), GCP (Cloud Run, Spanner, Pub/Sub), hay Azure.
3. **Không có công cụ sinh sơ đồ tự động**: Chỉ hướng dẫn vẽ sơ đồ bằng chữ hoặc Mermaid, không có công cụ sinh sơ đồ kiến trúc chuyên nghiệp độc lập.
4. **Không có script tính toán tự động**: Kỹ sư/Agent vẫn phải tự làm tính nhẩm bằng tay theo công thức.

---

## 6. Đề Xuất Tiếp Thu Cho Kế Hoạch Nâng Cấp Hệ Thống Skill

Từ phân tích trên, các thành phần tinh túy từ `wondelai/skills/system-design` cần được chắt lọc và tích hợp vào kế hoạch nâng cấp skill:
1. **Tích hợp bộ số liệu vàng vào Agent Prompt**: Bảng latency numbers của Jeff Dean, bảng availability nines, và công thức tính toán QPS/Storage.
2. **Áp dụng Thang điểm 10/10 & 8 Quick Diagnostic Rows**: Đưa vào giai đoạn Validate của skill System Design để bắt buộc Agent tự kiểm tra trước khi bàn giao tài liệu.
3. **Kế thừa các giải pháp cơ sở dữ liệu chuyên sâu**: Cơ chế Sharding, cách chọn Shard Key, xử lý bài toán Celebrity Hotspot, và giải pháp Read-your-writes cho replication lag.
4. **Tích hợp 8 Architecture Recipes**: Sử dụng 8 thiết kế mẫu làm kho dữ liệu tham khảo nhanh khi người dùng yêu cầu thiết kế các hệ thống tương tự.
5. **Chuẩn hóa quy trình Liveness/Readiness và SRE Observability**: Bổ sung Four Golden Signals và thiết kế probe K8s vào tiêu chuẩn đầu ra kiến trúc.
