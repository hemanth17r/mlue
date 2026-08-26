#!/usr/bin/env python3
"""MLUE CLI Runner — Phase 0.2 Bootstrap

Executes an MLUE document representation or simulation through the MLUE runtime engine.
"""

import sys
import argparse
from pathlib import Path
from runtime import load_mlue, MLUEEngine, TkinterAdapter, MLUEValidationError


def main() -> int:
    parser = argparse.ArgumentParser(
        description="MLUE Runtime Engine Runner (Phase 0.2)",
        usage="python mlue.py [run] <path_to_file.mlue> [options]"
    )
    parser.add_argument("command_or_file", nargs="*", help="File path, or 'run <path>'")
    parser.add_argument("--headless", action="store_true", help="Evaluate simulation without launching GUI window")
    parser.add_argument("--ticks", type=int, default=None, help="Number of simulation steps to evaluate in headless mode")
    parser.add_argument("--dt", type=float, default=1.0 / 60.0, help="Delta time per simulation step (default: 1/60 s)")
    parser.add_argument("--fps", type=int, default=60, help="Presentation frame rate (default: 60)")
    parser.add_argument("--duration", type=float, default=None, help="Simulation duration in seconds")

    args = parser.parse_args()

    pos_args = args.command_or_file
    if not pos_args:
        parser.print_help()
        return 0

    if pos_args[0] == "run":
        if len(pos_args) < 2:
            print("Error: Missing target .mlue file after 'run'.", file=sys.stderr)
            return 1
        target_file = pos_args[1]
    else:
        target_file = pos_args[0]

    file_path = Path(target_file)
    if not file_path.exists():
        print(f"Error: MLUE file not found at '{target_file}'", file=sys.stderr)
        return 1

    try:
        # 1. Load and validate MLUE representation
        doc = load_mlue(file_path)
        engine = MLUEEngine()

        has_motion = any(e.velocity.vx != 0.0 or e.velocity.vy != 0.0 for e in doc.entities)

        print(f"[MLUE Engine] Successfully loaded '{file_path.name}' (schema version: {doc.version})")
        print(f"[MLUE Engine] Viewport: {doc.environment.width}x{doc.environment.height}, Entities: {len(doc.entities)}")

        if not has_motion:
            # Static snapshot evaluation
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
            # Dynamic simulation
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
        print(f"[MLUE Runtime Error] Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
