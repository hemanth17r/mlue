"""Unit tests for MLUE Subphase 1.2: Zero-Copy Binary Document & WAL Persistence.

Tests .mlueb binary compilation, CRC32 corruption validation, string dictionary deduplication,
streaming WAL recording, crash recovery for truncated logs, and deterministic replay fidelity.
"""

import unittest
import tempfile
import hashlib
from pathlib import Path
from runtime.loader import load_mlue, MLUEValidationError
from runtime.engine import MLUEEngine
from runtime.binary import encode_mlueb, decode_mlueb, save_mlueb, load_mlueb
from runtime.wal import (
    WALWriter,
    WALReader,
    WALReplayer,
    FRAME_TYPE_INPUT_SIGNAL,
    FRAME_TYPE_COLLISION_TRIGGER,
    FRAME_TYPE_STATE_MUTATION,
    FRAME_TYPE_KEYFRAME_CHECKPOINT,
)


class TestBinaryAndWAL(unittest.TestCase):
    """Test suite for .mlueb binary document containers and .wal Write-Ahead Logs."""

    def setUp(self):
        self.engine = MLUEEngine()
        self.examples_dir = Path(__file__).resolve().parent.parent / "examples"
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    # =========================================================================
    # 1. .MLUEB ROUNDTRIP & EXAMPLE CONVERSIONS
    # =========================================================================

    def test_roundtrip_all_example_scenes(self):
        """Verify all example scenes compile to .mlueb and decode back with 100% semantic parity."""
        example_files = list(self.examples_dir.glob("*.mlue"))
        self.assertGreater(len(example_files), 0, "No example .mlue files found.")

        for ex_file in example_files:
            with self.subTest(scene=ex_file.name):
                doc_orig = load_mlue(ex_file)
                binary_data = encode_mlueb(doc_orig)
                doc_decoded = decode_mlueb(binary_data)

                # 1. Environment parity
                self.assertEqual((doc_decoded.environment.width, doc_decoded.environment.height), (doc_orig.environment.width, doc_orig.environment.height))
                self.assertEqual(doc_decoded.environment.background.upper(), doc_orig.environment.background.upper())

                # 2. Entity count and entity parity
                self.assertEqual(len(doc_decoded.entities), len(doc_orig.entities))
                for e_orig, e_dec in zip(doc_orig.entities, doc_decoded.entities):
                    self.assertEqual(e_dec.id, e_orig.id)
                    self.assertEqual(e_dec.type, e_orig.type)
                    self.assertAlmostEqual(e_dec.position.x, e_orig.position.x, places=6)
                    self.assertAlmostEqual(e_dec.position.y, e_orig.position.y, places=6)
                    self.assertAlmostEqual(e_dec.velocity.vx, e_orig.velocity.vx, places=6)
                    self.assertAlmostEqual(e_dec.velocity.vy, e_orig.velocity.vy, places=6)
                    self.assertEqual(e_dec.active, e_orig.active)

                # 3. Rules and State variables parity
                self.assertEqual(len(doc_decoded.rules), len(doc_orig.rules))
                self.assertEqual(doc_decoded.state_variables, doc_orig.state_variables)

    def test_binary_file_size_reduction(self):
        """Verify .mlueb binary size is smaller than the original human-readable JSON .mlue."""
        inv_path = self.examples_dir / "inventory_system.mlue"
        doc = load_mlue(inv_path)
        bin_data = encode_mlueb(doc)
        orig_size = inv_path.stat().st_size
        self.assertLess(len(bin_data), orig_size)

    # =========================================================================
    # 2. INTEGRITY CHECKS & CORRUPTION DETECTION
    # =========================================================================

    def test_binary_corrupt_crc_rejection(self):
        """Verify decode_mlueb rejects corrupted payloads with CRC32 mismatch."""
        doc = load_mlue(self.examples_dir / "pong.mlue")
        data = bytearray(encode_mlueb(doc))

        # Corrupt 1 byte in the middle of payload
        data[70] ^= 0xFF

        with self.assertRaises(MLUEValidationError) as ctx:
            decode_mlueb(bytes(data))
        self.assertIn("CRC32 mismatch", str(ctx.exception))

    def test_binary_corrupt_magic_rejection(self):
        """Verify decode_mlueb rejects files with invalid magic identifier."""
        import struct, zlib
        doc = load_mlue(self.examples_dir / "pong.mlue")
        data = bytearray(encode_mlueb(doc))
        data[0:4] = b"BADM"
        # Recompute CRC32 so that CRC check passes and magic validation fails specifically
        payload_len = len(data) - 4
        crc = zlib.crc32(data[:payload_len])
        data[payload_len:] = struct.pack("<I", crc)

        with self.assertRaises(MLUEValidationError) as ctx:
            decode_mlueb(bytes(data))
        self.assertIn("Invalid .mlueb magic header", str(ctx.exception))

    def test_binary_load_mlue_transparent_routing(self):
        """Verify load_mlue automatically handles both .mlue and .mlueb files."""
        doc_orig = load_mlue(self.examples_dir / "breakout.mlue")
        bin_path = self.temp_path / "breakout.mlueb"
        save_mlueb(doc_orig, bin_path)

        doc_loaded = load_mlue(bin_path)
        self.assertEqual(len(doc_loaded.entities), len(doc_orig.entities))
        self.assertEqual(len(doc_loaded.rules), len(doc_orig.rules))

    # =========================================================================
    # 3. WAL STREAMING & RECORDING
    # =========================================================================

    def test_wal_streaming_write_and_read(self):
        """Verify WALWriter records binary frames and WALReader parses all frame fields."""
        wal_file = self.temp_path / "session.wal"
        with WALWriter(wal_file, scene_hash=0x12345678) as writer:
            writer.log_input(0, 0.0, {"player_left": 1.0})
            writer.log_collision(1, 0.0167, "ball", "paddle_left")
            writer.log_state_mutation(2, 0.0333, "increment", "score_left", amount=1)

        scene_hash, frames, warning = WALReader.read_frames(wal_file)
        self.assertEqual(scene_hash, 0x12345678)
        self.assertIsNone(warning)
        self.assertEqual(len(frames), 3)

        self.assertEqual(frames[0].event_type, FRAME_TYPE_INPUT_SIGNAL)
        self.assertEqual(frames[0].payload["inputs"]["player_left"], 1.0)

        self.assertEqual(frames[1].event_type, FRAME_TYPE_COLLISION_TRIGGER)
        self.assertEqual(frames[1].payload["entities"], ["ball", "paddle_left"])

        self.assertEqual(frames[2].event_type, FRAME_TYPE_STATE_MUTATION)
        self.assertEqual(frames[2].payload["target"], "score_left")

    # =========================================================================
    # 4. WAL CRASH RECOVERY
    # =========================================================================

    def test_wal_crash_recovery_truncated_tail(self):
        """Verify WALReader cleanly recovers all complete frames when log is truncated abruptly mid-frame."""
        wal_file = self.temp_path / "crash_test.wal"

        with WALWriter(wal_file) as writer:
            for tick in range(15):
                writer.log_input(tick, tick * 0.0167, {"axis_x": 0.5})

        full_data = wal_file.read_bytes()
        # Truncate 10 bytes from end (simulating power failure / crash during write)
        corrupted_data = full_data[:-10]
        corrupted_file = self.temp_path / "corrupted.wal"
        corrupted_file.write_bytes(corrupted_data)

        _, frames, warning = WALReader.read_frames(corrupted_file)
        self.assertIsNotNone(warning)
        self.assertIn("Crash recovery", warning)
        # Should have recovered 14 full valid frames
        self.assertEqual(len(frames), 14)

    # =========================================================================
    # 5. DETERMINISTIC REPLAY & PARITY
    # =========================================================================

    def test_wal_replay_fidelity(self):
        """Verify replaying logged input signals from WAL produces identical simulation states."""
        doc = load_mlue(self.examples_dir / "pong.mlue")
        wal_file = self.temp_path / "pong_run.wal"

        # 1. Live run for 300 steps with simulated inputs
        sim_state = self.engine.init_simulation(doc)
        dt = 1.0 / 60.0

        with WALWriter(wal_file) as writer:
            for tick in range(300):
                inputs = {"player_left": 1.0 if (tick % 60) < 30 else -1.0}
                writer.log_input(tick, sim_state.time, inputs)
                sim_state = self.engine.step(sim_state, dt, inputs)

        # 2. Replay run via WALReplayer
        _, frames, _ = WALReader.read_frames(wal_file)
        replayer = WALReplayer(self.engine)
        replayed_state = replayer.replay(doc, frames, dt=dt, total_ticks=300)

        # 3. Assert bit-exact matching across all entities and state variables
        self.assertEqual(len(replayed_state.entities), len(sim_state.entities))
        for e_live, e_rep in zip(sim_state.entities, replayed_state.entities):
            self.assertEqual(e_live.position.x, e_rep.position.x)
            self.assertEqual(e_live.position.y, e_rep.position.y)
            self.assertEqual(e_live.velocity.vx, e_rep.velocity.vx)
            self.assertEqual(e_live.velocity.vy, e_rep.velocity.vy)

        self.assertEqual(replayed_state.state_variables, sim_state.state_variables)

    def test_50k_ticks_binary_determinism(self):
        """Verify 50,000 continuous simulation steps initialized from .mlueb produce bit-exact SHA-256 digest."""
        inv_path = self.examples_dir / "inventory_system.mlue"
        doc = load_mlue(inv_path)
        bin_path = self.temp_path / "inventory.mlueb"
        save_mlueb(doc, bin_path)

        def run_sim():
            loaded_doc = load_mlueb(bin_path)
            state = self.engine.init_simulation(loaded_doc)
            dt = 1.0 / 60.0
            for _ in range(50000):
                state = self.engine.step(state, dt)

            hasher = hashlib.sha256()
            for e in state.entities:
                hasher.update(f"{e.id}:{e.position.x:.12f}:{e.position.y:.12f}:{e.velocity.vx:.12f}:{e.velocity.vy:.12f}:{e.active}".encode("utf-8"))
            return hasher.hexdigest()

        hash1 = run_sim()
        hash2 = run_sim()
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)


if __name__ == "__main__":
    unittest.main()
