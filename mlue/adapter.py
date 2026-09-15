"""MLUE Phase 0.6 Bootstrap Display Adapter

Temporary scaffolding adapter that maps evaluated MLUE computational state,
simulations, dynamic entity destructions, and multi-variable HUDs to an
observable desktop window via Tkinter.
"""

import math
import sys
import time
from typing import Optional, Dict, Set, List
from .model import EvaluationResult, MLUEDocument, SimulationState, ComputedShape, ComputedConstraint
from .engine import MLUEEngine


class TkinterAdapter:
    """Disposable bootstrap scaffolding for rendering MLUE state and simulations to OS display."""

    def __init__(self, title: str = "MLUE Runtime — Presentation Adapter"):
        self.title = title

    def _draw_shape(self, canvas, shape: ComputedShape):
        """Draws a single ComputedShape to Tkinter canvas."""
        x0, y0, x1, y1 = shape.bbox
        if shape.type == "circle":
            return canvas.create_oval(x0, y0, x1, y1, fill=shape.color, outline="")
        elif shape.type == "box":
            outline_color = "#334155" if shape.color in ("#1E293B", "#161F30", "#0F172A") else ""
            if shape.theta != 0.0:
                cx, cy = shape.center
                w = max(1.0, x1 - x0)
                h = max(1.0, y1 - y0)
                hw, hh = w / 2.0, h / 2.0
                cos_t = math.cos(shape.theta)
                sin_t = math.sin(shape.theta)
                pts = [
                    (cx - hw * cos_t + hh * sin_t, cy - hw * sin_t - hh * cos_t),
                    (cx + hw * cos_t + hh * sin_t, cy + hw * sin_t - hh * cos_t),
                    (cx + hw * cos_t - hh * sin_t, cy + hw * sin_t + hh * cos_t),
                    (cx - hw * cos_t - hh * sin_t, cy - hw * sin_t + hh * cos_t),
                ]
                flat_pts = [c for pt in pts for c in pt]
                return canvas.create_polygon(*flat_pts, fill=shape.color, outline=outline_color)
            return canvas.create_rectangle(
                x0, y0, x1, y1,
                fill=shape.color,
                outline=outline_color,
                width=1 if outline_color else 0
            )
        elif shape.type == "segment":
            cy = (y0 + y1) / 2.0
            return canvas.create_line(x0, cy, x1, cy, fill=shape.color, width=2)
        elif shape.type == "capsule":
            w = max(1.0, x1 - x0)
            h = max(1.0, y1 - y0)
            if w >= h:
                r = h / 2.0
                canvas.create_oval(x0, y0, x0 + 2.0 * r, y1, fill=shape.color, outline="")
                canvas.create_oval(x1 - 2.0 * r, y0, x1, y1, fill=shape.color, outline="")
                rect_id = canvas.create_rectangle(x0 + r, y0, x1 - r, y1, fill=shape.color, outline="")
                if shape.text:
                    canvas.create_text(
                        shape.center[0], shape.center[1],
                        text=shape.text,
                        fill="#FFFFFF",
                        anchor="center",
                        font=("Segoe UI", max(8, int(h * 0.48)), "bold")
                    )
                return rect_id
            else:
                r = w / 2.0
                canvas.create_oval(x0, y0, x1, y0 + 2.0 * r, fill=shape.color, outline="")
                canvas.create_oval(x0, y1 - 2.0 * r, x1, y1, fill=shape.color, outline="")
                return canvas.create_rectangle(x0, y0 + r, x1, y1 - r, fill=shape.color, outline="")
        elif shape.type == "text":
            font_size = max(9, int((y1 - y0) * 0.85))
            is_header = any(k in (shape.text or "") for k in ("TELEMETRY", "CLUSTER", "TITLE", "DASHBOARD"))
            return canvas.create_text(
                x0, shape.center[1],
                text=shape.text or "",
                fill=shape.color,
                anchor="w",
                font=("Segoe UI", font_size, "bold" if is_header else "normal")
            )
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

        for c in result.constraints:
            canvas.create_line(c.p1[0], c.p1[1], c.p2[0], c.p2[1], fill=c.color, width=2, dash=(4, 2) if c.type == "spring" else ())
            canvas.create_oval(c.p1[0]-3, c.p1[1]-3, c.p1[0]+3, c.p1[1]+3, fill="#38BDF8")
            canvas.create_oval(c.p2[0]-3, c.p2[1]-3, c.p2[0]+3, c.p2[1]+3, fill="#38BDF8")

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

        # HUD Text item for state variables (e.g. scores, lives, game state)
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

            # Bottom horizontal channel for Breakout paddle (A/Left = -1.0, D/Right = +1.0)
            bottom_x = 0.0
            if "a" in pressed_keys or "left" in pressed_keys:
                bottom_x -= 1.0
            if "d" in pressed_keys or "right" in pressed_keys:
                bottom_x += 1.0
            inputs["player_bottom"] = bottom_x

            # Advance simulation step in MLUE Engine with input signals
            state = engine.step(state, dt, inputs=inputs)

            # Map active shapes
            active_shapes = {shape.id: shape for shape in state.result.shapes}

            # Update presentation layer coords or hide destroyed shapes
            for ent_id, cid in item_ids.items():
                if ent_id in active_shapes:
                    shape = active_shapes[ent_id]
                    x0, y0, x1, y1 = shape.bbox
                    canvas.coords(cid, x0, y0, x1, y1)
                    canvas.itemconfig(cid, fill=shape.color, state="normal")
                else:
                    canvas.itemconfig(cid, state="hidden")

            # Update HUD text if present
            if hud_id is not None and state.state_variables:
                hud_text = "   ".join(f"{k.upper()}: {int(v) if isinstance(v, (int, float)) else v}" for k, v in state.state_variables.items())
                canvas.itemconfig(hud_id, text=hud_text)

            if duration is not None and (time.time() - start_wall_time) >= duration:
                on_close()
                return

            if is_running[0]:
                root.after(interval_ms, tick)

        # Initial constraints creation
        for c in state.result.constraints:
            canvas.create_line(c.p1[0], c.p1[1], c.p2[0], c.p2[1], fill=c.color, width=2, dash=(4, 2) if c.type == "spring" else ())
            canvas.create_oval(c.p1[0]-3, c.p1[1]-3, c.p1[0]+3, c.p1[0]+3, fill="#38BDF8")
            canvas.create_oval(c.p2[0]-3, c.p2[1]-3, c.p2[0]+3, c.p2[1]+3, fill="#38BDF8")

        root.after(interval_ms, tick)

        if block:
            root.mainloop()
        else:
            root.update()


# Alias for presentation and multi-tier adapter architecture
PresentationAdapter = TkinterAdapter


if __name__ == "__main__":
    if len(sys.argv) > 1:
        from .loader import load_mlue
        from .engine import MLUEEngine
        mlue_path = sys.argv[1]
        doc = load_mlue(mlue_path)
        adapter = TkinterAdapter(title=f"MLUE Presentation — {mlue_path}")
        print(f"Loaded {mlue_path} ({len(doc.entities)} entities, {len(doc.constraints)} constraints). Starting presentation...")
        adapter.present(MLUEEngine().evaluate(doc), block=True)
    else:
        print("Usage: python -m runtime.adapter <path/to/file.mlue>")
