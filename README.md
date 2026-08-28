# MLUE — Phase 0.7 Machine-Accessible AI Interface (Phase 0 Complete)

> **"AI is the builder. Humans are users."**

MLUE is a long-term research and engineering project to build a fundamentally **AI-first software-to-hardware architecture**, built from physics and mathematics upward.

---

## 1. Phase 0.7 Objective (Phase 0 Grand Milestone)

Establish the **Machine-Accessible AI Interface Substrate** exposing the mature, mathematically verified Phase 0 primitive vocabulary to external and local AI agents:
1. **Programmatic AI Interface (`runtime/ai_interface.py`)**: High-level Python API to query schema, statically validate scenes, run in-memory simulations, evaluate action vectors, inspect live states, and mutate entities.
2. **Model Context Protocol (MCP) Server (`mcp_server.py`)**: Zero-dependency standard MCP JSON-RPC server enabling any AI assistant (Antigravity, Claude Desktop, Cursor, local scripts) to autonomously construct and test MLUE worlds.
3. **Static Spatial Reachability Invariant Validation**: Compile-time rejection of mathematically unreachable rule triggers before execution.
4. **Complete Phase 0 Foundation**: Unifying static geometry, dynamic motion, pairwise solid collisions, control channels, declarative state variables, destruction lifecycle, and AI tool introspection into a sovereign 100% self-contained codebase.

---

## 2. Repository Structure

```text
mlue/
├── README.md                          # Project overview and architectural boundaries
├── mcp_server.py                      # Standalone Model Context Protocol (MCP) JSON-RPC Server
├── spec/
│   ├── 0.1.md                        # Phase 0.1 spec (static circle)
│   ├── 0.2.md                        # Phase 0.2 spec (dynamic state, boxes & velocity)
│   ├── 0.3.md                        # Phase 0.3 spec (relational constraints & collisions)
│   ├── 0.4.md                        # Phase 0.4 spec (input signals & control channels)
│   ├── 0.5.md                        # Phase 0.5 spec (state variables, rules & Emergent Pong)
│   ├── 0.6.md                        # Phase 0.6 spec (collision events, destruction & Emergent Breakout)
│   └── replacement_map.md            # Dependency tracking and replacement map
├── runtime/
│   ├── __init__.py                    # Package exports
│   ├── loader.py                      # Parses & validates .mlue representations & spatial reachability
│   ├── model.py                       # Computational data structures, lifecycle & simulation state
│   ├── engine.py                      # Deterministic MLUE evaluation, collisions, destruction & rule engine
│   ├── ai_interface.py                # High-level programmatic interface for autonomous AI agents
│   └── adapter.py                     # Bootstrap scaffolding adapter (Tkinter animation & HUDs)
├── examples/
│   ├── first_object.mlue              # Phase 0.1 static circle entity
│   ├── bouncing_ball.mlue             # Phase 0.2 single bouncing ball simulation
│   ├── multi_entity_simulation.mlue   # Phase 0.2 multi-entity simulation (paddles + ball)
│   ├── collision_showcase.mlue        # Phase 0.3 multi-entity relational collision showcase
│   ├── interactive_paddles.mlue       # Phase 0.4 keyboard-controllable paddles
│   ├── pong.mlue                      # Phase 0.5 Emergent Pong (Complete Capstone Game)
│   └── breakout.mlue                  # Phase 0.6 Emergent Breakout (Destruction Capstone Game)
├── tests/
│   └── test_runtime.py                # Automated unit tests (19 tests: geometry, collisions, AI sessions, MCP)
└── mlue.py                            # CLI runner (static snapshot & dynamic simulation)
```

---

## 3. How to Run

### Interactive Simulations (Desktop Window)
```bash
# Play Phase 0.6 Emergent Breakout (Paddle: A/D or Left/Right)
python mlue.py run examples/breakout.mlue

# Play Phase 0.5 Emergent Pong (Left: W/S, Right: Up/Down)
python mlue.py run examples/pong.mlue

# Run Phase 0.4 interactive paddles
python mlue.py run examples/interactive_paddles.mlue

# Run Phase 0.3 collision showcase
python mlue.py run examples/collision_showcase.mlue

# Run Phase 0.2 bouncing ball
python mlue.py run examples/bouncing_ball.mlue

# Run Phase 0.1 static object
python mlue.py run examples/first_object.mlue
```

### Running the MCP Server
```bash
# Run standalone MCP protocol self-test
python mcp_server.py --test

# Run MCP server on standard I/O (for Antigravity, Claude Desktop, Cursor)
python mcp_server.py
```

### Headless Simulation Engine
```bash
# Evaluate 60 simulation steps of Breakout deterministically in headless mode
python mlue.py run examples/breakout.mlue --headless --ticks 60
```

### Run Unit Tests
```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## 4. Architectural Boundary

```text
                     MLUE LAYER (Native & Enduring)
─────────────────────────────────────────────────────────────────────────────
• Representation Schema (spec/0.1.md through spec/0.6.md)
• Normalized Spatial Extents, Geometry & Velocity Vectors
• Abstract Control Channels & Input Vector Modulation
• Pairwise Relational Collisions & Exact Normal Reflections
• Collision Event Sets, Entity Lifecycle Destruction & State Conditions
• Static Spatial Reachability Invariant Validation (runtime/loader.py)
• Programmatic AI Interface & In-Memory Sessions (runtime/ai_interface.py)
• Standard Model Context Protocol (MCP) Server (mcp_server.py)
─────────────────────────────────────────────────────────────────────────────
                     BOOTSTRAP LAYER (Disposable Scaffolding)
─────────────────────────────────────────────────────────────────────────────
• Host Runtime Language (Python 3.13 standard library)
• Host Windowing & Canvas Driver (Tkinter / Win32)
• Host Key Scancode Mapper & Multi-variable HUD Display
```

* **No External Dependencies**: Built 100% with Python standard library (0 third-party packages).
* **Pure Mathematical Core**: Operates with microsecond latency and zero external dependencies.

---

## 5. Scope Boundaries

### What Was Built in Phase 0 (Phases 0.1 through 0.7):
* Universal declarative 2D geometry (`circle`, `box`) in normalized coordinate space $[0, 1]$.
* First-order discrete time integration and deterministic step loop $\Delta t$.
* Pairwise relational collisions and impulse normal reflections.
* Abstract input channels with velocity modulation and boundary clamping.
* Declarative document-level state variables.
* Universal trigger rules (collision events, spatial conditions, state conditions).
* Dynamic lifecycle actions (`destroy_entity`, `set_property`, `increment`, `set`, `reset_entity`).
* Static spatial reachability invariant validation.
* Two emergent capstone applications (Pong and Breakout).
* High-level AI programmatic interface (`MLUEAIInterface`).
* Full Model Context Protocol (MCP) JSON-RPC server (`mcp_server.py`).
* 19 automated unit tests with 100% pass rate.

### What Is Next (Phase 1: Native Substrate Transition):
* Replacing Python host runtime with native compiled execution layer (Rust/C core).
* Direct binary representation serialization.
* Native rendering adapter replacing Tkinter.
