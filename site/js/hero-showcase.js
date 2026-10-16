/**
 * Continuous 30 FPS Motion Video Engine (agent_setup by Jin)
 * Square 1:1 Canvas Animation running smoothly without clunky video player controls.
 * Customized specifically for Antigravity CLI.
 */

export class HeroShowcase {
  constructor() {
    this.canvas = document.getElementById("hero-motion-canvas");
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext("2d");

    // Deterministic 30 FPS configuration
    this.fps = 30;
    this.frameDuration = 1000 / this.fps; // 33.33ms
    this.totalFrames = 1500; // 50 seconds total cycle @ 30 FPS
    this.currentFrame = 0;
    this.lastTimestamp = 0;
    this.accumulator = 0;
    this.isHovered = false;

    // Entities
    this.particles = [];
    this.initEntities();

    // Canvas sizing with DPR
    this.resize();
    window.addEventListener("resize", () => this.resize());

    // Pause slightly on hover to read, resume on leave
    const wrapper = document.querySelector(".showcase-card-wrapper");
    if (wrapper) {
      wrapper.addEventListener("mouseenter", () => {
        this.isHovered = true;
      });
      wrapper.addEventListener("mouseleave", () => {
        this.isHovered = false;
      });
    }

    // Start 30 FPS animation loop
    requestAnimationFrame((t) => this.loop(t));
  }

  resize() {
    const rect = this.canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.width = rect.width;
    this.height = rect.height;
    this.canvas.width = this.width * dpr;
    this.canvas.height = this.height * dpr;
    this.ctx.scale(dpr, dpr);
  }

  initEntities() {
    this.particles = [];
    for (let i = 0; i < 45; i++) {
      this.particles.push({
        x: Math.random() * 480,
        y: Math.random() * 480,
        size: Math.random() * 2 + 1,
        speedX: (Math.random() - 0.5) * 0.4,
        speedY: (Math.random() - 0.5) * 0.4,
        alpha: Math.random() * 0.5 + 0.2,
      });
    }
  }

  loop(timestamp) {
    if (!this.lastTimestamp) this.lastTimestamp = timestamp;
    const deltaTime = timestamp - this.lastTimestamp;
    this.lastTimestamp = timestamp;

    if (!this.isHovered) {
      this.accumulator += deltaTime;
      while (this.accumulator >= this.frameDuration) {
        this.currentFrame = (this.currentFrame + 1) % this.totalFrames;
        this.accumulator -= this.frameDuration;
      }
    }

    this.render();
    requestAnimationFrame((t) => this.loop(t));
  }

  render() {
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;

    // Clear background
    ctx.fillStyle = "#030611";
    ctx.fillRect(0, 0, w, h);

    // Subtle Cyber Grid & Floating Particles
    this.drawBackground(ctx, w, h);

    // 5 Story Beats (300 frames each = 10s each, total 1500 frames = 50s)
    const f = this.currentFrame;

    if (f < 300) {
      this.renderScene1(ctx, w, h, f); // 0s - 10s: Antigravity Core Awakening
    } else if (f < 600) {
      this.renderScene2(ctx, w, h, f - 300); // 10s - 20s: The Bottleneck
    } else if (f < 900) {
      this.renderScene3(ctx, w, h, f - 600); // 20s - 30s: 4 Bất Biến Kỹ Thuật
    } else if (f < 1200) {
      this.renderScene4(ctx, w, h, f - 900); // 30s - 40s: Cấu Trúc 1 Skill Thực Tế
    } else {
      this.renderScene5(ctx, w, h, f - 1200); // 40s - 50s: Custom Cho Antigravity CLI
    }
  }

  drawBackground(ctx, w, h) {
    ctx.save();
    // Grid lines
    ctx.strokeStyle = "rgba(15, 23, 42, 0.6)";
    ctx.lineWidth = 1;
    const step = 32;
    for (let x = 0; x < w; x += step) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
    }
    for (let y = 0; y < h; y += step) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }

    // Particles
    ctx.fillStyle = "#6ee7b7";
    for (let p of this.particles) {
      p.x += p.speedX;
      p.y += p.speedY;
      if (p.x < 0) p.x = w;
      if (p.x > w) p.x = 0;
      if (p.y < 0) p.y = h;
      if (p.y > h) p.y = 0;

      ctx.globalAlpha = p.alpha * 0.4;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  }

  // =========================================================================
  // SCENE 1: Antigravity Core Awakening & Identity (0s - 10s | Frames 0 - 300)
  // =========================================================================
  renderScene1(ctx, w, h, f) {
    const cx = w / 2;
    const cy = 148; // Nâng cao vị trí AGY core để tạo khoảng cách thoáng đãng với title
    const fadeIn = Math.min(1, f / 30);
    const fadeOut = f > 270 ? Math.max(0, (300 - f) / 30) : 1;
    const alpha = fadeIn * fadeOut;

    ctx.save();
    ctx.globalAlpha = alpha;

    // Glowing Neon Orbital Rings
    const orbitRadius = 76;
    const rot = f * 0.02;

    ctx.strokeStyle = "rgba(110, 231, 183, 0.25)";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(cx, cy, orbitRadius, 0, Math.PI * 2);
    ctx.stroke();

    ctx.strokeStyle = "rgba(16, 185, 129, 0.15)";
    ctx.beginPath();
    ctx.arc(cx, cy, orbitRadius + 16, 0, Math.PI * 2);
    ctx.stroke();

    // Central Antigravity Reactor Core
    const pulse = Math.sin(f * 0.1) * 4;
    const radGrad = ctx.createRadialGradient(cx, cy, 10, cx, cy, 46 + pulse);
    radGrad.addColorStop(0, "rgba(110, 231, 183, 0.9)");
    radGrad.addColorStop(0.5, "rgba(16, 185, 129, 0.25)");
    radGrad.addColorStop(1, "transparent");

    ctx.fillStyle = radGrad;
    ctx.beginPath();
    ctx.arc(cx, cy, 46 + pulse, 0, Math.PI * 2);
    ctx.fill();

    // Core Box
    ctx.fillStyle = "#0b1329";
    ctx.strokeStyle = "#6ee7b7";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.roundRect(cx - 24, cy - 24, 48, 48, 12);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "#6ee7b7";
    ctx.font = 'bold 15px "JetBrains Mono", monospace';
    ctx.textAlign = "center";
    ctx.fillText("AGY", cx, cy + 5);

    // 5 Orbiting Satellite Skills (Phân bổ đều 360 / 5 = 72 độ)
    const skills = [
      { name: "BA", angle: 0 },
      { name: "Coding", angle: (2 * Math.PI / 5) * 1 },
      { name: "UI & 3D", angle: (2 * Math.PI / 5) * 2 },
      { name: "System", angle: (2 * Math.PI / 5) * 3 },
      { name: "Spec", angle: (2 * Math.PI / 5) * 4 },
    ];

    skills.forEach((s) => {
      const a = s.angle + rot;
      const sx = cx + Math.cos(a) * orbitRadius;
      const sy = cy + Math.sin(a) * orbitRadius;

      // Đo độ dài text để co giãn card vừa vặn
      ctx.font = '10.5px "Inter", sans-serif';
      const textMetrics = ctx.measureText(s.name);
      const pillW = Math.max(54, textMetrics.width + 16);
      const pillH = 22;

      ctx.fillStyle = "#0f172a";
      ctx.strokeStyle = "rgba(110, 231, 183, 0.4)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(sx - pillW / 2, sy - pillH / 2, pillW, pillH, pillH / 2);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = "#ffffff";
      ctx.textAlign = "center";
      ctx.fillText(s.name, sx, sy + 3.5);
    });

    // Title & Typography below
    const textY = 286;
    ctx.fillStyle = "#ffffff";
    ctx.font = 'bold 22px "Inter", sans-serif';
    ctx.textAlign = "center";
    ctx.fillText("agent_setup", cx, textY);

    ctx.fillStyle = "#6ee7b7";
    ctx.font = '12.5px "Inter", sans-serif';
    ctx.fillText("Dạy nghề cho AI · 50+ Kỹ năng chuyên sâu", cx, textY + 22);

    ctx.fillStyle = "#94a3b8";
    ctx.font = '11px "JetBrains Mono", monospace';
    ctx.fillText("Customized for Antigravity · by Jin", cx, textY + 42);

    // Bottom Badges
    const badgeY = textY + 70;
    const badges = ["★ 50+ Skills", "Antigravity CLI", "MIT License"];
    badges.forEach((b, idx) => {
      const bx = cx + (idx - 1) * 115;
      ctx.fillStyle = "rgba(255, 255, 255, 0.05)";
      ctx.strokeStyle = "rgba(255, 255, 255, 0.12)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(bx - 50, badgeY - 11, 100, 22, 11);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = "#e2e8f0";
      ctx.font = '10px "Inter", sans-serif';
      ctx.fillText(b, bx, badgeY + 3.5);
    });

    ctx.restore();
  }

  // =========================================================================
  // SCENE 2: The Bottleneck (10s - 20s | Frames 300 - 600)
  // =========================================================================
  renderScene2(ctx, w, h, f) {
    const cx = w / 2;
    const fadeIn = Math.min(1, f / 30);
    const fadeOut = f > 270 ? Math.max(0, (300 - f) / 30) : 1;
    const alpha = fadeIn * fadeOut;

    ctx.save();
    ctx.globalAlpha = alpha;

    // Header
    ctx.fillStyle = "#ffffff";
    ctx.font = 'bold 18px "Inter", sans-serif';
    ctx.textAlign = "center";
    ctx.fillText("Nút thắt không nằm ở model.", cx, 48);

    ctx.fillStyle = "#6ee7b7";
    ctx.font = '13px "Inter", sans-serif';
    ctx.fillText("Nút thắt là thiếu kỹ năng chuẩn và kỷ luật.", cx, 70);

    // Pulsing Brain Node in Center
    const brainY = 118;
    ctx.fillStyle = "rgba(239, 68, 68, 0.12)";
    ctx.strokeStyle = "rgba(239, 68, 68, 0.4)";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(cx, brainY, 26 + Math.sin(f * 0.1) * 2, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "#ef4444";
    ctx.font = 'bold 12px "JetBrains Mono", monospace';
    ctx.fillText("AI FAULT", cx, brainY + 4);

    // 3 Hazard Warning Cards
    const cards = [
      {
        title: "1. Đoán mò & Over-engineering",
        desc: "Tự dựng 200 dòng pattern thừa thãi cho 1 hàm đơn giản",
      },
      {
        title: "2. Sửa lung tung (Messy Diffs)",
        desc: "Tiện tay refactor phá hỏng code vùng lân cận",
      },
      {
        title: "3. Làm bẩn môi trường máy",
        desc: "Cài đặt dependencies vào global system bừa bãi",
      },
    ];

    const cardW = Math.min(380, w - 48);
    const cardH = 58;
    const startY = 168;

    cards.forEach((c, idx) => {
      const y = startY + idx * (cardH + 12);
      const cardSlide = Math.min(1, Math.max(0, (f - idx * 25) / 30));

      ctx.save();
      ctx.globalAlpha = alpha * cardSlide;

      ctx.fillStyle = "rgba(239, 68, 68, 0.08)";
      ctx.strokeStyle = "rgba(239, 68, 68, 0.3)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect((w - cardW) / 2, y, cardW, cardH, 8);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = "#ef4444";
      ctx.font = 'bold 12.5px "Inter", sans-serif';
      ctx.textAlign = "left";
      ctx.fillText(c.title, (w - cardW) / 2 + 16, y + 24);

      ctx.fillStyle = "#94a3b8";
      ctx.font = '11px "Inter", sans-serif';
      ctx.fillText(c.desc, (w - cardW) / 2 + 16, y + 43);

      ctx.restore();
    });

    ctx.restore();
  }

  // =========================================================================
  // SCENE 3: 4 Bất Biến Kỹ Thuật (20s - 30s | Frames 600 - 900)
  // =========================================================================
  renderScene3(ctx, w, h, f) {
    const cx = w / 2;
    const fadeIn = Math.min(1, f / 30);
    const fadeOut = f > 270 ? Math.max(0, (300 - f) / 30) : 1;
    const alpha = fadeIn * fadeOut;

    ctx.save();
    ctx.globalAlpha = alpha;

    ctx.fillStyle = "#6ee7b7";
    ctx.font = '11px "JetBrains Mono", monospace';
    ctx.textAlign = "center";
    ctx.fillText("KARPATHY LESSONS · AGENTS.MD", cx, 42);

    ctx.fillStyle = "#ffffff";
    ctx.font = 'bold 18px "Inter", sans-serif';
    ctx.fillText("4 Bất Biến Kỹ Thuật", cx, 66);

    const rules = [
      {
        num: "01",
        title: "Think Before Coding",
        desc: "Không đoán mò. Nêu rõ giả định & đánh đổi trước khi code.",
      },
      {
        num: "02",
        Simplicity: "Simplicity First",
        desc: "Lượng code tối thiểu. Không thiết kế cho tương lai tưởng tượng.",
      },
      {
        num: "03",
        title: "Surgical Changes",
        desc: "Sửa đúng chỗ. Giữ nguyên style codebase. Diff sạch 100%.",
      },
      {
        num: "04",
        title: "Strict Isolation",
        desc: "Cô lập tuyệt đối trong workspace (.venv). Không đụng global.",
      },
    ];

    const boxW = 188;
    const boxH = 126;
    const gapX = 14;
    const gapY = 14;
    const startX = cx - boxW - gapX / 2;
    const startY = 96;

    rules.forEach((r, idx) => {
      const col = idx % 2;
      const row = Math.floor(idx / 2);
      const bx = startX + col * (boxW + gapX);
      const by = startY + row * (boxH + gapY);

      ctx.fillStyle = "#0f172a";
      ctx.strokeStyle = "rgba(110, 231, 183, 0.25)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(bx, by, boxW, boxH, 10);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = "#6ee7b7";
      ctx.font = 'bold 11px "JetBrains Mono", monospace';
      ctx.textAlign = "left";
      ctx.fillText(r.num, bx + 12, by + 22);

      ctx.fillStyle = "#ffffff";
      ctx.font = 'bold 12px "Inter", sans-serif';
      ctx.fillText(r.title || r.Simplicity, bx + 12, by + 42);

      ctx.fillStyle = "#94a3b8";
      ctx.font = '10.5px "Inter", sans-serif';
      this.wrapText(ctx, r.desc, bx + 12, by + 64, boxW - 24, 15);
    });

    ctx.restore();
  }

  // =========================================================================
  // SCENE 4: Cấu Trúc 1 Skill Thực Tế (30s - 40s | Frames 900 - 1200)
  // =========================================================================
  renderScene4(ctx, w, h, f) {
    const cx = w / 2;
    const fadeIn = Math.min(1, f / 30);
    const fadeOut = f > 270 ? Math.max(0, (300 - f) / 30) : 1;
    const alpha = fadeIn * fadeOut;

    ctx.save();
    ctx.globalAlpha = alpha;

    ctx.fillStyle = "#6ee7b7";
    ctx.font = '11px "JetBrains Mono", monospace';
    ctx.textAlign = "center";
    ctx.fillText("ANATOMY OF A SKILL", cx, 42);

    ctx.fillStyle = "#ffffff";
    ctx.font = 'bold 18px "Inter", sans-serif';
    ctx.fillText("Cấu Trúc 1 Kỹ Năng Chuẩn", cx, 66);

    // Code Window
    const winW = Math.min(390, w - 48);
    const winH = 170;
    const winX = (w - winW) / 2;
    const winY = 94;

    ctx.fillStyle = "#080d1a";
    ctx.strokeStyle = "rgba(110, 231, 183, 0.3)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.roundRect(winX, winY, winW, winH, 10);
    ctx.fill();
    ctx.stroke();

    // Window Header
    ctx.fillStyle = "#0d1527";
    ctx.beginPath();
    ctx.roundRect(winX, winY, winW, 32, [10, 10, 0, 0]);
    ctx.fill();

    ctx.fillStyle = "#6ee7b7";
    ctx.font = '11.5px "JetBrains Mono", monospace';
    ctx.textAlign = "left";
    ctx.fillText(".agents/skills/clean-code/", winX + 16, winY + 20);

    // Tree lines
    const items = [
      { icon: "📄", name: "SKILL.md", desc: "Quy chuẩn & trigger prompts" },
      { icon: "📁", name: "scripts/", desc: "Mã nguồn thực thi tự động" },
      { icon: "📁", name: "references/", desc: "66 quy tắc Clean Code" },
    ];

    items.forEach((item, idx) => {
      const iy = winY + 62 + idx * 36;
      ctx.fillStyle = "#ffffff";
      ctx.font = '12px "JetBrains Mono", monospace';
      ctx.fillText(`${item.icon} ${item.name}`, winX + 18, iy);

      ctx.fillStyle = "#94a3b8";
      ctx.font = '11px "Inter", sans-serif';
      ctx.textAlign = "right";
      ctx.fillText(item.desc, winX + winW - 16, iy);
      ctx.textAlign = "left";
    });

    // Efficiency Bottom Card
    const effY = winY + winH + 18;
    ctx.fillStyle = "rgba(16, 185, 129, 0.08)";
    ctx.strokeStyle = "rgba(16, 185, 129, 0.3)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.roundRect(winX, effY, winW, 60, 8);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "#ffffff";
    ctx.font = 'bold 12.5px "Inter", sans-serif';
    ctx.fillText("Nạp kỹ năng động theo ngữ cảnh", winX + 16, effY + 24);

    ctx.fillStyle = "#94a3b8";
    ctx.font = '11px "Inter", sans-serif';
    ctx.fillText("Không làm phình to context window", winX + 16, effY + 44);

    ctx.fillStyle = "#6ee7b7";
    ctx.font = 'bold 16px "JetBrains Mono", monospace';
    ctx.textAlign = "right";
    ctx.fillText("10x Gọn", winX + winW - 16, effY + 36);

    ctx.restore();
  }

  // =========================================================================
  // SCENE 5: Custom Cho Antigravity CLI & Cài Đặt (40s - 50s | Frames 1200 - 1500)
  // =========================================================================
  renderScene5(ctx, w, h, f) {
    const cx = w / 2;
    const fadeIn = Math.min(1, f / 30);
    const fadeOut = f > 270 ? Math.max(0, (300 - f) / 30) : 1;
    const alpha = fadeIn * fadeOut;

    ctx.save();
    ctx.globalAlpha = alpha;

    ctx.fillStyle = "#6ee7b7";
    ctx.font = '11px "JetBrains Mono", monospace';
    ctx.textAlign = "center";
    ctx.fillText("ANTIGRAVITY CLI ENGINE", cx, 42);

    ctx.fillStyle = "#ffffff";
    ctx.font = 'bold 17px "Inter", sans-serif';
    ctx.fillText("Custom Riêng Cho Antigravity", cx, 66);

    // Terminal Card
    const termW = Math.min(390, w - 48);
    const termH = 150;
    const termX = (w - termW) / 2;
    const termY = 96;

    ctx.fillStyle = "#060b16";
    ctx.strokeStyle = "rgba(110, 231, 183, 0.35)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.roundRect(termX, termY, termW, termH, 10);
    ctx.fill();
    ctx.stroke();

    ctx.font = '12px "JetBrains Mono", monospace';
    ctx.textAlign = "left";

    ctx.fillStyle = "#94a3b8";
    ctx.fillText(
      "# 1. Sao chép cấu hình vào project root",
      termX + 16,
      termY + 30,
    );

    ctx.fillStyle = "#6ee7b7";
    ctx.fillText("$ cp -r agent_setup/.agents ./", termX + 16, termY + 54);
    ctx.fillText("$ cp agent_setup/AGENTS.md ./", termX + 16, termY + 74);

    ctx.fillStyle = "#94a3b8";
    ctx.fillText("# 2. Khởi chạy Antigravity CLI", termX + 16, termY + 104);

    ctx.fillStyle = "#6ee7b7";
    ctx.fillText("$ agy", termX + 16, termY + 128);

    // Ready Status
    const statY = termY + termH + 24;
    ctx.fillStyle = "rgba(16, 185, 129, 0.12)";
    ctx.strokeStyle = "#10b981";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.roundRect((w - 290) / 2, statY, 290, 32, 16);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "#6ee7b7";
    ctx.font = 'bold 11px "JetBrains Mono", monospace';
    ctx.textAlign = "center";
    ctx.fillText("⚡ 50+ SKILLS LOADED & READY", cx, statY + 20);

    ctx.restore();
  }

  wrapText(ctx, text, x, y, maxWidth, lineHeight) {
    const words = text.split(" ");
    let line = "";
    let currY = y;

    for (let n = 0; n < words.length; n++) {
      const testLine = line + words[n] + " ";
      const metrics = ctx.measureText(testLine);
      const testWidth = metrics.width;
      if (testWidth > maxWidth && n > 0) {
        ctx.fillText(line, x, currY);
        line = words[n] + " ";
        currY += lineHeight;
      } else {
        line = testLine;
      }
    }
    ctx.fillText(line, x, currY);
  }
}
