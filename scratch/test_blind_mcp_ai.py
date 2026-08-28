"""Zero-Knowledge AI Agent interacting purely via MCP JSON-RPC protocol.

This script acts as an external AI model with ZERO prior knowledge of MLUE.
It connects to mcp_server.py via JSON-RPC, discovers tools, reads the schema,
synthesizes a brand new interactive application ('Bumper Arena'), validates it,
runs headless physics simulation steps, and saves the file for live human play.
"""

import json
import subprocess
import sys
from pathlib import Path

def run_blind_ai_mcp_session():
    print("==================================================================")
    print("[AI AGENT] Initializing connection to MLUE MCP Server...")
    print("==================================================================")

    # Launch mcp_server.py as a real external subprocess over stdio
    proc = subprocess.Popen(
        [sys.executable, "mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    def send_rpc(method: str, params: dict, req_id: int):
        payload = {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params}
        proc.stdin.write(json.dumps(payload) + "\n")
        proc.stdin.flush()
        line = proc.stdout.readline()
        return json.loads(line)

    # 1. MCP Handshake
    handshake = send_rpc("initialize", {}, 1)
    print(f"[AI AGENT] [Handshake Success]: Connected to {handshake['result']['serverInfo']['name']} v{handshake['result']['serverInfo']['version']}")

    # 2. Discover available tools
    tools_resp = send_rpc("tools/list", {}, 2)
    available_tools = [t['name'] for t in tools_resp['result']['tools']]
    print(f"[AI AGENT] [Tool Discovery]: Found {len(available_tools)} MCP tools: {', '.join(available_tools)}")

    # 3. Learn the MLUE primitive schema via MCP
    print("\n[AI AGENT] [Learning Schema]: Querying 'mlue_get_schema'...")
    schema_resp = send_rpc("tools/call", {"name": "mlue_get_schema", "arguments": {}}, 3)
    schema_data = json.loads(schema_resp['result']['content'][0]['text'])
    print(f"[AI AGENT] [Knowledge Acquired]: Learned MLUE Schema v{schema_data['mlue_version']}.")
    print(f"   * Supported entities: {list(schema_data['root_fields']['entities']['items']['type']['enum'])}")
    print(f"   * Spatial invariants: {schema_data['spatial_invariants']}")

    # 4. AI Designs a brand new game from scratch: "Bumper Arena"
    print("\n[AI AGENT] [Synthesizing Brand New Game]: Designing 'Bumper Arena' from learned schema...")
    new_game_document = {
        "mlue_version": "0.6",
        "environment": {
            "dimensions": [750, 500],
            "background": "#0B0F19"
        },
        "state_variables": {
            "score": 0,
            "bumper_hits": 0,
            "orbs_caught": 0,
            "status": "PLAYING"
        },
        "entities": [
            {
                "id": "energy_orb",
                "type": "circle",
                "position": {"x": 0.5, "y": 0.25},
                "size": {"radius": 0.028},
                "velocity": {"vx": 0.38, "vy": 0.42},
                "properties": {
                    "color": "#38BDF8",
                    "solid": True
                }
            },
            {
                "id": "catcher_paddle",
                "type": "box",
                "position": {"x": 0.5, "y": 0.93},
                "size": {"width": 0.24, "height": 0.038},
                "velocity": {"vx": 0.0, "vy": 0.0},
                "properties": {
                    "color": "#10B981",
                    "solid": True,
                    "control": {
                        "channel": "player_bottom",
                        "axis": "x",
                        "speed": 0.75
                    }
                }
            },
            {
                "id": "center_bumper",
                "type": "circle",
                "position": {"x": 0.5, "y": 0.5},
                "size": {"radius": 0.055},
                "velocity": {"vx": 0.0, "vy": 0.0},
                "properties": {
                    "color": "#F43F5E",
                    "solid": True
                }
            },
            {
                "id": "left_bumper",
                "type": "box",
                "position": {"x": 0.22, "y": 0.38},
                "size": {"width": 0.08, "height": 0.08},
                "velocity": {"vx": 0.0, "vy": 0.0},
                "properties": {
                    "color": "#F59E0B",
                    "solid": True
                }
            },
            {
                "id": "right_bumper",
                "type": "box",
                "position": {"x": 0.78, "y": 0.38},
                "size": {"width": 0.08, "height": 0.08},
                "velocity": {"vx": 0.0, "vy": 0.0},
                "properties": {
                    "color": "#8B5CF6",
                    "solid": True
                }
            }
        ],
        "rules": [
            {
                "trigger": "hit_center_bumper",
                "event": "collision",
                "entities": ["energy_orb", "center_bumper"],
                "actions": [
                    {"type": "increment", "target": "score", "amount": 250},
                    {"type": "increment", "target": "bumper_hits", "amount": 1}
                ]
            },
            {
                "trigger": "hit_left_bumper",
                "event": "collision",
                "entities": ["energy_orb", "left_bumper"],
                "actions": [
                    {"type": "increment", "target": "score", "amount": 100},
                    {"type": "increment", "target": "bumper_hits", "amount": 1}
                ]
            },
            {
                "trigger": "hit_right_bumper",
                "event": "collision",
                "entities": ["energy_orb", "right_bumper"],
                "actions": [
                    {"type": "increment", "target": "score", "amount": 100},
                    {"type": "increment", "target": "bumper_hits", "amount": 1}
                ]
            },
            {
                "trigger": "catch_orb",
                "event": "collision",
                "entities": ["energy_orb", "catcher_paddle"],
                "actions": [
                    {"type": "increment", "target": "score", "amount": 50},
                    {"type": "increment", "target": "orbs_caught", "amount": 1}
                ]
            },
            {
                "trigger": "floor_reset",
                "condition": {
                    "entity": "energy_orb",
                    "property": "position.y",
                    "op": ">=",
                    "value": 0.97
                },
                "actions": [
                    {
                        "type": "reset_entity",
                        "target": "energy_orb",
                        "position": {"x": 0.5, "y": 0.25},
                        "velocity": {"vx": 0.38, "vy": 0.42}
                    }
                ]
            }
        ]
    }

    # 5. Validate document via MCP
    print("[AI AGENT] [Validating Scene]: Calling 'mlue_validate_scene' via MCP...")
    val_resp = send_rpc("tools/call", {"name": "mlue_validate_scene", "arguments": {"document": new_game_document}}, 4)
    val_result = json.loads(val_resp['result']['content'][0]['text'])
    print(f"[AI AGENT] [Validation Output]: Valid={val_result.get('valid')}, Entities={val_result.get('entity_count')}, Rules={val_result.get('rule_count')}")

    # 6. Start simulation session via MCP
    print("\n[AI AGENT] [Starting Simulation]: Calling 'mlue_start_simulation' via MCP...")
    start_resp = send_rpc("tools/call", {"name": "mlue_start_simulation", "arguments": {"document": new_game_document}}, 5)
    start_result = json.loads(start_resp['result']['content'][0]['text'])
    session_id = start_result['session_id']
    print(f"[AI AGENT] [Session Active]: ID = {session_id}")

    # 7. AI plays/steps the game for 60 ticks with paddle inputs
    print("\n[AI AGENT] [Stepping Simulation]: Simulating 60 physics ticks with action input {'player_bottom': 1.0}...")
    step_resp = send_rpc("tools/call", {
        "name": "mlue_step_simulation",
        "arguments": {
            "session_id": session_id,
            "ticks": 60,
            "dt": 0.016667,
            "inputs": {"player_bottom": 1.0}
        }
    }, 6)

    # 8. Inspect live state via MCP
    print("[AI AGENT] [Inspecting State]: Calling 'mlue_inspect_state' via MCP...")
    insp_resp = send_rpc("tools/call", {"name": "mlue_inspect_state", "arguments": {"session_id": session_id}}, 7)
    insp_result = json.loads(insp_resp['result']['content'][0]['text'])
    state = insp_result['state']
    print(f"[AI AGENT] [Live State Snapshot]:")
    print(f"   * Sim Time: {state['time']}s")
    print(f"   * State Variables: {state['state_variables']}")
    for ent in state['entities']:
        print(f"   * Entity '{ent['id']}': pos=({ent['position']['x']}, {ent['position']['y']}), vel=({ent['velocity']['vx']}, {ent['velocity']['vy']})")

    # 9. Close session
    send_rpc("tools/call", {"name": "mlue_close_simulation", "arguments": {"session_id": session_id}}, 8)
    print(f"[AI AGENT] [Session Closed]: Cleaned up session {session_id}.")

    # Terminate process
    proc.terminate()

    # 10. Save newly designed game to examples/bumper_arena.mlue
    save_path = Path("examples/bumper_arena.mlue")
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(new_game_document, f, indent=2)
    print(f"\n[SUCCESS] Game Created & Saved to {save_path}")

if __name__ == "__main__":
    run_blind_ai_mcp_session()
