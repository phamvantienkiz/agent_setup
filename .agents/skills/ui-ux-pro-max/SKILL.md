---
name: ui-ux-pro-max
description: "UI/UX design intelligence for web, mobile, and desktop. This skill should be used when designing, building, reviewing, or fixing interfaces, including pages, components, design systems, accessibility, interaction, responsive layout, typography, color, charts, and stack-specific UI implementation. Searchable local data: 79 searchable styles (50 active), 192 product palettes and reasoning profiles, 74 font pairings, 119 UX guidelines, 105 icons, 17 GSAP presets, 25 chart types, and 22 stacks."
---

# UI/UX Pro Max - Design Intelligence

Searchable local UI/UX guidance: 79 searchable styles (50 active), 192 product palettes and exact reasoning profiles, 74 font pairings, 119 UX guidelines, 105 curated icons, 17 GSAP presets, 25 chart types, and 22 technology stacks.

## When to Apply

Use this Skill when the task involves **UI structure, visual design decisions, interaction patterns, or user experience quality control**:
- Designing new pages (Landing Page, Dashboard, SaaS, Admin, Mobile App)
- Creating or refactoring UI components (buttons, modals, forms, tables, cards)
- Choosing color schemes, typography systems, spacing scales, or layout grids
- Reviewing UI for UX, accessibility (WCAG), or visual consistency
- Implementing animations, responsive breakpoints, or navigation patterns
- Implementing stack-specific UI best practices (React 19+, Tailwind v4, SwiftUI, Flutter, etc.)

Skip it for pure backend logic, API/database design, or non-visual automation unless the task impacts how something **looks, feels, moves, or is interacted with**.

---

## Ecosystem & Specialized Sub-Skills Routing

When a task expands into specialized domains, **automatically reference and activate** the corresponding sibling skills located in `.agents/skills/`:

| Specialized Need | Sibling Skill | Trigger Conditions |
|:---|:---|:---|
| **Design Tokens & System Architecture** | `design-system` | Establishing 3-tier token architecture (`primitive → semantic → component`), CSS variables system, component specs, or design-to-code token handoff. |
| **Component Styling & shadcn/ui** | `ui-styling` | Detailed styling with Tailwind CSS, shadcn/ui component integration, Radix accessibility patterns, dark mode theming, or form UI patterns. |
| **Brand Identity & Guidelines** | `brand` | Defining brand voice, content tone, messaging frameworks, logo usage rules, or creating/syncing `docs/brand-guidelines.md`. |
| **Banners & Creative Assets** | `banner-design` | Designing banners, social covers (Facebook, X, LinkedIn, YouTube), display ads, website hero visuals, or print assets with format safe-zones. |
| **HTML Presentations & Pitch Decks** | `slides` | Building interactive HTML presentation slides with Chart.js, responsive slide layouts, and copywriting formulas. |

---

## Rule Categories by Priority (Quick Reference)

*Follow priority 1→10 to decide which category to focus on first. Full rule text for every category lives in `references/quick-reference.md`. Detailed app polish rules live in `references/pro-rules.md`.*

| Priority | Category | Impact | Domain | Key Checks (Must Have) | Anti-Patterns (Avoid) |
|:---|:---|:---|:---|:---|:---|
| 1 | **Accessibility** | CRITICAL | `ux` | Contrast 4.5:1, Alt text, Keyboard nav, Aria-labels | Removing focus rings, Icon-only buttons without labels |
| 2 | **Touch & Interaction** | CRITICAL | `ux` | Min size 44×44px, 8px+ spacing, Loading feedback | Reliance on hover only, Instant state changes (0ms) |
| 3 | **Performance** | HIGH | `ux` | WebP/AVIF, Lazy loading, Reserve space (CLS &lt; 0.1) | Layout thrashing, Cumulative Layout Shift |
| 4 | **Style Selection** | HIGH | `style`, `product` | Match product type, Consistency, SVG icons (no emoji) | Mixing flat & skeuomorphic randomly, Emoji as icons |
| 5 | **Layout & Responsive** | HIGH | `ux` | Mobile-first breakpoints, Viewport meta, No horizontal scroll | Horizontal scroll, Fixed px container widths, Disable zoom |
| 6 | **Typography & Color** | MEDIUM | `typography`, `color` | Base 16px, Line-height 1.5, Semantic color tokens | Text &lt; 12px body, Gray-on-gray, Raw hex in components |
| 7 | **Animation** | MEDIUM | `ux`, `gsap` | Context-aware timing, Motion conveys meaning, Spatial continuity | One duration for every transition, Animating width/height, No reduced-motion |
| 8 | **Forms & Feedback** | MEDIUM | `ux` | Visible labels, Error near field, Helper text, Progressive disclosure | Placeholder-only label, Errors only at top, Overwhelm upfront |
| 9 | **Navigation Patterns** | HIGH | `ux` | Predictable back, Bottom nav ≤5, Deep linking | Overloaded nav, Broken back behavior, No deep links |
| 10 | **Charts & Data** | LOW | `chart` | Legends, Tooltips, Accessible colors | Relying on color alone to convey meaning |

---

## Running the Search Tool

The search script is self-contained within this skill directory and uses standard Python 3 (no pip packages or network access required). Run it from your workspace:

```bash
python .agents/skills/ui-ux-pro-max/scripts/search.py "<query>" [options]
```

*(On Windows, use `python`; on Linux/macOS, use `python3` or `python`).*

### Mode 1: Generate Complete Design System (New Projects / Pages)

Use `--design-system` when the task needs a coherent, product-wide visual direction:

```bash
python .agents/skills/ui-ux-pro-max/scripts/search.py "<product_type> <keywords>" --design-system [-p "Project Name"]
```

**Example:**
```bash
python .agents/skills/ui-ux-pro-max/scripts/search.py "fintech crypto wallet" --design-system -p "CryptoPay"
```

#### Design Dials (1–10, optional with `--design-system`)
Tune the design system output with 3 sliders without altering your query:
```bash
python .agents/skills/ui-ux-pro-max/scripts/search.py "<query>" --design-system --variance <1-10> --motion <1-10> --density <1-10>
```
- `--variance` (1=centered/minimal, 10=bold/asymmetric)
- `--motion` (1=subtle, 10=complex; attaches matching GSAP snippet)
- `--density` (1=spacious, 10=dense/dashboard; overrides spacing scale tokens)

#### Persist Design System (Master + Overrides Pattern)
Save the design system to `design-system/<project-slug>/MASTER.md` for consistent cross-session retrieval:
```bash
python .agents/skills/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p "Project Name" --output-dir "."
```
To add page-specific overrides:
```bash
python .agents/skills/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p "Project Name" --page "dashboard" --output-dir "."
```

---

### Mode 2: Targeted Domain Search

Query specific design aspects using `--domain`:

```bash
python .agents/skills/ui-ux-pro-max/scripts/search.py "<query>" --domain <domain> [-n <max_results>]
```

| Need | Domain | Example Query |
|:---|:---|:---|
| Product patterns & styles | `product` | `"fintech banking" --domain product` |
| UI styles & visual directions | `style` | `"glassmorphism dark" --domain style` |
| Color palettes & contrast | `color` | `"saas analytics modern" --domain color` |
| Font pairings & typography | `typography` | `"editorial modern sans" --domain typography` |
| Individual Google Fonts | `google-fonts` | `"sans serif popular variable" --domain google-fonts` |
| Chart & data visualization | `chart` | `"real-time time-series" --domain chart` |
| UX guidelines & Do/Don't | `ux` | `"form error validation" --domain ux` |
| Landing page structures | `landing` | `"conversion social proof hero" --domain landing` |
| Icon recommendations & code | `icons` | `"navigation menu user" --domain icons` |
| GSAP animation presets | `gsap` | `"hover card transition" --domain gsap` |
| React/Next.js performance | `react` | `"list rerender memo" --domain react` |
| Mobile & Native app patterns | `web` | `"safe-area touch target" --domain web` |

---

### Mode 3: Technology Stack Guidelines

Get stack-specific idioms, Do/Don't guidelines, and concrete code examples:

```bash
python .agents/skills/ui-ux-pro-max/scripts/search.py "<query>" --stack <stack>
```

**Supported Stacks (22):**
`html-tailwind`, `react`, `nextjs`, `vue`, `svelte`, `astro`, `swiftui`, `react-native`, `flutter`, `shadcn`, `jetpack-compose`, `threejs`, `angular`, `laravel`, `javafx`, `wpf`, `winui`, `avalonia`, `uno`, `uwp`, `nuxtjs`, `nuxt-ui`.

**Example:**
```bash
python .agents/skills/ui-ux-pro-max/scripts/search.py "accessibility input label" --stack react
python .agents/skills/ui-ux-pro-max/scripts/search.py "responsive navbar" --stack html-tailwind
```

---

## Query Contract & Best Practices

1. **One intent per query:** Search for `"button focus indicator"`, not an entire page audit.
2. **2 to 5 meaningful terms:** Combine a domain term with a platform or interaction constraint.
3. **Verify results:** Check that the returned recommendation matches the project's actual stack and constraints.
4. **If 0 results found:** Retry once with broader terms or an explicit `--domain`/`--stack`. If still not found, state clearly that no database match occurred and use general defaults.
5. **Offline / Markdown Fallback:** If Python execution is disabled or unavailable, read the complete guidelines in `references/quick-reference.md` and `references/pro-rules.md` directly.

---

## Pre-Delivery Checklist (App UI)

Before concluding UI work, verify:
- [ ] No raw emojis used as icons (use SVG: Lucide, Heroicons, Phosphor)
- [ ] `cursor-pointer` on all interactive/clickable elements
- [ ] Hover states with smooth transitions (150–300ms)
- [ ] Text contrast meets WCAG 4.5:1 minimum (3:1 for large text)
- [ ] Focus rings visible for keyboard navigation (`:focus-visible`)
- [ ] `prefers-reduced-motion` media query respected
- [ ] Touch targets at least 44×44px (8px+ spacing between targets)
- [ ] Responsive layouts verified across mobile (375px), tablet (768px), and desktop (1024px, 1440px)
- [ ] Form inputs have associated `<label>` (not placeholder alone)
- [ ] No unexpected horizontal scrollbars on mobile viewports
