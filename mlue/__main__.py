#!/usr/bin/env python3
"""MLUE Runner & Viewer

Usage:
    python -m mlue <path/to/scene.mlue> [--headless] [--ticks N]
"""

import sys
from pathlib import Path
from mlue import load_mlue, MLUEEngine, TkinterAdapter, lint_mlue


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("MLUE: AI-Native Software Substrate (v2.5.0)")
        print("\nUsage:")
        print("  mlue-mcp                          Start the Model Context Protocol (MCP) server for AI agents")
        print("  python -m mlue <scene.mlue>       Launch desktop visual preview of an MLUE scene")
        print("  python -m mlue <scene.mlue> --lint Statically lint an MLUE document")
        print("  python -m mlue <scene.mlue> --headless Run simulation headlessly")
        sys.exit(0)

    target = Path(sys.argv[1])
    if not target.exists():
        print(f"Error: File not found: {target}", file=sys.stderr)
        sys.exit(1)

    if "--lint" in sys.argv:
        report = lint_mlue(target)
        print(report.format_console())
        sys.exit(0 if report.valid else 1)

    doc = load_mlue(target)
    engine = MLUEEngine()

    if "--headless" in sys.argv:
        state = engine.init_simulation(doc)
        ticks = 10
        print(f"[MLUE Engine] Running {ticks} headless simulation ticks for '{target.name}'...")
        for _ in range(ticks):
            state = engine.step(state, dt=1.0 / 60.0)
        print(f"[MLUE Engine] Headless run complete. Entities active: {len(state.entities)}")
    else:
        print(f"[MLUE Adapter] Launching preview for '{target.name}'...")
        adapter = TkinterAdapter()
        adapter.run_simulation(engine, doc, block=True)


if __name__ == "__main__":
    main()
