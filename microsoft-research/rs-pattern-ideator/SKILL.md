---
name: rs-pattern-ideator
description: Maps a confirmed research bottleneck to the empirical taxonomy of 15 Ideation Patterns and 31 Sub-patterns induced from 1,947 ICLR/ICML/NeurIPS Oral papers. Formulates 2-3 concrete, reviewer-defensible mechanism proposals with explicit mathematical operators or architectures. STOPS to discuss and co-decide with the human researcher.
allowed-tools: Read Write Edit Bash
metadata:
  framework: Microsoft Research Studio (HITL Edition)
  phase: "Pre-Paper Ideation (Phase 2)"
---

# RS Pattern Ideator

## Overview

Translate a confirmed research bottleneck into **concrete, implementable algorithmic or architectural mechanisms**. Instead of unconstrained brainstorming, this skill maps the problem to an empirical taxonomy of **15 Ideation Patterns** induced from 1,947 top-tier machine learning conference publications (ICLR, ICML, NeurIPS 2021–2025).

## The 15 Empirical Ideation Patterns (Reference in `references/patterns/`)

| ID | Pattern Name | Operational Signature |
| :--- | :--- | :--- |
| `assumption_audit_and_pivot` | Audit and Pivot an Assumption | Identify load-bearing implicit assumption $\rightarrow$ relax it (weaker condition) or violate it (counterexample/exploit) $\rightarrow$ re-derive guarantee or demonstrate new capability. |
| `architectural_operator_substitution` | Substitute Operator or Representation | Identify expensive operator/representation $\rightarrow$ substitute cheaper surrogate $\rightarrow$ prove it preserves essential property (expressivity, curvature, spectrum). |
| `generative_process_redesign` | Liberate Fixed Generative Component | Identify conventionally-fixed component (prior, trajectory, step schedule) $\rightarrow$ treat as free design variable $\rightarrow$ redesign for quality/efficiency. |
| `controlled_diagnostic_design` | Design Confound-Isolating Diagnostic | Identify confound inflating measurement $\rightarrow$ construct controlled instances that isolate it $\rightarrow$ measure true property vs artifact. |
| `unify_into_shared_representation` | Unify into Shared Representation | Identify heterogeneous inputs/tasks $\rightarrow$ map into one shared representation/vocabulary $\rightarrow$ process with a single uniform substrate. |
| `reframe_as_solvable_object` | Reframe as a Solvable Object | Recast intractable problem as well-studied mathematical object (convex program, equilibrium, combinatorial selection) $\rightarrow$ apply proven solvers. |
| `self_supervised_signal_engineering` | Manufacture Supervisory Signal | Formulate supervisory signal from intrinsic data structure (temporal order, geometric symmetry, cycle consistency) $\rightarrow$ train without manual annotations. |
| `structural_prior_encoding` | Encode Structure by Construction | Identify physical/mathematical invariant $\rightarrow$ hard-code symmetry/equivariance directly into neural architecture $\rightarrow$ eliminate empirical sample complexity. |
| `algebraic_equivalence_unification` | Prove Equivalence to Unify | Prove seemingly distinct methods are algebraically equivalent variants of a broader formulation $\rightarrow$ synthesize optimal composite method. |
| `heterogeneous_decomposition` | Decompose for Differentiated Treatment | Split problem/data into structurally distinct components $\rightarrow$ route each to specialized computational treatment. |
| `decompose_and_delegate` | Decompose and Delegate to Solvers | Decompose monolithic task into sub-problems $\rightarrow$ delegate each to specialized downstream solvers or foundation models. |
| `relax_discrete_search_to_continuous` | Relax Discrete Search to Continuous | Transform combinatorial or discrete optimization space into continuous, differentiable formulation $\rightarrow$ optimize via Gradient Descent. |
| `adapt_via_conditioning` | Adapt by Conditioning | Achieve specialization by conditioning/prompting or lightweight adapters rather than full fine-tuning or separate models. |
| `characterize_limit_then_surpass` | Characterize Limit, Then Surpass | Formulate theoretical performance bound of current paradigm $\rightarrow$ propose architectural mechanism that provably breaks through that bound. |
| `targeted_self_supervised_objective` | Design Property-Targeting Objective | Design specialized pretext loss function that forces latent representations to preserve a specific semantic or geometric property. |

## Mandatory Human-in-the-Loop (HITL) Gate

> [!IMPORTANT]
> **DO NOT COMMIT TO A SINGLE MECHANISM SILENTLY.**  
> Formulate 2–3 distinct candidate mechanisms grounded in different ideation patterns. Write the proposal matrix to `docs/ai/proposed-mechanisms.md`. STOP and present the options to the researcher to debate trade-offs, feasibility, and alignment with available experimental compute.

## Execution Procedure

### Step 1: Pattern Matching
Read `docs/ai/bottleneck-diagnosis.md`. Evaluate the diagnosed bottleneck against the operational signatures in `references/patterns/overview.md`. Select the **top 2–3 most compatible patterns**.

### Step 2: Formulation of Candidate Mechanisms
For each selected pattern, construct an explicit technical proposal:
1. **Handle & Headline:** Descriptive title capturing the core technical move.
2. **Operational Move:** Step-by-step description of the proposed algorithm or architecture.
3. **Formal Mechanism:** Specific equations, objective functions, or module block diagrams.
4. **Why It Should Work:** Grounded argument connecting the mechanism directly to the bottleneck.
5. **Compute & Resource Profile:** Categorize the compute requirements (e.g., *Feasible on local CPU/small GPU for toy validation* vs. *Requires multi-GPU cluster for full pretraining*).

### Step 3: Write Proposal Report
Save the candidate proposals to `docs/ai/proposed-mechanisms.md`.

### Step 4: Collaborative Decision Checkpoint
Present the candidate mechanisms to the researcher:
- Highlight the comparative trade-offs (e.g., *Option A offers theoretical guarantees but requires mathematical proofs; Option B is empirically aggressive and faster to prototype*).
- Solicit researcher feedback:
  > *"Here are 2–3 viable mechanism designs derived from empirical ML patterns. Which direction do you want to pursue, or how would you like to refine the mathematical formulation before we proceed to novelty verification (Scoop Check)?"*
