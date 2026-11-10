/**
 * Internationalization (i18n) Module for agent_setup (by Jin)
 * Genuine bilingual support (Vietnamese & English) with zero automated translation widgets.
 */

export const UI_TRANSLATIONS = {
  vi: {
    pageTitle: "agent_setup · Antigravity Agent Skills (by Hi Jin)",
    metaDescription: "Bộ cấu hình chuẩn mực và kho hơn 50+ kỹ năng chuyên sâu được tuyển chọn và custom riêng cho Antigravity CLI. Tác giả: Hi Jin.",
    skipLink: "Bỏ qua đến nội dung chính",
    brandAria: "Trang chủ agent_setup by Hi Jin",
    brandAuthor: "by Jin",
    
    // Navbar
    navOverview: "Giới Thiệu",
    navPhilosophy: "Triết Lý",
    navSkills: "Kho Skills",
    navSetup: "Cài Đặt",
    searchShortcut: "Tìm kiếm",
    githubAria: "Xem mã nguồn trên GitHub",
    
    // Hero Section
    heroTag: "Antigravity Agent Skills Ecosystem",
    heroHeadline: `Dạy nghề cho AI.<br><span class="gradient-text">Biến Antigravity thành kỹ sư thực thụ.</span>`,
    heroDescription: "Kho cấu hình chuẩn mực và hơn 50+ kỹ năng chuyên sâu được tuyển chọn từ cộng đồng Claude Code và tùy biến riêng cho Antigravity CLI. Bớt đoán mò, không over-engineering, giữ môi trường biệt lập và sửa code chuẩn xác.",
    heroBtnSkills: "Khám phá 50+ Skills",
    heroBtnSetup: "Xem hướng dẫn setup",
    heroShowcaseAria: "Hoạt cảnh chuyển động giới thiệu agent_setup cho Antigravity",
    
    // Philosophy Section
    philosophyTag: "Kỷ Luật Tác Chiến",
    philosophyTitle: "4 Nguyên Tắc Kỹ Thuật Bất Biến",
    philosophySubtitle: "Học tập từ nhận xét của Andrej Karpathy về các lỗi điển hình của LLM khi viết code: bớt đoán mò, tối giản, và sửa đúng chỗ.",
    
    p1Num: "01 / DISCIPLINE",
    p1Title: "Think Before Coding",
    p1Desc: "Không được tự giả định nếu yêu cầu mơ hồ. Nêu rõ các giả định, đánh đổi và hỏi lại trước khi viết mã.",
    
    p2Num: "02 / MINIMALISM",
    p2Title: "Simplicity First",
    p2Desc: "Chỉ viết lượng code tối thiểu giải quyết bài toán. Tuyệt đối không thêm abstraction hay suy đoán tương lai.",
    
    p3Num: "03 / PRECISION",
    p3Title: "Surgical Changes",
    p3Desc: "Chỉ sửa đúng phạm vi yêu cầu. Giữ nguyên style của codebase. Mọi dòng code thay đổi đều phải truy vết được.",
    
    p4Num: "04 / SAFETY",
    p4Title: "Strict Isolation",
    p4Desc: "Mọi gói phụ thuộc phải nằm trong môi trường ảo (.venv) cục bộ của workspace. Nghiêm cấm làm bẩn host system.",
    
    // Skills Section
    skillsTag: "Thư Viện Thực Chiến",
    skillsTitle: "Kho 50+ Kỹ Năng Của agent_setup",
    skillsSubtitle: "Tuyển chọn và tối ưu hóa riêng cho Antigravity CLI. Tra cứu nhanh chóng, nắm bắt cú pháp kích hoạt và sao chép prompt mẫu chuẩn hoá.",
    searchPlaceholder: "Tìm kiếm skill (ví dụ: fastapi, clean-code, user-story, diagram, 3d...)",
    searchAria: "Tìm kiếm kỹ năng",
    filterTabsAria: "Bộ lọc phân loại kỹ năng",
    
    // Skills Card & Modal
    emptySearchTitle: "Không tìm thấy kỹ năng phù hợp",
    emptySearchDesc: 'Hãy thử tìm với từ khóa khác như "fastapi", "clean-code", "rag", "langchain", hoặc "3d".',
    btnCopyPrompt: "Copy Prompt",
    btnCopied: "Đã chép!",
    btnDetails: "Chi tiết",
    
    modalDefaultTitle: "Chi Tiết Kỹ Năng",
    modalCloseAria: "Đóng hộp thoại (Esc)",
    modalOverviewLabel: "Mô tả tổng quát:",
    modalTriggersLabel: "Từ khóa kích hoạt (Triggers):",
    modalPromptLabel: "Prompt Mẫu Sẵn Sàng Kích Hoạt:",
    modalCopyBtn: "Sao Chép Prompt Này",
    modalModularPackBadge: "Gói Modular On-Demand:",
    modalModularPackText: "Bộ công cụ này được lưu trữ tại thư mục gốc <code>{path}</code> để giữ cho Antigravity CLI luôn siêu nhẹ. Khi cần dùng, chỉ cần sao chép vào <code>.agents/skills/</code>.",
    toastCopied: "Đã sao chép prompt vào clipboard!",
    
    // Setup Section
    setupTag: "Tích Hợp Dễ Dàng",
    setupTitle: "Khởi Động agent_setup Trong 3 Bước",
    setupSubtitle: "Cấu hình nhẹ gọn, nạp trực tiếp vào dự án của bạn và chạy cùng Antigravity CLI.",
    setupTerminalTitle: "Terminal Quickstart cho Antigravity",
    setupCopyBtn: "Sao chép lệnh",
    setupCopied: "Đã sao chép!",
    setupCard1Title: "Nguyên Tắc Bất Biến",
    setupCard1Desc: "Nghiêm cấm cài đặt package toàn cục. Mọi thay đổi đều được cô lập trong dự án.",
    setupCard2Title: "Surgical Changes",
    setupCard2Desc: "Chỉ viết lượng code tối thiểu để giải quyết bài toán. Kiểm thử trước khi kết thúc.",
    setupCodeBlock: `# 1. Clone repository hoặc copy cấu hình cốt lõi vào root dự án
git clone https://github.com/phamvantienkiz/agent_setup.git
cp -r agent_setup/.agents agent_setup/AGENTS.md ./your-project/

# (Tùy chọn) Nếu làm nghiên cứu khoa học, nạp thêm từ gói on-demand:
# cp -r agent_setup/cs-research-skills/paper-lookup ./your-project/.agents/skills/
# cp -r agent_setup/microsoft-research/rs-paper-search ./your-project/.agents/skills/

# 2. Khởi tạo môi trường ảo Python biệt lập (Strict Environment Isolation)
cd ./your-project
python -m venv .venv
source .venv/bin/activate  # Hoặc trên Windows: .venv\\Scripts\\activate

# 3. Kích hoạt Antigravity CLI và tận hưởng kho 50+ Skills
agy`,

    // Footer
    footerBrandDesc: "Bộ cấu hình chuẩn mực và kho kỹ năng chuyên sâu tuyển chọn cho Antigravity CLI.",
    footerNavTitle: "Điều Hướng",
    footerNavTop: "Về Đầu Trang ↑",
    footerNavPhilosophy: "Kỷ Luật Tác Chiến",
    footerNavSkills: "Kho Kỹ Năng (50+)",
    footerNavSetup: "Hướng Dẫn Cài Đặt",
    footerAuthorTitle: "Tác Giả (Jin)",
    footerGithubPersonal: "GitHub Cá Nhân",
    footerBottomLeft: "© 2026 agent_setup · Created by Jin · MIT License.",
    footerBottomRight: "Tailored specifically for Antigravity CLI"
  },

  en: {
    pageTitle: "agent_setup · Antigravity Agent Skills (by Hi Jin)",
    metaDescription: "Production-grade configurations and curated repository of 50+ specialized skills tailored for Antigravity CLI. Author: Hi Jin.",
    skipLink: "Skip to main content",
    brandAria: "agent_setup homepage by Hi Jin",
    brandAuthor: "by Jin",
    
    // Navbar
    navOverview: "Overview",
    navPhilosophy: "Philosophy",
    navSkills: "Skills Arsenal",
    navSetup: "Setup",
    searchShortcut: "Search",
    githubAria: "View source code on GitHub",
    
    // Hero Section
    heroTag: "Antigravity Agent Skills Ecosystem",
    heroHeadline: `Upskill Your AI.<br><span class="gradient-text">Turn Antigravity into a True Engineer.</span>`,
    heroDescription: "Production-grade configurations and 50+ specialized skills curated from the Claude Code ecosystem, tailored specifically for Antigravity CLI. Eliminate guesswork, avoid over-engineering, enforce environment isolation, and ship surgical code diffs.",
    heroBtnSkills: "Explore 50+ Skills",
    heroBtnSetup: "View Setup Guide",
    heroShowcaseAria: "Interactive motion showcase presenting agent_setup for Antigravity",
    
    // Philosophy Section
    philosophyTag: "Operational Discipline",
    philosophyTitle: "4 Uncompromising Engineering Principles",
    philosophySubtitle: "Grounded in Andrej Karpathy's insights on common LLM coding pitfalls: stop guessing, embrace minimalism, and make surgical fixes.",
    
    p1Num: "01 / DISCIPLINE",
    p1Title: "Think Before Coding",
    p1Desc: "Never assume when requirements are ambiguous. Explicitly state assumptions, surface tradeoffs, and verify before coding.",
    
    p2Num: "02 / MINIMALISM",
    p2Title: "Simplicity First",
    p2Desc: "Write the minimum code that solves the problem. Absolutely no speculative abstractions or hypothetical future-proofing.",
    
    p3Num: "03 / PRECISION",
    p3Title: "Surgical Changes",
    p3Desc: "Touch only what must be touched. Preserve codebase style and invariants. Every modified line must be strictly traceable.",
    
    p4Num: "04 / SAFETY",
    p4Title: "Strict Isolation",
    p4Desc: "All dependencies must stay confined within a workspace-local virtual environment (.venv). Never pollute the global host system.",
    
    // Skills Section
    skillsTag: "Battle-Tested Library",
    skillsTitle: "agent_setup 50+ Skills Arsenal",
    skillsSubtitle: "Curated and engineered exclusively for Antigravity CLI. Search instantly, master activation triggers, and copy standardized execution prompts.",
    searchPlaceholder: "Search skills (e.g., fastapi, clean-code, user-story, diagram, 3d...)",
    searchAria: "Search skills",
    filterTabsAria: "Skill category filter",
    
    // Skills Card & Modal
    emptySearchTitle: "No matching skills found",
    emptySearchDesc: 'Try searching for other keywords like "fastapi", "clean-code", "rag", "langchain", or "3d".',
    btnCopyPrompt: "Copy Prompt",
    btnCopied: "Copied!",
    btnDetails: "Details",
    
    modalDefaultTitle: "Skill Specification",
    modalCloseAria: "Close dialog (Esc)",
    modalOverviewLabel: "Overview:",
    modalTriggersLabel: "Trigger Keywords:",
    modalPromptLabel: "Ready-to-Use Prompt Template:",
    modalCopyBtn: "Copy This Prompt",
    modalModularPackBadge: "Modular On-Demand Pack:",
    modalModularPackText: "Stored at repository root <code>{path}</code> to keep Antigravity CLI featherlight. Whenever needed, simply copy into <code>.agents/skills/</code>.",
    toastCopied: "Prompt copied to clipboard!",
    
    // Setup Section
    setupTag: "Frictionless Integration",
    setupTitle: "Quickstart agent_setup in 3 Steps",
    setupSubtitle: "Featherweight configuration, drop directly into your project root and run with Antigravity CLI.",
    setupTerminalTitle: "Terminal Quickstart for Antigravity",
    setupCopyBtn: "Copy Commands",
    setupCopied: "Copied!",
    setupCard1Title: "Core Invariant",
    setupCard1Desc: "Never install global packages. All dependencies and executions must stay strictly isolated within the project.",
    setupCard2Title: "Surgical Changes",
    setupCard2Desc: "Write only the minimal code necessary to solve the problem. Verify thoroughly before completion.",
    setupCodeBlock: `# 1. Clone repository or copy core configurations into your project root
git clone https://github.com/phamvantienkiz/agent_setup.git
cp -r agent_setup/.agents agent_setup/AGENTS.md ./your-project/

# (Optional) For scientific research, load on-demand modular packs:
# cp -r agent_setup/cs-research-skills/paper-lookup ./your-project/.agents/skills/
# cp -r agent_setup/microsoft-research/rs-paper-search ./your-project/.agents/skills/

# 2. Initialize isolated Python virtual environment (Strict Environment Isolation)
cd ./your-project
python -m venv .venv
source .venv/bin/activate  # Or on Windows: .venv\\Scripts\\activate

# 3. Launch Antigravity CLI and unleash 50+ skills
agy`,

    // Footer
    footerBrandDesc: "Production-grade agent configurations and curated skills repository for Antigravity CLI.",
    footerNavTitle: "Navigation",
    footerNavTop: "Back to Top ↑",
    footerNavPhilosophy: "Operational Discipline",
    footerNavSkills: "Skills Arsenal (50+)",
    footerNavSetup: "Setup Guide",
    footerAuthorTitle: "Author (Jin)",
    footerGithubPersonal: "Personal GitHub",
    footerBottomLeft: "© 2026 agent_setup · Created by Jin · MIT License.",
    footerBottomRight: "Tailored specifically for Antigravity CLI"
  }
};

class I18nManager {
  constructor() {
    let saved = null;
    try {
      if (typeof localStorage !== 'undefined') {
        saved = localStorage.getItem('agent_setup_lang');
      }
    } catch (e) {
      // Storage unavailable or restricted
    }
    this.currentLang = (saved === 'en') ? 'en' : 'vi';
    this.listeners = [];
  }

  getLang() {
    return this.currentLang;
  }

  t(key) {
    const dict = UI_TRANSLATIONS[this.currentLang] || UI_TRANSLATIONS.vi;
    return dict[key] || UI_TRANSLATIONS.vi[key] || '';
  }

  onLanguageChange(callback) {
    if (typeof callback === 'function') {
      this.listeners.push(callback);
    }
  }

  setLang(lang) {
    const targetLang = (lang === 'en') ? 'en' : 'vi';
    this.currentLang = targetLang;
    try {
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem('agent_setup_lang', targetLang);
      }
    } catch (e) {}

    if (typeof document !== 'undefined') {
      document.documentElement.lang = targetLang;
      this.updateDOM();
    }

    // Notify listeners (HeroShowcase, SkillsExplorer, etc.)
    this.listeners.forEach((cb) => {
      try {
        cb(targetLang);
      } catch (err) {
        console.error('Error in i18n listener:', err);
      }
    });
  }

  updateDOM() {
    if (typeof document === 'undefined') return;
    const dict = UI_TRANSLATIONS[this.currentLang] || UI_TRANSLATIONS.vi;

    // Document Meta
    if (dict.pageTitle) document.title = dict.pageTitle;
    const metaDesc = document.querySelector('meta[name="description"]');
    if (metaDesc && dict.metaDescription) {
      metaDesc.setAttribute('content', dict.metaDescription);
    }

    // Text content
    document.querySelectorAll('[data-i18n]').forEach((el) => {
      const key = el.getAttribute('data-i18n');
      if (dict[key] !== undefined) {
        el.textContent = dict[key];
      }
    });

    // HTML content (for elements containing nested markup like gradients or <br>)
    document.querySelectorAll('[data-i18n-html]').forEach((el) => {
      const key = el.getAttribute('data-i18n-html');
      if (dict[key] !== undefined) {
        el.innerHTML = dict[key];
      }
    });

    // Placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach((el) => {
      const key = el.getAttribute('data-i18n-placeholder');
      if (dict[key] !== undefined) {
        el.setAttribute('placeholder', dict[key]);
      }
    });

    // Aria labels
    document.querySelectorAll('[data-i18n-aria]').forEach((el) => {
      const key = el.getAttribute('data-i18n-aria');
      if (dict[key] !== undefined) {
        el.setAttribute('aria-label', dict[key]);
      }
    });

    // Update active state on language switcher buttons
    document.querySelectorAll('.lang-btn').forEach((btn) => {
      const btnLang = btn.getAttribute('data-lang');
      const isActive = btnLang === this.currentLang;
      btn.classList.toggle('active', isActive);
      btn.setAttribute('aria-pressed', isActive ? 'true' : 'false');
    });

    // Update Setup Code block if present
    const setupBlock = document.getElementById('setup-code-block');
    if (setupBlock && dict.setupCodeBlock) {
      const codeElem = setupBlock.querySelector('code') || setupBlock;
      codeElem.textContent = dict.setupCodeBlock;
    }
  }
}

export const i18n = new I18nManager();
