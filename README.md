# MLUE — Machine-Accessible Simulation & Physics Substrate
### *Deterministic, Zero-Dependency Execution Substrate for Autonomous AI Agents*

[![Live Benchmarks](https://img.shields.io/badge/Live%20Telemetry-10%2F10%20Passing-success?style=for-the-badge&logo=vercel)](https://mlue-bench.vercel.app)
[![Substrate Tier](https://img.shields.io/badge/Substrate-Tier%20L1%20Decoupled-blue?style=for-the-badge)](https://mlue-bench.vercel.app)
[![Dependencies](https://img.shields.io/badge/Dependencies-0%20(Pure%20Stdlib)-brightgreen?style=for-the-badge)](file:///c:/Users/AKKALA%20HEMANTH%20REDDY/OneDrive/Desktop/mlue/README.md)
[![Tests](https://img.shields.io/badge/Tests-19%2F19%20Passing%20(100%25)-brightgreen?style=for-the-badge)](file:///c:/Users/AKKALA%20HEMANTH%20REDDY/OneDrive/Desktop/mlue/tests/test_runtime.py)
[![Throughput](https://img.shields.io/badge/Throughput-37.4k%20ticks%2Fs-orange?style=for-the-badge)](https://mlue-bench.vercel.app)
[![Determinism](https://img.shields.io/badge/Determinism-100%25%20Bit--Exact-purple?style=for-the-badge)](https://mlue-bench.vercel.app)

> **"AI is the builder. Humans are users."**
>
> MLUE is an AI-first, mathematically verified simulation substrate built from physics and computational geometry upward. It provides autonomous AI agents with an ultra-lightweight, zero-latency execution layer to programmatically construct, inspect, validate, and simulate emergent interactive environments.

👉 **[Explore the Live Interactive Benchmark & Telemetry Dashboard →](https://mlue-bench.vercel.app)**

---

## ⚡ What is MLUE (And What It Is NOT)

In an ecosystem crowded with superficial LLM wrappers and heavyweight game engines, MLUE is engineered as a foundational, zero-dependency computational substrate:

| Architectural Dimension | Superficial "AI Wrapper" | Heavy Game Engines (Unity / Godot) | **MLUE Substrate (Phase 0)** |
| :--- | :--- | :--- | :--- |
| **External Dependencies** | 15+ third-party `pip` / `npm` packages | Multi-gigabyte binaries & runtimes | **0 (Pure Python Standard Library)** |
| **Simulation Latency** | 500ms – 2,000ms (Remote API roundtrips) | 16.6ms (GPU / frame-locked) | **26.77 µs per tick (37,359 ticks/s)** |
| **Agent Introspection** | Unstructured text scraping / regex | Complex native C++ / C# bindings | **Native Model Context Protocol (MCP) JSON-RPC** |
| **Mathematical Space** | Hallucinated / Non-deterministic | Viewport-dependent float drift | **Strict normalized $[0, 1]$ coordinate space (>16 decades precision)** |
| **Memory Footprint** | Bloated browser / Node runtime | 300 MB – 2 GB RAM | **0.72 Bytes/tick churn (Near-zero GC overhead)** |
| **Safety Invariants** | Unhandled runtime crashes | Scene-graph runtime exceptions | **Compile-time static spatial reachability validation** |
| **Determinism** | Non-repeatable execution | Platform-dependent floating point | **100% Bit-exact SHA-256 state digest across 50,000 ticks** |

---

## 📊 The 10 Ruthless Architectural Benchmarks

MLUE is continuously audited against 10 rigorous architectural, physical, and engineering benchmarks via an automated AST and hardware-timer telemetry harness (`bench/harness/runner.py`):

| ID | Benchmark Pillar | Target Requirement | Measured Value | Verification Method |
| :---: | :--- | :--- | :--- | :--- |
| **B1** | **Substrate Decoupling** | `0 Foreign Imports` | **0 Violations (Tier L1)** | AST parser across `model.py`, `engine.py`, `loader.py` |
| **B2** | **Declarative Emergence** | $\ge 3.0\times$ Expansion | **3.5x Multiplier** | 7 emergent games / 2 universal primitives (0 heuristics) |
| **B3** | **Spatial Invariance** | $\Delta \le 10^{-7}$ drift across viewports | **>16.0 Decades Precision** | Bit-exact trajectory ($0.0\times 10^0$ drift) from 100x100 to 4K |
| **B4** | **Physical Conservation** | $\Delta E_k \le 1,000\text{ PPB}$ | **0.0 PPB Drift** | Kinetic energy conservation over 1,000 collision trajectories |
| **B5** | **Static Reachability** | $10/10$ Statically Blocked | **10/10 Blocked (100%)** | Compile-time rejection of mathematically unreachable triggers |
| **B6** | **Step Latency & Speed** | $> 10,000\text{ ticks/s}$ | **37,359 ticks/s (26.8 µs)** | 10,000 continuous collision steps (10.7x faster than baseline) |
| **B7** | **Memory Allocation Churn** | $< 500\text{ B/tick}$ churn | **0.72 B/tick Churn** | `tracemalloc` heap delta across 5,000 steps (3.50 KB total) |
| **B8** | **Structural Complexity** | Peak McCabe $CC \le 30$ | **Max CC = 21 (Bounded)** | AST branching complexity audit across all 13 core functions |
| **B9** | **Determinism & Replay** | $100\%$ Bit-Exact Digest Match | **Bit-Exact (`23a940449ab2...`)** | Cryptographic SHA-256 digest match across 50,000 ticks |
| **B10**| **Tunneling Stress** | $v_{\max} \ge 2.5\text{ u/s}$ ($0\%$ Defect) | **$v_{\max} = 2.5\text{ u/s}$ ($0\%$ Defect)**| High-velocity collision containment against 0.02 barrier |

> Live charts, formulas, and telemetry breakdown available at **[mlue-bench.vercel.app](https://mlue-bench.vercel.app)**.

---

## 🚀 Quickstart

### 1. Clone & Run (Zero Dependencies)
Requires only Python 3.10+ (no `pip install` required):

```bash
git clone https://github.com/hemanth17r/mlue.git
cd mlue

# Play Emergent Breakout (Paddle: A/D or Left/Right arrows)
python mlue.py run examples/breakout.mlue

# Play Emergent Pong (Left Paddle: W/S, Right Paddle: Up/Down)
python mlue.py run examples/pong.mlue

# Run Bumper Arena simulation
python mlue.py run examples/bumper_arena.mlue
```

### 2. High-Speed Headless Simulation
Evaluate 1,000 deterministic physics and rule steps in milliseconds without opening a window:

```bash
python mlue.py run examples/breakout.mlue --headless --ticks 1000
```

### 3. Connect AI Agents via Model Context Protocol (MCP)
MLUE includes a native zero-dependency MCP JSON-RPC server (`mcp_server.py`) compatible with **Claude Desktop, Antigravity, Cursor, and custom agent runtimes**:

```bash
# Run standalone MCP protocol self-test
python mcp_server.py --test

# Launch MCP server over stdio
python mcp_server.py
```

---

## 🤖 Machine-Accessible AI Agent Tool Suite

AI agents do not write fragile code—they interact with MLUE through a declarative mathematical representation and standard MCP tool calls:

```json
{
  "canvas": { "width": 800, "height": 600 },
  "entities": [
    {
      "id": "ball",
      "shape": "circle",
      "position": { "x": 0.5, "y": 0.7 },
      "radius": 0.025,
      "velocity": { "vx": 0.25, "vy": -0.45 },
      "properties": { "solid": true }
    }
  ],
  "rules": [
    {
      "trigger": "collision_with_brick",
      "condition": { "type": "collision", "entity_a": "ball", "entity_b": "brick_01" },
      "actions": [
        { "type": "destroy_entity", "target": "brick_01" },
        { "type": "increment", "variable": "score", "value": 10 }
      ]
    }
  ]
}
```

### Available MCP Tools for Autonomous Agents:
* `mlue_get_schema`: Returns the declarative MLUE schema specification and spatial invariant rules.
* `mlue_validate_scene`: Performs static reachability and geometric invariant validation on an MLUE document.
* `mlue_start_simulation`: Spawns a deterministic in-memory simulation session.
* `mlue_step_simulation`: Advances simulation by $N$ steps with optional input signal vectors.
* `mlue_inspect_state`: Returns entity positions, velocities, state variables, and active collisions.
* `mlue_mutate_entity`: Modifies entity properties or velocities dynamically during runtime.
* `mlue_close_simulation`: Cleanly terminates and frees the session.

---

## 🏗️ Architectural Topology

```text
                     MLUE CORE (Native & Invariant Substrate)
─────────────────────────────────────────────────────────────────────────────
• Continuous Normalized Coordinate Space [0, 1] (Resolution-Invariant)
• Exact Normal Impulse Reflections & Elastic Collision Physics
• Declarative Event Triggers & Dynamic Entity Lifecycle (destroy / reset)
• Static Spatial Reachability Invariant Solver (runtime/loader.py)
• Programmatic AI Interface & In-Memory Sessions (runtime/ai_interface.py)
• Zero-Dependency Model Context Protocol Server (mcp_server.py)
─────────────────────────────────────────────────────────────────────────────
                     SCAFFOLDING LAYER (Disposable Driver)
─────────────────────────────────────────────────────────────────────────────
• Host Runtime Driver (Python Standard Library)
• Windowing & Presentation Adapter (Tkinter / Canvas)
• Multi-Variable HUD Presentation & Keyboard Scancode Mapper
```

---

## 🗺️ Systems Roadmap

- [x] **Phase 0: Mathematical & Specification Foundation (Grand Milestone Complete)**
  - 100% pure Python standard-library implementation (0 dependencies).
  - Continuous normalized geometry (`circle`, `box`) & deterministic step loop $\Delta t$.
  - Pairwise impulse collisions, control channels, declarative state variables, and entity destruction.
  - Compile-time spatial reachability validation.
  - Native Model Context Protocol (MCP) server integration.
  - 10/10 Passing ruthless benchmarks on live telemetry dashboard.
- [ ] **Phase 1: Native Substrate Transition (Next)**
  - Bare-metal compiled Rust/C execution core (< 1 µs step latency, > 1,000,000 ticks/s).
  - Direct memory-mapped binary representation serialization.
  - SIMD-vectorized multi-agent rollout engine.
- [ ] **Phase 2: Multi-Agent Continuous Constraint Manifolds**
  - Arbitrary polygon collision manifolds & spatial partitioning mesh.
  - Distributed multi-agent RL simulation environment.

---

## 🧪 Verification & Unit Tests

Run the complete 19-test automated test suite:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

```text
...................
----------------------------------------------------------------------
Ran 19 tests in 0.064s

OK
```

---

## 📄 License
MIT License. Built from first principles.
