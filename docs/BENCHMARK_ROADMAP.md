# MLUE Benchmark Matrix Evolution & Expansion Roadmap

## Status: APPROVED
## Current Phase: Phase 1 (Subphase 1.2 Completed)
## Total Benchmark Pillars: 10 Active (B1 – B10) $\rightarrow$ Expanding to 12 (B1 – B12)

---

## 1. Executive Policy: When Do Benchmarks Get Added?

New top-level benchmark pillars ($B_x$) are **never added retroactively or prematurely**.

* **Rule**: A benchmark is introduced **directly inside the specific subphase that implements the capability**, serving as that subphase's mandatory empirical verification gate.
* **Why**:
  1. Adding a benchmark *before* its subphase means shipping a broken benchmark that fails for reasons unrelated to current code.
  2. Adding a benchmark *after* its subphase means shipping unbenchmarked code.
  3. Adding a benchmark *during* the subphase enforces **Test-Driven Architectural Verification (TDAV)**: the benchmark defines the mathematical standard the implementation must meet to pass.

---

## 2. Active Foundation Matrix (B1 – B10)

The following 10 foundational invariants were established in Phase 0 and remain permanently active across all versions:

| ID | Name | Category | Measured Invariant | Target Standard |
| :--- | :--- | :--- | :--- | :--- |
| **B1** | **Substrate Decoupling** | Architecture | Foreign OS/GUI imports in runtime AST | 0 Violations (Tier L1) |
| **B2** | **Declarative Emergence** | Architecture | App-to-primitive ratio without heuristics | $\ge 3.0\times$ Multiplier |
| **B3** | **Spatial Invariance** | Architecture | Precision across extreme viewports | $> 16.0$ Decades ($\Delta = 0.0$) |
| **B4** | **Physical Conservation**| Physics | Total kinetic energy drift | $\le 1,000\text{ PPB}$ ($0.0\text{ PPB}$) |
| **B5** | **Static Provability** | Verification | Compile-time defect interception | $100\%$ Blocked ($10/10$) |
| **B6** | **Speed & Step Latency** | Performance | Simulation step throughput & latency | $> 10,000\text{ ticks/s}$ ($< 100\,\mu\text{s}$) |
| **B7** | **Resource Churn** | Performance | Steady-state heap allocation delta | $< 500\text{ B/tick}$ ($< 1\text{ B/tick}$) |
| **B8** | **Structural Complexity**| Engineering | Peak McCabe Cyclomatic Complexity | $CC \le 30$ (Bounded) |
| **B9** | **Determinism** | Engineering | 50,000-tick cryptographic state hash | $100\%$ Bit-Exact SHA-256 |
| **B10**| **Tunneling Stress** | Physics | Containment under extreme velocity | $v_{\max} \ge 2.5\text{ u/s}$ ($0\%$ Defect) |

---

## 3. Scheduled New Benchmark Additions

Two new mathematical pillars will be added during Phase 1, expanding the matrix from **10 to 12 invariants ("The Universal 12")**:

```
Subphase 1.2 (Current)  ──>  10 Invariants (B1 – B10)
Subphase 1.3            ──>  + B11: Spatial Scaling & Broadphase Efficiency (11 Total)
Subphase 1.4            ──>  + B12: Cross-Architecture Bit-Exact Parity (12 Total)
Subphase 1.6 (Capstone) ──>  Lock "The Universal 12 Matrix" for all future releases
```

---

### 3.1 B11: High-Entity Spatial Scaling ($O(N \log N)$ Broadphase Efficiency)
* **Introduced In**: **Subphase 1.3 (Continuous Spatial Indexing & BVH)**.
* **Why It Earns Its Place**:
  * Currently, B6 benchmarks 10 entities. A pairwise $O(N^2)$ algorithm works for 10 entities but collapses catastrophically at $N=1,000$ (requiring 500,000 checks per frame).
  * B11 proves that MLUE can simulate massive interactive scenes ($N = 1,000$ active entities) in real time without frame drops.
* **Mathematical Formula**:
  $$\text{Broadphase Cull Efficiency} = 1.0 - \frac{\text{Narrowphase Pairs Tested}}{\frac{N(N-1)}{2}}$$
* **Target Metric**:
  * $\text{Cull Efficiency} \ge 98.0\%$ at $N = 1,000$.
  * Step throughput $\ge 1,000\text{ ticks/s}$ at $N = 1,000$ on single-threaded CPU.

---

### 3.2 B12: Cross-Architecture Bit-Exact Parity
* **Introduced In**: **Subphase 1.4 (Fixed-Point Deterministic Math Q32.32)**.
* **Why It Earns Its Place**:
  * Currently, B9 proves determinism on a single machine. However, standard IEEE 754 floating-point math diverges across x86 (Intel/AMD), ARM (Apple Silicon/Snapdragon), and WASM (Browsers) due to differing FMA (Fused Multiply-Add) and SIMD rounding rules.
  * B12 proves that the same simulation produces the **exact same SHA-256 state digest across all CPU architectures and platforms**.
* **Mathematical Formula**:
  $$\text{Parity Gate} = \left( \text{SHA256}_{\text{x86\_64}}(\text{sim}_{50k}) == \text{SHA256}_{\text{ARM64}}(\text{sim}_{50k}) == \text{SHA256}_{\text{WASM}}(\text{sim}_{50k}) \right)$$
* **Target Metric**:
  * $100\%$ Bit-Exact SHA-256 match across all 3 compilation targets.

---

## 4. Benchmark Lifecycle Summary

| Milestone | Active Invariants | Focus & Value |
| :--- | :--- | :--- |
| **Phase 0.7** | **B1 – B10** | Established foundation: decoupling, physics, basic latency, determinism. |
| **Subphase 1.1 – 1.2** | **B1 – B10** | Proved hierarchical state & `.mlueb` binary format with 49 unit tests. |
| **Subphase 1.3** | **B1 – B11** | Adds **B11 (Spatial Scaling)** to prove 1,000-entity BVH performance. |
| **Subphase 1.4** | **B1 – B12** | Adds **B12 (Cross-Architecture Parity)** to prove fixed-point universality. |
| **Subphase 1.5 – 1.6**| **B1 – B12** | Native C & WASM execution validated against the full 12-pillar matrix. |
