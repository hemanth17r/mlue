# MLUE Progressive Architectural Transition & Replacement Map

This document tracks the current external bootstrap dependencies, the role they provide, the targeted MLUE-native replacement capabilities, and their replacement readiness status.

---

## 1. Architectural Dual Path

* **Path A (MLUE Builds Applications)**: Progressively enable AI to construct applications, graphics, simulations, and hardware interactions directly in MLUE.
* **Path B (MLUE Builds MLUE)**: Progressively enable MLUE to build, extend, test, and replace its own runtime, tools, and substrate.

---

## 2. Dependency Replacement Map

| Current Bootstrap Dependency | What It Provides | Target MLUE-Native Replacement | Current Readiness | Confidence Level | Replacement Target Phase |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Python Standard Library (Runtime & Data Structures)** | Initial host execution runtime, dictionary/JSON parsing, and object evaluation loop | MLUE Native Core Runtime & Binary/Structured Evaluation Substrate | **Not Ready** *(Active Scaffolding)* | LOW | Phase 1.x / Phase 5.x |
| **Tkinter / OS Windowing (Adapter)** | Desktop window management and 2D canvas shape rasterization | MLUE Direct Presentation & Hardware Canvas Driver | **Not Ready** *(Active Scaffolding)* | LOW | Phase 3.x / Phase 4.x |
| **Host OS File System & OS APIs** | Storing `.mlue` definitions on disk and process management | MLUE Native State & Storage Substrate | **Not Ready** *(Active Scaffolding)* | LOW | Phase 4.x / Phase 5.x |
| **External Frontier AI Models (Claude, Gemini, etc.)** | Code generation and reasoning during bootstrap construction | MLUE-Optimized Fine-Tuned / Native Computational AI Models | **Not Ready** *(Active Scaffolding)* | LOW | Phase 6.x |

---

## 3. Transition Assessment Protocol

Before any external dependency is proposed for replacement:
1. **Role Identified**: Exactly what does the host dependency provide?
2. **MLUE Capability Built**: Has the MLUE-native equivalent been implemented?
3. **Empirical Validation**: Do automated tests, edge cases, and failure mode simulations prove equivalent reliability?
4. **Transition Report**: Submit formal assessment report with Confidence Rating (`LOW` / `MEDIUM` / `HIGH`) and explicit recommendation (`DO NOT REPLACE YET` / `READY FOR CONTROLLED REPLACEMENT` / `REPLACE NOW`).
5. **Incremental Migration**: Dual-run alongside existing scaffolding before final decommissioning.
