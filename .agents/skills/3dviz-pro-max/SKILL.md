---
name: 3dviz-pro-max
description: "3D visualization and spatial scene design intelligence for web, desktop, and creative engineering. Use when designing, building, inspecting, or refining 3D scenes, WebGL/Three.js interactive models, scientific visualizations, mechanical assemblies, and dioramas. Searchable local catalog: 24 domain directions, 223 recipes, 440 knowledge records (37 style profiles, 22 lighting rigs, 22 blueprint kits, material/motion profiles), 5 starter rigs, Vite+Three.js scaffold, and automated inspection checklists."
---

# 3Dviz Pro Max - 3D Visualization & Spatial Intelligence

Searchable local 3D guidance: 24 domain directions, 223 recipes, 440 knowledge records across 18 families (37 style profiles, 22 lighting rigs, 22 blueprint kits, material/motion/geometry profiles), 5 reusable starter rigs, a production Vite + Three.js scaffold, and automated inspection checklists.

Use the agent's spatial reasoning, geometry, composition, and programming abilities to realize the user's idea. The catalog, kits, rigs, and scripts accelerate decisions and construction; they do not set the boundaries of what you can make. A runnable scene still needs visual judgment.

---

## When to Apply

Use this Skill when the task involves **3D creation, spatial modeling, WebGL rendering, or interactive scene inspection**:
- **Interactive 3D Web & Dioramas**: Building explorable 3D web scenes, environments, games, or dioramas using Three.js, WebGL, or WebGPU.
- **Scientific & Technical Visualizations**: Modeling anatomy, physiology, molecular structures, physics simulations, or advanced mathematics (linear algebra, calculus, topology).
- **Engineering & Systems**: Mechanical assemblies (gears, linkages), robotics kinematics, operational logistics, architectural spaces, or abstract systems (Agent Harness, service graphs).
- **Lighting & Aesthetics**: Directing 3D lighting rigs (studio, dusk golden hour, night lantern practicals), camera staging, PBR materials (roughness, metalness, transmission), and post-processing.
- **Blender $\leftrightarrow$ Three.js Asset Pipeline**: Coordinating modeling, sculpting, UV unwrapping, baking, rigging, and GLTF/GLB optimization between Blender and Three.js.
- **Quality Control & Anti-Slop**: Inspecting rendered frames for contrast, clipping, camera angles, contact shadows, and motion legibility instead of hallucinating descriptions.

---

## Ecosystem & Specialized Sub-Skills Routing

When a task expands into specialized domains, **automatically reference and activate** the corresponding sibling skills located in `.agents/skills/`:

| Specialized Need | Sibling Skill | Trigger Conditions |
|:---|:---|:---|
| **2D UI/UX & Web Interface** | `ui-ux-pro-max` | Designing the web interface, HUD, controls, overlays, or dashboard wrapping the 3D canvas. |
| **Component Styling & Canvas Wrappers** | `ui-styling` | Styling canvas containers, toolbars, buttons, dialogs with Tailwind CSS or shadcn/ui. |
| **Design Tokens & Palette Harmony** | `design-system` | Syncing 3D scene lighting/material palettes with application UI tokens and CSS variables. |
| **System Architecture & Technical Diagrams** | `diagram-design` | Creating 2D/3D architecture, flowcharts, network topologies, sequence, or ER diagrams. |
| **Interactive Standalone HTML Artifacts** | `design-artifact` / `html-prototype` | Building self-contained single-file HTML deliverables, interactive demos, or prototypes. |
| **Code Quality & Architecture Standards** | `clean-code` | Enforcing Clean Code, SOLID principles, and Boy Scout Rule across Three.js / JS / TS codebases. |

---

## Running the Search & Context Tools

The search and retrieval scripts are self-contained within this skill directory and use standard Python 3 (stdlib only, zero external pip packages required). Run them from your workspace root:

*(On Windows, use `python`; on Linux/macOS, use `python3` or `python`).*

### 1. BM25 Search across 663 Records
Search recipes and knowledge profiles by plain text query:
```bash
python .agents/skills/3dviz-pro-max/scripts/search.py "<subject or query>" [options]
```

**Common Examples:**
- Search by subject: `python .agents/skills/3dviz-pro-max/scripts/search.py "fantasy village"`
- Search recipes only: `python .agents/skills/3dviz-pro-max/scripts/search.py "mechanical gears" --collection recipes`
- Filter by knowledge kind: `python .agents/skills/3dviz-pro-max/scripts/search.py "dusk" --kind lighting-profile`
- Filter by direction: `python .agents/skills/3dviz-pro-max/scripts/search.py "heart" --direction anatomy-structures`

### 2. Gather Complete Design Context
Aggregate matching recipes, style profiles, and blueprints for an objective:
```bash
python .agents/skills/3dviz-pro-max/scripts/design-context.py "<objective>" --blueprints --look <style-id>
```

**Example:**
```bash
python .agents/skills/3dviz-pro-max/scripts/design-context.py "fantasy village" --blueprints --look knowledge.style-clay
```

### 3. Resolve Detailed Record by ID
Inspect the complete JSON schema, entities, motion guidance, and limits of a specific record:
```bash
python .agents/skills/3dviz-pro-max/scripts/resolve.py <record-id>
```

**Example:**
```bash
python .agents/skills/3dviz-pro-max/scripts/resolve.py recipe.fantasy-village-diorama
```

### 4. Discover Host Environment Capabilities
Probe for installed tools (Blender, Node, Python, Playwright, GPU hardware renderer):
```bash
python .agents/skills/3dviz-pro-max/scripts/host-probe.py [--out host.json]
```

---

## Workflow (10 Steps)

For a new scene, work through the decisions below. For an existing artifact, inspect it first and apply only the steps affected by the change. User constraints override suggested tooling and records.

1. **Intent and visual direction.** Identify what the viewer should see, feel, understand or do. Choose a distinctive visual idea, useful references, and the intended viewing distance. Decide how shape, material, light, camera, and motion work together. Time of day matters for some environments; an anatomical study or mathematical object may need a studio, diagrammatic, or invented setting.
2. **Reason about the important objects.** Before selecting a template, identify the silhouette, proportions, parts, connections, surface identity, and behavior that make each important object convincing. Use [object reasoning](references/object-reasoning.md) and [object craft](references/object-craft.md). Solve the hardest or most distinctive object early.
3. **Ground the representation.** Choose illustration, discrete state, simulation, or playback; a scene can combine them if their boundaries are clear. For established academic, scientific, or technical claims, research the actual passages and fact-check `claim → model → rendered result` using [research and truth](references/research-and-truth.md). A decorative mesh, imported anatomy, or physics engine does not certify a scientific claim. Identify the authoritative state.
4. **Choose construction per object.** Use the routing table below. Search for the missing decision when useful; do not force a subject into the closest lexical match. Recipes, numerical defaults, and look profiles are candidates to adapt, not instructions to copy every value. At important joins, decide whether the object needs a continuous skin, a layered covering, or separate articulated parts. Use [surface continuity](references/object-craft.md#choose-continuity-at-the-join) when attached volumes look accidental; mesh merging is not a universal cleanup prescription.
5. **Set quality targets and discover tools.** State what the object must withstand at overview, inspection, and close-up distances, including factual fidelity where relevant. Discover available tools via `host-probe.py`. T0–T4 describe existing kit pipelines and declared proof status. Blender availability does not make an object high quality; Three.js-only procedural construction does not make it low quality.
6. **Build a convincing first view.** Keep the user's stack. Reuse shared scripts, renderer setup, [rigs and scaffold](templates/README.md), material utilities, and geometry operations where they help. For a large scene or collection, inspect one representative demanding object or scene before multiplying the approach. Author custom geometry, shaders, materials, textures, lighting, and interactions as needed. For lighting changes, read [lighting direction and scale](references/lighting-direction-and-scale.md) before implementing the rig.
7. **Make behavior belong to the model.** Keep transforms, joints, contacts, and controls tied to their authoritative state. Inspect surrounding objects too: a stand needs support, a light ray must stop at an opaque obstacle in its modeled scene, a creature needs clearance. Allocate reusable geometry once where practical; update transforms, uniforms, or buffers during motion. Park static scenes and respect reduced-motion preferences. Use [subject clarity and meaningful motion](references/subject-clarity-and-motion.md).
8. **Run and inspect the real output.** Build through the project's existing commands, then view the artifact in an available authorized browser. Inspect overview, meaningful close-ups, and the important interactions. If automated capture is allowed via Playwright:
   ```bash
   pnpm build
   python .agents/skills/3dviz-pro-max/scripts/capture.py --dir dist --all-views --click "#control" --out captures
   ```
   Never describe an unobserved frame. Check affected receivers and occluders, not just glowing bulbs.
9. **Refine by subject and evidence.** Use [visual review](templates/checklists/visual-anti-slop.md) and [interaction/frame inspection](templates/checklists/inspection-per-frame.md) as conditional prompts. Correct factual errors, broken controls, and misleading relationships, then improve the most consequential visual weakness. For pinching, detached attachments, or repeated pose fixes, use [regional deformation diagnosis](references/object-craft.md#diagnose-deformation-at-the-region-that-fails).
10. **Report honestly.** Separate what was built, observed, numerically checked, and still limited. Build success and collection completion do not establish artistic approval or subject clarity. For substantial deliverables, keep useful decisions in [design-system.md](templates/docs/design-system.md), [scene-spec.json](templates/docs/scene-spec.json), and [validation-report.md](templates/docs/validation-report.md) when requested.

---

## Construction Routing

| Route | When it helps | What to preserve |
|:---|:---|:---|
| **Reuse a kit directly** | Its shape, structure, behavior, and finish already fit the actual brief. | Inspect it at the intended distance; a kit can be a hero when it fits. |
| **Adapt a kit or compose parts** | Common construction is useful, but identity or behavior differs. | Change silhouette, proportions, joins, materials, or articulation; recoloring alone may not suffice. |
| **Author custom geometry/rigs** | A distinctive hero, analytical form, reference, or mechanism needs another solution. | Reuse low-level operations and tooling; custom does not mean rewriting infrastructure. |
| **Use a suitable external asset** | Authored/scanned/source geometry fits the subject better than reconstruction. | Verify provenance, rights, scale, registration, topology, and what the asset actually represents. |
| **Combine methods** | Different parts or roles benefit from different approaches. | Keep style, scale, state ownership, and interfaces coherent. |

Neither hero/background role nor Blender/Three.js decides the route by itself. Reuse the mechanism of construction freely; reuse a finished shape only when it fits.

---

## Core References (Read Only What Helps)

- **[Catalog Index](references/catalog-index.md)**: Candidates by topic across 24 directions.
- **[Object Reasoning](references/object-reasoning.md)**: Silhouette, proportions, parts, connections, and behavior.
- **[Object Craft](references/object-craft.md)**: Form, materials, joins, and surface continuity.
- **[Lighting Direction & Scale](references/lighting-direction-and-scale.md)**: Emitter/receiver ownership, azimuth, elevation, and rescale laws.
- **[Blender / Three.js Handoff](references/blender-threejs-handoff.md)**: Asset transport, UVs, baking, normals, and animations.
- **[Subject Clarity & Motion](references/subject-clarity-and-motion.md)**: Meaningful movement, state synchronization, and reduced-motion support.
- **[Physical Interaction](references/physical-interaction.md)**: Support, clearance, contact, and causality.
- **[Research and Truth](references/research-and-truth.md)**: Grounding scientific, anatomical, and mathematical claims.
- **[Design Synthesis](references/design-synthesis.md)**: Coherent visual system without uniform repetition.
- **[Kits & Blueprints](templates/kits/README.md)**: 22 proved blueprints and scoped pipeline proofs.
- **[Starter Scaffold & Rigs](templates/README.md)**: Vite + Three.js scaffold and 5 modular rigs.
- **[Visual Anti-Slop Checklist](templates/checklists/visual-anti-slop.md)**: Inspection checklist to eliminate AI visual slop.

---

## Small Edits

Inspect and change the affected behavior or visual directly. Preserve working interactions and the user's choices. A text, color, or small geometry edit does not require a new scene or full workflow.
