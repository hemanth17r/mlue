#!/usr/bin/env python3
"""MLUE CLI Runner & Toolchain -- v2.5.0 (Phase 2 Capstone)

Executes MLUE representations (.mlue, .mlueb), compiles binary containers,
and manages Write-Ahead Log (.wal) recording and deterministic replay.
"""

import sys
import json
import argparse
from pathlib import Path
from runtime import load_mlue, MLUEEngine, TkinterAdapter, MLUEValidationError, lint_mlue


def handle_lint(args: argparse.Namespace) -> int:
    """Executes high-speed compile-time static diagnostic linting on an MLUE document."""
    file_path = Path(args.target_file)
    if not file_path.exists():
        print(f"Error: Target file not found at '{file_path}'", file=sys.stderr)
        return 1

    report = lint_mlue(file_path)

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(report.format_console())

    return 0 if report.valid else 1


def handle_compile(args: argparse.Namespace) -> int:
    """Notice for deprecated binary compiler."""
    print("[MLUE Deprecation] The binary .mlueb container format is deprecated in favor of canonical declarative JSON (.mlue).")
    print("  AI models and runtimes interact directly via standardized, zero-friction .mlue JSON schemas.")
    return 0


def handle_replay(args: argparse.Namespace) -> int:
    """Notice for deprecated WAL replayer."""
    print("[MLUE Deprecation] The binary WAL replayer is deprecated. Use deterministic headless execution from canonical .mlue scenes.")
    return 0


def handle_run(args: argparse.Namespace) -> int:
    """Runs simulation in headless or GUI mode."""
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
                    for e in state.entities:
                        pos_str = f"({e.position.x:.4f}, {e.position.y:.4f})"
                        vel_str = f"({e.velocity.vx:.4f}, {e.velocity.vy:.4f})"
                        print(f"  {step_idx:<6} {state.time:<10.4f} {e.id:<16} {pos_str:<26} {vel_str:<24}")

                print(f"[MLUE Engine] Simulation completed {ticks} steps deterministically. Final sim time: {state.time:.4f}s")
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
        print(f"  - Aggregate Throughput  : {throughput:,.0f} steps/second ({1e6/throughput:.2f} us/step)")
        return 0

    except MLUEValidationError as e:
        print(f"[MLUE Validation Error] {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[MLUE Batch Error] {e}", file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="MLUE CLI Toolchain -- Binary Compiler, Engine & Batch Rollout (v2.5.0)",
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

    # 4. Lint subcommand
    lint_parser = subparsers.add_parser("lint", help="Execute compile-time self-healing static diagnostics on .mlue scene")
    lint_parser.add_argument("target_file", help="Path to .mlue file to validate")
    lint_parser.add_argument("--json", action="store_true", help="Output machine-actionable JSON diagnostic report")

    # 5. Run subcommand (default / backward-compatible)
    run_parser = subparsers.add_parser("run", help="Run MLUE scene in GUI or headless mode")
    run_parser.add_argument("target_file", help="Path to .mlue or .mlueb file")
    run_parser.add_argument("--headless", action="store_true", help="Evaluate simulation without launching GUI window")
    run_parser.add_argument("--ticks", type=int, default=None, help="Number of simulation steps in headless mode")
    run_parser.add_argument("--dt", type=float, default=1.0 / 60.0, help="Delta time per step (default: 1/60 s)")
    run_parser.add_argument("--fps", type=int, default=60, help="Presentation frame rate (default: 60)")
    run_parser.add_argument("--duration", type=float, default=None, help="Simulation duration in seconds")

    # Fallback compatibility check
    if len(sys.argv) > 1 and sys.argv[1] not in ("compile", "replay", "batch", "run", "lint", "-h", "--help"):
        # Synthesize 'run' command
        sys.argv.insert(1, "run")

    args = parser.parse_args()

    if args.subcommand == "compile":
        return handle_compile(args)
    elif args.subcommand == "replay":
        return handle_replay(args)
    elif args.subcommand == "batch":
        return handle_batch(args)
    elif args.subcommand == "lint":
        return handle_lint(args)
    elif args.subcommand == "run":
        return handle_run(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
