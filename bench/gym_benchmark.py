"""MLUE Gymnasium & RL Sensor Performance Benchmark.

Measures single-environment step throughput, LiDAR perception latency,
memory allocation churn (tracemalloc), and parallel multi-environment rollout speed.
Adheres strictly to Tier L1 Substrate Decoupling.
"""

import sys
import time
import tracemalloc
from pathlib import Path

# Ensure repo root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from runtime.gym import MLUEGymEnv
from runtime.tensor import ObservationSpec, BatchTensorObservationBuffer
from runtime.engine import MLUEEngine
from runtime.loader import load_mlue


def run_gym_benchmark(num_steps: int = 50000) -> dict:
    scene_path = Path(__file__).parent.parent / "examples" / "gym_warehouse_amr.mlue"
    print(f"[MLUE Benchmark] Loading reference AMR environment: {scene_path}")

    # 1. Single-Environment Step Throughput (With 8-Ray LiDAR)
    obs_spec = ObservationSpec(
        entity_ids=["amr_robot", "docking_bay"],
        include_velocities=True,
        lidar_entity_id="amr_robot",
        lidar_num_rays=8,
        state_variables=["score", "docked"],
    )

    env = MLUEGymEnv(
        mlue_source=scene_path,
        obs_spec=obs_spec,
        action_channels=["robot_drive"],
        continuous_actions=True,
        max_episode_steps=num_steps + 10,
    )

    env.reset()
    print(f"[MLUE Benchmark] Running {num_steps:,} steps on single Gym environment with 8-ray LiDAR...")

    # Warmup
    for _ in range(100):
        env.step([0.5])

    t0 = time.perf_counter_ns()
    for _ in range(num_steps):
        env.step([0.25])
    elapsed_ns = time.perf_counter_ns() - t0

    elapsed_s = elapsed_ns / 1e9
    throughput_steps_per_sec = num_steps / elapsed_s
    latency_us_per_step = (elapsed_ns / num_steps) / 1000.0

    print(f"[Result] Single-Env Throughput: {throughput_steps_per_sec:,.0f} steps/s ({latency_us_per_step:.2f} us/step)")

    # 2. Memory Allocation Churn Audit
    tracemalloc.start()
    snapshot_before = tracemalloc.take_snapshot()

    churn_steps = 10000
    for _ in range(churn_steps):
        env.step([0.1])

    snapshot_after = tracemalloc.take_snapshot()
    tracemalloc.stop()

    stats = snapshot_after.compare_to(snapshot_before, "lineno")
    total_alloc_bytes = sum(s.size_diff for s in stats if s.size_diff > 0)
    bytes_per_step = total_alloc_bytes / churn_steps

    print(f"[Result] Memory Churn: {bytes_per_step:.2f} B/step over {churn_steps:,} steps")

    # 3. Parallel Batch Rollout Throughput (100 Envs)
    doc = load_mlue(scene_path)
    engine = MLUEEngine()
    num_envs = 100
    batch_ticks = 1000
    batch_buf = BatchTensorObservationBuffer(num_envs=num_envs, spec=obs_spec, use_numpy=True)
    states = [engine.init_simulation(doc) for _ in range(num_envs)]

    print(f"[MLUE Benchmark] Stepping {num_envs} parallel environments across {batch_ticks} ticks ({num_envs * batch_ticks:,} total steps)...")
    t0_batch = time.perf_counter_ns()
    inputs = {"robot_drive": 0.3}

    for _ in range(batch_ticks):
        for i in range(num_envs):
            states[i] = engine.step(states[i], dt=0.0167, inputs=inputs)
            batch_buf.extract_env(i, states[i], engine=engine)

    batch_elapsed_ns = time.perf_counter_ns() - t0_batch
    batch_elapsed_s = batch_elapsed_ns / 1e9
    total_batch_steps = num_envs * batch_ticks
    batch_throughput = total_batch_steps / batch_elapsed_s

    print(f"[Result] 100-Env Batch Throughput: {batch_throughput:,.0f} steps/s ({(batch_elapsed_ns / total_batch_steps) / 1000.0:.2f} us/step)")

    return {
        "single_env_steps_per_sec": throughput_steps_per_sec,
        "latency_us_per_step": latency_us_per_step,
        "bytes_per_step": bytes_per_step,
        "batch_steps_per_sec": batch_throughput,
    }


if __name__ == "__main__":
    run_gym_benchmark()
