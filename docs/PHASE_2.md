# MLUE Phase 2: Multi-Agent Continuous Constraint Manifolds & Rich Primitives

## 1. Overview & Objective

Phase 2 expands MLUE from 2D linear kinematics (`circle`, `box`) into a rich **Continuous Constraint Simulation Substrate** with extended geometric primitives (`segment`, `capsule`, `text`), rotational dynamics, distance/spring constraints, and direct AI reinforcement learning adapters (`gym.Env` / Tensor buffers).

The primary objectives of Phase 2 are:
1. **Extended Geometric Primitives**: Full spatial support for line segments, rounded capsules, and declarative state-bound typography.
2. **Continuous Constraint Manifolds**: Friction coefficients, elasticity restitution, and multi-body distance/spring joints.
3. **Rotational Dynamics**: Angular orientation ($\theta$), rotational inertia, and torque impulse resolution.
4. **Zero-Copy AI RL Adapters**: Direct integration with Python `gym.Env`, PyTorch, and JAX tensor memory buffers.
5. **Live AI Canvas & Hot-Reload Protocol**: Real-time WebSocket state streaming for AI visual inspection without DOM scraping.

---

## 2. Subphase Progression & Roadmap

```text
[ 2.1: Rich Geometric Primitives (segment, capsule, text) ]
                          ↓
[ 2.2: Continuous Constraint Manifolds & Rotational Dynamics ]
                          ↓
[ 2.3: Zero-Copy AI RL Gym Adapters & Tensor Buffers ]
                          ↓
[ 2.4: Live AI Visual Canvas & WebSocket Hot-Reload ]
                          ↓
[ 2.5: Phase 2 Capstone: Multi-Agent Continuous Physics Arena ]
```

---

## 3. Subphase Detailed Breakdown

### 🔹 Subphase 2.1: Rich Geometric Primitives (`segment`, `capsule`, `text`)
* **Objective**: Introduce continuous line segments for ramps and polygon boundaries, capsules for character hitboxes, and text entities with dynamic state interpolation.
* **Declarative Schema Extensions**:
  * `segment`: Defined by start $(x_1, y_1)$ and end $(x_2, y_2)$ coordinates with line thickness.
  * `capsule`: Defined by line segment core and radius $r$.
  * `text`: Defined by position, font size, color, and formatted template string (e.g., `"Score: {game.score}"`).
* **Verification Gate**: Continuous raycast accuracy $< 10^{-7}$, analytical GJK/SAT distance parity, 0 text layout memory leaks.

---

### 🔹 Subphase 2.2: Continuous Constraint Manifolds & Rotational Dynamics
* **Objective**: Add angular momentum, rotational inertia ($I$), friction manifolds ($\mu_s, \mu_k$), and distance/spring constraints.
* **Scope**:
  * Angular orientation $\theta \in [-\pi, \pi]$ and angular velocity $\omega$.
  * Distance constraints (rigid rods, elastic springs) connecting pairs of entities.
  * Coulomb friction model along contact tangent planes.
* **Verification Gate**: Conservation of total angular and linear momentum (Drift $\le 1,000\text{ PPB}$).

---

### 🔹 Subphase 2.3: Zero-Copy AI RL Gym Adapters & Tensor Buffers
* **Objective**: Provide native compatibility with standard AI reinforcement learning libraries (Gymnasium, PettingZoo, Stable-Baselines3, RLlib).
* **Scope**:
  * `MLUEGymEnv(gym.Env)`: Direct vectorized observation tensors and action spaces.
  * Zero-copy pointer bridge passing C memory buffers directly into PyTorch / NumPy arrays without serialization.
* **Verification Gate**: $> 1,000,000\text{ steps/second}$ throughput inside standard PyTorch training loops.

---

### 🔹 Subphase 2.4: Live AI Visual Canvas & WebSocket Hot-Reload
* **Objective**: Enable real-time remote rendering and live interactive scene editing for AI developer interfaces.
* **Scope**:
  * Lightweight binary WebSocket server broadcasting compressed state snapshots.
  * Live declarative patching: mutate entities or rules on-the-fly with zero process restarts.
* **Verification Gate**: $< 5\text{ ms}$ broadcast latency over local loopback.

---

### 🔹 Subphase 2.5: Phase 2 Grand Capstone (Multi-Agent Physics Arena)
* **Objective**: Deliver a complex multi-agent simulation arena featuring rotating obstacles, spring-linked vehicles, dynamic score HUDs, and parallel AI training.
* **Verification Gate**: 100% passing across all unit tests and expanded invariant benchmarks.
