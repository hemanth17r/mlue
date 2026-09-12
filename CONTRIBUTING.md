# Contributing to MLUE

Thank you for your interest in contributing to the **Machine-Accessible Universal Software & Simulation Substrate (MLUE)**.

MLUE is built from first principles as an **AI-first computational and physical simulation substrate**. To preserve the mathematical rigor, extreme performance, and security of the substrate, all contributions must uphold the architectural invariants and verification protocols described below.

---

## 🏛️ Foundational Invariants (Non-Negotiable)

Every pull request must maintain the following core architectural invariants:

1. **Zero External Runtime Dependencies (Tier L1 Decoupling)**:
   The core runtime (`runtime/`) must execute exclusively on the Python standard library. No third-party packages (e.g. `numpy`, `scipy`, `pygame`, `torch`) may ever be imported into the core engine.
2. **Strict Continuous Coordinate Space $[0.0, 1.0]^2$**:
   All geometry, positions, sizes, and velocities exist in resolution-independent normalized space. Pixels are purely a presentation adapter concern.
3. **100% Bit-Exact Determinism**:
   Simulations must yield bit-exact cryptographic SHA-256 state hashes across runs and cross-architecture parity across x86_64, ARM64, and WASM.
4. **Compile-Time Static Reachability Validation**:
   Spatial rule conditions and entity event hooks must be statically verified at load time (`loader.py`). Unreachable conditions must be rejected before execution begins.
5. **Sandboxed & Zero Arbitrary Code Execution**:
   `eval()`, `exec()`, or dynamic code synthesis are 100% prohibited. All agent mutations operate through declarative dispatch tables.

---

## 🛠️ Local Development Setup

### Prerequisites
- **Python**: 3.10, 3.11, 3.12, or 3.13.
- **Node.js**: 18+ (for Web Studio and live benchmark interface).
- **Git**: 2.30+.

### 1. Clone the Repository
```bash
git clone https://github.com/hemanth17r/mlue.git
cd mlue
```

### 2. Verify Base Python Installation
Ensure Python 3.10+ is available:
```bash
python --version
```

### 3. Optional: Install Development Package in Editable Mode
```bash
pip install -e .
```
This registers the `mlue` and `mlue-mcp` CLI commands globally in your shell.

---

## 🧪 Comprehensive Verification Stack

Before opening a pull request, you **must run and pass all four verification gates**:

### 1. Unit Test Suite (174/174 Passing)
Runs all unit and integration tests across physics, constraints, spatial indexing, WAL persistence, and agent APIs:
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### 2. Model Context Protocol (MCP) Self-Test (12 Tools)
Verifies that the standalone JSON-RPC server initializes, passes schema validation, runs headless simulations, and executes state checkpoints:
```bash
python mcp_server.py --test
```

### 3. Universal 13-Pillar Invariant Benchmark Harness
Executes automated stress tests verifying kinetic energy conservation, broadphase culling, memory churn (< 1 Byte/tick), and Q32.32 cross-architecture parity:
```bash
python bench/harness/runner.py
```

### 4. Web Studio & Benchmarks Build
Verifies that the React + Vite web studio builds with zero compilation errors:
```bash
cd bench/web
npm install
npm run build
cd ../..
```

### 5. Zero-Knowledge AI Agent End-to-End Simulation
Simulates an external AI agent connecting via MCP, discovering tools, designing an application from scratch, and executing physics:
```bash
python scripts/test_blind_mcp_ai.py
```

---

## 📁 Repository Organization

```text
mlue/
├── .github/              # CI/CD workflows, issue templates, PR template
├── bench/                # Benchmark harness, baselines, and web studio
│   ├── harness/          # 13-pillar automated runner (runner.py)
│   ├── telemetry/        # Machine-readable benchmark run histories (runs.json)
│   └── web/              # Vite + React web studio & live dashboard
├── docs/                 # Architectural theses, roadmaps, and specifications
├── examples/             # Canonical declarative .mlue application and game scenes
├── runtime/              # Core zero-dependency substrate package
│   ├── adapter.py        # Presentation adapters (Tkinter, Canvas bridge)
│   ├── ai_interface.py   # Programmatic agent session API
│   ├── batch.py          # High-throughput parallel environment pool
│   ├── binary.py         # Zero-copy .mlueb serialization format
│   ├── engine.py         # Deterministic physics and continuous integrator
│   ├── fixed_point.py    # Q32.32 fixed-point integer math engine
│   ├── gym.py            # Gymnasium/PettingZoo RL environment adapter
│   ├── loader.py         # Schema parser & compile-time spatial invariant solver
│   ├── model.py          # Immutable domain dataclasses
│   ├── native_core.py    # C-FFI accelerated runtime bridge
│   ├── patch.py          # Micro-delta patch engine & state checkpoints
│   ├── spatial.py        # 2D Spatial Hash Grid & BVHTree broadphase
│   ├── tensor.py         # Zero-copy contiguous memory tensor bridge
│   └── wal.py            # Write-Ahead Log (.wal) persistence & replay
├── scripts/              # Developer automation and integration scripts
├── spec/                 # Versioned specification RFCs (0.1 through 2.1)
├── tests/                # 19 test suites covering 174 automated test cases
├── mcp_server.py         # Standalone zero-dependency MCP JSON-RPC server
├── mlue.py               # Unified CLI toolchain (run, compile, replay, batch)
└── pyproject.toml        # PEP 517 / PEP 621 package distribution configuration
```

---

## 🚀 Pull Request Workflow

1. **Create a Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Follow Coding Standards**:
   - Python code must conform to PEP 8 and include descriptive type annotations.
   - Core runtime changes must maintain pure standard-library decoupling.
   - Do not introduce runtime heap allocation churn inside hot inner loops.
3. **Add Tests**:
   - Every new primitive, constraint, or bugfix must include corresponding unit test coverage in `tests/`.
4. **Run Verification**:
   - Ensure all 174 unit tests, MCP self-test, and 13 benchmarks pass cleanly.
5. **Open Pull Request**:
   - Use the provided [PR Template](.github/PULL_REQUEST_TEMPLATE.md).
   - Describe the architectural motivation and attach verification logs.

---

## ⚖️ License
By contributing to MLUE, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
