# Contributing to MLUE

Thank you for your interest in contributing to MLUE!

MLUE is designed from first principles as an **AI-first, mathematically verified simulation substrate**. To preserve the integrity and performance of the core substrate, all contributions must adhere to the architectural invariants outlined below.

---

## Architectural Invariants (Must Be Upheld)

1. **Zero External Runtime Dependencies**:
   The core MLUE runtime (untime/model.py, untime/engine.py, untime/loader.py, untime/ai_interface.py) must remain 100% written in the Python standard library. No third-party packages may be imported into the core.

2. **Normalized Continuous Coordinate Space**:
   All positions, sizes, and velocities are specified in the continuous normalized unit space [0.0, 1.0]. Pixels are purely an adapter presentation artifact.

3. **Deterministic Discrete Integration**:
   Simulation steps must be 100% deterministic and reproducible bit-exact via cryptographic SHA-256 state hashing across runs.

4. **100% Passing Test & Invariant Suite**:
   All 19 core unit tests and the 10-pillar benchmark harness must pass before any PR is merged.

---

## Development Workflow

### 1. Clone & Set Up
`ash
git clone https://github.com/hemanth17r/mlue.git
cd mlue
`

### 2. Run Test Suite
`ash
python -m unittest discover -s tests -p "test_*.py" -v
`

### 3. Run MCP Protocol Verification
`ash
python mcp_server.py --test
`

### 4. Run 10-Pillar Invariant & Benchmark Harness
`ash
python bench/harness/runner.py
`

---

## Submitting Pull Requests

1. Fork the repository and create a feature branch (git checkout -b feature/polygon-primitives).
2. Implement your changes following standard PEP 8 formatting and type annotations.
3. Add unit test coverage in 	ests/test_runtime.py.
4. Ensure all CI checks pass.
5. Open a Pull Request with a clear description of the mathematical or architectural changes.
