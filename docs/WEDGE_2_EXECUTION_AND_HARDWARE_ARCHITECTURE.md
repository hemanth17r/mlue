# MLUE Wedge 2 Architecture Specification: Hardware Front-Layers & Zero-Redundancy Execution

> **Document Type:** Tactical System Specification & Agent Guardrail  
> **Target Wedge:** Wedge 2 (2D Deterministic Physics, Interactive Presentation & Games)  
> **Preceding Milestone:** Wedge 1 (Headless Simulation & RL Gym — Completed at commit `89a8b7f`)  
> **Governing Foundations:** [`docs/FOUNDATIONAL_THESIS.md`](file:///c:/Users/AKKALA%20HEMANTH%20REDDY/OneDrive/Desktop/mlue/docs/FOUNDATIONAL_THESIS.md) and [`docs/STRATEGIC_WEDGE_AND_VISION_GUARD.md`](file:///c:/Users/AKKALA%20HEMANTH%20REDDY/OneDrive/Desktop/mlue/docs/STRATEGIC_WEDGE_AND_VISION_GUARD.md)

---

## 1. Executive Mandate for Agents Building Wedge 2

When transitioning from **Wedge 1 (Headless Kernel)** to **Wedge 2 (Interactive 2D Presentation & Physics)**, agents are connecting pure mathematical state transitions to **hardware display pipelines and user input streams**.

Agents building W2 must adhere to this foundational principle:
> **Do not import the 50-year legacy mistakes of the human-centric web stack.**  
> A UI or game presentation layer must not poll continuously if nothing has changed, must not rebuild UI trees from scratch every frame, must not maintain complex DOM-style callback trees, and must respect the physics of silicon hardware.

---

## 2. The Core Problem: The "Two Buttons" Redundancy Dilemma

### The Problem Defined
In traditional human-centric web/app frameworks (React, Electron, DOM):
1. Two static buttons on a screen frequently trigger continuous component re-renders, virtual DOM reconciliations, layout tree reflows, and event bubbling traversals.
2. Even when the browser caches GPU compositor layers, the surrounding runtime engine (V8, GC) wastes millions of CPU cycles re-checking state, parsing JSON, or measuring font metrics.

### The Silicon Reality: Recomputing vs. Remembering
At the silicon level (CPU registers, L1/L2/L3 caches, VRAM, and GPU rasterizers), there is a strict physical trade-off:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            SILICON COST HIERARCHY                           │
├────────────────────────────────┬──────────────────────┬─────────────────────┤
│ Operation                      │ Hardware Cost        │ Time Scale          │
├────────────────────────────────┼──────────────────────┼─────────────────────┤
│ Register Arithmetic (ALU)      │ 1 Clock Cycle        │ ~0.25 - 0.3 ns      │
│ L1 Cache Access                │ ~4 Clock Cycles      │ ~1.0 ns             │
│ Hash Map / Table Cache Miss    │ 40 - 200 Cycles      │ 10.0 - 60.0 ns      │
│ DOM Reflow / Font Metrics      │ 10,000+ Cycles       │ 10,000 - 500,000 ns │
│ Full Screen Pixel Rasterize    │ Millions of Cycles   │ 1,000,000+ ns       │
└────────────────────────────────┴──────────────────────┴─────────────────────┘
```

* **Axiom 1:** *Recomputing lightweight math in registers ($x + v \cdot \Delta t$) is 50× faster than checking a memory table to see if it was computed before.*
* **Axiom 2:** *Rasterizing pixels, uploading vertex buffers across the PCIe bus, and traversing complex trees is millions of times slower than ALU math and MUST be memoized.*

---

## 3. The 4 Architectural Pillars of Wedge 2

```
                       ┌─────────────────────────────────────┐
                       │          MLUE DOCUMENT (.mlue)      │
                       │   Static Geometry & Dynamic Entities│
                       └──────────────────┬──────────────────┘
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
     [PILLAR 1: DUAL-MODE STEPPING]                  [PILLAR 2: SPATIAL POINTER]
     • Δt > 0: Continuous Sim (60Hz)                 • Cursor = Normalized Circle Probe
     • Δt = 0: Event-Driven UI (0% CPU)              • Broadphase Spatial Grid (B11)
                  │                                               │
                  └───────────────────────┬───────────────────────┘
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
     [PILLAR 3: HARDWARE GPU CANVAS]                 [PILLAR 4: STATE DETERMINISM]
     • Static VBOs: Uploaded ONCE                    • Fixed-point Q32.32 Parity
     • Dynamic Uniforms: Offsets only                • Deduplication via SHA-256 Digest
```

---

### Pillar 1: Dual-Mode Stepping Engine ($\Delta t > 0$ vs $\Delta t = 0$)

Every execution runner and adapter in W2 must honor **Rule 5 of the Gating Rubric**:

$$S_{t+1} = f(S_t, I_t, \Delta t)$$

1. **Continuous Simulation Mode ($\Delta t > 0$):**
   * Used when active entities possess nonzero velocity ($v_x \neq 0$ or $v_y \neq 0$), active continuous rules, or physical simulations.
   * Runs at a targeted fixed timestep (e.g., 60 Hz) or unthrottled headless batch.
2. **Event-Driven Application Mode ($\Delta t = 0$):**
   * Used for static applications, dashboards, forms, and tools with two or more stationary buttons.
   * **Mandate:** The engine must evaluate spatial geometry **once** at load time and immediately halt its integration loop, dropping to **0.0% idle CPU usage**.
   * The engine only steps when an external input signal arrives on an input channel ($I_t \neq \emptyset$).

```python
# Reference Invariant for W2 Execution Loops
if not state.has_dynamic_kinematics and not pending_inputs:
    # Do NOT spin CPU cycles
    wait_for_input_signal()
```

---

### Pillar 2: Spatial Intersection Event Dispatching (Pointer as Geometry)

Traditional stacks bind imperative event listeners (`button.onclick = ...`) to DOM nodes. W2 forbids this.

1. **The Cursor is an Entity:** The mouse pointer or touch point is modeled as a zero-mass spatial probe entity at normalized coordinates $(x, y) \in [0.0, 1.0]$ with an interaction radius $r$.
2. **Clicking is a Collision:** Clicking or hovering a button is mathematically identical to a spatial intersection test between the pointer probe and the entity's normalized bounding box (`bbox`).
3. **Broadphase Culling (B11):**
   * If the pointer does not move, its spatial grid bucket is unchanged.
   * The engine does **zero** intersection calculations on static frames.
   * When the pointer moves, only entities inside the touched spatial hash buckets are evaluated.

---

### Pillar 3: Hardware Canvas & Buffer Partitioning (GPU Acceleration)

In Wedge 2, interactive presentation moves from disposable scaffolding (`TkinterAdapter` and Canvas 2D) toward a hardware-accelerated presentation pipeline (WebGPU / native hardware canvas):

1. **Static Vertex Buffer (VBO):**
   * Visual elements that do not move (buttons, cards, panel backgrounds, grid borders) are computed once and stored in GPU VRAM as a static vertex array.
   * The CPU never re-measures, re-layouts, or re-uploads these vertices.
2. **Dynamic Instance / Uniform Buffer:**
   * Entities that move (balls, dynamic indicators, cursors) write only their normalized transform matrix and color delta into a contiguous memory block streamed to the GPU per frame.
3. **Compositor Passthrough:**
   * The GPU draws the entire frame via instanced draw calls directly from VRAM, completely bypassing CPU memory bandwidth bottlenecks.

---

### Pillar 4: Bit-Exact Determinism & Frame Deduplication

MLUE guarantees 100% bit-exact determinism across platforms via fixed-point math ($Q32.32$) and cryptographic state digests (Benchmarks B9 & B12).

1. **State Digest Hashing:**
   $$\text{Digest}_t = \text{SHA-256}(\text{CanonicalBinaryState}(S_t))$$
2. **Zero-Dirty Presentation:**
   * If $\text{Digest}_t == \text{Digest}_{t-1}$, the presentation layer skips rendering pipeline re-execution.
   * The display controller simply preserves the current scanout buffer.

---

## 4. Agent Checklist for Implementing Wedge 2 Features

Before committing any feature or PR in Wedge 2, verify compliance against this checklist:

- [ ] **No GUI Scaffolding in Core:** Does `runtime/engine.py`, `runtime/spatial.py`, or `runtime/native_core.py` remain 100% free of rendering imports (no Tkinter, no Canvas 2D, no WebGPU)?
- [ ] **Normalized Coordinate Integrity:** Are all pointer positions and spatial intersections strictly calculated in normalized $[0.0, 1.0]$ coordinate space?
- [ ] **Dual-Mode Verification:** Does a document with zero velocities drop to 0% CPU consumption when idle?
- [ ] **Zero-Allocation Churn:** Does the pointer intersection loop generate $< 1\text{ Byte/tick}$ of memory allocation (Benchmark B7)?
- [ ] **Spatial Grid Acceleration:** Does interaction scale with $O(\log N)$ or $O(1)$ through the spatial grid rather than $O(N)$ linear scans?

---

## 5. Architectural North Star

> *"We do not build a separate system for games and a separate system for software. An interactive button is merely a stationary obstacle, a mouse click is merely a zero-mass collision, and an application layout is merely a static physical equilibrium."*
