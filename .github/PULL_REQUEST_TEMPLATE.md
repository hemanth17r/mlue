## 📋 Summary

<!-- Briefly describe the purpose of this change, the underlying motivation, and what problem it solves. -->

## 🔬 Mathematical & Invariant Impact

- [ ] **Substrate Decoupling (B1)**: Zero third-party runtime dependencies added to core (`runtime/`).
- [ ] **Coordinate Invariance (B3)**: Preserves continuous normalized coordinate space $[0.0, 1.0]$.
- [ ] **Physical Conservation (B4)**: Conservation of momentum and energy maintained ($< 1,000$ PPB drift).
- [ ] **Static Reachability (B5)**: Spatial condition validation rules uphold compile-time guarantees.
- [ ] **Bit-Exact Determinism (B9 & B12)**: Cryptographic SHA-256 state digest identical across platforms.

## 🧪 Verification Plan

### Automated Tests
```bash
# 1. Run full unit test suite (174/174)
python -m unittest discover -s tests -p "test_*.py" -v

# 2. Run MCP JSON-RPC protocol self-test
python mcp_server.py --test

# 3. Run Universal 13 Invariant Benchmark Harness
python bench/harness/runner.py

# 4. Verify Web Studio production build
cd bench/web && npm run build
```

### Test Results
<!-- Paste summary output from unittest and bench/harness/runner.py -->

## 📦 Changes Checklist

- [ ] Code strictly formatted and clean of debugging statements.
- [ ] Unit tests added or updated in `tests/` covering new logic and edge cases.
- [ ] Documentation updated in `docs/` or `spec/` if specification or schema was modified.
- [ ] No breaking changes to existing `.mlue` scene representations without explicit migration.

## 🔗 Related Issues & RFCs

Closes #
