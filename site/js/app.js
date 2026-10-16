/**
 * Application Bootstrap (agent_setup by Jin)
 */

import { HeroShowcase } from './hero-showcase.js';
import { SkillsExplorer } from './explorer.js';

document.addEventListener('DOMContentLoaded', () => {
  // 1. Initialize Hero Showcase Motion Card
  const showcase = new HeroShowcase();

  // 2. Initialize Skills Explorer (Search, Filter, Modal)
  const skillsExplorer = new SkillsExplorer();

  // 3. Quick Copy for Setup Commands
  const copySetupBtn = document.getElementById('copy-setup-cmd');
  if (copySetupBtn) {
    copySetupBtn.addEventListener('click', () => {
      const code = document.getElementById('setup-code-block')?.textContent || '';
      navigator.clipboard.writeText(code.trim()).then(() => {
        const textSpan = copySetupBtn.querySelector('span');
        const originalText = textSpan ? textSpan.textContent : '';
        if (textSpan) textSpan.textContent = 'Đã sao chép!';
        copySetupBtn.style.borderColor = 'var(--color-brand-primary)';
        copySetupBtn.style.color = 'var(--color-brand-accent)';
        setTimeout(() => {
          if (textSpan) textSpan.textContent = originalText || 'Sao chép lệnh';
          copySetupBtn.style.borderColor = '';
          copySetupBtn.style.color = '';
        }, 2000);
      });
    });
  }

  // 4. Highlight Nav Link on Scroll
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
