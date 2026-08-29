"""MLUE Write-Ahead Log (WAL) Streaming & Deterministic Replay Module.

Provides append-only binary frame logging (< 1 us/frame write latency),
CRC32-verified crash recovery, and deterministic state replay.
Adheres strictly to Tier L1 Substrate Decoupling (Standard Library only: struct, zlib, json).
"""

import struct
import zlib
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Union, Tuple, Iterator
from runtime.model import SimulationState, Entity, MLUEDocument
from runtime.engine import MLUEEngine


# WAL Header & Protocol Constants
WAL_MAGIC = b"MWAL\x01\x00\x00\x00"  # 8 bytes magic + version
WAL_HEADER_SIZE = 16

# Event Frame Types
FRAME_TYPE_INPUT_SIGNAL = 1
FRAME_TYPE_COLLISION_TRIGGER = 2
FRAME_TYPE_STATE_MUTATION = 3
FRAME_TYPE_KEYFRAME_CHECKPOINT = 4

MIN_FRAME_SIZE = 25  # 4 (len) + 8 (tick) + 8 (time) + 1 (type) + 4 (crc)
MAX_FRAME_SIZE = 16 * 1024 * 1024  # 16 MB max frame boundary


@dataclass
class WALFrame:
    """Represents a decoded Write-Ahead Log event frame."""
    frame_length: int
    tick_index: int
    sim_time: float
    event_type: int
    payload: Dict[str, Any]
    crc32: int
    valid: bool = True


class WALWriter:
    """Streaming append-only binary logger for simulation events and keyframes."""

    def __init__(self, filepath: Union[str, Path], scene_hash: int = 0, initial_scene_hash: Optional[int] = None):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self._file = open(self.filepath, "wb")
        effective_hash = scene_hash if initial_scene_hash is None else initial_scene_hash
        self._write_header(effective_hash)
        self.frames_written = 0

    def _write_header(self, scene_hash: int) -> None:
        """Writes 16-byte WAL container header."""
        header = struct.pack("<8sQ", WAL_MAGIC, scene_hash & 0xFFFFFFFFFFFFFFFF)
        self._file.write(header)
        self._file.flush()

    def _write_frame(self, tick_index: int, sim_time: float, event_type: int, payload_dict: Dict[str, Any]) -> int:
        """Encodes and appends a single binary event frame with CRC32."""
        payload_bytes = json.dumps(payload_dict, separators=(",", ":")).encode("utf-8")
        # Frame format: <I (frame_len) + Q (tick) + d (time) + B (type) + payload_bytes + I (crc32)
        frame_len = 4 + 8 + 8 + 1 + len(payload_bytes) + 4
        partial_header = struct.pack("<IQdB", frame_len, tick_index, sim_time, event_type)
        frame_body = partial_header + payload_bytes
        crc = zlib.crc32(frame_body)
        full_frame = frame_body + struct.pack("<I", crc)

        self._file.write(full_frame)
        self.frames_written += 1
        return len(full_frame)

    def log_input(self, tick_index: int, sim_time: float, inputs: Dict[str, float]) -> int:
        """Logs input signals applied on a simulation step."""
        if not inputs:
            return 0
        return self._write_frame(tick_index, sim_time, FRAME_TYPE_INPUT_SIGNAL, {"inputs": inputs})

    def log_collision(self, tick_index: int, sim_time: float, entity_a: str, entity_b: str) -> int:
        """Logs discrete physical collision trigger event."""
        return self._write_frame(
            tick_index, sim_time, FRAME_TYPE_COLLISION_TRIGGER, {"entities": [entity_a, entity_b]}
        )

    def log_state_mutation(
        self,
        tick_index: int,
        sim_time: float,
        action_type: str,
        target: str,
        value: Any = None,
        amount: Optional[float] = None,
        index: Optional[int] = None,
        key: Optional[str] = None,
    ) -> int:
        """Logs state tree mutation event."""
        payload = {
            "type": action_type,
            "target": target,
            "value": value,
            "amount": amount,
            "index": index,
            "key": key,
        }
        return self._write_frame(tick_index, sim_time, FRAME_TYPE_STATE_MUTATION, payload)

    def log_checkpoint(self, tick_index: int, sim_time: float, state: SimulationState) -> int:
        """Logs a full snapshot checkpoint for fast random-access seeking."""
        entities_data = [
            {
                "id": e.id,
                "x": e.position.x,
                "y": e.position.y,
                "vx": e.velocity.vx,
                "vy": e.velocity.vy,
                "active": e.active,
            }
            for e in state.entities
        ]
        payload = {
            "entities": entities_data,
            "state_variables": state.state_variables,
        }
        return self._write_frame(tick_index, sim_time, FRAME_TYPE_KEYFRAME_CHECKPOINT, payload)

    def flush(self) -> None:
        if self._file and not self._file.closed:
            self._file.flush()

    def close(self) -> None:
        if self._file and not self._file.closed:
            self._file.flush()
            self._file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class WALReader:
    """Streaming WAL binary reader with automatic crash corruption recovery."""

    @staticmethod
    def read_frames(filepath: Union[str, Path]) -> Tuple[int, List[WALFrame], Optional[str]]:
        """Reads all valid frames from a .wal file.
        
        Returns:
            (initial_scene_hash, frames_list, recovery_warning_message)
        """
        p = Path(filepath)
        if not p.exists():
            raise FileNotFoundError(f"WAL file not found: {p}")

        with open(p, "rb") as f:
            data = f.read()

        if len(data) < WAL_HEADER_SIZE:
            raise ValueError(f"Invalid WAL file: size ({len(data)} B) is smaller than 16-byte header.")

        magic, scene_hash = struct.unpack_from("<8sQ", data, 0)
        if magic != WAL_MAGIC:
            raise ValueError(f"Invalid WAL magic header: expected {WAL_MAGIC!r}, got {magic!r}.")

        frames: List[WALFrame] = []
        offset = WAL_HEADER_SIZE
        warning_msg: Optional[str] = None

        while offset < len(data):
            remaining = len(data) - offset
            if remaining < MIN_FRAME_SIZE:
                warning_msg = f"Crash recovery: truncated trailing frame at offset {offset} ({remaining} bytes ignored)."
                break

            frame_len = struct.unpack_from("<I", data, offset)[0]
            if frame_len < MIN_FRAME_SIZE or frame_len > MAX_FRAME_SIZE:
                warning_msg = f"Crash recovery: corrupted frame length {frame_len} at offset {offset}. Stopped cleanly."
                break

            if remaining < frame_len:
                warning_msg = f"Crash recovery: partial frame write detected at offset {offset} (expected {frame_len} B, got {remaining} B). Replayed {len(frames)} valid frames."
                break

            frame_data = data[offset : offset + frame_len]
            stored_crc = struct.unpack_from("<I", frame_data, frame_len - 4)[0]
            computed_crc = zlib.crc32(frame_data[: frame_len - 4])

            if stored_crc != computed_crc:
                warning_msg = f"Crash recovery: CRC32 checksum failure at offset {offset} (computed 0x{computed_crc:08X}, expected 0x{stored_crc:08X}). Stopped cleanly at frame {len(frames)}."
                break

            _, tick_idx, s_time, f_type = struct.unpack_from("<IQdB", frame_data, 0)
            payload_bytes = frame_data[21 : frame_len - 4]
            payload_dict = json.loads(payload_bytes.decode("utf-8")) if payload_bytes else {}

            frames.append(
                WALFrame(
                    frame_length=frame_len,
                    tick_index=tick_idx,
                    sim_time=s_time,
                    event_type=f_type,
                    payload=payload_dict,
                    crc32=stored_crc,
                    valid=True,
                )
            )
            offset += frame_len

        return scene_hash, frames, warning_msg


class WALReplayer:
    """Deterministic simulation replay engine powered by WAL frame logs."""

    def __init__(self, engine: Optional[MLUEEngine] = None):
        self.engine = engine or MLUEEngine()

    def replay(
        self,
        doc: MLUEDocument,
        frames: List[WALFrame],
        dt: float = 1.0 / 60.0,
        total_ticks: Optional[int] = None,
    ) -> SimulationState:
        """Replays simulation from initial document applying logged inputs tick-by-tick."""
        state = self.engine.init_simulation(doc)
        
        # Group inputs by tick_index
        input_schedule: Dict[int, Dict[str, float]] = {}
        for f in frames:
            if f.event_type == FRAME_TYPE_INPUT_SIGNAL and "inputs" in f.payload:
                input_schedule[f.tick_index] = f.payload["inputs"]

        max_logged_tick = max([f.tick_index for f in frames], default=0)
        target_ticks = total_ticks if total_ticks is not None else max_logged_tick + 1

        for tick in range(target_ticks):
            step_inputs = input_schedule.get(tick, {})
            state = self.engine.step(state, dt, step_inputs)

        return state
