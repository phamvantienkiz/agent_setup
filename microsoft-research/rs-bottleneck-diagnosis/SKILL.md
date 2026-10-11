---
name: rs-bottleneck-diagnosis
description: Diagnose genuine theoretical, algorithmic, or empirical bottlenecks in State-of-the-Art (SOTA) research literature. Distinguish load-bearing bottlenecks from superficial soft targets. STOP and present findings to the human researcher for alignment before proceeding to ideation.
allowed-tools: Read Write Edit Bash
metadata:
  framework: Microsoft Research Studio (HITL Edition)
  phase: "Pre-Paper Ideation (Phase 1)"
---

# RS Bottleneck Diagnosis

## Overview

Diagnose the **load-bearing bottleneck** in existing State-of-the-Art (SOTA) literature that prevents current approaches from solving the core problem. This skill performs deep structural analysis of literature surveyed in `rs-paper-search`, avoiding soft targets (convenient, superficial gaps chosen merely to make a trivial solution look effective).

## Mandatory Human-in-the-Loop (HITL) Gate

> [!IMPORTANT]
> **DO NOT PROCEED AUTONOMOUSLY TO IDEATION.**  
> Upon completing the diagnostic pass, you MUST stop execution, write the diagnostic findings to `docs/ai/bottleneck-diagnosis.md`, and present the findings to the human researcher for explicit review and directional alignment.

## Core Diagnostic Dimensions

Examine the collected SOTA papers across four structural layers:

1. **Implicit Load-Bearing Assumptions:**
   - What implicit assumptions do current guarantees, proofs, or architectures rely upon? (e.g., i.i.d. data distribution, infinite memory/compute budget, invertible Jacobian, noise-free observations).
   - What breaks down in realistic, out-of-distribution, or adversarial regimes when these assumptions are violated?

2. **Fundamental Trade-offs & Inherent Costs:**
   - What operational price does SOTA pay to achieve current performance? (e.g., $O(N^2)$ quadratic attention complexity, exponential sample complexity, high inference latency, massive KV cache footprint).
   - Is this cost fundamental or an artifact of the current computational formulation?

3. **Confound vs. True Capability:**
   - Are reported SOTA gains measuring genuine capability or exploiting superficial shortcuts/confounds in standard benchmarks?

4. **Root Cause vs. Symptom:**
   - Distinguish the superficial failure mode (e.g., "model hallucinates on long documents") from the architectural root cause (e.g., "unbounded loss of positional precision in geometric rotary embeddings").

## Execution Procedure

### Step 1: Literature Synthesis & Deep Extraction
Read the core literature identified during literature retrieval. Extract:
- Key operational signatures of baseline methods.
- Stated limitations and acknowledged failure modes in author discussions.
- Empirical saturation points on standard benchmarks.

### Step 2: Bottleneck Formulation
Synthesize the extracted evidence into a rigorous bottleneck formulation:
- **Bottleneck Handle:** Concise technical label (e.g., `Information-Bottleneck in Low-Rank Projection`).
- **Mathematical / Mechanistic Description:** Explicit equations, operators, or algorithmic routines causing the failure.
- **Why Naive Fixes Fail:** Explain why standard incremental tweaks (hyperparameter tuning, additional regularization loss terms, deeper backbones) cannot overcome this bottleneck.

### Step 3: Write Diagnostic Report
Persist the structured analysis directly to disk at `docs/ai/bottleneck-diagnosis.md` using the following schema:
- `# Research Bottleneck Diagnostic: <Domain / Topic>`
- `## 1. SOTA Landscape & Baseline Analysis`
- `## 2. Identified Load-Bearing Bottleneck`
- `## 3. Evidence from Literature (Cited Papers & Quotes)`
- `## 4. Why Incremental Solutions Fail`
- `## 5. Potential Pivot Directions for Ideation`

### Step 4: Human Alignment Checkpoint (The Stop Gate)
Present a concise synthesis to the researcher and solicit directional confirmation:
- Summarize the diagnosed bottleneck in 3–5 bullet points.
- Pose 2 concrete alignment questions:
  1. *Does this diagnosed bottleneck capture the core obstacle you intend to tackle in this research project?*
  2. *Which of the suggested pivot directions aligns best with your research intuition and available compute resources?*
- Wait for researcher response before invoking `rs-pattern-ideator`.
