/**
 * Application Bootstrap (agent_setup by Jin)
 * Genuine bilingual support (Vietnamese & English)
 */

import { HeroShowcase } from './hero-showcase.js';
import { SkillsExplorer } from './explorer.js';
import { i18n } from './i18n.js';

document.addEventListener('DOMContentLoaded', () => {
  // 1. Initialize Hero Showcase Motion Card
  const showcase = new HeroShowcase();

  // 2. Initialize Skills Explorer (Search, Filter, Modal)
  const skillsExplorer = new SkillsExplorer();

  // 3. Connect i18n Language Change Callbacks
  i18n.onLanguageChange((lang) => {
    showcase.setLanguage(lang);
    skillsExplorer.setLanguage(lang);
  });

  // 4. Bind Language Switcher Buttons
  const langButtons = document.querySelectorAll('.lang-btn');
  langButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      const targetLang = btn.getAttribute('data-lang');
      if (targetLang && targetLang !== i18n.getLang()) {
        i18n.setLang(targetLang);
      }
    });
  });

  // 5. Initial DOM Synchronization
  i18n.updateDOM();
  showcase.setLanguage(i18n.getLang());
  skillsExplorer.setLanguage(i18n.getLang());

  // 6. Quick Copy for Setup Commands
  const copySetupBtn = document.getElementById('copy-setup-cmd');
  if (copySetupBtn) {
    copySetupBtn.addEventListener('click', () => {
      const code = document.getElementById('setup-code-block')?.textContent || '';
      navigator.clipboard.writeText(code.trim()).then(() => {
        const textSpan = copySetupBtn.querySelector('span');
        const copiedLabel = i18n.t('setupCopied') || 'Đã sao chép!';
        const defaultLabel = i18n.t('setupCopyBtn') || 'Sao chép lệnh';

        if (textSpan) textSpan.textContent = copiedLabel;
        copySetupBtn.style.borderColor = 'var(--color-brand-primary)';
        copySetupBtn.style.color = 'var(--color-brand-accent)';
        setTimeout(() => {
          if (textSpan) textSpan.textContent = defaultLabel;
          copySetupBtn.style.borderColor = '';
          copySetupBtn.style.color = '';
        }, 2000);
      });
    });
  }

  // 7. Highlight Nav Link on Scroll
  const navLinks = document.querySelectorAll('.nav-link');
  const sections = document.querySelectorAll('section[id]');

  window.addEventListener('scroll', () => {
    let current = '';
    sections.forEach((sec) => {
      const top = sec.offsetTop - 120;
      if (window.scrollY >= top) {
        current = sec.getAttribute('id');
      }
    });

    navLinks.forEach((link) => {
      link.classList.remove('active');
      if (link.getAttribute('href') === `#${current}`) {
        link.classList.add('active');
      }
    });
  });
});
