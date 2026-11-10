/**
 * Skills Database for agent_setup (by Jin)
 * Curated and customized for Antigravity CLI (agy)
 * Bilingual support: Vietnamese & English
 */

export const SKILL_CATEGORIES = {
  vi: [
    { id: 'all', label: 'Tất Cả Kỹ Năng' },
    { id: 'llm-agent', label: 'LLM - Agent' },
    { id: 'coding', label: 'Coding' },
    { id: 'system', label: 'System Design' },
    { id: 'design', label: 'Design & UI/UX' },
    { id: 'ba', label: 'BA & Requirements' },
    { id: 'docs', label: 'Docs & Diagrams' },
    { id: 'research', label: 'Scientific Research' },
  ],
  en: [
    { id: 'all', label: 'All Skills' },
    { id: 'llm-agent', label: 'LLM - Agents' },
    { id: 'coding', label: 'Engineering & Code' },
    { id: 'system', label: 'System Design' },
    { id: 'design', label: 'Design & UI/UX' },
    { id: 'ba', label: 'BA & Requirements' },
    { id: 'docs', label: 'Docs & Diagrams' },
    { id: 'research', label: 'Scientific Research' },
  ]
};

export function getCategories(lang = 'vi') {
  return SKILL_CATEGORIES[lang] || SKILL_CATEGORIES.vi;
}

export const RAW_SKILLS_DATA = [
  // ===================== 1. LLM - AGENT =====================
  {
    id: 'agent-harness',
    name: 'agent-harness',
    category: 'llm-agent',
    categories: ['llm-agent', 'system'],
    triggers: ['harness', 'agent loop', 'long-running agent', 'session persist', 'agent crashes', 'lifecycle hook'],
    vi: {
      categoryLabel: 'LLM - Agent / System',
      title: 'Enterprise Multi-Turn Agent Harness',
      description: 'Khung vận hành AI Agent doanh nghiệp chạy dài hạn: quản lý ngữ cảnh qua nhiều phiên (session persistence), checkpoint an toàn, Human-in-the-loop, tự hồi phục khi gặp sự cố.',
      promptTemplate: 'Thiết lập mô hình Agent Harness cho luồng hỗ trợ tác chiến dài hạn với checkpoint lưu vết phiên làm việc và Human-in-the-loop.',
      details: `### Mục đích & Khả năng vận hành:
Khung điều phối chuyên sâu cho hệ thống AI Agent chạy xuyên suốt hàng trăm lượt (turns) mà không bị mất ngữ cảnh hay crash.

#### Tính năng cốt lõi:
1. **Quản lý Context & Trí nhớ**: Lưu trạng thái phiên làm việc (Session Persistence) và tự nén context khi gần ngưỡng token.
2. **Safety Guardrails**: Kiểm soát hành động không thể đảo ngược, bắt buộc phê duyệt với các thao tác rủi ro cao.
3. **Tool Registry & Lifecycle Hooks**: Đăng ký công cụ linh hoạt, hook vào trước/sau mỗi lượt gọi tool để ghi log kiểm toán (audit trail).`
    },
    en: {
      categoryLabel: 'LLM - Agent / System',
      title: 'Enterprise Multi-Turn Agent Harness',
      description: 'Production framework for long-running AI Agents: multi-turn session persistence, safety checkpoints, Human-in-the-loop governance, and crash resilience.',
      promptTemplate: 'Configure an enterprise Agent Harness for long-running workflows featuring session persistence checkpoints and Human-in-the-loop approval.',
      details: `### Purpose & Operational Capabilities:
Specialized orchestration framework designed for AI Agents to execute across hundreds of turns without losing context or crashing.

#### Core Features:
1. **Context & Memory Management**: Session persistence and automatic context compression near token thresholds.
2. **Safety Guardrails**: Strict execution control over irreversible actions, requiring human approval for high-risk operations.
3. **Tool Registry & Lifecycle Hooks**: Dynamic tool registration with pre/post hooks for audit trailing.`
    }
  },
  {
    id: 'rag-architect',
    name: 'rag-architect',
    category: 'llm-agent',
    categories: ['llm-agent', 'system'],
    triggers: ['rag', 'vector database', 'hybrid search', 'reranking', 'embeddings', 'semantic search'],
    vi: {
      categoryLabel: 'LLM - Agent / System',
      title: 'Enterprise RAG Architecture',
      description: 'Thiết kế hệ thống RAG đa tầng, tối ưu Vector Database (Pinecone, Qdrant, Chroma), Hybrid Search (BM25 + Dense Vectors), Cross-Encoder Re-ranking và Context Augmentation.',
      promptTemplate: 'Dùng skill rag-architect để thiết kế kiến trúc hệ thống RAG phục vụ tra cứu hàng triệu tài liệu pháp lý với độ chính xác cao bằng Hybrid Search.',
      details: `### Kiến trúc RAG chuẩn doanh nghiệp:
- **Chiến lược Chunking**: Semantic Chunking, Recursive Text Splitting theo cấu trúc tài liệu.
- **Hybrid Retrieval**: Kết hợp từ khóa chính xác (BM25) và ngữ nghĩa vector đa chiều.
- **Tối ưu suy luận**: Re-ranking bằng mô hình Cross-Encoder để lọc nhiễu trước khi đưa vào Context Window của LLM.`
    },
    en: {
      categoryLabel: 'LLM - Agent / System',
      title: 'Enterprise RAG Architecture',
      description: 'Multi-stage enterprise RAG system design: Vector DB optimization (Pinecone, Qdrant, Chroma), Hybrid Search (BM25 + Dense Vectors), Cross-Encoder Re-ranking, and Context Augmentation.',
      promptTemplate: 'Use the rag-architect skill to design a high-precision RAG architecture for searching millions of legal documents using Hybrid Search.',
      details: `### Enterprise RAG Architecture:
- **Chunking Strategy**: Semantic Chunking and Recursive Text Splitting tailored to document hierarchies.
- **Hybrid Retrieval**: Combines exact lexical matching (BM25) with dense semantic vector embeddings.
- **Inference Optimization**: Cross-Encoder Re-ranking to filter out noise before passing context to the LLM context window.`
    }
  },
  {
    id: 'langchain-skills',
    name: 'langchain-skills',
    category: 'llm-agent',
    categories: ['llm-agent', 'coding'],
    triggers: ['langchain', 'langgraph', 'state graph', 'agentic workflow', 'deep agents'],
    vi: {
      categoryLabel: 'LLM - Agent / Coding',
      title: 'LangChain & LangGraph Orchestration',
      description: 'Xây dựng luồng tác chiến Agentic AI đa bước với LangChain v0.3 và LangGraph, quản lý State Graph, chu trình có điều kiện (Conditional Edges) và Human-in-the-loop.',
      promptTemplate: 'Thiết kế một State Graph bằng LangGraph để điều phối quy trình phân tích dữ liệu, tự động sửa lỗi và gọi tool ngoài.',
      details: `### Hướng dẫn ứng dụng:
- Xây dựng sơ đồ trạng thái \`StateGraph\` với các node xử lý chuyên biệt.
- Quản lý bộ nhớ phiên làm việc bằng Checkpointer và SQLite/Postgres.
- Điều phối nhiều sub-agent cộng tác song song.`
    },
    en: {
      categoryLabel: 'LLM - Agent / Coding',
      title: 'LangChain & LangGraph Orchestration',
      description: 'Multi-step Agentic AI workflows with LangChain v0.3 and LangGraph: State Graph management, conditional edges, parallel sub-agents, and Human-in-the-loop approval.',
      promptTemplate: 'Design a LangGraph StateGraph to orchestrate an automated data analysis pipeline with error self-correction and external tool invocation.',
      details: `### Implementation Guide:
- Construct modular \`StateGraph\` state machines with specialized operational nodes.
- Manage persistent session memory with checkpointers backed by SQLite or PostgreSQL.
- Coordinate multiple specialized sub-agents executing tasks in parallel.`
    }
  },
  {
    id: 'prompt-engineer',
    name: 'prompt-engineer',
    category: 'llm-agent',
    categories: ['llm-agent'],
    triggers: ['prompt', 'prompt engineering', 'chain-of-thought', 'few-shot', 'structured outputs'],
    vi: {
      categoryLabel: 'LLM - Agent',
      title: 'Advanced Prompt Engineering & Evals',
      description: 'Thiết kế cấu trúc prompt chuyên sâu cho LLMs: Chain-of-Thought (CoT), Few-Shot Learning, Structured Outputs (Pydantic / JSON Schema) và framework đánh giá độ chính xác.',
      promptTemplate: 'Tối ưu hóa hệ thống Prompt này bằng kỹ thuật Chain-of-Thought và ràng buộc Structured Output theo JSON Schema.',
      details: `### Kỹ thuật áp dụng:
- Cấu trúc prompt theo vai trò, mục tiêu, ràng buộc biên và ví dụ mẫu.
- Ngăn ngừa hallucination bằng các chỉ dẫn ground-truth và negative constraints.
- Tự động hóa đánh giá định lượng (Evals) về độ tin cậy của mô hình.`
    },
    en: {
      categoryLabel: 'LLM - Agent',
      title: 'Advanced Prompt Engineering & Evals',
      description: 'Systematic prompt architecture for LLMs: Chain-of-Thought (CoT), Few-Shot Learning, Structured Outputs (Pydantic / JSON Schema), and quantitative evaluation frameworks.',
      promptTemplate: 'Optimize this prompt architecture using Chain-of-Thought reasoning and strict JSON Schema Structured Output constraints.',
      details: `### Applied Techniques:
- Structured prompt engineering: persona, objective, boundary constraints, and validated few-shot exemplars.
- Hallucination mitigation using ground-truth citations and strict negative constraints.
- Automated quantitative evaluation pipelines (Evals) to measure reliability and consistency.`
    }
  },

  // ===================== 2. CODING =====================
  {
    id: 'clean-code',
    name: 'clean-code',
    category: 'coding',
    categories: ['coding'],
    triggers: ['clean code', 'refactor', 'boy scout rule', 'code review', 'code smell'],
    vi: {
      categoryLabel: 'Coding',
      title: '66 Canonical Clean Code Rules & Boy Scout',
      description: 'Áp dụng 66 quy tắc Clean Code kinh điển của Robert C. Martin, quy tắc Boy Scout, quy chuẩn đặt tên, kiến trúc Clean Architecture và phát hiện code smells trên 21 ngôn ngữ.',
      promptTemplate: 'Review và tái cấu trúc (refactor) đoạn code này theo nghiêm ngặt 66 quy tắc Clean Code và nguyên lý Boy Scout Rule.',
      details: `### Kỷ luật Clean Code:
- **Boy Scout Rule**: Luôn để lại codebase sạch sẽ hơn lúc bạn tiếp nhận.
- **Hàm đơn nhiệm (SRP)**: Mỗi hàm chỉ làm duy nhất một việc và làm thật tốt.
- **Surgical Diff**: Chỉ sửa đúng những dòng liên quan đến yêu cầu, không reformat code lân cận.`
    },
    en: {
      categoryLabel: 'Engineering & Code',
      title: '66 Canonical Clean Code Rules & Boy Scout',
      description: "Enforce Robert C. Martin's 66 Clean Code rules, the Boy Scout Rule, naming conventions, Clean Architecture, and static code smell detection across 21 languages.",
      promptTemplate: 'Review and refactor this codebase strictly according to the 66 Clean Code rules and the Boy Scout Rule.',
      details: `### Clean Code Invariants:
- **Boy Scout Rule**: Always leave the codebase cleaner than you found it.
- **Single Responsibility Principle (SRP)**: Every function does one thing and does it well.
- **Surgical Diffs**: Modify only lines directly tied to the request without reformatting unrelated regions.`
    }
  },
  {
    id: 'python-fastapi-code',
    name: 'python-fastapi-code',
    category: 'coding',
    categories: ['coding'],
    triggers: ['fastapi', 'pydantic v2', 'async sqlalchemy', 'pytest-asyncio', 'jwt'],
    vi: {
      categoryLabel: 'Coding',
      title: 'Senior Python & FastAPI Engineer',
      description: 'Kỹ sư Senior Python/FastAPI: SOLID, Pydantic V2, async SQLAlchemy, xác thực JWT/OAuth2, Dependency Injection, async testing (pytest-asyncio) và WebSockets.',
      promptTemplate: 'Viết router và service quản trị người dùng bằng FastAPI, Pydantic V2, SQLAlchemy 2.0 Async Session và kiểm thử với pytest-asyncio.',
      details: `### Chuẩn cấu trúc phân tầng:
1. **Routers**: Nhận request, xác thực schema bằng Pydantic V2.
2. **Services**: Xử lý toàn bộ logic nghiệp vụ (Business Rules).
3. **Repositories**: Thao tác dữ liệu qua Async SQLAlchemy 2.0.
4. **Schemas**: Định nghĩa DTO request/response rõ ràng.`
    },
    en: {
      categoryLabel: 'Engineering & Code',
      title: 'Senior Python & FastAPI Engineer',
      description: 'Senior Python/FastAPI engineering: SOLID principles, Pydantic V2, async SQLAlchemy 2.0, JWT/OAuth2 authentication, Dependency Injection, async testing (pytest-asyncio), and WebSockets.',
      promptTemplate: 'Build a user management router and service using FastAPI, Pydantic V2, SQLAlchemy 2.0 Async Session, and async unit tests with pytest-asyncio.',
      details: `### Layered Architecture Standards:
1. **Routers**: Ingest HTTP requests, validate input schemas with Pydantic V2.
2. **Services**: Encapsulate all domain business rules.
3. **Repositories**: Isolate asynchronous database operations via SQLAlchemy 2.0.
4. **Schemas**: Define strict DTO request/response schemas.`
    }
  },
  {
    id: 'fastapi-backend-scaffold',
    name: 'fastapi-backend-scaffold',
    category: 'coding',
    categories: ['coding'],
    triggers: ['scaffold backend', 'fastapi project', 'backend template', 'uvicorn'],
    vi: {
      categoryLabel: 'Coding',
      title: 'FastAPI Microservice Scaffolding',
      description: 'Bộ khung chuẩn mực cho microservice FastAPI: phân chia controller/service/repo, virtual environment cô lập tại chỗ (.venv), pyproject.toml và middleware cross-cutting.',
      promptTemplate: 'Scaffold một backend FastAPI mới hoàn chỉnh theo chuẩn kiến trúc backend/ và môi trường cô lập .venv.',
      details: `### Quy chuẩn khởi tạo:
- Thư mục gốc luôn đặt là \`backend/\`.
- Môi trường ảo bắt buộc tại \`backend/.venv\`.
- Quản lý gói bằng \`pyproject.toml\` (uv toolchain).`
    },
    en: {
      categoryLabel: 'Engineering & Code',
      title: 'FastAPI Microservice Scaffolding',
      description: 'Production microservice scaffolding for FastAPI: strict controller/service/repo separation, isolated local virtual environment (.venv), pyproject.toml, and cross-cutting middleware.',
      promptTemplate: 'Scaffold a complete production-grade FastAPI microservice following the backend/ directory layout and isolated .venv standard.',
      details: `### Scaffolding Specifications:
- Root directory is strictly designated as \`backend/\`.
- Isolated virtual environment mandatory at \`backend/.venv\`.
- Dependency management via modern \`pyproject.toml\` (uv toolchain).`
    }
  },
  {
    id: 'nvidia-cuda',
    name: 'nvidia-cuda',
    category: 'coding',
    categories: ['coding'],
    triggers: ['cuda', 'gpu optimization', 'kernel optimization', 'cublas', 'cudnn'],
    vi: {
      categoryLabel: 'Coding',
      title: 'NVIDIA CUDA GPU Programming',
      description: 'Lập trình tăng tốc phần cứng GPU với CUDA C/C++, cuBLAS, cuDNN, NCCL, tối ưu hóa bộ nhớ Shared Memory, parallel thread execution và profiling qua Nsight.',
      promptTemplate: 'Viết một CUDA kernel tối ưu phép tính ma trận lớn sử dụng Shared Memory và vectorization.',
      details: `### Nguồn tri thức trực tiếp:
Tích hợp MCP Server chính thức từ NVIDIA, đảm bảo tra cứu API docs mới nhất và tính toán Occupancy GPU chuẩn xác.`
    },
    en: {
      categoryLabel: 'Engineering & Code',
      title: 'NVIDIA CUDA GPU Programming',
      description: 'Hardware-accelerated GPU programming with CUDA C/C++, cuBLAS, cuDNN, NCCL, Shared Memory optimization, parallel warp execution, and profiling with NVIDIA Nsight.',
      promptTemplate: 'Write an optimized CUDA kernel for large-scale matrix multiplication utilizing Shared Memory tiling and vectorized loads.',
      details: `### Authoritative Knowledge Base:
Powered by NVIDIA's live engineer-curated MCP documentation server, ensuring real-time API accuracy and precise GPU occupancy calculation.`
    }
  },
  {
    id: 'stm32-embedded-workflow',
    name: 'stm32-embedded-workflow',
    category: 'coding',
    categories: ['coding'],
    triggers: ['stm32', 'cubemx', 'embedded', 'hal driver', 'gpio/uart/spi', 'timer math'],
    vi: {
      categoryLabel: 'Coding',
      title: 'Senior Embedded STM32 Workflow',
      description: 'Kỹ sư nhúng STM32 chuyên sâu: phân tích datasheet, cấu hình chân CubeMX, tính toán timer/clock, viết mã HAL drivers an toàn thanh ghi và debug bring-up.',
      promptTemplate: 'Phân tích datasheet STM32F4 và tính toán thanh ghi Timer để phát xung PWM 20kHz điều khiển động cơ.',
      details: `### Quy trình kỹ thuật nhúng:
1. Tra cứu sơ đồ chân (Pin Mapping) đối chiếu PDF ST Microelectronics.
2. Lập danh sách kiểm tra cấu hình STM32CubeMX.
3. Xuất mã nguồn tham khảo \`main.c\` tuân thủ chuẩn HAL.`
    },
    en: {
      categoryLabel: 'Engineering & Code',
      title: 'Senior Embedded STM32 Workflow',
      description: 'Senior STM32 embedded engineering: datasheet verification, STM32CubeMX pin mapping, clock/timer math, register-level HAL drivers, and board bring-up/debug planning.',
      promptTemplate: 'Analyze the STM32F4 datasheet and calculate Timer registers to generate a 20kHz PWM signal for precision motor control.',
      details: `### Embedded Engineering Workflow:
1. Verify hardware pin multiplexing directly against ST Microelectronics datasheets.
2. Generate step-by-step STM32CubeMX configuration checklists.
3. Produce register-safe \`main.c\` reference code adhering to strict HAL practices.`
    }
  },

  // ===================== 3. SYSTEM DESIGN =====================
  {
    id: 'system-design',
    name: 'system-design',
    category: 'system',
    categories: ['system'],
    triggers: ['system design', 'scalability', 'distributed architecture', 'caching', 'rate limiter', 'sharding'],
    vi: {
      categoryLabel: 'System Design',
      title: 'Distributed System Architecture',
      description: 'Thiết kế kiến trúc phân tán cấp doanh nghiệp: High Availability, Caching (Redis), Database Sharding, Message Queue (Kafka), CAP Theorem, tính toán dung lượng (TPS/QPS).',
      promptTemplate: 'Hãy thiết kế kiến trúc hệ thống URL Shortener có khả năng phục vụ 100,000 QPS với độ trễ P99 < 15ms.',
      details: `### Nội dung thẩm định:
- Phân tích SLA, độ khả dụng 99.99% và ước lượng phần cứng.
- Mô hình nhất quán dữ liệu (Strong vs Eventual Consistency).
- Thiết kế luồng xử lý bất đồng bộ qua hàng đợi thông điệp.`
    },
    en: {
      categoryLabel: 'System Design',
      title: 'Distributed System Architecture',
      description: 'Enterprise distributed system architecture: High Availability (99.99%), Redis caching strategies, Database sharding, Kafka message queues, CAP Theorem trade-offs, and capacity planning (TPS/QPS).',
      promptTemplate: 'Design a high-scale distributed URL Shortener capable of serving 100,000 QPS with P99 latency under 15ms.',
      details: `### Architectural Review Scope:
- SLA calculation, 99.99% availability targets, and infrastructure sizing.
- Consistency models (Strong vs. Eventual Consistency).
- Asynchronous decoupling via distributed message queues.`
    }
  },
  {
    id: 'api-design-patterns',
    name: 'api-design-patterns',
    category: 'system',
    categories: ['system'],
    triggers: ['api design', 'idempotency', 'pagination', 'restful standards', 'cursor pagination'],
    vi: {
      categoryLabel: 'System Design',
      title: 'Enterprise API Design Patterns',
      description: 'Các mẫu thiết kế API chuẩn mực (RESTful, GraphQL, gRPC, phân trang Cursor-based, bảo mật Idempotency và Rate Limiting).',
      promptTemplate: 'Áp dụng skill api-design-patterns để thiết kế API thanh toán an toàn với Idempotency-Key và Cursor Pagination.',
      details: `Chuẩn hóa mã lỗi RFC 7807 (Problem Details for HTTP APIs) và hợp đồng dữ liệu chuẩn mực giữa Frontend và Backend.`
    },
    en: {
      categoryLabel: 'System Design',
      title: 'Enterprise API Design Patterns',
      description: 'Essential enterprise API design patterns: RESTful standards, Cursor-based pagination, Idempotency-Key security, RFC 7807 error responses, and Rate Limiting.',
      promptTemplate: 'Use the api-design-patterns skill to design an idempotent payment API endpoint featuring Idempotency-Key handling and Cursor-based pagination.',
      details: `Standardized error contracts using RFC 7807 (Problem Details for HTTP APIs) and robust frontend-backend data agreements.`
    }
  },

  // ===================== 4. DESIGN & UI/UX (WITH 3D) =====================
  {
    id: '3dviz-pro-max',
    name: '3dviz-pro-max',
    category: 'design',
    categories: ['design'],
    triggers: ['3d', 'three.js', 'webgl', 'spatial scene', 'diorama', '3d visualization', 'gltf'],
    vi: {
      categoryLabel: 'Design & UI/UX',
      title: '3D WebGL & Three.js Scene Design',
      description: 'Thiết kế không gian và mô hình 3D tương tác trên WebGL/Three.js: 223 công thức, 37 phong cách 3D, hệ thống chiếu sáng studio, vật liệu PBR và diorama khoa học.',
      promptTemplate: 'Dùng skill 3dviz-pro-max để tạo một mô hình mạng lưới nơ-ron 3D tương tác bằng Three.js trong file HTML.',
      details: `### Kho tri thức 3D tích hợp:
- **223 công thức & 37 style profile**: Cyberpunk, Sci-Fi Studio, Minimalist Clay, Holographic Neon...
- **22 Lighting Rigs**: 3-point studio lighting, HDR skybox, ambient occlusion.
- **Tối ưu GPU**: Đảm bảo 60 FPS, draw call batching, LOD (Level of Detail).`
    },
    en: {
      categoryLabel: 'Design & UI/UX',
      title: '3D WebGL & Three.js Scene Design',
      description: 'Interactive 3D spatial scenes and WebGL/Three.js engineering: 223 recipes, 37 visual styles, studio lighting rigs, PBR materials, and scientific dioramas.',
      promptTemplate: 'Use the 3dviz-pro-max skill to create an interactive 3D neural network visualization using Three.js inside a single standalone HTML file.',
      details: `### Integrated 3D Knowledge Base:
- **223 recipes & 37 visual profiles**: Cyberpunk, Sci-Fi Studio, Minimalist Clay, Holographic Neon, and more.
- **22 Lighting Rigs**: 3-point studio lighting, HDR skyboxes, and ambient occlusion.
- **GPU Optimization**: 60 FPS performance guarantees, draw call batching, and LOD management.`
    }
  },
  {
    id: 'ui-ux-pro-max',
    name: 'ui-ux-pro-max',
    category: 'design',
    categories: ['design'],
    triggers: ['ui', 'ux', 'redesign', 'style', 'palette', 'dark mode', 'component'],
    vi: {
      categoryLabel: 'Design & UI/UX',
      title: 'UI/UX Design Intelligence',
      description: 'Trí tuệ thiết kế giao diện toàn diện: 50 phong cách thị giác, 192 bảng màu chuyên dụng, 74 bộ ghép font, 119 quy tắc UX, hỗ trợ 22 stack frontend.',
      promptTemplate: 'Dùng skill ui-ux-pro-max để tư vấn phong cách thiết kế, bảng màu OLED Dark/Emerald và bố cục Dashboard quản trị.',
      details: `### Thư viện tri thức có sẵn:
- 50 phong cách giao diện (Minimalist, Glassmorphism, Brutalism, Cybernetic...).
- Bộ quy tắc khoảng cách, phân cấp kiểu chữ, và độ tương phản màu sắc chuẩn WCAG 2.2 AA.
- Code mẫu responsive cho React, Vue, Svelte, Tailwind CSS, và Vanilla Web.`
    },
    en: {
      categoryLabel: 'Design & UI/UX',
      title: 'UI/UX Design Intelligence',
      description: 'Comprehensive UI/UX design intelligence: 50 visual styles, 192 product color palettes, 74 font pairings, 119 UX guidelines, supporting 22 frontend stacks.',
      promptTemplate: 'Use ui-ux-pro-max to define the visual style, an OLED Dark/Emerald palette, and an accessible layout for an executive admin dashboard.',
      details: `### Design Knowledge Catalog:
- 50 visual interface styles (Minimalist, Glassmorphism, Brutalism, Cybernetic...).
- Spacing scales, typographic hierarchy, and WCAG 2.2 AA contrast compliance.
- Responsive implementation guidelines for React, Vue, Svelte, Tailwind CSS, and Vanilla Web.`
    }
  },
  {
    id: 'ui-styling',
    name: 'ui-styling',
    category: 'design',
    categories: ['design'],
    triggers: ['shadcn', 'tailwind', 'ui styling', 'radix', 'accessible modal'],
    vi: {
      categoryLabel: 'Design & UI/UX',
      title: 'Tailwind CSS & shadcn/ui Expert',
      description: 'Triển khai giao diện chuẩn mực bằng Tailwind CSS, shadcn/ui (Radix UI) và Canvas visual patterns, đảm bảo 100% tiếp cận accessible.',
      promptTemplate: 'Dùng skill ui-styling để dựng một form xác thực đăng nhập có validate dữ liệu bằng Tailwind CSS và Radix UI primitives.',
      details: `Xây dựng component accessible (Dialog, Dropdown Menu, Data Table), hỗ trợ chế độ Dark Mode OLED tự nhiên qua CSS Custom Properties.`
    },
    en: {
      categoryLabel: 'Design & UI/UX',
      title: 'Tailwind CSS & shadcn/ui Expert',
      description: 'Accessible, modern UI implementation using Tailwind CSS, shadcn/ui (Radix UI primitives), and visual canvas patterns with 100% WCAG accessibility.',
      promptTemplate: 'Use ui-styling to build an accessible authentication modal with full client validation using Tailwind CSS and Radix UI primitives.',
      details: `Accessible component patterns (Dialog, Dropdown Menu, Data Table) with seamless native OLED Dark Mode via CSS Custom Properties.`
    }
  },
  {
    id: 'design-system',
    name: 'design-system',
    category: 'design',
    categories: ['design'],
    triggers: ['design system', 'tokens', 'component specs', 'css variables'],
    vi: {
      categoryLabel: 'Design & UI/UX',
      title: 'Token Architecture & Design System',
      description: 'Xây dựng kiến trúc Token 3 tầng (Primitive -> Semantic -> Component), CSS Custom Properties, quy chuẩn khoảng cách và typography scale.',
      promptTemplate: 'Dùng skill design-system để xuất ra bộ Design Tokens CSS chuẩn 3 tầng cho giao diện nền tảng công nghệ.',
      details: `Đồng bộ triệt để giữa file thiết kế Figma và mã nguồn CSS, hạn chế tối đa việc hardcode mã màu hex.`
    },
    en: {
      categoryLabel: 'Design & UI/UX',
      title: 'Token Architecture & Design System',
      description: '3-layer Token Architecture (Primitive -> Semantic -> Component), CSS Custom Properties, spacing/typography scales, and design-to-code synchronization.',
      promptTemplate: 'Use the design-system skill to export a complete 3-layer CSS Design Token architecture for an enterprise tech platform.',
      details: `Strict synchronization between Figma tokens and CSS custom properties, eliminating hardcoded hex color values.`
    }
  },
  {
    id: 'design-artifact',
    name: 'design-artifact',
    category: 'design',
    categories: ['design'],
    triggers: ['html artifact', 'landing page', 'report', 'demo html'],
    vi: {
      categoryLabel: 'Design & UI/UX',
      title: 'HTML Artifacts & Creative Direction',
      description: 'Định hướng thẩm mỹ và tạo các file HTML độc lập (Single-file HTML): báo cáo, landing page, demo không mang cảm giác AI generic.',
      promptTemplate: 'Dùng skill design-artifact để tạo một trang landing page giới thiệu tính năng mới dưới dạng một file HTML tự chứa (single-file).',
      details: `Toàn bộ CSS, SVG và JS được nhúng gọn trong 1 file HTML duy nhất, không phụ thuộc bundler hay CDN ngoài.`
    },
    en: {
      categoryLabel: 'Design & UI/UX',
      title: 'HTML Artifacts & Creative Direction',
      description: 'Creative art direction for standalone Single-File HTML deliverables: reports, landing pages, interactive decks, and demos that avoid generic AI aesthetics.',
      promptTemplate: 'Use design-artifact to generate a self-contained single-file HTML landing page showcasing our new developer feature.',
      details: `Zero bundler dependencies: all CSS, SVG graphics, and JavaScript are bundled self-contained into a single portable HTML document.`
    }
  },
  {
    id: 'html',
    name: 'html',
    category: 'design',
    categories: ['design'],
    triggers: ['html deliverable', 'single file html', 'self-contained'],
    vi: {
      categoryLabel: 'Design & UI/UX',
      title: 'Self-Contained Single-File Deliverable',
      description: 'Bộ định tuyến tạo hoặc tái thiết kế các sản phẩm HTML đóng gói trọn vẹn (single-file): tài liệu kỹ thuật, trang giới thiệu, dashboard báo cáo.',
      promptTemplate: 'Dùng skill html để xuất bản tài liệu báo cáo kỹ thuật thành file HTML độc lập hoàn chỉnh.',
      details: `Tối ưu hóa khả năng xem ngoại tuyến (offline-ready), nhúng font an toàn và đảm bảo hiển thị hoàn hảo trên mọi kích thước màn hình.`
    },
    en: {
      categoryLabel: 'Design & UI/UX',
      title: 'Self-Contained Single-File Deliverable',
      description: 'Primary router for creating or redesigning fully packaged single-file HTML deliverables: technical documentation, showcase pages, and executive dashboards.',
      promptTemplate: 'Use the html skill to package this technical report into an independent, self-contained single-file HTML deliverable.',
      details: `Engineered for offline reliability, safe system font fallbacks, and flawless rendering across all viewport breakpoints.`
    }
  },
  {
    id: 'banner-design',
    name: 'banner-design',
    category: 'design',
    categories: ['design'],
    triggers: ['banner', 'social banner', 'hero asset', 'ad creative'],
    vi: {
      categoryLabel: 'Design & UI/UX',
      title: 'Marketing & Hero Banner Design',
      description: 'Thiết kế banner mạng xã hội, ảnh quảng cáo, hero banner trang web với phong cách typography ấn tượng, gradient và bố cục 3D.',
      promptTemplate: 'Dùng skill banner-design để thiết kế banner kích thước 1200x630 cho LinkedIn chủ đề Antigravity Agent Setup.',
      details: `Định hướng bố cục và xuất file hình ảnh hoặc vector chất lượng cao phục vụ truyền thông sản phẩm.`
    },
    en: {
      categoryLabel: 'Design & UI/UX',
      title: 'Marketing & Hero Banner Design',
      description: 'High-impact banner design for social media, display ads, and website hero sections with bold typography, custom gradients, and 3D compositions.',
      promptTemplate: 'Use banner-design to create a 1200x630 LinkedIn hero banner announcing the Antigravity Agent Setup release.',
      details: `Creative composition guidance and export specifications for digital marketing and developer relations campaigns.`
    }
  },
  {
    id: 'brand',
    name: 'brand',
    category: 'design',
    categories: ['design'],
    triggers: ['brand voice', 'tone of voice', 'brand guidelines', 'messaging'],
    vi: {
      categoryLabel: 'Design & UI/UX',
      title: 'Brand Voice & Consistency',
      description: 'Định hình giọng văn thương hiệu (Brand Voice), hệ thống thông điệp, kiểm tra độ nhất quán của nội dung và tài sản thương hiệu.',
      promptTemplate: 'Dùng skill brand để xây dựng hướng dẫn giọng điệu thương hiệu (Voice & Tone) cho sản phẩm công nghệ AI.',
      details: `Thiết lập phong cách giao tiếp tự tin, chuẩn xác, khiêm tốn và tập trung vào kỹ thuật cho sản phẩm.`
    },
    en: {
      categoryLabel: 'Design & UI/UX',
      title: 'Brand Voice & Consistency',
      description: 'Brand voice guidelines, messaging frameworks, tone-of-voice governance, and visual asset consistency audits for engineering products.',
      promptTemplate: 'Use the brand skill to establish a Voice & Tone messaging framework for our AI developer tooling product.',
      details: `Defines a clear, confident, humble, and technically authoritative tone of voice across all developer-facing touchpoints.`
    }
  },

  // ===================== 5. BA & REQUIREMENTS =====================
  {
    id: 'user-story-ac-writer',
    name: 'user-story-ac-writer',
    category: 'ba',
    categories: ['ba'],
    triggers: ['user story', 'acceptance criteria', 'gherkin', 'invest', 'backlog'],
    vi: {
      categoryLabel: 'BA & Requirements',
      title: 'User Story & Gherkin AC Writer',
      description: 'Bóc tách User Story chuẩn INVEST và Acceptance Criteria định dạng Given-When-Then (Gherkin), bóc tách kịch bản lỗi, thiết lập Architecture Guardrails.',
      promptTemplate: 'Hãy dùng skill user-story-ac-writer để phân tích và viết bộ User Story chi tiết kèm Acceptance Criteria chuẩn Gherkin cho tính năng [TÊN_TÍNH_NĂNG].',
      details: `### Quy trình xử lý BA:
1. Bóc tách luồng nghiệp vụ từ Sequence hoặc Activity Diagram.
2. Kiểm tra độ bao phủ nhánh lỗi (Fact-list Coverage Check).
3. Viết kịch bản Given-When-Then chuẩn mực.
4. Thiết lập Architecture Guardrails để Agent lập trình không phá vỡ bất biến của hệ thống.`
    },
    en: {
      categoryLabel: 'BA & Requirements',
      title: 'User Story & Gherkin AC Writer',
      description: 'INVEST-standard User Story decomposition, Given-When-Then (Gherkin) Acceptance Criteria, edge-case analysis, and Architecture Guardrails for AI agents.',
      promptTemplate: 'Use user-story-ac-writer to decompose and write detailed INVEST User Stories and Gherkin Acceptance Criteria for [FEATURE_NAME].',
      details: `### Business Analysis Protocol:
1. Deconstruct business workflows from Sequence or Activity Diagrams.
2. Fact-list coverage checks to capture edge cases and failure paths.
3. Rigorous Given-When-Then Gherkin specifications.
4. Establish Architecture Guardrails to prevent AI coding agents from violating invariants.`
    }
  },
  {
    id: 'product-requirements',
    name: 'product-requirements',
    category: 'ba',
    categories: ['ba'],
    triggers: ['prd', 'requirements', 'scope', 'business analysis', 'oq'],
    vi: {
      categoryLabel: 'BA & Requirements',
      title: 'Interactive BA & PRD Generator',
      description: 'Phân tích yêu cầu cấp độ Senior IT-BA & PO, lập bảng Open Questions (OQ), thiết kế Scope Diagram và sinh PRD tích hợp chuẩn 3 tầng tài liệu.',
      promptTemplate: 'Kích hoạt skill product-requirements để lập bản đặc tả yêu cầu PRD và đặt các câu hỏi mở (Open Questions) làm rõ phạm vi dự án [TÊN_DỰ_ÁN].',
      details: `### Tính năng cốt lõi:
- Phỏng vấn làm rõ yêu cầu với bảng Open Questions (OQ) có đánh số.
- Vẽ Scope Diagram trực quan hóa ranh giới trong/ngoài phạm vi (In-scope vs Out-of-scope).
- Xuất tài liệu PRD trực tiếp vào đúng tầng nghiệp vụ: \`docs/business/prd.md\`.`
    },
    en: {
      categoryLabel: 'BA & Requirements',
      title: 'Interactive BA & PRD Generator',
      description: 'Senior IT-BA & PO requirements engineering: numbered Open Questions (OQ) register, Scope Boundary Diagrams, and 3-layer architecture PRD generation.',
      promptTemplate: 'Activate product-requirements to conduct an interactive requirements discovery interview and produce an enterprise PRD for [PROJECT_NAME].',
      details: `### Core Capabilities:
- Interactive discovery interviews using numbered Open Questions (OQ).
- Visual Scope Diagrams clearly defining In-Scope vs. Out-of-Scope boundaries.
- Direct output into the 3-layer documentation hierarchy at \`docs/business/prd.md\`.`
    }
  },

  // ===================== 6. DOCS & DIAGRAMS =====================
  {
    id: 'documentation',
    name: 'documentation',
    category: 'docs',
    categories: ['docs'],
    triggers: ['doc structure', 'architecture doc', 'adr', 'documentation system'],
    vi: {
      categoryLabel: 'Docs & Diagrams',
      title: '3-Layer Documentation Architecture',
      description: 'Hệ thống tài liệu 3 tầng (Business / Architecture / Implementation), Single Source of Truth, thiết lập Architecture Guardrails chống hallucination.',
      promptTemplate: 'Khởi tạo cấu trúc tài liệu 3 tầng (Business, Architecture, Implementation) cho dự án theo chuẩn documentation skill.',
      details: `### Cấu trúc 3 tầng:
1. \`docs/business/\`: PRD, BRD, User Stories, Roadmap.
2. \`docs/architecture/\`: C4 Architecture, Tech Stack, ADR, Data Model.
3. \`docs/implementation/\`: Sprint tasks, API contracts, changelogs.`
    },
    en: {
      categoryLabel: 'Docs & Diagrams',
      title: '3-Layer Documentation Architecture',
      description: '3-Layer Documentation Architecture (Business / Architecture / Implementation), Single Source of Truth governance, and AI agent hallucination guardrails.',
      promptTemplate: 'Initialize the 3-Layer Documentation Architecture (Business, Architecture, Implementation) for this repository according to the documentation skill.',
      details: `### 3-Layer Architecture:
1. \`docs/business/\`: PRD, BRD, User Stories, Strategic Roadmaps.
2. \`docs/architecture/\`: C4 Models, Tech Stack, ADRs, Data Models.
3. \`docs/implementation/\`: Sprint tasks, API contracts, changelogs.`
    }
  },
  {
    id: 'diagram-design',
    name: 'diagram-design',
    category: 'docs',
    categories: ['docs'],
    triggers: ['architecture diagram', 'sequence diagram', 'flowchart', 'c4 model', 'erd', 'drawio'],
    vi: {
      categoryLabel: 'Docs & Diagrams',
      title: 'Enterprise Architecture Diagrams',
      description: 'Vẽ sơ đồ kiến trúc chuẩn doanh nghiệp: Flowchart, Sequence, State Machine, C4 Model, ERD, Network Topology (hỗ trợ HTML/SVG, .drawio, .excalidraw).',
      promptTemplate: 'Dùng skill diagram-design để vẽ sơ đồ Sequence Diagram mô tả luồng xác thực OAuth2 / JWT bằng HTML/SVG sắc nét.',
      details: `Xuất file vector SVG nét căng hoặc file import trực tiếp vào draw.io / Excalidraw.`
    },
    en: {
      categoryLabel: 'Docs & Diagrams',
      title: 'Enterprise Architecture Diagrams',
      description: 'Enterprise architecture diagrams: Flowcharts, Sequence, State Machine, C4 Model, ERD, and Network Topologies (HTML/SVG, .drawio, .excalidraw).',
      promptTemplate: 'Use diagram-design to generate a crisp SVG/HTML Sequence Diagram illustrating the OAuth2 / JWT authentication handshake.',
      details: `Outputs pixel-perfect vector SVGs or native files ready for direct import into draw.io and Excalidraw.`
    }
  },
  {
    id: 'html-diagram',
    name: 'html-diagram',
    category: 'docs',
    categories: ['docs'],
    triggers: ['html-diagram', 'interactive diagram', 'topology map'],
    vi: {
      categoryLabel: 'Docs & Diagrams',
      title: 'Interactive HTML Diagrams',
      description: 'Tạo sơ đồ HTML tương tác độc lập (interactive single-file HTML diagram) hỗ trợ zoom, lọc nhánh và khám phá trạng thái.',
      promptTemplate: 'Tạo sơ đồ tương tác giải thích luồng hoạt động của hệ thống Agent bằng html-diagram.',
      details: `Cho phép click vào từng node trên sơ đồ để xem thông số chi tiết và giải thích tương ứng.`
    },
    en: {
      categoryLabel: 'Docs & Diagrams',
      title: 'Interactive HTML Diagrams',
      description: 'Interactive standalone HTML diagrams supporting pan, zoom, dynamic branch filtering, and interactive state exploration.',
      promptTemplate: 'Generate an interactive HTML diagram explaining the orchestration lifecycle of an AI Agent system.',
      details: `Enables users to click individual diagram nodes to inspect specifications, payloads, and runtime telemetry.`
    }
  },
  {
    id: 'html-plan',
    name: 'html-plan',
    category: 'docs',
    categories: ['docs'],
    triggers: ['html-plan', 'interactive plan', 'roadmap html', 'gantt'],
    vi: {
      categoryLabel: 'Docs & Diagrams',
      title: 'Interactive HTML Implementation Plans',
      description: 'Trực quan hóa kế hoạch triển khai (Implementation Plan) dưới dạng HTML trực quan, phân cấp rõ ràng theo timeline, phụ thuộc và trách nhiệm.',
      promptTemplate: 'Chuyển đổi tài liệu kế hoạch này thành file html-plan trực quan để báo cáo tiến độ với Tech Lead.',
      details: `Cung cấp bảng tiến độ Gantt, checkbox nghiệm thu và đánh dấu độ ưu tiên rõ ràng.`
    },
    en: {
      categoryLabel: 'Docs & Diagrams',
      title: 'Interactive HTML Implementation Plans',
      description: 'Interactive HTML Implementation Plans preserving structural hierarchy, milestone timelines, task ownership, and dependency graphs.',
      promptTemplate: 'Transform this implementation plan into an interactive html-plan deliverable for engineering lead sign-off.',
      details: `Features interactive Gantt schedules, acceptance checkboxes, and explicit critical-path priority tagging.`
    }
  },
  {
    id: 'html-wireframe',
    name: 'html-wireframe',
    category: 'docs',
    categories: ['docs'],
    triggers: ['wireframe', 'html-wireframe', 'mockup low-fi'],
    vi: {
      categoryLabel: 'Docs & Diagrams',
      title: 'Low-Fidelity HTML Wireframing',
      description: 'Tạo bản vẽ khung xương (wireframe) HTML nhanh chóng để kiểm chứng cấu trúc thông tin và luồng thao tác trước khi thiết kế chi tiết.',
      promptTemplate: 'Vẽ một bản wireframe HTML luồng checkout thanh toán thương mại điện tử bằng html-wireframe.',
      details: `Tập trung vào phân cấp thông tin, thứ tự hành động và khoảng cách mà không bị xao nhãng bởi màu sắc cầu kỳ.`
    },
    en: {
      categoryLabel: 'Docs & Diagrams',
      title: 'Low-Fidelity HTML Wireframing',
      description: 'Rapid low-fidelity HTML wireframes to validate information hierarchy, user flows, and responsive layouts before visual design.',
      promptTemplate: 'Produce a low-fidelity HTML wireframe for an e-commerce checkout flow using html-wireframe.',
      details: `Focuses strictly on content hierarchy, interaction order, and ergonomic spacing without color distraction.`
    }
  },
  {
    id: 'html-prototype',
    name: 'html-prototype',
    category: 'docs',
    categories: ['docs'],
    triggers: ['prototype', 'html-prototype', 'high-fi mockup'],
    vi: {
      categoryLabel: 'Docs & Diagrams',
      title: 'High-Fidelity HTML Interactive Prototype',
      description: 'Tạo mẫu thử tương tác (interactive prototype) mô phỏng chính xác giao diện và hành vi của sản phẩm cuối.',
      promptTemplate: 'Dùng skill html-prototype để dựng mẫu thử tương tác hoàn chỉnh cho bảng điều khiển giám sát AI Agent.',
      details: `Tích hợp giả lập dữ liệu, bộ lọc bảng và trạng thái loading/error chân thực.`
    },
    en: {
      categoryLabel: 'Docs & Diagrams',
      title: 'High-Fidelity HTML Interactive Prototype',
      description: 'High-fidelity, responsive single-file HTML prototypes simulating authentic production UI states, transitions, and interactions.',
      promptTemplate: 'Use html-prototype to build a high-fidelity interactive prototype for an AI Agent monitoring telemetry dashboard.',
      details: `Incorporates mock data stores, real-time table filtering, and authentic loading/error feedback loops.`
    }
  },
  {
    id: 'slides',
    name: 'slides',
    category: 'docs',
    categories: ['docs'],
    triggers: ['slides', 'presentation', 'pitch deck html'],
    vi: {
      categoryLabel: 'Docs & Diagrams',
      title: 'Executive HTML Presentation Slides',
      description: 'Tạo bài thuyết trình slide chuyên nghiệp bằng HTML/CSS tích hợp Chart.js, responsive và hỗ trợ trình chiếu bằng bàn phím.',
      promptTemplate: 'Tạo bộ 10 slide HTML thuyết trình chiến lược nâng cấp quy trình phát triển phần mềm với Antigravity CLI.',
      details: `Điều hướng bằng phím mũi tên Trái/Phải, tích hợp biểu đồ dữ liệu sống động bằng Chart.js.`
    },
    en: {
      categoryLabel: 'Docs & Diagrams',
      title: 'Executive HTML Presentation Slides',
      description: 'Professional executive HTML pitch decks with integrated Chart.js, responsive layouts, design token styling, and keyboard navigation.',
      promptTemplate: 'Create a 10-slide HTML presentation pitch outlining our software delivery modernization strategy with Antigravity CLI.',
      details: `Seamless keyboard navigation (Arrow keys), responsive slide transitions, and dynamic data charts via Chart.js.`
    }
  },
  {
    id: 'lecture-visualizer',
    name: 'lecture-visualizer',
    category: 'docs',
    categories: ['docs', 'design'],
    triggers: ['lecture', 'algorithm simulation', 'interactive visualizer', 'academic 3d'],
    vi: {
      categoryLabel: 'Docs & Diagrams / 3D',
      title: 'Academic Algorithm & Concept Visualizer',
      description: 'Xây dựng bài giảng trực quan hóa học thuật cao cấp (2D/3D), mô phỏng thuật toán từng bước (Step-by-step interactive algorithm).',
      promptTemplate: 'Dùng skill lecture-visualizer để giải thích trực quan thuật toán Attention Mechanism trong Transformer dưới dạng HTML tương tác.',
      details: `Phương pháp sư phạm trực quan: Giải thích bản chất toán học bằng ví dụ thực tế và widget điều khiển từng bước thực thi.`
    },
    en: {
      categoryLabel: 'Docs & Diagrams / 3D',
      title: 'Academic Algorithm & Concept Visualizer',
      description: 'Interactive graduate-level academic lecture visualizer: step-by-step algorithm walkthroughs, mathematical intuition, and 2D/3D spatial simulations.',
      promptTemplate: 'Use lecture-visualizer to construct an interactive step-by-step visualizer explaining the Multi-Head Attention Mechanism in Transformers.',
      details: `Pedagogical deep-dive: deconstruct complex mathematical concepts using visual intuition, side-by-side matrices, and interactive simulation widgets.`
    }
  },

  // ===================== 7. SCIENTIFIC RESEARCH =====================
  {
    id: 'cs-research-skills',
    name: 'cs-research-skills',
    category: 'research',
    categories: ['research'],
    isModularPack: true,
    packPath: 'cs-research-skills/',
    triggers: ['cs research', 'pytorch-lightning', 'transformers', 'qiskit', 'pennylane', 'peer-review', 'paper-lookup', 'polars', 'shap'],
    vi: {
      categoryLabel: 'CS Research (46 Modules Pack)',
      title: 'Computer Science Research Skills Pack',
      description: 'Gói 46 kỹ năng nghiên cứu Khoa học Máy tính & AI (lưu tại thư mục gốc để tối ưu tải nhẹ): PyTorch Lightning, Transformers, GPU Optimization, NetworkX, UMAP, Qiskit, PennyLane, Paper Lookup, Peer Review...',
      promptTemplate: 'Sao chép kỹ năng cần thiết từ gói cs-research-skills vào .agents/skills:\ncp -r cs-research-skills/paper-lookup .agents/skills/\ncp -r cs-research-skills/transformers .agents/skills/',
      details: `### Gói 46 kỹ năng \`cs-research-skills/\`:
Được lưu tại thư mục gốc repository để giữ cho Antigravity CLI luôn siêu nhẹ. Khi cần nghiên cứu đề tài cụ thể, chỉ cần copy kỹ năng tương ứng vào \`.agents/skills/\`:
- **AI & Deep Learning**: \`transformers\`, \`pytorch-lightning\`, \`stable-baselines3\`, \`scikit-learn\`, \`shap\`, \`umap-learn\`, \`torch-geometric\`.
- **Quantum Computing & Physics**: \`qiskit\`, \`pennylane\`, \`cirq\`.
- **Học thuật & Xuất bản**: \`paper-lookup\`, \`peer-review\`, \`literature-review\`, \`scientific-writing\`, \`scientific-visualization\`, \`citation-management\`.
- **Big Data & Math**: \`polars\`, \`dask\`, \`networkx\`, \`zarr-python\`, \`timesfm-forecasting\`.`
    },
    en: {
      categoryLabel: 'CS Research (46 Modules Pack)',
      title: 'Computer Science Research Skills Pack',
      description: 'Pack of 46 Computer Science & AI research modules (stored at root for featherweight CLI): PyTorch Lightning, Transformers, GPU Optimization, NetworkX, UMAP, Qiskit, Paper Lookup, Peer Review...',
      promptTemplate: 'Copy required skills from the cs-research-skills pack into .agents/skills:\ncp -r cs-research-skills/paper-lookup .agents/skills/\ncp -r cs-research-skills/transformers .agents/skills/',
      details: `### 46-Skill Pack in \`cs-research-skills/\`:
Kept at repository root to keep the Antigravity CLI baseline ultra-lean. Whenever embarking on specialized research, simply copy the required skills into \`.agents/skills/\`:
- **AI & Deep Learning**: \`transformers\`, \`pytorch-lightning\`, \`stable-baselines3\`, \`scikit-learn\`, \`shap\`, \`umap-learn\`, \`torch-geometric\`.
- **Quantum Computing & Physics**: \`qiskit\`, \`pennylane\`, \`cirq\`.
- **Academic & Publishing**: \`paper-lookup\`, \`peer-review\`, \`literature-review\`, \`scientific-writing\`, \`scientific-visualization\`, \`citation-management\`.
- **Big Data & Mathematics**: \`polars\`, \`dask\`, \`networkx\`, \`zarr-python\`, \`timesfm-forecasting\`.`
    }
  },
  {
    id: 'microsoft-research',
    name: 'microsoft-research',
    category: 'research',
    categories: ['research'],
    isModularPack: true,
    packPath: 'microsoft-research/',
    triggers: ['microsoft research', 'idea spark', 'paper search', 'paper2video', 'scoop check', 'bottleneck diagnosis'],
    vi: {
      categoryLabel: 'Microsoft Research (11 Tools Pack)',
      title: 'Microsoft Research Pipeline Suite',
      description: 'Quy trình nghiên cứu chuẩn Microsoft Research (lưu tại thư mục gốc): tìm kiếm bài báo, nảy sinh ý tưởng (Idea Spark), chẩn đoán điểm nghẽn, kiểm tra tính trùng lặp (Scoop Check) và chuyển đổi Paper sang Poster/Video/Blog.',
      promptTemplate: 'Kích hoạt công cụ từ microsoft-research vào .agents/skills:\ncp -r microsoft-research/rs-paper-search .agents/skills/\ncp -r microsoft-research/rs-idea-spark .agents/skills/',
      details: `### Bộ 11 công cụ \`microsoft-research/\`:
1. \`rs-paper-search\`: Tìm kiếm và tổng hợp tài liệu khoa học chuyên sâu.
2. \`rs-idea-spark\`: Gợi ý hướng nghiên cứu mới từ các khoảng trống tri thức.
3. \`rs-idea-quality\`: Đánh giá chất lượng và tính khả thi của ý tưởng nghiên cứu.
4. \`rs-scoop-check\`: Kiểm tra xem ý tưởng nghiên cứu đã bị ai công bố trước hay chưa.
5. \`rs-bottleneck-diagnosis\`: Chẩn đoán nút thắt kỹ thuật trong mô hình thực nghiệm.
6. \`rs-paper2blog\` / \`rs-paper2video\` / \`rs-paper2poster\`: Tự động hóa truyền thông khoa học đa định dạng.`
    },
    en: {
      categoryLabel: 'Microsoft Research (11 Tools Pack)',
      title: 'Microsoft Research Pipeline Suite',
      description: 'End-to-end Microsoft Research workflow (stored at repository root): paper search, idea generation (Idea Spark), bottleneck diagnosis, scoop checks, and paper-to-video/poster pipelines.',
      promptTemplate: 'Activate tools from microsoft-research into .agents/skills:\ncp -r microsoft-research/rs-paper-search .agents/skills/\ncp -r microsoft-research/rs-idea-spark .agents/skills/',
      details: `### 11-Tool Suite in \`microsoft-research/\`:
1. \`rs-paper-search\`: Deep scientific literature retrieval and synthesis.
2. \`rs-idea-spark\`: Novel research hypothesis generation targeting literature white-spaces.
3. \`rs-idea-quality\`: Feasibility and scientific rigor evaluation.
4. \`rs-scoop-check\`: Pre-publication prior-art verification to avoid duplicate research.
5. \`rs-bottleneck-diagnosis\`: Empirical debugging of experimental bottlenecks.
6. \`rs-paper2blog\` / \`rs-paper2video\` / \`rs-paper2poster\`: Multi-format science communication.`
    }
  },
  {
    id: 'research-hub',
    name: 'research-hub',
    category: 'research',
    categories: ['research'],
    isModularPack: true,
    packPath: 'research-hub/',
    triggers: ['research hub', 'academic workflow', 'experiment management', 'hypothesis matrix'],
    vi: {
      categoryLabel: 'Research Hub (Orchestrator)',
      title: 'Research Hub Master Orchestrator',
      description: 'Bộ khung điều phối và quản lý toàn bộ vòng đời nghiên cứu khoa học: thiết kế thực nghiệm, quản lý giả thuyết, tổng hợp trích dẫn và giám sát tiến độ.',
      promptTemplate: 'cp -r research-hub .agents/skills/\nKích hoạt Research Hub để thiết lập quy trình theo dõi thực nghiệm khoa học.',
      details: `### Trung tâm điều phối nghiên cứu học thuật:
- Quản lý giả thuyết và ma trận kiểm chứng khoa học.
- Tự động đồng bộ với các công cụ trong \`cs-research-skills\` và \`microsoft-research\`.
- Xuất báo cáo tiến độ và biên bản đánh giá học thuật.`
    },
    en: {
      categoryLabel: 'Research Hub (Orchestrator)',
      title: 'Research Hub Master Orchestrator',
      description: 'Master orchestrator managing the complete scientific research lifecycle: experimental design, hypothesis matrices, citation synthesis, and milestone tracking.',
      promptTemplate: 'cp -r research-hub .agents/skills/\nActivate Research Hub to orchestrate the end-to-end experimental research workflow.',
      details: `### Academic Research Command Center:
- Structured hypothesis registries and experimental verification matrices.
- Seamless coordination with tools from \`cs-research-skills\` and \`microsoft-research\`.
- Automated generation of research dossiers and peer-review audits.`
    }
  },
  {
    id: 'literature-search-arxiv',
    name: 'literature-search-arxiv',
    category: 'research',
    categories: ['research'],
    triggers: ['arxiv', 'paper search', 'literature review', 'research paper'],
    vi: {
      categoryLabel: 'Scientific Research',
      title: 'ArXiv Scientific Literature Search',
      description: 'Tìm kiếm bài báo khoa học, preprint và các công trình nghiên cứu trên arXiv, trích xuất tóm tắt và tải bản PDF toàn văn.',
      promptTemplate: 'Tìm kiếm các bài báo mới nhất trên arXiv về chủ đề "LLM Multi-Agent Coordination and Task Planning" trong năm 2025-2026.',
      details: `Trích xuất tác giả, ngày công bố, abstract và liên kết tải PDF chính xác.`
    },
    en: {
      categoryLabel: 'Scientific Research',
      title: 'ArXiv Scientific Literature Search',
      description: 'Search scientific publications and preprints on arXiv, extract abstracts and metadata, and download open-access full-text PDFs.',
      promptTemplate: 'Search arXiv for recent 2025-2026 papers on "LLM Multi-Agent Coordination and Task Planning".',
      details: `Extracts author rosters, publication timestamps, abstracts, and direct PDF download links with precision.`
    }
  },
  {
    id: 'literature-search-openalex',
    name: 'literature-search-openalex',
    category: 'research',
    categories: ['research'],
    triggers: ['openalex', 'doi lookup', 'citation count', 'h-index', 'scholarly search'],
    vi: {
      categoryLabel: 'Scientific Research',
      title: 'OpenAlex Scholarly Database & DOI',
      description: 'Truy vấn kho dữ liệu học thuật mở OpenAlex: tìm kiếm bài báo, tác giả, tổ chức, số lượng trích dẫn, h-index và giải mã DOI.',
      promptTemplate: 'Dùng skill literature-search-openalex để tra cứu danh sách các bài báo có trích dẫn cao nhất về Transformer Architecture.',
      details: `Cung cấp thông tin tác giả, cơ quan nghiên cứu, nguồn tài trợ và liên kết tải tài liệu Open Access.`
    },
    en: {
      categoryLabel: 'Scientific Research',
      title: 'OpenAlex Scholarly Database & DOI',
      description: 'Query the OpenAlex scholarly database: retrieve papers, author profiles, affiliations, citation counts, h-index metrics, and resolve DOIs.',
      promptTemplate: 'Use literature-search-openalex to identify the most highly cited papers on Transformer Architecture and extract open-access PDFs.',
      details: `Provides comprehensive bibliographic metadata, institutional provenance, funding sources, and open-access links.`
    }
  },
  {
    id: 'pubmed-database',
    name: 'pubmed-database',
    category: 'research',
    categories: ['research'],
    triggers: ['pubmed', 'clinical trial', 'biomedical literature', 'ncbi', 'pmid'],
    vi: {
      categoryLabel: 'Scientific Research',
      title: 'PubMed Biomedical & Clinical Trials',
      description: 'Tra cứu tài liệu y sinh học, thử nghiệm lâm sàng đã công bố và liên kết chéo với các cơ sở dữ liệu NCBI (Gene, Protein, Nucleotide, PubChem).',
      promptTemplate: 'Tìm kiếm các công trình thử nghiệm lâm sàng trên PubMed về thuốc ức chế kinase thế hệ mới.',
      details: `Truy vấn trực tiếp qua NCBI E-utilities và PMC BioC APIs để lấy tóm tắt và văn bản toàn văn.`
    },
    en: {
      categoryLabel: 'Scientific Research',
      title: 'PubMed Biomedical & Clinical Trials',
      description: 'Search biomedical literature and published clinical trials on PubMed with cross-referencing across NCBI databases (Gene, Protein, Nucleotide, PubChem).',
      promptTemplate: 'Search PubMed for published clinical trial literature regarding next-generation kinase inhibitors.',
      details: `Directly interfaces NCBI E-utilities and PMC BioC APIs to retrieve verified abstracts and full texts.`
    }
  },
  {
    id: 'alphafold-database-fetch-and-analyze',
    name: 'alphafold-database-fetch-and-analyze',
    category: 'research',
    categories: ['research'],
    triggers: ['alphafold', 'protein structure', 'plddt', 'uniprot', 'structural biology'],
    vi: {
      categoryLabel: 'Scientific Research',
      title: 'AlphaFold Structural Biology Analysis',
      description: 'Truy xuất và phân tích cấu trúc 3D protein dự đoán từ AlphaFold DB bằng UniProt ID, đánh giá độ tin cậy pLDDT và ranh giới vùng miền domain.',
      promptTemplate: 'Dùng skill alphafold-database-fetch-and-analyze để phân tích độ tin cậy cấu trúc protein UniProt ID [P05067].',
      details: `Đo lường chỉ số pLDDT theo từng residue và phân tích ranh giới domain cấu trúc.`
    },
    en: {
      categoryLabel: 'Scientific Research',
      title: 'AlphaFold Structural Biology Analysis',
      description: 'Retrieve and analyze AlphaFold predicted 3D protein structures via UniProt ID, evaluating pLDDT confidence metrics and domain boundaries.',
      promptTemplate: 'Use alphafold-database-fetch-and-analyze to inspect the structural confidence of UniProt ID [P05067].',
      details: `Quantifies residue-level pLDDT confidence scores and identifies structural domain boundaries.`
    }
  }
];

export function getSkills(lang = 'vi') {
  const currentLang = (lang === 'en') ? 'en' : 'vi';
  return RAW_SKILLS_DATA.map((s) => {
    const loc = s[currentLang] || s.vi;
    return {
      id: s.id,
      name: s.name,
      category: s.category,
      categories: s.categories,
      isModularPack: s.isModularPack || false,
      packPath: s.packPath || '',
      triggers: s.triggers,
      categoryLabel: loc.categoryLabel,
      title: loc.title,
      description: loc.description,
      promptTemplate: loc.promptTemplate,
      details: loc.details,
    };
  });
}

// Default export for backward compatibility
export const SKILLS_DATA = getSkills('vi');
