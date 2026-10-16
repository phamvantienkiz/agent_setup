/**
 * Skills Explorer Component (agent_setup by Jin)
 * Real-time search, category filtering, copy prompt with SVG icons, and detail modal
 */

import { SKILLS_DATA, SKILL_CATEGORIES } from './skills-data.js';

// SVG Icon Helpers
const ICONS = {
  copy: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`,
  check: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`,
  arrowRight: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>`,
  code: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>`
};

export class SkillsExplorer {
  constructor() {
    this.skills = SKILLS_DATA;
    this.categories = SKILL_CATEGORIES;
    this.activeCategory = 'all';
    this.searchQuery = '';

    // DOM Elements
    this.cardsContainer = document.getElementById('skills-grid');
    this.searchInput = document.getElementById('skills-search-input');
    this.tabsContainer = document.getElementById('filter-tabs');
    this.modalBackdrop = document.getElementById('skill-modal');
    this.modalTitle = document.getElementById('modal-skill-title');
    this.modalBadge = document.getElementById('modal-skill-badge');
    this.modalBody = document.getElementById('modal-skill-body');
    this.modalCopyBtn = document.getElementById('modal-copy-btn');
    this.modalCloseBtn = document.getElementById('modal-close-btn');
    this.toastElem = document.getElementById('toast-notice');

    this.activeModalSkill = null;

    this.init();
  }

  init() {
    this.renderTabs();
    this.renderCards();
    this.bindEvents();
  }

  bindEvents() {
    if (this.searchInput) {
      this.searchInput.addEventListener('input', (e) => {
        this.searchQuery = e.target.value.toLowerCase().trim();
        this.renderCards();
      });
    }

    if (this.modalCloseBtn) {
      this.modalCloseBtn.addEventListener('click', () => this.closeModal());
    }

    if (this.modalBackdrop) {
      this.modalBackdrop.addEventListener('click', (e) => {
        if (e.target === this.modalBackdrop) {
          this.closeModal();
        }
      });
    }

    if (this.modalCopyBtn) {
      this.modalCopyBtn.addEventListener('click', () => {
        if (this.activeModalSkill) {
          this.copyPrompt(this.activeModalSkill.promptTemplate, this.modalCopyBtn);
        }
      });
    }

    window.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        this.searchInput?.focus();
      }
      if (e.key === 'Escape' && this.modalBackdrop?.classList.contains('open')) {
        this.closeModal();
      }
    });
  }

  renderTabs() {
    if (!this.tabsContainer) return;
    this.tabsContainer.innerHTML = '';

    this.categories.forEach((cat) => {
      const count = cat.id === 'all'
        ? this.skills.length
        : this.skills.filter(s => s.category === cat.id || (Array.isArray(s.categories) && s.categories.includes(cat.id))).length;

      const btn = document.createElement('button');
      btn.className = `tab-btn ${cat.id === this.activeCategory ? 'active' : ''}`;
      btn.setAttribute('role', 'tab');
      btn.setAttribute('aria-selected', cat.id === this.activeCategory ? 'true' : 'false');
      btn.innerHTML = `
        <span>${cat.label}</span>
        <span class="tab-count">${count}</span>
      `;

      btn.addEventListener('click', () => {
        this.activeCategory = cat.id;
        this.renderTabs();
        this.renderCards();
      });

      this.tabsContainer.appendChild(btn);
    });
  }

  getFilteredSkills() {
    return this.skills.filter((skill) => {
      const matchCat = this.activeCategory === 'all' || 
        skill.category === this.activeCategory ||
        (Array.isArray(skill.categories) && skill.categories.includes(this.activeCategory));

      const matchQuery = !this.searchQuery || 
        skill.name.toLowerCase().includes(this.searchQuery) ||
        skill.title.toLowerCase().includes(this.searchQuery) ||
        skill.description.toLowerCase().includes(this.searchQuery) ||
        skill.triggers.some(t => t.toLowerCase().includes(this.searchQuery));

      return matchCat && matchQuery;
    });
  }

  renderCards() {
    if (!this.cardsContainer) return;
    const filtered = this.getFilteredSkills();

    if (filtered.length === 0) {
      this.cardsContainer.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 48px; background: var(--color-surface-muted); border-radius: var(--radius-md); border: 1px dashed var(--color-border-subtle);">
          <p style="color: var(--color-brand-accent); font-size: var(--font-size-lg); font-weight: 600; margin-bottom: 8px;">Không tìm thấy kỹ năng phù hợp</p>
          <p style="color: var(--color-text-muted); font-size: var(--font-size-sm);">Hãy thử tìm với từ khóa khác như "fastapi", "clean-code", "rag", "langchain", hoặc "3d".</p>
        </div>
      `;
      return;
    }

    this.cardsContainer.innerHTML = '';
    filtered.forEach((skill) => {
      const card = document.createElement('div');
      card.className = 'skill-card';

      let badgeClass = 'badge-emerald';
      if (skill.isModularPack) {
        badgeClass = 'badge-amber';
      } else if (skill.category === 'llm-agent' || (Array.isArray(skill.categories) && skill.categories.includes('llm-agent'))) {
        badgeClass = 'badge-purple';
      } else if (skill.category === 'coding' || (Array.isArray(skill.categories) && skill.categories.includes('coding'))) {
        badgeClass = 'badge-cyan';
      }

      const triggersHtml = skill.triggers
        .map(t => `<span class="trigger-tag">${t}</span>`)
        .join('');

      card.innerHTML = `
        <div class="skill-card-header">
          <div class="skill-name-group">
            <div class="skill-icon-box">${ICONS.code}</div>
            <h3 class="skill-title">${skill.name}</h3>
          </div>
          <span class="badge ${badgeClass}">${skill.categoryLabel}</span>
        </div>
        <p class="skill-desc">${skill.description}</p>
        <div class="skill-triggers">
          ${triggersHtml}
        </div>
        <div class="skill-card-footer">
          <button class="btn btn-secondary btn-sm copy-btn" data-id="${skill.id}">
            ${ICONS.copy}
            <span>Copy Prompt</span>
          </button>
          <button class="btn btn-ghost btn-sm detail-btn" data-id="${skill.id}">
            <span>Chi tiết</span>
            ${ICONS.arrowRight}
          </button>
        </div>
      `;

      const copyBtn = card.querySelector('.copy-btn');
      copyBtn.addEventListener('click', () => {
        this.copyPrompt(skill.promptTemplate, copyBtn);
      });

      const detailBtn = card.querySelector('.detail-btn');
      detailBtn.addEventListener('click', () => {
        this.openModal(skill);
      });

      this.cardsContainer.appendChild(card);
    });
  }

  copyPrompt(text, btnElement = null) {
    navigator.clipboard.writeText(text).then(() => {
      this.showToast('Đã sao chép prompt vào clipboard!');
      if (btnElement) {
        const textSpan = btnElement.querySelector('span');
        const originalText = textSpan ? textSpan.textContent : '';
        btnElement.innerHTML = `${ICONS.check} <span>Đã chép!</span>`;
        btnElement.style.borderColor = 'var(--color-brand-primary)';
        btnElement.style.color = 'var(--color-brand-accent)';
        setTimeout(() => {
          btnElement.innerHTML = `${ICONS.copy} <span>${originalText || 'Copy Prompt'}</span>`;
          btnElement.style.borderColor = '';
          btnElement.style.color = '';
        }, 1800);
      }
    });
  }

  showToast(message) {
    if (!this.toastElem) return;
    this.toastElem.innerHTML = `${ICONS.check} <span>${message}</span>`;
    this.toastElem.classList.add('show');
    setTimeout(() => {
      this.toastElem.classList.remove('show');
    }, 2500);
  }

  openModal(skill) {
    this.activeModalSkill = skill;
    if (!this.modalBackdrop) return;

    if (this.modalTitle) this.modalTitle.textContent = skill.name;
    if (this.modalBadge) {
      this.modalBadge.textContent = skill.categoryLabel;
      let badgeClass = 'badge badge-emerald';
      if (skill.isModularPack) {
        badgeClass = 'badge badge-amber';
      } else if (skill.category === 'llm-agent' || (Array.isArray(skill.categories) && skill.categories.includes('llm-agent'))) {
        badgeClass = 'badge badge-purple';
      } else if (skill.category === 'coding' || (Array.isArray(skill.categories) && skill.categories.includes('coding'))) {
        badgeClass = 'badge badge-cyan';
      }
      this.modalBadge.className = badgeClass;
    }

    const formattedHtml = this.formatMarkdown(skill.details);
    if (this.modalBody) {
      const modularBanner = skill.isModularPack ? `
        <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: var(--radius-sm); padding: 12px 14px; margin-bottom: 20px; color: #fbbf24; font-size: 13.5px; line-height: 1.6;">
          <strong>⚡ Gói Modular On-Demand:</strong> Bộ công cụ này được lưu trữ tại thư mục gốc <code>${skill.packPath}</code> để giữ cho Antigravity CLI luôn siêu nhẹ. Khi cần dùng, chỉ cần sao chép vào <code>.agents/skills/</code>.
        </div>
      ` : '';

      this.modalBody.innerHTML = `
        ${modularBanner}
        <div style="margin-bottom: 20px;">
          <h4 style="color: var(--color-brand-accent); font-size: 13px; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">Mô tả tổng quát:</h4>
          <p style="color: var(--color-text-primary); font-size: 15px;">${skill.description}</p>
        </div>

        <div style="margin-bottom: 20px;">
          <h4 style="color: var(--color-brand-accent); font-size: 13px; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">Từ khóa kích hoạt (Triggers):</h4>
          <div style="display: flex; gap: 6px; flex-wrap: wrap;">
            ${skill.triggers.map(t => `<span class="trigger-tag" style="font-size: 12px; padding: 2px 8px;">${t}</span>`).join('')}
          </div>
        </div>

        <div style="margin-bottom: 24px;">
          <h4 style="color: var(--color-brand-accent); font-size: 13px; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">Prompt Mẫu Sẵn Sàng Kích Hoạt:</h4>
          <pre><code>${skill.promptTemplate}</code></pre>
        </div>

        <div>
          ${formattedHtml}
        </div>
      `;
    }

    this.modalBackdrop.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  closeModal() {
    if (!this.modalBackdrop) return;
    this.modalBackdrop.classList.remove('open');
    document.body.style.overflow = '';
    this.activeModalSkill = null;
  }

  formatMarkdown(mdText) {
    if (!mdText) return '';
    return mdText
      .replace(/^### (.*$)/gim, '<h4 style="color: #6ee7b7; margin-top: 18px; margin-bottom: 8px;">$1</h4>')
      .replace(/^#### (.*$)/gim, '<h5 style="color: #ffffff; margin-top: 14px; margin-bottom: 6px;">$1</h5>')
      .replace(/`([^`]+)`/g, '<code style="background: #060b16; border: 1px solid #1e293b; padding: 2px 6px; border-radius: 4px; color: #6ee7b7; font-family: monospace;">$1</code>')
      .replace(/\n\n/g, '<p style="margin-bottom: 12px;"></p>');
  }
}
