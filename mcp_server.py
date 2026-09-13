#!/usr/bin/env python3
"""MLUE Model Context Protocol (MCP) Server

A standalone, zero-dependency MCP server providing machine-accessible tools for AI models
to discover MLUE primitives, statically validate scenes, run in-memory simulations,
evaluate action vectors, inspect live states, and mutate entities.
"""

import sys
import json
from typing import Dict, Any, Optional
from runtime.ai_interface import MLUEAIInterface

SERVER_NAME = "mlue-mcp-server"
SERVER_VERSION = "1.1.0"
PROTOCOL_VERSION = "2024-11-05"

ai_interface = MLUEAIInterface()

TOOLS_DEFINITIONS = [
    {
        "name": "mlue_get_schema",
        "description": "Returns the complete machine-readable MLUE specification schema, valid entity primitives (circle, box), property rules, and mathematical spatial invariant constraints.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    {
        "name": "mlue_validate_scene",
        "description": "Statically validates an MLUE document representation against syntax, schema types, and spatial reachability invariants.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "document": {
                    "type": "object",
                    "description": "The MLUE document object to validate."
                }
            },
            "required": ["document"],
            "additionalProperties": False,
        },
    },
    {
        "name": "mlue_lint",
        "description": "Performs compile-time static diagnostic linting on an MLUE document, returning structured issues with JSON pointers, error codes, and suggested fixes for self-healing AI generation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "document": {
                    "type": "object",
                    "description": "The MLUE document object to lint."
                },
                "scene_string": {
                    "type": "string",
                    "description": "Raw JSON string of the MLUE document."
                },
                "file_path": {
                    "type": "string",
                    "description": "File path on disk to the .mlue scene."
                }
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "mlue_start_simulation",
        "description": "Initializes a stateful in-memory MLUE simulation session from a document object or file path.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "document": {
                    "type": "object",
                    "description": "MLUE document object containing environment, entities, state_variables, and rules."
                },
                "file_path": {
                    "type": "string",
                    "description": "Optional file path to load MLUE document from disk."
                }
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "mlue_step_simulation",
        "description": "Advances an active MLUE simulation session by N ticks with optional normalized action control signals (e.g. {'player_bottom': 1.0}).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "The active simulation session ID returned by mlue_start_simulation."
                },
                "ticks": {
                    "type": "integer",
                    "default": 1,
                    "description": "Number of discrete simulation steps to evaluate."
                },
                "dt": {
                    "type": "number",
                    "default": 0.016667,
                    "description": "Time delta per tick in seconds (defaults to ~60 FPS / 0.0167s)."
                },
                "inputs": {
                    "type": "object",
                    "description": "Dictionary of normalized control channel signals in range [-1.0, 1.0] (e.g. {'player_bottom': 1.0, 'player_left': -1.0}).",
                    "additionalProperties": {"type": "number"}
                }
            },
            "required": ["session_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "mlue_inspect_state",
        "description": "Queries the live state of an active simulation session, including all entity coordinates, velocities, active states, rendered shapes, and state variables.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "The active simulation session ID."
                }
            },
            "required": ["session_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "mlue_mutate_entity",
        "description": "Dynamically mutates an entity in an active simulation session (updating position, velocity, active flag, or custom properties).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "The active simulation session ID."
                },
                "entity_id": {
                    "type": "string",
                    "description": "ID of the entity to mutate."
                },
                "updates": {
                    "type": "object",
                    "description": "Dictionary of updates: position (x, y), velocity (vx, vy), active (bool), or properties (dict)."
                }
            },
            "required": ["session_id", "entity_id", "updates"],
            "additionalProperties": False,
        },
    },
    {
        "name": "mlue_close_simulation",
        "description": "Terminates and frees an active in-memory simulation session.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "The active simulation session ID to close."
                }
            },
            "required": ["session_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "mlue_patch_document",
        "description": "Applies a compact array of micro-delta operations (insert_entity, update_entity, delete_entity, insert_rule, delete_rule, set_state, delete_state) to an MLUE document dictionary and verifies invariants in < 1ms.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "document": {
                    "type": "object",
                    "description": "The MLUE document dictionary to patch."
                },
                "operations": {
                    "type": "array",
                    "description": "List of micro-delta patch operations.",
                    "items": {"type": "object"}
                }
            },
            "required": ["document", "operations"],
            "additionalProperties": False,
        },
    },
    {
        "name": "mlue_patch_session",
        "description": "Hot-patches an active in-memory simulation session using micro-delta operations without interrupting the simulation clock.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "The active simulation session ID."
                },
                "operations": {
                    "type": "array",
                    "description": "List of micro-delta patch operations to apply.",
                    "items": {"type": "object"}
                }
            },
            "required": ["session_id", "operations"],
            "additionalProperties": False,
        },
    },
    {
        "name": "mlue_create_checkpoint",
        "description": "Creates an immutable, bit-exact cryptographic snapshot of an active session for zero-latency time-travel or branching.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "The active simulation session ID."
                },
                "checkpoint_id": {
                    "type": "string",
                    "description": "Optional custom identifier for the checkpoint."
                }
            },
            "required": ["session_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "mlue_restore_checkpoint",
        "description": "Restores an active simulation session back to a previously saved checkpoint.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "The active simulation session ID."
                },
                "checkpoint_id": {
                    "type": "string",
                    "description": "The checkpoint ID to restore."
                }
            },
            "required": ["session_id", "checkpoint_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "mlue_list_checkpoints",
        "description": "Lists all active cryptographic checkpoints for a session.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "The active simulation session ID."
                }
            },
            "required": ["session_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "mlue_catalog_query",
        "description": "Searches the MLUE catalog for standardized shapes, parts, design tokens, and blueprints using semantic keyword and tag matching.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keyword or tag (e.g. 'paddle', 'ball', 'bounce', 'card', 'slate', 'breakout')."
                },
                "kind": {
                    "type": "string",
                    "enum": ["shape", "part", "token", "blueprint"],
                    "description": "Optional category filter."
                }
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    {
        "name": "mlue_catalog_get",
        "description": "Fetches the complete schema, default properties, entity templates, and rules for a specific catalog shape, part, token, or blueprint.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "kind": {
                    "type": "string",
                    "enum": ["shape", "part", "token", "blueprint"],
                    "description": "Category of the catalog entry."
                },
                "name": {
                    "type": "string",
                    "description": "Identifier of the catalog entry (e.g. 'paddle', 'ball', 'palettes', 'breakout')."
                }
            },
            "required": ["kind", "name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "mlue_catalog_register",
        "description": "Programmatically registers and persists a newly synthesized shape, part, token, or blueprint into the MLUE catalog after validating [0.0, 1.0] coordinate invariants.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "kind": {
                    "type": "string",
                    "enum": ["shape", "part", "token", "blueprint"],
                    "description": "Category of the catalog entry."
                },
                "name": {
                    "type": "string",
                    "description": "Unique identifier for the new entry."
                },
                "entry": {
                    "type": "object",
                    "description": "The complete catalog entry dictionary conforming to MLUE specification."
                },
                "overwrite": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to overwrite an existing entry with the same name."
                }
            },
            "required": ["kind", "name", "entry"],
            "additionalProperties": False,
        },
    },
]


def handle_tool_call(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Dispatches a tool call to the MLUEAIInterface and formats the output."""
    if name == "mlue_get_schema":
        schema_data = ai_interface.get_schema()
        return {"content": [{"type": "text", "text": json.dumps(schema_data, indent=2)}]}

    elif name == "mlue_validate_scene":
        doc = arguments.get("document")
        result = ai_interface.validate_scene(doc)
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

    elif name == "mlue_lint":
        from runtime.linter import lint_mlue
        target = arguments.get("document") or arguments.get("scene_string") or arguments.get("file_path")
        if not target:
            return {"isError": True, "content": [{"type": "text", "text": "Error: Must provide 'document', 'scene_string', or 'file_path'."}]}
        report = lint_mlue(target)
        return {"content": [{"type": "text", "text": json.dumps(report.to_dict(), indent=2)}]}

    elif name == "mlue_start_simulation":
        target = arguments.get("document") or arguments.get("file_path")
        if not target:
            return {"isError": True, "content": [{"type": "text", "text": "Error: Must provide 'document' or 'file_path'."}]}
        result = ai_interface.create_session(target)
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

    elif name == "mlue_step_simulation":
        session_id = arguments.get("session_id", "")
        ticks = int(arguments.get("ticks", 1))
        dt = float(arguments.get("dt", 0.016667))
        inputs = arguments.get("inputs")
        result = ai_interface.step_session(session_id, dt=dt, inputs=inputs, ticks=ticks)
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

    elif name == "mlue_inspect_state":
        session_id = arguments.get("session_id", "")
        result = ai_interface.inspect_session(session_id)
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

    elif name == "mlue_mutate_entity":
        session_id = arguments.get("session_id", "")
        entity_id = arguments.get("entity_id", "")
        updates = arguments.get("updates", {})
        result = ai_interface.mutate_entity(session_id, entity_id, updates)
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

    elif name == "mlue_patch_document":
        doc = arguments.get("document", {})
        ops = arguments.get("operations", [])
        result = ai_interface.patch_document(doc, ops)
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

    elif name == "mlue_patch_session":
        session_id = arguments.get("session_id", "")
        ops = arguments.get("operations", [])
        result = ai_interface.patch_session(session_id, ops)
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

    elif name == "mlue_create_checkpoint":
        session_id = arguments.get("session_id", "")
        cid = arguments.get("checkpoint_id")
        result = ai_interface.create_checkpoint(session_id, cid)
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

    elif name == "mlue_restore_checkpoint":
        session_id = arguments.get("session_id", "")
        cid = arguments.get("checkpoint_id", "")
        result = ai_interface.restore_checkpoint(session_id, cid)
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

    elif name == "mlue_list_checkpoints":
        session_id = arguments.get("session_id", "")
        result = ai_interface.list_checkpoints(session_id)
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

    elif name == "mlue_close_simulation":
        session_id = arguments.get("session_id", "")
        result = ai_interface.close_session(session_id)
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

    elif name == "mlue_catalog_query":
        query = arguments.get("query", "")
        kind = arguments.get("kind")
        result = ai_interface.catalog_query(query, kind=kind)
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

    elif name == "mlue_catalog_get":
        kind = arguments.get("kind", "")
        entry_name = arguments.get("name", "")
        result = ai_interface.catalog_get(kind, entry_name)
        if result is None:
            return {"isError": True, "content": [{"type": "text", "text": f"Catalog entry '{kind}/{entry_name}' not found."}]}
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

    elif name == "mlue_catalog_register":
        kind = arguments.get("kind", "")
        entry_name = arguments.get("name", "")
        entry = arguments.get("entry", {})
        overwrite = arguments.get("overwrite", False)
        result = ai_interface.catalog_register(kind, entry_name, entry, overwrite=overwrite)
        if not result.get("success"):
            return {"isError": True, "content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

    else:
        return {"isError": True, "content": [{"type": "text", "text": f"Unknown tool '{name}'."}]}


def handle_jsonrpc_message(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Processes a standard JSON-RPC request and returns a corresponding response object."""
    msg_id = msg.get("id")
    method = msg.get("method")
    params = msg.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "serverInfo": {
                    "name": SERVER_NAME,
                    "version": SERVER_VERSION,
                }
            }
        }

    elif method == "notifications/initialized":
        return None

    elif method == "ping":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {}}

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": TOOLS_DEFINITIONS
            }
        }

    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        res = handle_tool_call(tool_name, arguments)
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": res
        }

    elif method == "resources/list":
        resources = ai_interface.catalog_list_resources()
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "resources": resources
            }
        }

    elif method == "resources/read":
        uri = params.get("uri", "")
        if uri.startswith("mlue://catalog/"):
            parts = uri.replace("mlue://catalog/", "").strip("/").split("/")
            if len(parts) >= 2:
                kind, name = parts[0], parts[1]
                entry = ai_interface.catalog_get(kind, name)
                if entry is not None:
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "contents": [
                                {
                                    "uri": uri,
                                    "mimeType": "application/json",
                                    "text": json.dumps(entry, indent=2)
                                }
                            ]
                        }
                    }
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32602, "message": f"Resource '{uri}' not found."}
        }

    else:
        if msg_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found."
                }
            }
        return None


def run_stdio_server():
    """Starts the standard I/O JSON-RPC loop."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            line_str = line.strip()
            if not line_str:
                continue

            msg = json.loads(line_str)
            response = handle_jsonrpc_message(msg)
            if response is not None:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
        except KeyboardInterrupt:
            break
        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


def run_self_test():
    """Runs a standalone test suite over the MCP JSON-RPC protocol."""
    print("=== Running MLUE MCP Server Protocol Self-Test ===")

    # 1. Initialize
    init_req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    init_resp = handle_jsonrpc_message(init_req)
    assert init_resp["result"]["serverInfo"]["name"] == SERVER_NAME
    print("[PASS] MCP initialize handshake verified.")

    # 2. List tools
    tools_req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    tools_resp = handle_jsonrpc_message(tools_req)
    assert len(tools_resp["result"]["tools"]) == len(TOOLS_DEFINITIONS)
    print(f"[PASS] MCP tools/list verified ({len(tools_resp['result']['tools'])} tools available).")

    # 3. Get schema
    schema_req = {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "mlue_get_schema", "arguments": {}}}
    schema_resp = handle_jsonrpc_message(schema_req)
    schema_obj = json.loads(schema_resp["result"]["content"][0]["text"])
    assert "mlue_version" in schema_obj and float(schema_obj["mlue_version"]) >= 0.7
    print("[PASS] mlue_get_schema verified.")

    # 4. Start simulation with breakout
    start_req = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "mlue_start_simulation",
            "arguments": {"file_path": "examples/breakout.mlue"}
        }
    }
    start_resp = handle_jsonrpc_message(start_req)
    start_obj = json.loads(start_resp["result"]["content"][0]["text"])
    assert start_obj["success"] is True
    session_id = start_obj["session_id"]
    print(f"[PASS] mlue_start_simulation verified (Session ID: {session_id}).")

    # 5. Step simulation with action inputs
    step_req = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "mlue_step_simulation",
            "arguments": {
                "session_id": session_id,
                "ticks": 10,
                "dt": 0.016667,
                "inputs": {"player_bottom": 1.0}
            }
        }
    }
    step_resp = handle_jsonrpc_message(step_req)
    step_obj = json.loads(step_resp["result"]["content"][0]["text"])
    assert step_obj["success"] is True
    print("[PASS] mlue_step_simulation verified with input signals.")

    # 6. Inspect state
    inspect_req = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "mlue_inspect_state",
            "arguments": {"session_id": session_id}
        }
    }
    inspect_resp = handle_jsonrpc_message(inspect_req)
    inspect_obj = json.loads(inspect_resp["result"]["content"][0]["text"])
    assert inspect_obj["success"] is True
    assert "score" in inspect_obj["state"]["state_variables"]
    print(f"[PASS] mlue_inspect_state verified (State variables: {inspect_obj['state']['state_variables']}).")

    # 7. Mutate entity
    mutate_req = {
        "jsonrpc": "2.0",
        "id": 7,
        "method": "tools/call",
        "params": {
            "name": "mlue_mutate_entity",
            "arguments": {
                "session_id": session_id,
                "entity_id": "ball_01",
                "updates": {"properties": {"color": "#FF00FF"}}
            }
        }
    }
    mutate_resp = handle_jsonrpc_message(mutate_req)
    mutate_obj = json.loads(mutate_resp["result"]["content"][0]["text"])
    assert mutate_obj["success"] is True
    print("[PASS] mlue_mutate_entity verified.")

    # 8. Close simulation
    close_req = {
        "jsonrpc": "2.0",
        "id": 8,
        "method": "tools/call",
        "params": {
            "name": "mlue_close_simulation",
            "arguments": {"session_id": session_id}
        }
    }
    close_resp = handle_jsonrpc_message(close_req)
    close_obj = json.loads(close_resp["result"]["content"][0]["text"])
    assert close_obj["success"] is True
    print("[PASS] mlue_close_simulation verified.")

    # 9. Resources List
    res_list_req = {"jsonrpc": "2.0", "id": 9, "method": "resources/list", "params": {}}
    res_list_resp = handle_jsonrpc_message(res_list_req)
    resources = res_list_resp["result"]["resources"]
    assert len(resources) >= 18
    assert any(r["uri"] == "mlue://catalog/part/paddle" for r in resources)
    print(f"[PASS] MCP resources/list verified ({len(resources)} catalog resources discovered).")

    # 10. Resources Read
    res_read_req = {
        "jsonrpc": "2.0",
        "id": 10,
        "method": "resources/read",
        "params": {"uri": "mlue://catalog/part/paddle"}
    }
    res_read_resp = handle_jsonrpc_message(res_read_req)
    content_text = res_read_resp["result"]["contents"][0]["text"]
    paddle_obj = json.loads(content_text)
    assert paddle_obj["id"] == "paddle"
    print("[PASS] MCP resources/read verified for mlue://catalog/part/paddle.")

    # 11. Tool: mlue_catalog_query
    query_req = {
        "jsonrpc": "2.0",
        "id": 11,
        "method": "tools/call",
        "params": {
            "name": "mlue_catalog_query",
            "arguments": {"query": "paddle"}
        }
    }
    query_resp = handle_jsonrpc_message(query_req)
    query_results = json.loads(query_resp["result"]["content"][0]["text"])
    assert len(query_results) > 0
    assert query_results[0]["id"] == "paddle"
    print("[PASS] mlue_catalog_query verified.")

    # 12. Tool: mlue_catalog_get
    get_req = {
        "jsonrpc": "2.0",
        "id": 12,
        "method": "tools/call",
        "params": {
            "name": "mlue_catalog_get",
            "arguments": {"kind": "part", "name": "ball"}
        }
    }
    get_resp = handle_jsonrpc_message(get_req)
    ball_obj = json.loads(get_resp["result"]["content"][0]["text"])
    assert ball_obj["id"] == "ball"
    assert ball_obj["entity_template"]["type"] == "circle"
    print("[PASS] mlue_catalog_get verified.")

    print("=== All MCP Protocol Tests Passed Successfully! ===")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_self_test()
    else:
        run_stdio_server()


if __name__ == "__main__":
    main()
