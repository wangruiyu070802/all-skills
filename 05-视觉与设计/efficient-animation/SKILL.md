---
name: efficient-animation
description: >
  Select and generate ultra-compact, high-fidelity visual animations or dynamic diagrams
  (SVG, Mermaid, Manim, p5.js core logic) instead of full-page HTML boilerplate. Use when the
  user requests animations, dynamic flowcharts, visual explanations of algorithms, physics/math
  concepts, or state machines, especially when aiming to minimize token usage.
  当用户说「画个动画」「做个动态图」「可视化解释」「讲清楚这个算法/定理」「动图演示」
  「流程图动画」「用动画演示」时触发。
license: MIT
---

# Efficient Animation Visualizer

A skill for generating lightweight, high-performance visual animations using minimal tokens. It eliminates heavy HTML/CSS boilerplate by matching the concept to the most token-efficient output format.

## Format Selection Heuristic

Evaluate the user's concept and choose the corresponding lightweight format:

1. **Logic Flow / State Machine / Protocol Handshake**
   - **Format**: Mermaid (`sequenceDiagram` or `stateDiagram-v2`).
   - **Token Cost**: ~30–80 tokens.
   - **Target**: Native Markdown rendering (zero browser/file overhead).

2. **Continuous Motion / Vector Diagram / Mechanical Cycle**
   - **Format**: Standalone Inline SVG (with CSS `@keyframes` or native SMIL `<animate>`).
   - **Token Cost**: ~100–300 tokens.
   - **Target**: Direct browser/preview render (no `<!DOCTYPE html>`, `<html>`, or `<body>`).

3. **Math Proofs / Physics Theorems / Formula Transitions**
   - **Format**: Manim Community Edition Script (Python).
   - **Token Cost**: ~100–250 tokens.
   - **Target**: Local execution (`manim -pql scene.py`) or online Jupyter/Colab notebooks.

4. **Interactive Sandbox / Particle Systems / Physics Simulation**
   - **Format**: p5.js or HTML5 Canvas **Core Logic Only**.
   - **Token Cost**: ~150–350 tokens.
   - **Target**: User pastes logic into a local shell template or canvas runner.

---

## Output Rules by Format

### 1. Mermaid (Flow & Sequences)
- Always wrap the diagram in a fenced code block tagged `mermaid`.
- Keep state and node names concise and descriptive.
- Do not output additional conversational filler.

### 2. Standalone Inline SVG
- Enclose everything within a single root `<svg ...> ... </svg>`.
- **FORBIDDEN**: Do not wrap in `<!DOCTYPE html>`, `<html>`, `<head>`, or `<body>`.
- Include `viewBox`, `xmlns="http://www.w3.org/2000/svg"`, and an internal `<style>` block for `@keyframes` or use SMIL `<animateTransform>`.

### 3. Manim Python Script
- Provide a clean, standalone Python class inheriting from `Scene`.
- Include only `from manim import *`.
- Append a one-line execution command comment at the bottom (e.g., `# Run: manim -pql script.py SceneName`).

### 4. p5.js / Canvas Core Logic
- Unless the user explicitly asks for a runnable HTML file, **output only the internal logic**:
  - For p5.js: Output only `function setup() { ... }` and `function draw() { ... }`.
  - For Canvas: Output only the update/render loop function.
- Mark tweakable parameters (speed, gravity, particle count) clearly at the top.

---

## Gotchas & Guidelines

- **Defaulting to Full HTML**: Never generate a monolithic HTML file unless the user explicitly uses words like "give me a full index.html file".
- **External Dependencies**: For SVG animations, do not depend on external JavaScript or external CSS files.
- **Brevity**: Let the code do the demonstration; avoid long text explanations before and after the code snippet.
