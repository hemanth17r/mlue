#!/usr/bin/env python3
"""MLUE CLI Runner & Toolchain — Subphase 1.2

Executes MLUE representations (.mlue, .mlueb), compiles binary containers,
and manages Write-Ahead Log (.wal) recording and deterministic replay.
"""

import sys
import argparse
from pathlib import Path
from runtime import load_mlue, MLUEEngine, TkinterAdapter, MLUEValidationError
from runtime.binary import save_mlueb, load_mlueb
from runtime.wal import WALWriter, WALReader, WALReplayer


def handle_compile(args: argparse.Namespace) -> int:
    """Compiles a .mlue JSON document into a zero-copy .mlueb binary document."""
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return 1

    out_path = Path(args.output) if args.output else input_path.with_suffix(".mlueb")

    try:
        doc = load_mlue(input_path)
        bytes_written = save_mlueb(doc, out_path)
        orig_size = input_path.stat().st_size
        ratio = (1.0 - (bytes_written / max(orig_size, 1))) * 100.0
        print(f"[MLUE Binary Compiler] Successfully compiled '{input_path.name}' -> '{out_path.name}'")
        print(f"  - Original JSON Size: {orig_size} bytes")
        print(f"  - Binary .mlueb Size: {bytes_written} bytes ({ratio:.1f}% reduction)")
        return 0
    except Exception as e:
        print(f"[MLUE Compiler Error] {e}", file=sys.stderr)
        return 1


def handle_replay(args: argparse.Namespace) -> int:
    """Replays a simulation from a .wal log file deterministically."""
    scene_path = Path(args.scene_file)
    wal_path = Path(args.wal_file)

    if not scene_path.exists():
        print(f"Error: Scene file not found: {scene_path}", file=sys.stderr)
        return 1
    if not wal_path.exists():
        print(f"Error: WAL file not found: {wal_path}", file=sys.stderr)
        return 1

    try:
        doc = load_mlue(scene_path)
        scene_hash, frames, warning = WALReader.read_frames(wal_path)
        if warning:
            print(f"[MLUE WAL Warning] {warning}")

        print(f"[MLUE WAL Replayer] Loaded {len(frames)} frames from '{wal_path.name}' for scene '{scene_path.name}'.")
        replayer = WALReplayer()
        final_state = replayer.replay(doc, frames, dt=args.dt, total_ticks=args.ticks)

        print(f"[MLUE WAL Replayer] Replay complete. Final sim time: {final_state.time:.4f}s.")
        print(f"  Active entities: {sum(1 for e in final_state.entities if e.active)}/{len(final_state.entities)}")
        print(f"  State Variables: {final_state.state_variables}")
        return 0
    except Exception as e:
        print(f"[MLUE Replay Error] {e}", file=sys.stderr)
        return 1


def handle_run(args: argparse.Namespace) -> int:
    """Runs simulation with optional WAL logging."""
    file_path = Path(args.target_file)
    if not file_path.exists():
        print(f"Error: MLUE file not found at '{file_path}'", file=sys.stderr)
        return 1

    try:
        doc = load_mlue(file_path)
        engine = MLUEEngine()

        has_interactive = any(
            e.velocity.vx != 0.0 or e.velocity.vy != 0.0 or "control" in e.properties for e in doc.entities
        ) or bool(doc.rules)

        print(f"[MLUE Engine] Successfully loaded '{file_path.name}' (schema version: {doc.version})")
        print(f"[MLUE Engine] Viewport: {doc.environment.width}x{doc.environment.height}, Entities: {len(doc.entities)}")

        wal_writer = WALWriter(args.wal) if args.wal else None

        if not has_interactive:
            result = engine.evaluate(doc)
            print(f"[MLUE Engine] Evaluated {len(result.shapes)} static shape(s):")
            for shape in result.shapes:
                print(f"  - ID: '{shape.id}', Type: {shape.type}, Center: {shape.center}, BBox: {shape.bbox}, Color: {shape.color}")

            if not args.headless:
                print("[MLUE Adapter] Launching presentation window...")
                adapter = TkinterAdapter()
                adapter.present(result, block=True)
                print("[MLUE Adapter] Presentation closed.")
        else:
            state = engine.init_simulation(doc)
            print(f"[MLUE Engine] Dynamic simulation initialized with {len(state.entities)} entity(ies).")

            if args.headless:
                ticks = args.ticks if args.ticks is not None else 10
                dt = args.dt
                print(f"[MLUE Engine] Evaluating {ticks} simulation step(s) in headless mode (dt={dt:.4f}s):")
                print(f"  {'Step':<6} {'SimTime':<10} {'Entity ID':<16} {'Norm Position (x, y)':<26} {'Velocity (vx, vy)':<24}")
                print("  " + "-" * 84)

                for step_idx in range(1, ticks + 1):
                    state = engine.step(state, dt)
                    if wal_writer:
                        wal_writer.log_checkpoint(step_idx, state.time, state)

                    for e in state.entities:
                        pos_str = f"({e.position.x:.4f}, {e.position.y:.4f})"
                        vel_str = f"({e.velocity.vx:.4f}, {e.velocity.vy:.4f})"
                        print(f"  {step_idx:<6} {state.time:<10.4f} {e.id:<16} {pos_str:<26} {vel_str:<24}")

                print(f"[MLUE Engine] Simulation completed {ticks} steps deterministically. Final sim time: {state.time:.4f}s")
                if wal_writer:
                    wal_writer.close()
                    print(f"[MLUE WAL] Recorded {wal_writer.frames_written} frames to '{args.wal}'")
            else:
                print(f"[MLUE Adapter] Launching interactive simulation at {args.fps} FPS...")
                adapter = TkinterAdapter()
                adapter.run_simulation(engine, doc, fps=args.fps, duration=args.duration, block=True)
                print("[MLUE Adapter] Simulation presentation closed.")

        return 0

    except MLUEValidationError as e:
        print(f"[MLUE Validation Error] {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[MLUE Execution Error] {e}", file=sys.stderr)
        return 1


def handle_batch(args) -> int:
    """Execute high-speed vectorized multi-agent parallel simulation batch."""
    from runtime.batch import BatchEnvironmentPool
    import time

    target_path = Path(args.target_file).resolve()
    if not target_path.exists():
        print(f"[MLUE Error] Scene file not found: {target_path}", file=sys.stderr)
        return 1

    try:
        doc = load_mlue(target_path)
        num_envs = args.envs
        ticks = args.ticks
        dt = args.dt

        print(f"[MLUE Batch Engine] Initializing {num_envs:,} parallel environments from '{target_path.name}'...")
        pool = BatchEnvironmentPool(doc, num_envs=num_envs)

        start_time = time.perf_counter()
        for t in range(ticks):
            pool.step(dt=dt)
        elapsed = time.perf_counter() - start_time

        total_steps = num_envs * ticks
        throughput = total_steps / max(elapsed, 1e-9)

        print(f"[MLUE Batch Engine] Completed {total_steps:,} total simulation steps in {elapsed:.4f}s.")
        print(f"  - Parallel Environments : {num_envs:,}")
        print(f"  - Ticks per Environment : {ticks:,}")
        print(f"  - Aggregate Throughput  : {throughput:,.0f} steps/second ({1e6/throughput:.2f} µs/step)")
        return 0

    except MLUEValidationError as e:
        print(f"[MLUE Validation Error] {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[MLUE Batch Error] {e}", file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="MLUE CLI Toolchain — Binary Compiler, Engine & Batch Rollout (Phase 1.6)",
    )
    subparsers = parser.add_subparsers(dest="subcommand")

    # 1. Compile subcommand
    compile_parser = subparsers.add_parser("compile", help="Compile .mlue JSON scene to .mlueb binary document")
    compile_parser.add_argument("input_file", help="Path to input .mlue file")
    compile_parser.add_argument("-o", "--output", help="Path to output .mlueb file (default: same name with .mlueb)")

    # 2. Replay subcommand
    replay_parser = subparsers.add_parser("replay", help="Replay simulation deterministically from .wal log")
    replay_parser.add_argument("scene_file", help="Path to .mlue or .mlueb scene file")
    replay_parser.add_argument("wal_file", help="Path to .wal log file")
    replay_parser.add_argument("--ticks", type=int, default=None, help="Number of ticks to replay (default: all logged ticks)")
    replay_parser.add_argument("--dt", type=float, default=1.0 / 60.0, help="Delta time step (default: 1/60s)")

    # 3. Batch subcommand
    batch_parser = subparsers.add_parser("batch", help="Run high-throughput parallel batch simulation")
    batch_parser.add_argument("target_file", help="Path to .mlue or .mlueb file")
    batch_parser.add_argument("--envs", type=int, default=100, help="Number of parallel environments (default: 100)")
    batch_parser.add_argument("--ticks", type=int, default=1000, help="Number of simulation steps per environment (default: 1000)")
    batch_parser.add_argument("--dt", type=float, default=1.0 / 60.0, help="Delta time per step (default: 1/60 s)")

    # 4. Run subcommand (default / backward-compatible)
    run_parser = subparsers.add_parser("run", help="Run MLUE scene in GUI or headless mode")
    run_parser.add_argument("target_file", help="Path to .mlue or .mlueb file")
    run_parser.add_argument("--headless", action="store_true", help="Evaluate simulation without launching GUI window")
    run_parser.add_argument("--ticks", type=int, default=None, help="Number of simulation steps in headless mode")
    run_parser.add_argument("--dt", type=float, default=1.0 / 60.0, help="Delta time per step (default: 1/60 s)")
    run_parser.add_argument("--fps", type=int, default=60, help="Presentation frame rate (default: 60)")
    run_parser.add_argument("--duration", type=float, default=None, help="Simulation duration in seconds")
    run_parser.add_argument("--wal", type=str, default=None, help="Path to write Write-Ahead Log (.wal)")

    # Fallback compatibility check
    if len(sys.argv) > 1 and sys.argv[1] not in ("compile", "replay", "batch", "run", "-h", "--help"):
        # Synthesize 'run' command
        sys.argv.insert(1, "run")

    args = parser.parse_args()

    if args.subcommand == "compile":
        return handle_compile(args)
    elif args.subcommand == "replay":
        return handle_replay(args)
    elif args.subcommand == "batch":
        return handle_batch(args)
    elif args.subcommand == "run":
        return handle_run(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
