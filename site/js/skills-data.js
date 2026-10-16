/**
 * Skills Database for agent_setup (by Jin)
 * Curated and customized for Antigravity CLI (agy)
 */

export const SKILL_CATEGORIES = [
  { id: 'all', label: 'Tất Cả Kỹ Năng' },
  { id: 'llm-agent', label: 'LLM - Agent' },
  { id: 'coding', label: 'Coding' },
  { id: 'system', label: 'System Design' },
  { id: 'design', label: 'Design & UI/UX' },
  { id: 'ba', label: 'BA & Requirements' },
  { id: 'docs', label: 'Docs & Diagrams' },
  { id: 'research', label: 'Scientific Research' },
];

export const SKILLS_DATA = [
  // ===================== 1. LLM - AGENT =====================
  {
    id: 'agent-harness',
    name: 'agent-harness',
    category: 'llm-agent',
    categories: ['llm-agent', 'system'],
    categoryLabel: 'LLM - Agent / System',
    title: 'Enterprise Multi-Turn Agent Harness',
    description: 'Khung vận hành AI Agent doanh nghiệp chạy dài hạn: quản lý ngữ cảnh qua nhiều phiên (session persistence), checkpoint an toàn, Human-in-the-loop, tự hồi phục khi gặp sự cố.',
    triggers: ['harness', 'agent loop', 'long-running agent', 'session persist', 'agent crashes', 'lifecycle hook'],
    promptTemplate: 'Thiết lập mô hình Agent Harness cho luồng hỗ trợ tác chiến dài hạn với checkpoint lưu vết phiên làm việc và Human-in-the-loop.',
    details: `### Mục đích & Khả năng vận hành:
Khung điều phối chuyên sâu cho hệ thống AI Agent chạy xuyên suốt hàng trăm lượt (turns) mà không bị mất ngữ cảnh hay crash.

#### Tính năng cốt lõi:
1. **Quản lý Context & Trí nhớ**: Lưu trạng thái phiên làm việc (Session Persistence) và tự nén context khi gần ngưỡng token.
2. **Safety Guardrails**: Kiểm soát hành động không thể đảo ngược, bắt buộc phê duyệt với các thao tác rủi ro cao.
3. **Tool Registry & Lifecycle Hooks**: Đăng ký công cụ linh hoạt, hook vào trước/sau mỗi lượt gọi tool để ghi log kiểm toán (audit trail).`
  },
  {
    id: 'rag-architect',
    name: 'rag-architect',
    category: 'llm-agent',
    categories: ['llm-agent', 'system'],
    categoryLabel: 'LLM - Agent / System',
    title: 'Enterprise RAG Architecture',
    description: 'Thiết kế hệ thống RAG đa tầng, tối ưu Vector Database (Pinecone, Qdrant, Chroma), Hybrid Search (BM25 + Dense Vectors), Cross-Encoder Re-ranking và Context Augmentation.',
    triggers: ['rag', 'vector database', 'hybrid search', 'reranking', 'embeddings', 'semantic search'],
    promptTemplate: 'Dùng skill rag-architect để thiết kế kiến trúc hệ thống RAG phục vụ tra cứu hàng triệu tài liệu pháp lý với độ chính xác cao bằng Hybrid Search.',
    details: `### Kiến trúc RAG chuẩn doanh nghiệp:
- **Chiến lược Chunking**: Semantic Chunking, Recursive Text Splitting theo cấu trúc tài liệu.
- **Hybrid Retrieval**: Kết hợp từ khóa chính xác (BM25) và ngữ nghĩa vector đa chiều.
- **Tối ưu suy luận**: Re-ranking bằng mô hình Cross-Encoder để lọc nhiễu trước khi đưa vào Context Window của LLM.`
  },
  {
    id: 'langchain-skills',
    name: 'langchain-skills',
    category: 'llm-agent',
    categories: ['llm-agent', 'coding'],
    categoryLabel: 'LLM - Agent / Coding',
    title: 'LangChain & LangGraph Orchestration',
    description: 'Xây dựng luồng tác chiến Agentic AI đa bước với LangChain v0.3 và LangGraph, quản lý State Graph, chu trình có điều kiện (Conditional Edges) và Human-in-the-loop.',
    triggers: ['langchain', 'langgraph', 'state graph', 'agentic workflow', 'deep agents'],
    promptTemplate: 'Thiết kế một State Graph bằng LangGraph để điều phối quy trình phân tích dữ liệu, tự động sửa lỗi và gọi tool ngoài.',
    details: `### Hướng dẫn ứng dụng:
- Xây dựng sơ đồ trạng thái \`StateGraph\` với các node xử lý chuyên biệt.
- Quản lý bộ nhớ phiên làm việc bằng Checkpointer và SQLite/Postgres.
- Điều phối nhiều sub-agent cộng tác song song.`
  },
  {
    id: 'prompt-engineer',
    name: 'prompt-engineer',
    category: 'llm-agent',
    categories: ['llm-agent'],
    categoryLabel: 'LLM - Agent',
    title: 'Advanced Prompt Engineering & Evals',
    description: 'Thiết kế cấu trúc prompt chuyên sâu cho LLMs: Chain-of-Thought (CoT), Few-Shot Learning, Structured Outputs (Pydantic / JSON Schema) và framework đánh giá độ chính xác.',
    triggers: ['prompt', 'prompt engineering', 'chain-of-thought', 'few-shot', 'structured outputs'],
    promptTemplate: 'Tối ưu hóa hệ thống Prompt này bằng kỹ thuật Chain-of-Thought và ràng buộc Structured Output theo JSON Schema.',
    details: `### Kỹ thuật áp dụng:
- Cấu trúc prompt theo vai trò, mục tiêu, ràng buộc biên và ví dụ mẫu.
- Ngăn ngừa hallucination bằng các chỉ dẫn ground-truth và negative constraints.
- Tự động hóa đánh giá định lượng (Evals) về độ tin cậy của mô hình.`
  },

  // ===================== 2. CODING =====================
  {
    id: 'clean-code',
    name: 'clean-code',
    category: 'coding',
    categories: ['coding'],
    categoryLabel: 'Coding',
    title: '66 Canonical Clean Code Rules & Boy Scout',
    description: 'Áp dụng 66 quy tắc Clean Code kinh điển của Robert C. Martin, quy tắc Boy Scout, quy chuẩn đặt tên, kiến trúc Clean Architecture và phát hiện code smells trên 21 ngôn ngữ.',
    triggers: ['clean code', 'refactor', 'boy scout rule', 'code review', 'code smell'],
    promptTemplate: 'Review và tái cấu trúc (refactor) đoạn code này theo nghiêm ngặt 66 quy tắc Clean Code và nguyên lý Boy Scout Rule.',
    details: `### Kỷ luật Clean Code:
- **Boy Scout Rule**: Luôn để lại codebase sạch sẽ hơn lúc bạn tiếp nhận.
- **Hàm đơn nhiệm (SRP)**: Mỗi hàm chỉ làm duy nhất một việc và làm thật tốt.
- **Surgical Diff**: Chỉ sửa đúng những dòng liên quan đến yêu cầu, không reformat code lân cận.`
  },
  {
    id: 'python-fastapi-code',
    name: 'python-fastapi-code',
    category: 'coding',
    categories: ['coding'],
    categoryLabel: 'Coding',
    title: 'Senior Python & FastAPI Engineer',
    description: 'Kỹ sư Senior Python/FastAPI: SOLID, Pydantic V2, async SQLAlchemy, xác thực JWT/OAuth2, Dependency Injection, async testing (pytest-asyncio) và WebSockets.',
    triggers: ['fastapi', 'pydantic v2', 'async sqlalchemy', 'pytest-asyncio', 'jwt'],
    promptTemplate: 'Viết router và service quản trị người dùng bằng FastAPI, Pydantic V2, SQLAlchemy 2.0 Async Session và kiểm thử với pytest-asyncio.',
    details: `### Chuẩn cấu trúc phân tầng:
1. **Routers**: Nhận request, xác thực schema bằng Pydantic V2.
2. **Services**: Xử lý toàn bộ logic nghiệp vụ (Business Rules).
3. **Repositories**: Thao tác dữ liệu qua Async SQLAlchemy 2.0.
4. **Schemas**: Định nghĩa DTO request/response rõ ràng.`
  },
  {
    id: 'fastapi-backend-scaffold',
    name: 'fastapi-backend-scaffold',
    category: 'coding',
    categories: ['coding'],
    categoryLabel: 'Coding',
    title: 'FastAPI Microservice Scaffolding',
    description: 'Bộ khung chuẩn mực cho microservice FastAPI: phân chia controller/service/repo, virtual environment cô lập tại chỗ (.venv), pyproject.toml và middleware cross-cutting.',
    triggers: ['scaffold backend', 'fastapi project', 'backend template', 'uvicorn'],
    promptTemplate: 'Scaffold một backend FastAPI mới hoàn chỉnh theo chuẩn kiến trúc backend/ và môi trường cô lập .venv.',
    details: `### Quy chuẩn khởi tạo:
- Thư mục gốc luôn đặt là \`backend/\`.
- Môi trường ảo bắt buộc tại \`backend/.venv\`.
- Quản lý gói bằng \`pyproject.toml\` (uv toolchain).`
  },
  {
    id: 'nvidia-cuda',
    name: 'nvidia-cuda',
    category: 'coding',
    categories: ['coding'],
    categoryLabel: 'Coding',
    title: 'NVIDIA CUDA GPU Programming',
    description: 'Lập trình tăng tốc phần cứng GPU với CUDA C/C++, cuBLAS, cuDNN, NCCL, tối ưu hóa bộ nhớ Shared Memory, parallel thread execution và profiling qua Nsight.',
    triggers: ['cuda', 'gpu optimization', 'kernel optimization', 'cublas', 'cudnn'],
    promptTemplate: 'Viết một CUDA kernel tối ưu phép tính ma trận lớn sử dụng Shared Memory và vectorization.',
    details: `### Nguồn tri thức trực tiếp:
Tích hợp MCP Server chính thức từ NVIDIA, đảm bảo tra cứu API docs mới nhất và tính toán Occupancy GPU chuẩn xác.`
  },
  {
    id: 'stm32-embedded-workflow',
    name: 'stm32-embedded-workflow',
    category: 'coding',
    categories: ['coding'],
    categoryLabel: 'Coding',
    title: 'Senior Embedded STM32 Workflow',
    description: 'Kỹ sư nhúng STM32 chuyên sâu: phân tích datasheet, cấu hình chân CubeMX, tính toán timer/clock, viết mã HAL drivers an toàn thanh ghi và debug bring-up.',
    triggers: ['stm32', 'cubemx', 'embedded', 'hal driver', 'gpio/uart/spi', 'timer math'],
    promptTemplate: 'Phân tích datasheet STM32F4 và tính toán thanh ghi Timer để phát xung PWM 20kHz điều khiển động cơ.',
    details: `### Quy trình kỹ thuật nhúng:
1. Tra cứu sơ đồ chân (Pin Mapping) đối chiếu PDF ST Microelectronics.
2. Lập danh sách kiểm tra cấu hình STM32CubeMX.
3. Xuất mã nguồn tham khảo \`main.c\` tuân thủ chuẩn HAL.`
  },

  // ===================== 3. SYSTEM DESIGN =====================
  {
    id: 'system-design',
    name: 'system-design',
    category: 'system',
    categories: ['system'],
    categoryLabel: 'System Design',
    title: 'Distributed System Architecture',
    description: 'Thiết kế kiến trúc phân tán cấp doanh nghiệp: High Availability, Caching (Redis), Database Sharding, Message Queue (Kafka), CAP Theorem, tính toán dung lượng (TPS/QPS).',
    triggers: ['system design', 'scalability', 'distributed architecture', 'caching', 'rate limiter', 'sharding'],
    promptTemplate: 'Hãy thiết kế kiến trúc hệ thống URL Shortener có khả năng phục vụ 100,000 QPS với độ trễ P99 < 15ms.',
    details: `### Nội dung thẩm định:
- Phân tích SLA, độ khả dụng 99.99% và ước lượng phần cứng.
- Mô hình nhất quán dữ liệu (Strong vs Eventual Consistency).
- Thiết kế luồng xử lý bất đồng bộ qua hàng đợi thông điệp.`
  },
  {
    id: 'api-design-patterns',
    name: 'api-design-patterns',
    category: 'system',
    categories: ['system'],
    categoryLabel: 'System Design',
    title: 'Enterprise API Design Patterns',
    description: 'Các mẫu thiết kế API chuẩn mực (RESTful, GraphQL, gRPC, phân trang Cursor-based, bảo mật Idempotency và Rate Limiting).',
    triggers: ['api design', 'idempotency', 'pagination', 'restful standards', 'cursor pagination'],
    promptTemplate: 'Áp dụng skill api-design-patterns để thiết kế API thanh toán an toàn với Idempotency-Key và Cursor Pagination.',
    details: `Chuẩn hóa mã lỗi RFC 7807 (Problem Details for HTTP APIs) và hợp đồng dữ liệu chuẩn mực giữa Frontend và Backend.`
  },

  // ===================== 4. DESIGN & UI/UX (WITH 3D) =====================
  {
    id: '3dviz-pro-max',
    name: '3dviz-pro-max',
    category: 'design',
    categories: ['design'],
    categoryLabel: 'Design & UI/UX',
    title: '3D WebGL & Three.js Scene Design',
    description: 'Thiết kế không gian và mô hình 3D tương tác trên WebGL/Three.js: 223 công thức, 37 phong cách 3D, hệ thống chiếu sáng studio, vật liệu PBR và diorama khoa học.',
    triggers: ['3d', 'three.js', 'webgl', 'spatial scene', 'diorama', '3d visualization', 'gltf'],
    promptTemplate: 'Dùng skill 3dviz-pro-max để tạo một mô hình mạng lưới nơ-ron 3D tương tác bằng Three.js trong file HTML.',
    details: `### Kho tri thức 3D tích hợp:
- **223 công thức & 37 style profile**: Cyberpunk, Sci-Fi Studio, Minimalist Clay, Holographic Neon...
- **22 Lighting Rigs**: 3-point studio lighting, HDR skybox, ambient occlusion.
- **Tối ưu GPU**: Đảm bảo 60 FPS, draw call batching, LOD (Level of Detail).`
  },
  {
    id: 'ui-ux-pro-max',
    name: 'ui-ux-pro-max',
    category: 'design',
    categories: ['design'],
    categoryLabel: 'Design & UI/UX',
    title: 'UI/UX Design Intelligence',
    description: 'Trí tuệ thiết kế giao diện toàn diện: 50 phong cách thị giác, 192 bảng màu chuyên dụng, 74 bộ ghép font, 119 quy tắc UX, hỗ trợ 22 stack frontend.',
    triggers: ['ui', 'ux', 'redesign', 'style', 'palette', 'dark mode', 'component'],
    promptTemplate: 'Dùng skill ui-ux-pro-max để tư vấn phong cách thiết kế, bảng màu OLED Dark/Emerald và bố cục Dashboard quản trị.',
    details: `### Thư viện tri thức có sẵn:
- 50 phong cách giao diện (Minimalist, Glassmorphism, Brutalism, Cybernetic...).
- Bộ quy tắc khoảng cách, phân cấp kiểu chữ, và độ tương phản màu sắc chuẩn WCAG 2.2 AA.
- Code mẫu responsive cho React, Vue, Svelte, Tailwind CSS, và Vanilla Web.`
  },
  {
    id: 'ui-styling',
    name: 'ui-styling',
    category: 'design',
    categories: ['design'],
    categoryLabel: 'Design & UI/UX',
    title: 'Tailwind CSS & shadcn/ui Expert',
    description: 'Triển khai giao diện chuẩn mực bằng Tailwind CSS, shadcn/ui (Radix UI) và Canvas visual patterns, đảm bảo 100% tiếp cận accessible.',
    triggers: ['shadcn', 'tailwind', 'ui styling', 'radix', 'accessible modal'],
    promptTemplate: 'Dùng skill ui-styling để dựng một form xác thực đăng nhập có validate dữ liệu bằng Tailwind CSS và Radix UI primitives.',
    details: `Xây dựng component accessible (Dialog, Dropdown Menu, Data Table), hỗ trợ chế độ Dark Mode OLED tự nhiên qua CSS Custom Properties.`
  },
  {
    id: 'design-system',
    name: 'design-system',
    category: 'design',
    categories: ['design'],
    categoryLabel: 'Design & UI/UX',
    title: 'Token Architecture & Design System',
    description: 'Xây dựng kiến trúc Token 3 tầng (Primitive -> Semantic -> Component), CSS Custom Properties, quy chuẩn khoảng cách và typography scale.',
    triggers: ['design system', 'tokens', 'component specs', 'css variables'],
    promptTemplate: 'Dùng skill design-system để xuất ra bộ Design Tokens CSS chuẩn 3 tầng cho giao diện nền tảng công nghệ.',
    details: `Đồng bộ triệt để giữa file thiết kế Figma và mã nguồn CSS, hạn chế tối đa việc hardcode mã màu hex.`
  },
  {
    id: 'design-artifact',
    name: 'design-artifact',
    category: 'design',
    categories: ['design'],
    categoryLabel: 'Design & UI/UX',
    title: 'HTML Artifacts & Creative Direction',
    description: 'Định hướng thẩm mỹ và tạo các file HTML độc lập (Single-file HTML): báo cáo, landing page, demo không mang cảm giác AI generic.',
    triggers: ['html artifact', 'landing page', 'report', 'demo html'],
    promptTemplate: 'Dùng skill design-artifact để tạo một trang landing page giới thiệu tính năng mới dưới dạng một file HTML tự chứa (single-file).',
    details: `Toàn bộ CSS, SVG và JS được nhúng gọn trong 1 file HTML duy nhất, không phụ thuộc bundler hay CDN ngoài.`
  },
  {
    id: 'html',
    name: 'html',
    category: 'design',
    categories: ['design'],
    categoryLabel: 'Design & UI/UX',
    title: 'Self-Contained Single-File Deliverable',
    description: 'Bộ định tuyến tạo hoặc tái thiết kế các sản phẩm HTML đóng gói trọn vẹn (single-file): tài liệu kỹ thuật, trang giới thiệu, dashboard báo cáo.',
    triggers: ['html deliverable', 'single file html', 'self-contained'],
    promptTemplate: 'Dùng skill html để xuất bản tài liệu báo cáo kỹ thuật thành file HTML độc lập hoàn chỉnh.',
    details: `Tối ưu hóa khả năng xem ngoại tuyến (offline-ready), nhúng font an toàn và đảm bảo hiển thị hoàn hảo trên mọi kích thước màn hình.`
  },
  {
    id: 'banner-design',
    name: 'banner-design',
    category: 'design',
    categories: ['design'],
    categoryLabel: 'Design & UI/UX',
    title: 'Marketing & Hero Banner Design',
    description: 'Thiết kế banner mạng xã hội, ảnh quảng cáo, hero banner trang web với phong cách typography ấn tượng, gradient và bố cục 3D.',
    triggers: ['banner', 'social banner', 'hero asset', 'ad creative'],
    promptTemplate: 'Dùng skill banner-design để thiết kế banner kích thước 1200x630 cho LinkedIn chủ đề Antigravity Agent Setup.',
    details: `Định hướng bố cục và xuất file hình ảnh hoặc vector chất lượng cao phục vụ truyền thông sản phẩm.`
  },
  {
    id: 'brand',
    name: 'brand',
    category: 'design',
    categories: ['design'],
    categoryLabel: 'Design & UI/UX',
    title: 'Brand Voice & Consistency',
    description: 'Định hình giọng văn thương hiệu (Brand Voice), hệ thống thông điệp, kiểm tra độ nhất quán của nội dung và tài sản thương hiệu.',
    triggers: ['brand voice', 'tone of voice', 'brand guidelines', 'messaging'],
    promptTemplate: 'Dùng skill brand để xây dựng hướng dẫn giọng điệu thương hiệu (Voice & Tone) cho sản phẩm công nghệ AI.',
    details: `Thiết lập phong cách giao tiếp tự tin, chuẩn xác, khiêm tốn và tập trung vào kỹ thuật cho sản phẩm.`
  },

  // ===================== 5. BA & REQUIREMENTS =====================
  {
    id: 'user-story-ac-writer',
    name: 'user-story-ac-writer',
    category: 'ba',
    categories: ['ba'],
    categoryLabel: 'BA & Requirements',
    title: 'User Story & Gherkin AC Writer',
    description: 'Bóc tách User Story chuẩn INVEST và Acceptance Criteria định dạng Given-When-Then (Gherkin), bóc tách kịch bản lỗi, thiết lập Architecture Guardrails.',
    triggers: ['user story', 'acceptance criteria', 'gherkin', 'invest', 'backlog'],
    promptTemplate: 'Hãy dùng skill user-story-ac-writer để phân tích và viết bộ User Story chi tiết kèm Acceptance Criteria chuẩn Gherkin cho tính năng [TÊN_TÍNH_NĂNG].',
    details: `### Quy trình xử lý BA:
1. Bóc tách luồng nghiệp vụ từ Sequence hoặc Activity Diagram.
2. Kiểm tra độ bao phủ nhánh lỗi (Fact-list Coverage Check).
3. Viết kịch bản Given-When-Then chuẩn mực.
4. Thiết lập Architecture Guardrails để Agent lập trình không phá vỡ bất biến của hệ thống.`
  },
  {
    id: 'product-requirements',
    name: 'product-requirements',
    category: 'ba',
    categories: ['ba'],
    categoryLabel: 'BA & Requirements',
    title: 'Interactive BA & PRD Generator',
    description: 'Phân tích yêu cầu cấp độ Senior IT-BA & PO, lập bảng Open Questions (OQ), thiết kế Scope Diagram và sinh PRD tích hợp chuẩn 3 tầng tài liệu.',
    triggers: ['prd', 'requirements', 'scope', 'business analysis', 'oq'],
    promptTemplate: 'Kích hoạt skill product-requirements để lập bản đặc tả yêu cầu PRD và đặt các câu hỏi mở (Open Questions) làm rõ phạm vi dự án [TÊN_DỰ_ÁN].',
    details: `### Tính năng cốt lõi:
- Phỏng vấn làm rõ yêu cầu với bảng Open Questions (OQ) có đánh số.
- Vẽ Scope Diagram trực quan hóa ranh giới trong/ngoài phạm vi (In-scope vs Out-of-scope).
- Xuất tài liệu PRD trực tiếp vào đúng tầng nghiệp vụ: \`docs/business/prd.md\`.`
  },

  // ===================== 6. DOCS & DIAGRAMS =====================
  {
    id: 'documentation',
    name: 'documentation',
    category: 'docs',
    categories: ['docs'],
    categoryLabel: 'Docs & Diagrams',
    title: '3-Layer Documentation Architecture',
    description: 'Hệ thống tài liệu 3 tầng (Business / Architecture / Implementation), Single Source of Truth, thiết lập Architecture Guardrails chống hallucination.',
    triggers: ['doc structure', 'architecture doc', 'adr', 'documentation system'],
    promptTemplate: 'Khởi tạo cấu trúc tài liệu 3 tầng (Business, Architecture, Implementation) cho dự án theo chuẩn documentation skill.',
    details: `### Cấu trúc 3 tầng:
1. \`docs/business/\`: PRD, BRD, User Stories, Roadmap.
2. \`docs/architecture/\`: C4 Architecture, Tech Stack, ADR, Data Model.
3. \`docs/implementation/\`: Sprint tasks, API contracts, changelogs.`
  },
  {
    id: 'diagram-design',
    name: 'diagram-design',
    category: 'docs',
    categories: ['docs'],
    categoryLabel: 'Docs & Diagrams',
    title: 'Enterprise Architecture Diagrams',
    description: 'Vẽ sơ đồ kiến trúc chuẩn doanh nghiệp: Flowchart, Sequence, State Machine, C4 Model, ERD, Network Topology (hỗ trợ HTML/SVG, .drawio, .excalidraw).',
    triggers: ['architecture diagram', 'sequence diagram', 'flowchart', 'c4 model', 'erd', 'drawio'],
    promptTemplate: 'Dùng skill diagram-design để vẽ sơ đồ Sequence Diagram mô tả luồng xác thực OAuth2 / JWT bằng HTML/SVG sắc nét.',
    details: `Xuất file vector SVG nét căng hoặc file import trực tiếp vào draw.io / Excalidraw.`
  },
  {
    id: 'html-diagram',
    name: 'html-diagram',
    category: 'docs',
    categories: ['docs'],
    categoryLabel: 'Docs & Diagrams',
    title: 'Interactive HTML Diagrams',
    description: 'Tạo sơ đồ HTML tương tác độc lập (interactive single-file HTML diagram) hỗ trợ zoom, lọc nhánh và khám phá trạng thái.',
    triggers: ['html-diagram', 'interactive diagram', 'topology map'],
    promptTemplate: 'Tạo sơ đồ tương tác giải thích luồng hoạt động của hệ thống Agent bằng html-diagram.',
    details: `Cho phép click vào từng node trên sơ đồ để xem thông số chi tiết và giải thích tương ứng.`
  },
  {
    id: 'html-plan',
    name: 'html-plan',
    category: 'docs',
    categories: ['docs'],
    categoryLabel: 'Docs & Diagrams',
    title: 'Interactive HTML Implementation Plans',
    description: 'Trực quan hóa kế hoạch triển khai (Implementation Plan) dưới dạng HTML trực quan, phân cấp rõ ràng theo timeline, phụ thuộc và trách nhiệm.',
    triggers: ['html-plan', 'interactive plan', 'roadmap html', 'gantt'],
    promptTemplate: 'Chuyển đổi tài liệu kế hoạch này thành file html-plan trực quan để báo cáo tiến độ với Tech Lead.',
    details: `Cung cấp bảng tiến độ Gantt, checkbox nghiệm thu và đánh dấu độ ưu tiên rõ ràng.`
  },
  {
    id: 'html-wireframe',
    name: 'html-wireframe',
    category: 'docs',
    categories: ['docs'],
    categoryLabel: 'Docs & Diagrams',
    title: 'Low-Fidelity HTML Wireframing',
    description: 'Tạo bản vẽ khung xương (wireframe) HTML nhanh chóng để kiểm chứng cấu trúc thông tin và luồng thao tác trước khi thiết kế chi tiết.',
    triggers: ['wireframe', 'html-wireframe', 'mockup low-fi'],
    promptTemplate: 'Vẽ một bản wireframe HTML luồng checkout thanh toán thương mại điện tử bằng html-wireframe.',
    details: `Tập trung vào phân cấp thông tin, thứ tự hành động và khoảng cách mà không bị xao nhãng bởi màu sắc cầu kỳ.`
  },
  {
    id: 'html-prototype',
    name: 'html-prototype',
    category: 'docs',
    categories: ['docs'],
    categoryLabel: 'Docs & Diagrams',
    title: 'High-Fidelity HTML Interactive Prototype',
    description: 'Tạo mẫu thử tương tác (interactive prototype) mô phỏng chính xác giao diện và hành vi của sản phẩm cuối.',
    triggers: ['prototype', 'html-prototype', 'high-fi mockup'],
    promptTemplate: 'Dùng skill html-prototype để dựng mẫu thử tương tác hoàn chỉnh cho bảng điều khiển giám sát AI Agent.',
    details: `Tích hợp giả lập dữ liệu, bộ lọc bảng và trạng thái loading/error chân thực.`
  },
  {
    id: 'slides',
    name: 'slides',
    category: 'docs',
    categories: ['docs'],
    categoryLabel: 'Docs & Diagrams',
    title: 'Executive HTML Presentation Slides',
    description: 'Tạo bài thuyết trình slide chuyên nghiệp bằng HTML/CSS tích hợp Chart.js, responsive và hỗ trợ trình chiếu bằng bàn phím.',
    triggers: ['slides', 'presentation', 'pitch deck html'],
    promptTemplate: 'Tạo bộ 10 slide HTML thuyết trình chiến lược nâng cấp quy trình phát triển phần mềm với Antigravity CLI.',
    details: `Điều hướng bằng phím mũi tên Trái/Phải, tích hợp biểu đồ dữ liệu sống động bằng Chart.js.`
  },
  {
    id: 'lecture-visualizer',
    name: 'lecture-visualizer',
    category: 'docs',
    categories: ['docs', 'design'],
    categoryLabel: 'Docs & Diagrams / 3D',
    title: 'Academic Algorithm & Concept Visualizer',
    description: 'Xây dựng bài giảng trực quan hóa học thuật cao cấp (2D/3D), mô phỏng thuật toán từng bước (Step-by-step interactive algorithm).',
    triggers: ['lecture', 'algorithm simulation', 'interactive visualizer', 'academic 3d'],
    promptTemplate: 'Dùng skill lecture-visualizer để giải thích trực quan thuật toán Attention Mechanism trong Transformer dưới dạng HTML tương tác.',
    details: `Phương pháp sư phạm trực quan: Giải thích bản chất toán học bằng ví dụ thực tế và widget điều khiển từng bước thực thi.`
  },

  // ===================== 7. SCIENTIFIC RESEARCH =====================
  {
    id: 'cs-research-skills',
    name: 'cs-research-skills',
    category: 'research',
    categories: ['research'],
    categoryLabel: 'CS Research (46 Modules Pack)',
    title: 'Computer Science Research Skills Pack',
    isModularPack: true,
    packPath: 'cs-research-skills/',
    description: 'Gói 46 kỹ năng nghiên cứu Khoa học Máy tính & AI (lưu tại thư mục gốc để tối ưu tải nhẹ): PyTorch Lightning, Transformers, GPU Optimization, NetworkX, UMAP, Qiskit, PennyLane, Paper Lookup, Peer Review...',
    triggers: ['cs research', 'pytorch-lightning', 'transformers', 'qiskit', 'pennylane', 'peer-review', 'paper-lookup', 'polars', 'shap'],
    promptTemplate: 'Sao chép kỹ năng cần thiết từ gói cs-research-skills vào .agents/skills:\ncp -r cs-research-skills/paper-lookup .agents/skills/\ncp -r cs-research-skills/transformers .agents/skills/',
    details: `### Gói 46 kỹ năng \`cs-research-skills/\`:
Được lưu tại thư mục gốc repository để giữ cho Antigravity CLI luôn siêu nhẹ. Khi cần nghiên cứu đề tài cụ thể, chỉ cần copy kỹ năng tương ứng vào \`.agents/skills/\`:
- **AI & Deep Learning**: \`transformers\`, \`pytorch-lightning\`, \`stable-baselines3\`, \`scikit-learn\`, \`shap\`, \`umap-learn\`, \`torch-geometric\`.
- **Quantum Computing & Physics**: \`qiskit\`, \`pennylane\`, \`cirq\`.
- **Học thuật & Xuất bản**: \`paper-lookup\`, \`peer-review\`, \`literature-review\`, \`scientific-writing\`, \`scientific-visualization\`, \`citation-management\`.
- **Big Data & Math**: \`polars\`, \`dask\`, \`networkx\`, \`zarr-python\`, \`timesfm-forecasting\`.`
  },
  {
    id: 'microsoft-research',
    name: 'microsoft-research',
    category: 'research',
    categories: ['research'],
    categoryLabel: 'Microsoft Research (11 Tools Pack)',
    title: 'Microsoft Research Pipeline Suite',
    isModularPack: true,
    packPath: 'microsoft-research/',
    description: 'Quy trình nghiên cứu chuẩn Microsoft Research (lưu tại thư mục gốc): tìm kiếm bài báo, nảy sinh ý tưởng (Idea Spark), chẩn đoán điểm nghẽn, kiểm tra tính trùng lặp (Scoop Check) và chuyển đổi Paper sang Poster/Video/Blog.',
    triggers: ['microsoft research', 'idea spark', 'paper search', 'paper2video', 'scoop check', 'bottleneck diagnosis'],
    promptTemplate: 'Kích hoạt công cụ từ microsoft-research vào .agents/skills:\ncp -r microsoft-research/rs-paper-search .agents/skills/\ncp -r microsoft-research/rs-idea-spark .agents/skills/',
    details: `### Bộ 11 công cụ \`microsoft-research/\`:
1. \`rs-paper-search\`: Tìm kiếm và tổng hợp tài liệu khoa học chuyên sâu.
2. \`rs-idea-spark\`: Gợi ý hướng nghiên cứu mới từ các khoảng trống tri thức.
3. \`rs-idea-quality\`: Đánh giá chất lượng và tính khả thi của ý tưởng nghiên cứu.
4. \`rs-scoop-check\`: Kiểm tra xem ý tưởng nghiên cứu đã bị ai công bố trước hay chưa.
5. \`rs-bottleneck-diagnosis\`: Chẩn đoán nút thắt kỹ thuật trong mô hình thực nghiệm.
6. \`rs-paper2blog\` / \`rs-paper2video\` / \`rs-paper2poster\`: Tự động hóa truyền thông khoa học đa định dạng.`
  },
  {
    id: 'research-hub',
    name: 'research-hub',
    category: 'research',
    categories: ['research'],
    categoryLabel: 'Research Hub (Orchestrator)',
    title: 'Research Hub Master Orchestrator',
    isModularPack: true,
    packPath: 'research-hub/',
    description: 'Bộ khung điều phối và quản lý toàn bộ vòng đời nghiên cứu khoa học: thiết kế thực nghiệm, quản lý giả thuyết, tổng hợp trích dẫn và giám sát tiến độ.',
    triggers: ['research hub', 'academic workflow', 'experiment management', 'hypothesis matrix'],
    promptTemplate: 'cp -r research-hub .agents/skills/\nKích hoạt Research Hub để thiết lập quy trình theo dõi thực nghiệm khoa học.',
    details: `### Trung tâm điều phối nghiên cứu học thuật:
- Quản lý giả thuyết và ma trận kiểm chứng khoa học.
- Tự động đồng bộ với các công cụ trong \`cs-research-skills\` và \`microsoft-research\`.
- Xuất báo cáo tiến độ và biên bản đánh giá học thuật.`
  },
  {
    id: 'literature-search-arxiv',
    name: 'literature-search-arxiv',
    category: 'research',
    categories: ['research'],
    categoryLabel: 'Scientific Research',
    title: 'ArXiv Scientific Literature Search',
    description: 'Tìm kiếm bài báo khoa học, preprint và các công trình nghiên cứu trên arXiv, trích xuất tóm tắt và tải bản PDF toàn văn.',
    triggers: ['arxiv', 'paper search', 'literature review', 'research paper'],
    promptTemplate: 'Tìm kiếm các bài báo mới nhất trên arXiv về chủ đề "LLM Multi-Agent Coordination and Task Planning" trong năm 2025-2026.',
    details: `Trích xuất tác giả, ngày công bố, abstract và liên kết tải PDF chính xác.`
  },
  {
    id: 'literature-search-openalex',
    name: 'literature-search-openalex',
    category: 'research',
    categories: ['research'],
    categoryLabel: 'Scientific Research',
    title: 'OpenAlex Scholarly Database & DOI',
    description: 'Truy vấn kho dữ liệu học thuật mở OpenAlex: tìm kiếm bài báo, tác giả, tổ chức, số lượng trích dẫn, h-index và giải mã DOI.',
    triggers: ['openalex', 'doi lookup', 'citation count', 'h-index', 'scholarly search'],
    promptTemplate: 'Dùng skill literature-search-openalex để tra cứu danh sách các bài báo có trích dẫn cao nhất về Transformer Architecture.',
    details: `Cung cấp thông tin tác giả, cơ quan nghiên cứu, nguồn tài trợ và liên kết tải tài liệu Open Access.`
  },
  {
    id: 'pubmed-database',
    name: 'pubmed-database',
    category: 'research',
    categories: ['research'],
    categoryLabel: 'Scientific Research',
    title: 'PubMed Biomedical & Clinical Trials',
    description: 'Tra cứu tài liệu y sinh học, thử nghiệm lâm sàng đã công bố và liên kết chéo với các cơ sở dữ liệu NCBI (Gene, Protein, Nucleotide, PubChem).',
    triggers: ['pubmed', 'clinical trial', 'biomedical literature', 'ncbi', 'pmid'],
    promptTemplate: 'Tìm kiếm các công trình thử nghiệm lâm sàng trên PubMed về thuốc ức chế kinase thế hệ mới.',
    details: `Truy vấn trực tiếp qua NCBI E-utilities và PMC BioC APIs để lấy tóm tắt và văn bản toàn văn.`
  },
  {
    id: 'alphafold-database-fetch-and-analyze',
    name: 'alphafold-database-fetch-and-analyze',
    category: 'research',
    categories: ['research'],
    categoryLabel: 'Scientific Research',
    title: 'AlphaFold Structural Biology Analysis',
    description: 'Truy xuất và phân tích cấu trúc 3D protein dự đoán từ AlphaFold DB bằng UniProt ID, đánh giá độ tin cậy pLDDT và ranh giới vùng miền domain.',
    triggers: ['alphafold', 'protein structure', 'plddt', 'uniprot', 'structural biology'],
    promptTemplate: 'Dùng skill alphafold-database-fetch-and-analyze để phân tích độ tin cậy cấu trúc protein UniProt ID [P05067].',
    details: `Đo lường chỉ số pLDDT theo từng residue và phân tích ranh giới domain cấu trúc.`
  }
];
