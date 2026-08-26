# MLUE — Phase 0.6 Emergent Destruction & Dynamic Collision Triggers

> **"AI is the builder. Humans are users."**

MLUE is a long-term research and engineering project to build a fundamentally **AI-first software-to-hardware architecture**, built from physics and mathematics upward.

---

## 1. Phase 0.6 Objective

Advance MLUE declarative architecture from boundary rules to **dynamic collision-based triggers and entity lifecycle management**:
1. **Collision-Based Rule Triggers**: First-class detection and firing of events when two solid entities collide (`event: "collision"`).
2. **Entity Lifecycle Management**: Deactivation and removal of entities from the computational and rendering space (`"destroy_entity"` / `"deactivate_entity"`).
3. **Property Mutations**: Dynamic modification of entity properties (`"set_property"`).
4. **State Variable Condition Triggers**: Evaluating rules based on document-level state variables (e.g. win/loss thresholds: `bricks_remaining <= 0`).
5. **Emergent Breakout Capstone**: A complete Brick Breaker game (`examples/breakout.mlue`) composed 100% from declarative MLUE primitives without bespoke game engine code.

---

## 2. Repository Structure

```text
mlue/
├── README.md                          # Project overview and architectural boundaries
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
│   ├── loader.py                      # Parses & validates .mlue representations (0.1 through 0.6)
│   ├── model.py                       # Computational data structures, lifecycle & simulation state
│   ├── engine.py                      # Deterministic MLUE evaluation, collisions, destruction & rule engine
│   └── adapter.py                     # Bootstrap scaffolding adapter (Tkinter animation, keys & multi-HUD)
├── examples/
│   ├── first_object.mlue              # Phase 0.1 static circle entity
│   ├── bouncing_ball.mlue             # Phase 0.2 single bouncing ball simulation
│   ├── multi_entity_simulation.mlue   # Phase 0.2 multi-entity simulation (paddles + ball)
│   ├── collision_showcase.mlue        # Phase 0.3 multi-entity relational collision showcase
│   ├── interactive_paddles.mlue       # Phase 0.4 keyboard-controllable paddles
│   ├── pong.mlue                      # Phase 0.5 Emergent Pong (Complete Capstone Game)
│   └── breakout.mlue                  # Phase 0.6 Emergent Breakout (Destruction Capstone Game)
├── tests/
│   └── test_runtime.py                # Automated unit tests (14 tests: geometry, collisions, destruction, matches)
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

### Headless Mode (Deterministic Evaluation Engine)
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
• Collision Event Sets, Entity Lifecycle Destruction & State Conditions (runtime/engine.py)
─────────────────────────────────────────────────────────────────────────────
                     BOOTSTRAP LAYER (Disposable Scaffolding)
─────────────────────────────────────────────────────────────────────────────
• Host Runtime Language (Python 3.13 standard library)
• Host Windowing & Canvas Driver (Tkinter / Win32)
• Host Key Scancode Mapper & Multi-variable HUD Display
```

* **No External Dependencies**: Built 100% with Python standard library (0 third-party packages).
* **Pure Mathematical Core**: Collision detection, destruction filtering, and state transitions operate inside `MLUEEngine`, with zero external dependencies.

---

## 5. Scope Boundaries

### What Was Built in Phase 0.6:
* First-class collision event rules (`event: "collision"`).
* Entity lifecycle deactivation actions (`destroy_entity`, `deactivate_entity`).
* Property mutation actions (`set_property`).
* State variable condition rules (e.g. `bricks_remaining <= 0`).
* Horizontal player control routing (`player_bottom`).
* The complete Emergent Breakout game document (`examples/breakout.mlue`).
* 14 automated unit tests verifying destruction, collision triggers, state conditions, and regression.

### What Was Deliberately NOT Built in Phase 0.6 (Strict Scope Control):
* Bespoke `BreakoutManager` or hardcoded brick grid scripts.
* Particle effect explosion engines.
* Audio synthesis libraries.
* Network multiplayer sockets.
