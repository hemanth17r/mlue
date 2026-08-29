# MLUE — Machine-Accessible Simulation & Physics Substrate
### *Deterministic, Zero-Dependency 2D Simulation Substrate for Autonomous AI Agents*

[![CI](https://github.com/hemanth17r/mlue/actions/workflows/ci.yml/badge.svg)](https://github.com/hemanth17r/mlue/actions)
[![Live Benchmarks](https://img.shields.io/badge/Live%20Telemetry-10%2F10%20Passing-success?style=for-the-badge&logo=vercel)](https://mlue-bench.vercel.app)
[![Substrate Tier](https://img.shields.io/badge/Substrate-Tier%20L1%20Decoupled-blue?style=for-the-badge)](https://mlue-bench.vercel.app)
[![Dependencies](https://img.shields.io/badge/Dependencies-0%20(Pure%20Stdlib)-brightgreen?style=for-the-badge)](https://github.com/hemanth17r/mlue)
[![Tests](https://img.shields.io/badge/Tests-19%2F19%20Passing%20(100%25)-brightgreen?style=for-the-badge)](https://github.com/hemanth17r/mlue)
[![Throughput](https://img.shields.io/badge/Throughput-25k--37k%20ticks%2Fs-orange?style=for-the-badge)](https://mlue-bench.vercel.app)
[![Determinism](https://img.shields.io/badge/Determinism-100%25%20Bit--Exact-purple?style=for-the-badge)](https://mlue-bench.vercel.app)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

> **"AI is the builder. Humans are users."**
>
> MLUE is an **MCP-native, deterministic 2D simulation substrate** engineered from first principles for autonomous AI agent evaluation, rule synthesis, and world prototyping. It provides AI agents with an ultra-lightweight, zero-dependency mathematical sandbox to construct, inspect, validate, and simulate emergent interactive environments in microseconds.

👉 **[Explore the Live Interactive Benchmark & Telemetry Dashboard →](https://mlue-bench.vercel.app)**

---

## ⚡ What is MLUE (And What It Is NOT)

In an ecosystem crowded with high-level prompt wrappers and heavyweight 3D game engines, MLUE is positioned specifically as a foundational, zero-dependency computational substrate:

| Architectural Dimension | High-Level "AI Wrapper" | Heavy Game Engines (Unity / Godot) | **MLUE Substrate (Phase 0)** |
| :--- | :--- | :--- | :--- |
| **Primary Purpose** | Prompt chaining / UI skins | 3D visual rendering & player games | **Lightweight simulation sandbox for AI agent loops** |
| **External Dependencies** | 15+ third-party `pip` / `npm` packages | Multi-gigabyte binaries & runtimes | **0 (Pure Python Standard Library)** |
| **Simulation Latency** | 500ms – 2,000ms (Remote API roundtrips) | 16.6ms (GPU / frame-locked) | **26.8 µs – 40.0 µs per tick (25k–37k ticks/s)** |
| **Agent Introspection** | Unstructured text scraping / regex | Complex native C++ / C# bindings | **Native Model Context Protocol (MCP) JSON-RPC** |
| **Coordinate Space** | Non-standardized / Hallucinated | Viewport-dependent pixel drift | **Strict normalized $[0, 1]$ coordinate space (>16 decades precision)** |
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
| **B6** | **Step Latency & Speed** | $> 10,000\text{ ticks/s}$ | **25.0k–37.4k ticks/s (26.8–40.0 µs)** | 10,000 continuous collision steps (10.7x faster than baseline) |
| **B7** | **Memory Allocation Churn** | $< 500\text{ B/tick}$ churn | **0.72 B/tick Churn** | `tracemalloc` heap delta across 5,000 steps (3.50 KB total) |
| **B8** | **Structural Complexity** | Peak McCabe $CC \le 30$ | **Max CC = 21 (Bounded)** | AST branching complexity audit across all 13 core functions |
| **B9** | **Determinism & Replay** | $100\%$ Bit-Exact Digest Match | **Bit-Exact (`23a940449ab2...`)** | Cryptographic SHA-256 digest match across 50,000 ticks |
| **B10**| **Tunneling Stress** | $v_{\max} \ge 2.5\text{ u/s}$ ($0\%$ Defect) | **$v_{\max} = 2.5\text{ u/s}$ ($0\%$ Defect)**| High-velocity collision containment against 0.02 barrier |

---

## 🔬 Benchmark Methodology & Reproducibility

To ensure scientific integrity and independent reproduction:

1. **Hardware & Environment Specification**:
   - **Host CPU**: AMD / Intel x86_64 or Apple Silicon (evaluated via `platform.processor()`).
   - **Runtime**: Python 3.10+ standard library (evaluated across 3.10, 3.11, 3.12, 3.13 in CI).
   - **Timers**: High-resolution monotonic hardware clocks (`time.perf_counter_ns`).
2. **Workload Scope**:
   - All latency and throughput benchmarks measure **pure headless state integration** (excluding OS windowing, event pump, and rendering overhead).
   - The Pygame baseline comparison is an illustrative CPU baseline comparing equivalent headless discrete collision steps.
3. **Artifact Transparency**:
   - Raw benchmark outputs, timestamps, and commit digests are committed in `bench/telemetry/runs.json` and visualized live at **[mlue-bench.vercel.app](https://mlue-bench.vercel.app)**.

To re-run the benchmark suite locally:
```bash
python bench/harness/runner.py
```

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

### 3. Run Unit Tests (19/19 Tests Passing)
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

---

## 🔌 Connecting AI Agents via Model Context Protocol (MCP)

MLUE supports two connection transports:
1. **Public Cloud Gateway (Zero Setup)**: Connect directly over HTTPS without downloading code.
2. **Local Standard I/O (Private & Sovereign)**: Run `mcp_server.py` locally with 0 dependencies.

---

### Option A: Public Cloud Remote MCP (Zero Local Setup)

Connect any MCP client (Claude Desktop, Cursor, remote agent loops) to the live cloud endpoint:

**Endpoint URL**: `https://mlue-bench.vercel.app/api/mcp`

#### Claude Desktop Configuration (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "mlue-cloud": {
      "url": "https://mlue-bench.vercel.app/api/mcp"
    }
  }
}
```

---

### Option B: Local Private MCP Server (`stdio`)

Run the zero-dependency Python server directly on your local machine:

#### 1. Test Protocol Locally
```bash
python mcp_server.py --test
```

#### 2. Configure Claude Desktop
* **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
* **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "mlue-local": {
      "command": "python",
      "args": [
        "C:\\path\\to\\mlue\\mcp_server.py"
      ]
    }
  }
}
```
*(On macOS/Linux, replace `command` with `python3` and specify the absolute POSIX path).*

#### 3. Configure Cursor / VS Code MCP Extension
```json
{
  "name": "mlue-local",
  "command": "python",
  "args": ["/absolute/path/to/mlue/mcp_server.py"]
}
```

---

## 🤖 Available MCP AI Agent Tools

AI agents interact with MLUE through declarative mathematical representations and standard JSON-RPC tool calls:

| Tool Name | Description | Key Parameters |
| :--- | :--- | :--- |
| `mlue_get_schema` | Returns the declarative schema specification and spatial invariant rules. | None |
| `mlue_validate_scene` | Statically verifies geometric invariants and reachability conditions. | `file_path` or `scene_dict` |
| `mlue_start_simulation` | Spawns an isolated in-memory deterministic simulation session. | `file_path` or `scene_dict` |
| `mlue_step_simulation` | Advances physics by $N$ steps with optional control signal vectors. | `session_id`, `dt`, `ticks`, `inputs` |
| `mlue_inspect_state` | Returns positions, velocities, state variables, and active collision pairs. | `session_id` |
| `mlue_mutate_entity` | Dynamically alters entity properties or velocities during simulation. | `session_id`, `entity_id`, `mutations` |
| `mlue_close_simulation`| Cleanly terminates and frees the session state. | `session_id` |

---

## 🛡️ Security & Path Sandboxing

MLUE enforces strict boundary safety:
* **Path Invariants**: `loader.py` and `ai_interface.py` canonicalize all file paths and validate document schemas prior to execution. Path traversal tokens (`..`) outside authorized workspace trees are strictly rejected.
* **Isolated Memory Sessions**: Dynamic AI simulation sessions run in memory-isolated `SimulationState` dataclasses with zero OS subprocess execution or arbitrary code evaluation (`eval` / `exec` are 100% prohibited across the codebase).
* **Least Privilege**: When running MLUE in multi-tenant or untrusted cloud environments, running inside a lightweight container or sandbox is recommended.

---

## 📐 Current Capabilities & Explicit Limitations

To maintain architectural rigor, MLUE documents its exact operational boundaries:

### Supported in Phase 0 (Current):
* **Geometry**: Continuous 2D circles (`CircleSize`) and axis-aligned bounding boxes (`BoxSize`) in normalized coordinate space $[0.0, 1.0]$.
* **Physics**: First-order deterministic discrete time integration ($\Delta t$), exact normal impulse reflections, and spatial containment clamping.
* **State & Rules**: Declarative document-level state variables, collision event triggers, spatial threshold triggers, and entity lifecycles (`destroy_entity`, `reset_entity`, `set_property`, `increment`, `set`).
* **Determinism**: 100% bit-exact SHA-256 reproducibility on IEEE 754 floating-point runtimes.

### Current Limitations (Roadmap for Phase 1 & Phase 2):
* **No Angular Momentum / Rotation**: Entities currently translate linearly without rotational torque.
* **No Arbitrary Polygons**: Non-axis-aligned polygons and concave geometry are scheduled for Phase 2.
* **No Continuous Friction Manifolds**: Collisions are currently modeled as ideal elastic normal impulses.
* **Single-Threaded Reference Core**: The current Python reference core executes sequentially; multi-threaded SIMD parallel rollouts are part of the Phase 1 native Rust transition.

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

## 🤝 Contributing & Community

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting pull requests.

* **Bug Reports**: Use the [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md).
* **Feature Requests & RFCs**: Use the [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md).

---

## 📄 License
MIT License. Copyright (c) 2026 Akkala Hemanth Reddy. Built from first principles.

