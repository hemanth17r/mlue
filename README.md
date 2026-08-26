# MLUE — Phase 0.5 Capstone (Emergent Pong)

> **"AI is the builder. Humans are users."**

MLUE is a long-term research and engineering project to build a fundamentally **AI-first software-to-hardware architecture**, built from physics and mathematics upward.

---

## 1. Phase 0.5 Objective (Phase 0 Capstone Proof)

Deliver the foundational capstone proof of the MLUE primitive vocabulary: **Emergent Pong**.

Proving that a complete, real-time interactive game emerges **100% from declarative MLUE primitives** without a single line of bespoke "game engine" code:
1. **State Variables**: Declarative document-level variables (`score_left`, `score_right`).
2. **Relational Condition Triggers & Actions**: Universal declarative rules evaluated on every simulation step:
   $$\text{Condition } (x_{\text{ball}} \le 0.025) \implies \text{Actions } \{\text{increment score\_right}, \text{reset ball position \& velocity}\}$$
3. **Emergent Game Loop**: Combining solid geometry, velocity integration, pairwise collisions, input channels, and trigger rules into a sovereign game system.

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
│   └── replacement_map.md            # Dependency tracking and replacement map
├── runtime/
│   ├── __init__.py                    # Package exports
│   ├── loader.py                      # Parses & validates .mlue representations (0.1 through 0.5)
│   ├── model.py                       # Computational data structures, rules & simulation state
│   ├── engine.py                      # Deterministic MLUE evaluation, collisions, inputs & rule engine
│   └── adapter.py                     # Bootstrap scaffolding adapter (Tkinter animation, keys & score HUD)
├── examples/
│   ├── first_object.mlue              # Phase 0.1 static circle entity
│   ├── bouncing_ball.mlue             # Phase 0.2 single bouncing ball simulation
│   ├── multi_entity_simulation.mlue   # Phase 0.2 multi-entity simulation (paddles + ball)
│   ├── collision_showcase.mlue        # Phase 0.3 multi-entity relational collision showcase
│   ├── interactive_paddles.mlue       # Phase 0.4 keyboard-controllable paddles
│   └── pong.mlue                      # Phase 0.5 Emergent Pong (Complete Capstone Game)
├── tests/
│   └── test_runtime.py                # Automated unit tests (12 tests: geometry, collisions, rules, match loop)
└── mlue.py                            # CLI runner (static snapshot & dynamic simulation)
```

---

## 3. How to Run

### Interactive Simulations (Desktop Window)
```bash
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
# Evaluate 60 simulation steps of Pong deterministically in headless mode
python mlue.py run examples/pong.mlue --headless --ticks 60
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
• Representation Schema (spec/0.1.md through spec/0.5.md)
• Normalized Spatial Extents, Geometry & Velocity Vectors
• Abstract Control Channels & Input Vector Modulation
• Pairwise Relational Collisions & Exact Normal Reflections
• Declarative Trigger Rules, State Variable Mutations & Entity Resets (runtime/engine.py)
─────────────────────────────────────────────────────────────────────────────
                     BOOTSTRAP LAYER (Disposable Scaffolding)
─────────────────────────────────────────────────────────────────────────────
• Host Runtime Language (Python 3.13 standard library)
• Host Windowing & Canvas Driver (Tkinter / Win32)
• Host Key Scancode Mapper & Score Header Display
```

* **No External Dependencies**: Built 100% with Python standard library (0 third-party packages).
* **Pure Mathematical Core**: All game rules, collision responses, input modulations, and score updates run inside `MLUEEngine`, with zero dependencies on external game frameworks.

---

## 5. Scope Boundaries

### What Was Built in Phase 0.5:
* Declarative state variables (`state_variables`).
* Universal declarative trigger rules (`rules`: conditions + actions).
* State variable mutations (`increment`, `set`) and entity state resets (`reset_entity`).
* The complete Emergent Pong game document (`examples/pong.mlue`).
* 12 automated unit tests verifying rules, triggers, score mutations, and full headless match simulations.

### What Was Deliberately NOT Built in Phase 0.5 (Strict Scope Control):
* Bespoke `PongManager` classes or hardcoded game scripts.
* Audio synthesis libraries.
* Network multiplayer sockets.
* Custom binary execution runtimes (Phase 1).
