# MLUE Phase 1: Native Performance & Hierarchical Storage Core

## 1. Overview & Objective

Phase 1 transitions MLUE from the Python standard library reference specification into a **bare-metal compiled execution core** with a **hierarchical document-state database** and **zero-copy binary persistence**.

The goal of Phase 1 is to achieve:
1. **Sub-Microsecond Step Latency**: Single-step execution $< 1.0\,\mu\text{s}$ ($> 1,000,000\text{ ticks/s}$).
2. **Hierarchical State-Tree Storage**: Direct nested collections, arrays, and paths replacing traditional SQL/ORMs for AI agents.
3. **Zero-Copy Disk Persistence**: Fixed-alignment binary format (`.mlueb`) with microsecond Write-Ahead Logging (WAL).
4. **SIMD Multi-Agent Parallelism**: $> 10,000,000\text{ aggregate ticks/s}$ across batch simulation rollouts.
5. **Progressive Scaffolding Elimination**: Removing Python from the computational hot path while maintaining universal embeddability via a standard C ABI.

---

## 2. Subphase Progression & Dependencies

```text
[ 1.1: Hierarchical State-Trees ]
               ↓
[ 1.2: Zero-Copy Binary .mlueb & WAL ]
               ↓
[ 1.3: Pure C-ABI & FFI Bridge ]
               ↓
[ 1.4: Native Physics & Collision Core ]
               ↓
[ 1.5: Native Rule Engine & Primary Cutover ]
               ↓
[ 1.6: SIMD Multi-Agent Rollout (Capstone) ]
```

---

## 3. Subphase Detailed Breakdown

### 🔹 Subphase 1.1: Hierarchical State-Trees & Query/Mutation Primitives

* **Objective**: Extend flat `state_variables` into nested document trees (objects, arrays, primitives) with declarative keypath mutations and conditions.
* **Why First**: State is MLUE's database. The data representation and mutation semantics must be locked before designing the binary memory layout or native engine.
* **Scope**:
  * **In-Scope**: Nested state JSON schema, dot/bracket path navigation (`a.b[0].c`), 5 atomic actions (`set_path`, `increment_path`, `push`, `pop`, `delete_key`), path condition triggers, array `.length` queries, static path validation in `loader.py`.
  * **Out-of-Scope**: Binary serialization, compiled native code, multi-threading.
* **Verification Gate**:
  * 100% backward compatibility with Phase 0 scenes.
  * Static rejection of malformed paths and type mismatches.
  * Emergent inventory/database capstone (`examples/inventory_system.mlue`) with 0 bespoke code.

---

### 🔹 Subphase 1.2: Zero-Copy Binary Document & WAL Persistence (`.mlueb`)

* **Objective**: Define a C-aligned binary format (`.mlueb`) and streaming Write-Ahead Log (WAL) for sub-microsecond disk persistence and instant state recovery.
* **Why Second**: Binary memory layout must directly encode the hierarchical state model defined in 1.1.
* **Scope**:
  * **In-Scope**: Fixed-alignment binary schema (64-bit alignment, IEEE 754 floats, interned string tables), append-only delta WAL, bidirectional lossless converter (`.mlue` $\leftrightarrow$ `.mlueb`).
  * **Out-of-Scope**: Native physics integration, C-ABI bindings.
* **Verification Gate**:
  * Lossless 1:1 roundtrip conversion across all example scenes.
  * Snapshot reload latency $< 10\,\mu\text{s}$.
  * Zero corruption across 1,000 simulated process crash/recovery cycles.

---

### 🔹 Subphase 1.3: Pure C-ABI Specification & Decoupled FFI Bridge

* **Objective**: Define the unalterable standard C header (`include/mlue_core.h`) and minimal FFI bridge to decouple the native engine from host languages.
* **Why Third**: The interface and memory ownership contract must be frozen before implementing internal native algorithms.
* **Scope**:
  * **In-Scope**: C header (`mlue_core.h`), opaque context handles, memory ownership invariants, minimal Python `ctypes` bridge (`runtime/native_bridge.py`) for dual-running tests.
  * **Out-of-Scope**: Physics algorithms, Python-specific bindings (`pybind11`/`Cython`).
* **Verification Gate**:
  * Cross-platform dynamic library linking (`.dll`, `.so`, `.dylib`).
  * 0 memory leaks across 1,000,000 create/step/free lifecycle cycles.

---

### 🔹 Subphase 1.4: Native Compiled Integrator & Spatial Collision Core

* **Objective**: Implement the bare-metal compiled physics engine (Rust / C) for 2D kinematics, boundary reflections, and pairwise circle/box collisions.
* **Why Fourth**: Implements validated Phase 0.2/0.3 physics in machine code before adding high-level rule complexity.
* **Scope**:
  * **In-Scope**: Discrete time integration ($\vec{v} \cdot \Delta t$), boundary clamping, circle/box collision impulses, uniform spatial hash grid ($O(N)$ broadphase).
  * **Out-of-Scope**: High-level rule triggers, entity destruction/spawning.
* **Verification Gate**:
  * **Throughput**: Single-threaded throughput $> 1,000,000\text{ ticks/s}$ ($< 1\,\mu\text{s}$ latency).
  * **Equivalence**: 100% bit-exact SHA-256 state digest match with Phase 0 reference engine after 50,000 steps.

---

### 🔹 Subphase 1.5: Native Rule Evaluator, Lifecycle & Primary Cutover

* **Objective**: Implement native rule condition evaluation and zero-allocation entity lifecycle mutations, switching CLI and MCP server to the compiled native engine by default.
* **Why Fifth**: Unifies native physics (1.4) with hierarchical state (1.1), completing the standalone native engine.
* **Scope**:
  * **In-Scope**: Native trigger evaluation (collision events, spatial bounds, state paths), native actions (`destroy`, `reset`, `set_property`, hierarchical mutations), default execution cutover in `mlue.py` and `mcp_server.py`.
  * **Out-of-Scope**: SIMD multi-agent batch vectorization.
* **Verification Gate**:
  * Full native execution of `breakout.mlue` and `pong.mlue` with 0 heap allocations per tick.
  * Python completely removed from the simulation hot path.

---

### 🔹 Subphase 1.6: SIMD Multi-Agent Vectorized Rollout Engine (Capstone)

* **Objective**: Vectorize the native core into a batched Structure-of-Arrays (SoA) engine for parallel multi-agent AI reinforcement learning rollouts.
* **Why Sixth (Capstone)**: Delivers the ultimate Phase 1 milestone: high-speed multi-environment simulation across multi-core CPU threads.
* **Scope**:
  * **In-Scope**: Batched step API (`mlue_step_batch`), Structure-of-Arrays memory layout, multi-threaded Rayon/OpenMP distribution, vectorized Python/MCP bridge.
  * **Out-of-Scope**: Network streaming / WebTransport (Phase 3).
* **Verification Gate**:
  * **Scale Benchmark**: 1,000 parallel game instances stepping at $> 10,000,000\text{ aggregate ticks/s}$.
  * Live telemetry export to web benchmark dashboard.

---

## 4. Scaffolding Boundary Policy for Phase 1

1. **Permitted Temporary Bridges**:
   * Standard C-FFI (`ctypes`) allowing existing Python CLI and MCP tools to invoke `libmlue_core`.
   * Dual-engine lockstep validator to verify 0 numerical drift between Python reference and Native core.
2. **Strictly Prohibited**:
   * No third-party physics libraries (Box2D, PhysX).
   * No Python-locked wrappers (`pybind11`, `Cython`).
   * No foreign runtime dependencies (standard C runtime linkage only).

---

## 5. Subphase Summary Matrix

| Subphase | Focus | Predecessor | Verification Gate |
| :--- | :--- | :--- | :--- |
| **1.1** | Hierarchical State-Trees | Phase 0.7 | Complete nested data mutations |
| **1.2** | Binary `.mlueb` & WAL | Subphase 1.1 | $< 10\,\mu\text{s}$ reload, 0 byte loss |
| **1.3** | Pure C-ABI & FFI Bridge | Subphase 1.2 | Zero leaks on 1M create/free cycles |
| **1.4** | Native Physics Core | Subphase 1.3 | $> 1,000,000\text{ ticks/s}$, bit-exact digest |
| **1.5** | Native Rule Engine & Cutover | Subphase 1.4 + 1.1 | Zero-allocation Pong/Breakout native run |
| **1.6** | SIMD Multi-Agent Rollout | Subphase 1.5 | $> 10,000,000\text{ aggregate ticks/s}$ |
