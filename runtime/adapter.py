"""MLUE Phase 0.5 Bootstrap Display Adapter

Temporary scaffolding adapter that maps evaluated MLUE computational state,
simulations, and state variable HUDs to an observable desktop window via Tkinter.
"""

import sys
import time
from typing import Optional, Dict, Set
from .model import EvaluationResult, MLUEDocument, SimulationState, ComputedShape
from .engine import MLUEEngine


class TkinterAdapter:
    """Disposable bootstrap scaffolding for rendering MLUE state and simulations to OS display."""

    def __init__(self, title: str = "MLUE Runtime — Phase 0.5 Capstone"):
        self.title = title

    def _draw_shape(self, canvas, shape: ComputedShape):
        """Draws a single ComputedShape to Tkinter canvas."""
        x0, y0, x1, y1 = shape.bbox
        if shape.type == "circle":
            return canvas.create_oval(x0, y0, x1, y1, fill=shape.color, outline="")
        elif shape.type == "box":
            return canvas.create_rectangle(x0, y0, x1, y1, fill=shape.color, outline="")
        return None

    def present(self, result: EvaluationResult, block: bool = True) -> None:
        """Renders an instantaneous evaluated MLUE state in a static GUI window."""
        try:
            import tkinter as tk
        except ImportError as e:
            print(f"[MLUE Scaffolding Error] Tkinter is not available: {e}", file=sys.stderr)
            return

        root = tk.Tk()
        root.title(self.title)
        root.geometry(f"{result.width}x{result.height}")
        root.resizable(False, False)

        canvas = tk.Canvas(
            root,
            width=result.width,
            height=result.height,
            bg=result.background,
            highlightthickness=0,
        )
        canvas.pack(fill=tk.BOTH, expand=True)

        for shape in result.shapes:
            self._draw_shape(canvas, shape)

        if block:
            root.mainloop()
        else:
            root.update()

    def run_simulation(
        self,
        engine: MLUEEngine,
        doc: MLUEDocument,
        fps: int = 60,
        duration: Optional[float] = None,
        block: bool = True,
    ) -> None:
        """Runs a fixed-timestep interactive simulation loop presenting in a GUI window with input routing and HUD."""
        try:
            import tkinter as tk
        except ImportError as e:
            print(f"[MLUE Scaffolding Error] Tkinter is not available: {e}", file=sys.stderr)
            return

        state = engine.init_simulation(doc)
        dt = 1.0 / max(1, fps)
        interval_ms = int(1000.0 / max(1, fps))

        root = tk.Tk()
        root.title(f"{self.title} ({fps} FPS)")
        root.geometry(f"{state.environment.width}x{state.environment.height}")
        root.resizable(False, False)

        canvas = tk.Canvas(
            root,
            width=state.environment.width,
            height=state.environment.height,
            bg=state.environment.background,
            highlightthickness=0,
        )
        canvas.pack(fill=tk.BOTH, expand=True)

        # Initial shape creation
        item_ids: Dict[str, int] = {}
        for shape in state.result.shapes:
            cid = self._draw_shape(canvas, shape)
            if cid is not None:
                item_ids[shape.id] = cid

        # HUD Text item for state variables (e.g. scores)
        hud_id: Optional[int] = None
        if state.state_variables:
            hud_text = "   ".join(f"{k.upper()}: {int(v) if isinstance(v, (int, float)) else v}" for k, v in state.state_variables.items())
            hud_id = canvas.create_text(
                state.environment.width / 2.0,
                24,
                text=hud_text,
                fill="#94A3B8",
                font=("Consolas", 14, "bold"),
            )

        # Track active pressed keys in scaffolding
        pressed_keys: Set[str] = set()

        def on_key_press(event):
            pressed_keys.add(event.keysym.lower())

        def on_key_release(event):
            pressed_keys.discard(event.keysym.lower())

        root.bind("<KeyPress>", on_key_press)
        root.bind("<KeyRelease>", on_key_release)

        is_running = [True]

        def on_close():
            is_running[0] = False
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_close)

        start_wall_time = time.time()

        def tick():
            nonlocal state
            if not is_running[0]:
                return

            # Map pressed keys to normalized channel signals
            inputs: Dict[str, float] = {}

            # Left player vertical channel (W = -1.0 up, S = +1.0 down)
            left_y = 0.0
            if "w" in pressed_keys:
                left_y -= 1.0
            if "s" in pressed_keys:
                left_y += 1.0
            inputs["player_left"] = left_y

            # Right player vertical channel (Up = -1.0 up, Down = +1.0 down)
            right_y = 0.0
            if "up" in pressed_keys:
                right_y -= 1.0
            if "down" in pressed_keys:
                right_y += 1.0
            inputs["player_right"] = right_y

            # Advance simulation step in MLUE Engine with input signals
            state = engine.step(state, dt, inputs=inputs)

            # Update presentation layer coords
            for shape in state.result.shapes:
                cid = item_ids.get(shape.id)
                if cid is not None:
                    x0, y0, x1, y1 = shape.bbox
                    canvas.coords(cid, x0, y0, x1, y1)

            # Update HUD text if present
            if hud_id is not None and state.state_variables:
                hud_text = "   ".join(f"{k.upper()}: {int(v) if isinstance(v, (int, float)) else v}" for k, v in state.state_variables.items())
                canvas.itemconfig(hud_id, text=hud_text)

            if duration is not None and (time.time() - start_wall_time) >= duration:
                on_close()
                return

            if is_running[0]:
                root.after(interval_ms, tick)

        root.after(interval_ms, tick)

        if block:
            root.mainloop()
        else:
            root.update()
