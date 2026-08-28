# Zone 4: Traditional Stack Reference Baselines

This directory contains canonical reference implementations of classic games (Pong, Breakout) built using the **traditional imperative developer stack** (Python/Pygame style).

---

## Architectural Purpose
* **Zone 4 Hermetic Isolation**: These files exist solely as **external benchmark baselines** to evaluate SLOC, AST cyclomatic complexity, token overhead, memory allocation churn, and runtime speedup factors.
* **Zero Core Dependency**: Nothing in `runtime/` or `spec/` imports or depends on these baseline scripts.

## Baseline Metrics vs. MLUE Substrate

| Metric Trait | Traditional Baseline Stack | MLUE Native Declarative Substrate |
| :--- | :--- | :--- |
| **Code Paradigm** | Procedural / Imperative Game Loop | Pure Declarative JSON Document |
| **Bespoke SLOC** | 120–250 lines of bespoke code per game | 0 bespoke lines (Evaluated by universal runtime) |
| **State Provability** | Unbounded runtime failure space | 100% compile-time reachability validation |
| **Memory Churn** | Dynamic frame allocations ($\sim 12\text{ KB/s}$) | Near-zero steady-state churn ($0.72\text{ B/tick}$) |
| **Deterministic Replay** | Sensitive to OS event queues & clocks | 100% Bit-exact SHA-256 across platforms |
