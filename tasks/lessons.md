# Lessons Learned

## Antigravity Skill Specification & Directory Standards
1. **Self-Contained Encapsulation:** Every Antigravity skill must be completely self-contained within `.agents/skills/<skill-name>/`.
2. **References Location:** Reference files must reside in `.agents/skills/<skill-name>/references/` (or child directories of the skill) rather than a global top-level `.agents/references/` folder. This guarantees that copying `.agents/` or any individual skill to another project/repository retains 100% functionality without broken dependencies.
3. **Relative Pathing in `SKILL.md`:** Reference links within `SKILL.md` should use relative paths (e.g. `references/<file>.md` or `./references/<file>.md`), avoiding hardcoded `.agents/...` or `@.agents/...` paths which can break when skills are relocated.

## Clean Code Architectures & Scope Adherence
1. **Strict User Scope Adherence:** Never add speculative or unrequested rules (e.g., A1-A10 agent smells or anti-loopholes) when the user explicitly restricts which sections of a source repository to include.
2. **The Boy Scout Rule as Core:** Continuous, small, behavior-preserving improvements with every touch prevent technical debt accumulation without the risk and friction of massive "Big-Bang" refactorings.
3. **Pure Markdown with Modular Enhancements:** Combining canonical rule IDs (66 rules) with local offline AST/lexer scripts and multi-stack reference packs provides targeted guidance while staying minimal and disciplined.

## System Design Skills & Architectural Reasoning
1. **Reasoning Over Memorization:** System design is not about memorizing static textbook diagrams, but about hypothesizing solutions based on strict constraints and knowing how the design changes when constraints evolve.
2. **Quantitative Anchoring:** Qualitative statements like "high traffic" are meaningless; every architecture must be grounded in Back-of-the-Envelope numbers (QPS, peak QPS, storage growth, latency SLAs).
3. **Solves / Worsens / Change It When:** Every technology introduced must state what problem it solves, what complexity it adds/worsens, and the exact threshold that would trigger replacing it.
4. **Complementary Ecosystems:** Combining `wondelai`'s end-to-end common designs and 10/10 scoring with `proyecto26`'s 22-block modular taxonomy, cloud provider mappings, and diagram engine provides the ideal blueprint for an enterprise-grade system-design skill.
5. **Zero Pollution in Skills Workspaces:** In metadata and agent skill setup repositories (`agent_setup`), avoid creating virtual environments or managing external package toolchains. Utility scripts should rely strictly on standard libraries and remain lightweight file assets.
6. **Three-Layer Documentation Harmony:** To prevent architecture erosion, skills must divide outputs cleanly between living invariants (`docs/architecture/`), delivery artifacts (`docs/implementation/{release}/`), and business scope (`docs/business/`). System design skills must hand off detailed interface patterns to specialized API skills via structured summaries instead of duplicating concerns.
7. **Pure Markdown Invariant vs On-Demand Visual Views (`docs/views/`):** Analytical and specification skills (`product-requirements`, `system-design`, `api-design-patterns`, `documentation`, `user-story-ac-writer`) must focus strictly on deep analysis, domain logic, and clean Markdown (`.md`) documentation using native Mermaid blocks. Core documentation layers (`docs/business/`, `docs/architecture/`, `docs/implementation/`) must never be polluted with inline HTML, scripts, CSS, or binary image dumps. All visual, styled, or interactive views must be centralized strictly into `docs/views/`, generated on-demand only upon user request, and delegated to dedicated visual specialist skills (`diagram-design`, `html-diagram`, `html-prototype`, `html-wireframe`, `html-plan`, `design-artifact`, `html`).

