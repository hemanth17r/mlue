"""MLUE Binary Document (.mlueb) Encoding & Decoding Module.

Provides zero-copy, C-aligned binary serialization and deserialization for MLUE documents.
Adheres strictly to Tier L1 Substrate Decoupling (Standard Library only: struct, zlib, json).
"""

import struct
import zlib
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Union
from runtime.model import (
    MLUEDocument,
    Environment,
    Entity,
    Position,
    Velocity,
    CircleSize,
    BoxSize,
    Rule,
    Condition,
    Action,
)
from runtime.loader import MLUEValidationError, validate_and_parse


# Magic identifiers & format constants
MLUEB_MAGIC = b"MLUE"
MLUEB_VERSION_MAJOR = 1
MLUEB_VERSION_MINOR = 2
HEADER_SIZE = 64
ENTITY_RECORD_SIZE = 64


def _hex_to_rgba32(hex_color: str) -> int:
    """Converts a hex color string (#RGB, #RRGGBB, #RRGGBBAA) to a packed uint32 RGBA integer."""
    if not hex_color:
        return 0xFFFFFFFF
    s = hex_color.lstrip("#")
    if len(s) == 3:
        r = int(s[0] * 2, 16)
        g = int(s[1] * 2, 16)
        b = int(s[2] * 2, 16)
        a = 255
    elif len(s) == 6:
        r = int(s[0:2], 16)
        g = int(s[2:4], 16)
        b = int(s[4:6], 16)
        a = 255
    elif len(s) == 8:
        r = int(s[0:2], 16)
        g = int(s[2:4], 16)
        b = int(s[4:6], 16)
        a = int(s[6:8], 16)
    else:
        return 0xFFFFFFFF
    return (r << 24) | (g << 16) | (b << 8) | a


def _rgba32_to_hex(rgba: int) -> str:
    """Converts a packed uint32 RGBA integer to a hex color string (#RRGGBB or #RRGGBBAA)."""
    r = (rgba >> 24) & 0xFF
    g = (rgba >> 16) & 0xFF
    b = (rgba >> 8) & 0xFF
    a = rgba & 0xFF
    if a == 255:
        return f"#{r:02X}{g:02X}{b:02X}"
    return f"#{r:02X}{g:02X}{b:02X}{a:02X}"


class StringTableBuilder:
    """Helper to deduplicate and build an 8-byte aligned string dictionary table."""

    def __init__(self):
        self.strings: List[str] = []
        self._index_map: Dict[str, int] = {}
        self._offsets: List[int] = []
        self._blob: bytearray = bytearray()

    def get_or_add(self, s: Optional[str]) -> int:
        if s is None:
            s = ""
        if s in self._index_map:
            return self._index_map[s]
        idx = len(self.strings)
        offset = len(self._blob)
        encoded = s.encode("utf-8")
        # Store string as: uint16 len + utf8 bytes
        self._blob.extend(struct.pack("<H", len(encoded)) + encoded)
        self.strings.append(s)
        self._index_map[s] = idx
        self._offsets.append(offset)
        return idx

    def build(self) -> bytes:
        # Header: uint32 count + array of uint32 offsets + raw string blob
        count = len(self.strings)
        header = struct.pack("<I", count)
        offset_table = struct.pack(f"<{count}I", *self._offsets) if count > 0 else b""
        combined = header + offset_table + bytes(self._blob)
        # Pad to 8-byte alignment
        pad_len = (8 - (len(combined) % 8)) % 8
        return combined + (b"\x00" * pad_len)


class StringTableReader:
    """Helper to read strings from string table binary block."""

    def __init__(self, data: bytes):
        if len(data) < 4:
            self.strings = [""]
            return
        count = struct.unpack_from("<I", data, 0)[0]
        offset_start = 4
        offsets = struct.unpack_from(f"<{count}I", data, offset_start) if count > 0 else ()
        blob_start = offset_start + (count * 4)
        self.strings = []
        for off in offsets:
            str_pos = blob_start + off
            if str_pos + 2 <= len(data):
                str_len = struct.unpack_from("<H", data, str_pos)[0]
                val = data[str_pos + 2 : str_pos + 2 + str_len].decode("utf-8", errors="replace")
                self.strings.append(val)
            else:
                self.strings.append("")

    def get(self, idx: int) -> str:
        if 0 <= idx < len(self.strings):
            return self.strings[idx]
        return ""


def encode_mlueb(doc: MLUEDocument) -> bytes:
    """Encodes an MLUEDocument dataclass into a zero-copy aligned .mlueb binary container."""
    str_builder = StringTableBuilder()
    str_builder.get_or_add("")  # Empty string at index 0

    # 1. Encode Entity Table
    entity_records = bytearray()
    for e in doc.entities:
        id_idx = str_builder.get_or_add(e.id)
        color_rgba = _hex_to_rgba32(e.properties.get("color", "#FFFFFF"))
        etype = 1 if e.type == "circle" else 2
        flags = 0
        if e.properties.get("solid", False):
            flags |= 0x01
        if e.active:
            flags |= 0x02
        if "control" in e.properties:
            flags |= 0x04

        ctrl_axis = 0
        ctrl_channel_idx = 0
        if "control" in e.properties:
            ctrl = e.properties["control"]
            axis_str = ctrl.get("axis", "")
            if axis_str == "x":
                ctrl_axis = 1
            elif axis_str == "y":
                ctrl_axis = 2
            ctrl_channel_idx = str_builder.get_or_add(ctrl.get("channel", ""))

        pos_x = float(e.position.x)
        pos_y = float(e.position.y)
        vel_vx = float(e.velocity.vx)
        vel_vy = float(e.velocity.vy)

        if e.type == "circle" and isinstance(e.size, CircleSize):
            p1 = float(e.size.radius)
            p2 = 0.0
        elif e.type == "box" and isinstance(e.size, BoxSize):
            p1 = float(e.size.width)
            p2 = float(e.size.height)
        else:
            p1, p2 = 0.0, 0.0

        rec = struct.pack(
            "<IIBBBBIdddddd",
            id_idx,
            color_rgba,
            etype,
            flags,
            ctrl_axis,
            0,  # reserved_1
            ctrl_channel_idx,
            pos_x,
            pos_y,
            vel_vx,
            vel_vy,
            p1,
            p2,
        )
        entity_records.extend(rec)

    # 2. Encode Rules Table as JSON payload or structured blocks
    # For rules, we serialize full declarative structure into a UTF-8 string entry in string table or sub-block
    rules_dict = [
        {
            "trigger": r.trigger,
            "event": r.event,
            "entities": r.entities,
            "condition": {
                "entity": r.condition.entity,
                "property": r.condition.property,
                "state_variable": r.condition.state_variable,
                "state_path": r.condition.state_path,
                "op": r.condition.op,
                "value": r.condition.value,
            }
            if r.condition
            else None,
            "actions": [
                {
                    "type": a.type,
                    "target": a.target,
                    "property": a.property,
                    "value": a.value,
                    "amount": a.amount,
                    "index": a.index,
                    "key": a.key,
                }
                for a in r.actions
            ],
        }
        for r in doc.rules
    ]
    rules_json_bytes = json.dumps(rules_dict, separators=(",", ":")).encode("utf-8")
    rules_block = struct.pack("<I", len(doc.rules)) + struct.pack("<I", len(rules_json_bytes)) + rules_json_bytes
    pad_len = (8 - (len(rules_block) % 8)) % 8
    rules_block += b"\x00" * pad_len

    # 3. Encode State Tree Block
    state_json_bytes = json.dumps(doc.state_variables, separators=(",", ":")).encode("utf-8")
    state_block = struct.pack("<I", len(state_json_bytes)) + state_json_bytes
    pad_len = (8 - (len(state_block) % 8)) % 8
    state_block += b"\x00" * pad_len

    # 4. Build String Table
    string_table_block = str_builder.build()

    # 5. Compute Table Offsets (aligned to 8 bytes)
    offset_entities = HEADER_SIZE
    offset_rules = offset_entities + len(entity_records)
    offset_strings = offset_rules + len(rules_block)
    offset_state = offset_strings + len(string_table_block)

    env_width = doc.environment.width
    env_height = doc.environment.height
    bg_rgba = _hex_to_rgba32(doc.environment.background)
    num_entities = len(doc.entities)
    num_rules = len(doc.rules)

    # 6. Pack 64-byte Header
    header = struct.pack(
        "<4sBBHIIIIIIQQQQ",
        MLUEB_MAGIC,
        MLUEB_VERSION_MAJOR,
        MLUEB_VERSION_MINOR,
        HEADER_SIZE,
        env_width,
        env_height,
        bg_rgba,
        num_entities,
        num_rules,
        0,  # reserved_0
        offset_entities,
        offset_rules,
        offset_strings,
        offset_state,
    )

    payload = header + bytes(entity_records) + rules_block + string_table_block + state_block
    crc = zlib.crc32(payload)
    # Append CRC32 at the end (4 bytes)
    return payload + struct.pack("<I", crc)


def decode_mlueb(data: bytes) -> MLUEDocument:
    """Decodes a .mlueb binary blob into an MLUEDocument dataclass with CRC32 verification."""
    if len(data) < HEADER_SIZE + 4:
        raise MLUEValidationError(f"Invalid .mlueb file: length ({len(data)} B) is smaller than minimum header size.")

    # 1. Verify CRC32
    payload_len = len(data) - 4
    stored_crc = struct.unpack_from("<I", data, payload_len)[0]
    computed_crc = zlib.crc32(data[:payload_len])
    if stored_crc != computed_crc:
        raise MLUEValidationError(
            f"Corrupted .mlueb binary document: CRC32 mismatch (computed 0x{computed_crc:08X}, expected 0x{stored_crc:08X})."
        )

    # 2. Unpack Header
    (
        magic,
        ver_maj,
        ver_min,
        hdr_size,
        env_w,
        env_h,
        bg_rgba,
        num_entities,
        num_rules,
        _,
        off_entities,
        off_rules,
        off_strings,
        off_state,
    ) = struct.unpack_from("<4sBBHIIIIIIQQQQ", data, 0)

    if magic != MLUEB_MAGIC:
        raise MLUEValidationError(f"Invalid .mlueb magic header: expected {MLUEB_MAGIC!r}, got {magic!r}.")

    if ver_maj != MLUEB_VERSION_MAJOR:
        raise MLUEValidationError(
            f"Unsupported .mlueb major version {ver_maj}.{ver_min} (engine supports {MLUEB_VERSION_MAJOR}.x)."
        )

    # 3. Read String Table
    str_data = data[off_strings:off_state]
    str_reader = StringTableReader(str_data)

    # 4. Read Environment
    bg_hex = _rgba32_to_hex(bg_rgba)
    environment = Environment(width=env_w, height=env_h, background=bg_hex)

    # 5. Read Entities
    entities: List[Entity] = []
    for i in range(num_entities):
        rec_offset = off_entities + (i * ENTITY_RECORD_SIZE)
        (
            id_idx,
            color_rgba,
            etype,
            flags,
            ctrl_axis,
            _,
            ctrl_channel_idx,
            pos_x,
            pos_y,
            vel_vx,
            vel_vy,
            p1,
            p2,
        ) = struct.unpack_from("<IIBBBBIdddddd", data, rec_offset)

        eid = str_reader.get(id_idx)
        is_solid = bool(flags & 0x01)
        is_active = bool(flags & 0x02)
        is_controlled = bool(flags & 0x04)

        props: Dict[str, Any] = {
            "color": _rgba32_to_hex(color_rgba),
            "solid": is_solid,
        }

        if is_controlled:
            axis_str = "x" if ctrl_axis == 1 else "y"
            channel_name = str_reader.get(ctrl_channel_idx)
            props["control"] = {
                "channel": channel_name,
                "axis": axis_str,
                "speed": 1.0,
            }

        if etype == 1:
            type_str = "circle"
            size_obj: Union[CircleSize, BoxSize] = CircleSize(radius=p1)
        else:
            type_str = "box"
            size_obj = BoxSize(width=p1, height=p2)

        entity = Entity(
            id=eid,
            type=type_str,
            position=Position(x=pos_x, y=pos_y),
            size=size_obj,
            velocity=Velocity(vx=vel_vx, vy=vel_vy),
            properties=props,
            active=is_active,
        )
        entities.append(entity)

    # 6. Read Rules Block
    rules: List[Rule] = []
    if off_rules < off_strings:
        r_count, r_json_len = struct.unpack_from("<II", data, off_rules)
        r_json_bytes = data[off_rules + 8 : off_rules + 8 + r_json_len]
        if r_json_bytes:
            raw_rules = json.loads(r_json_bytes.decode("utf-8"))
            for r_raw in raw_rules:
                cond = None
                if r_raw.get("condition"):
                    c = r_raw["condition"]
                    cond = Condition(
                        entity=c.get("entity"),
                        property=c.get("property"),
                        state_variable=c.get("state_variable"),
                        state_path=c.get("state_path"),
                        op=c.get("op", "=="),
                        value=c.get("value"),
                    )
                actions = [
                    Action(
                        type=a["type"],
                        target=a.get("target"),
                        property=a.get("property"),
                        value=a.get("value"),
                        amount=a.get("amount"),
                        index=a.get("index"),
                        key=a.get("key"),
                    )
                    for a in r_raw.get("actions", [])
                ]
                rules.append(
                    Rule(
                        trigger=r_raw.get("trigger", ""),
                        event=r_raw.get("event"),
                        entities=r_raw.get("entities"),
                        condition=cond,
                        actions=actions,
                    )
                )

    # 7. Read State Tree Block
    state_variables: Dict[str, Any] = {}
    if off_state < len(data) - 4:
        st_len = struct.unpack_from("<I", data, off_state)[0]
        st_json_bytes = data[off_state + 4 : off_state + 4 + st_len]
        if st_json_bytes:
            state_variables = json.loads(st_json_bytes.decode("utf-8"))

    return MLUEDocument(
        version=f"{ver_maj}.{ver_min}",
        environment=environment,
        state_variables=state_variables,
        entities=entities,
        rules=rules,
    )


def save_mlueb(doc: MLUEDocument, filepath: Union[str, Path]) -> int:
    """Encodes and writes an MLUEDocument to a .mlueb binary file. Returns number of bytes written."""
    data = encode_mlueb(doc)
    p = Path(filepath)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "wb") as f:
        f.write(data)
    return len(data)


def load_mlueb(filepath: Union[str, Path]) -> MLUEDocument:
    """Loads and decodes an MLUEDocument from a .mlueb binary file."""
    p = Path(filepath)
    if not p.exists():
        raise FileNotFoundError(f"Binary MLUE document not found: {p}")
    with open(p, "rb") as f:
        data = f.read()
    return decode_mlueb(data)
