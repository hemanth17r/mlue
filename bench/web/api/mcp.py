import json
import sys
import base64
import urllib.parse
from http.server import BaseHTTPRequestHandler
from pathlib import Path

# Add local directory to sys.path to resolve bundled runtime
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from runtime.loader import validate_and_parse, MLUEValidationError
from runtime.engine import MLUEEngine
from runtime.ai_interface import MLUEAIInterface

MAX_TICKS = 500
MAX_ENTITIES = 50

ai_interface = MLUEAIInterface()
engine = MLUEEngine()


def make_playable_url(scene: dict) -> str:
    """Generates direct zero-install playable web link for an MLUE scene."""
    try:
        raw_json = json.dumps(scene)
        encoded = urllib.parse.quote(raw_json)
        b64 = base64.b64encode(encoded.encode('utf-8')).decode('utf-8')
        return f"https://mlue-bench.vercel.app/#data={b64}"
    except Exception:
        return "https://mlue-bench.vercel.app/#playground"


class handler(BaseHTTPRequestHandler):

    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()

        response = {
            'status': 'healthy',
            'service': 'MLUE Remote MCP Gateway (Phase 0 Substrate)',
            'version': '0.7.0',
            'protocol': 'Model Context Protocol (JSON-RPC 2.0)',
            'endpoints': {
                'POST /api/mcp': 'JSON-RPC 2.0 tool execution endpoint'
            },
            'guardrails': {
                'max_ticks': MAX_TICKS,
                'max_entities': MAX_ENTITIES,
                'file_system_access': 'DISABLED (in-memory JSON only)'
            }
        }
        self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            payload = json.loads(body) if body else {}
        except Exception as e:
            self._send_error(None, -32700, f'Parse error: Invalid JSON payload ({e})')
            return

        method = payload.get('method')
        params = payload.get('params', {})
        rpc_id = payload.get('id')

        # 1. Initialize Handshake
        if method == 'initialize':
            self._send_result(rpc_id, {
                'protocolVersion': '2024-11-05',
                'serverInfo': {
                    'name': 'mlue-remote-mcp-gateway',
                    'version': '0.7.0'
                },
                'capabilities': {
                    'tools': {}
                }
            })
            return

        # 2. Tools Discovery
        if method == 'tools/list':
            self._send_result(rpc_id, {
                'tools': [
                    {
                        'name': 'mlue_get_schema',
                        'description': 'Returns the declarative MLUE schema specification and spatial invariant rules.',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {}
                        }
                    },
                    {
                        'name': 'mlue_validate_scene',
                        'description': 'Statically validates a declarative MLUE scene JSON for geometric invariants and reachability.',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'scene': {
                                    'type': 'object',
                                    'description': 'Declarative MLUE scene document dictionary'
                                }
                            },
                            'required': ['scene']
                        }
                    },
                    {
                        'name': 'mlue_simulate_scene',
                        'description': 'Executes N deterministic simulation ticks on a declarative MLUE scene JSON in memory.',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'scene': {
                                    'type': 'object',
                                    'description': 'Declarative MLUE scene document dictionary'
                                },
                                'ticks': {
                                    'type': 'integer',
                                    'minimum': 1,
                                    'maximum': MAX_TICKS,
                                    'description': f'Number of simulation steps to evaluate (1 to {MAX_TICKS})'
                                },
                                'dt': {
                                    'type': 'number',
                                    'description': 'Time step in seconds (default: 0.01667)'
                                },
                                'inputs': {
                                    'type': 'object',
                                    'description': 'Optional input signal vector mapping channel names to float values [-1.0, 1.0]'
                                }
                            },
                            'required': ['scene'],
                            'additionalProperties': False
                        }
                    }
                ]
            })
            return

        # 3. Tool Invocations
        if method == 'tools/call':
            tool_name = params.get('name')
            args = params.get('arguments', {})
            if not isinstance(args, dict):
                self._send_error(rpc_id, -32602, "Invalid arguments: Tool arguments must be a JSON object dictionary.")
                return

            if tool_name == 'mlue_get_schema':
                if args:
                    unexpected = next(iter(args.keys()))
                    self._send_error(rpc_id, -32602, f"Unexpected argument '{unexpected}'. 'mlue_get_schema' accepts no arguments.")
                    return
                schema = ai_interface.get_schema()
                self._send_tool_text(rpc_id, json.dumps(schema, indent=2))
                return

            if tool_name == 'mlue_validate_scene':
                allowed = {'scene'}
                unexpected = set(args.keys()) - allowed
                if unexpected:
                    self._send_error(rpc_id, -32602, f"Unexpected argument '{next(iter(unexpected))}'. Allowed arguments: ['scene'].")
                    return

                scene = args.get('scene')
                if not isinstance(scene, dict):
                    self._send_error(rpc_id, -32602, "Invalid arguments: 'scene' must be a JSON object dictionary.")
                    return
                
                try:
                    doc = validate_and_parse(scene)
                    res = {
                        'valid': True,
                        'version': doc.version,
                        'dimensions': [doc.environment.width, doc.environment.height],
                        'entity_count': len(doc.entities),
                        'rule_count': len(doc.rules),
                        'state_variables': doc.state_variables,
                        'playable_url': make_playable_url(scene)
                    }
                    self._send_tool_text(rpc_id, json.dumps(res, indent=2))
                except MLUEValidationError as e:
                    self._send_tool_text(rpc_id, json.dumps({'valid': False, 'error': str(e)}, indent=2))
                return

            if tool_name == 'mlue_simulate_scene':
                allowed = {'scene', 'ticks', 'dt', 'inputs'}
                unexpected = set(args.keys()) - allowed
                if unexpected:
                    self._send_error(rpc_id, -32602, f"Unexpected argument '{next(iter(unexpected))}'. Allowed arguments: ['scene', 'ticks', 'dt', 'inputs'].")
                    return

                scene = args.get('scene')
                if not isinstance(scene, dict):
                    self._send_error(rpc_id, -32602, "Invalid arguments: 'scene' must be a JSON object dictionary.")
                    return

                raw_ticks = args.get('ticks', 60)
                try:
                    requested_ticks = int(raw_ticks)
                except (ValueError, TypeError):
                    self._send_error(rpc_id, -32602, "Invalid arguments: 'ticks' must be an integer.")
                    return

                if requested_ticks < 1:
                    self._send_error(rpc_id, -32602, f"Invalid argument: 'ticks' must be >= 1 (got {requested_ticks}).")
                    return

                clamped = False
                warning_msg = None
                if requested_ticks > MAX_TICKS:
                    ticks = MAX_TICKS
                    clamped = True
                    warning_msg = f"Requested ticks ({requested_ticks}) exceeded maximum cloud limit ({MAX_TICKS}). Clamped execution to {MAX_TICKS} ticks."
                else:
                    ticks = requested_ticks

                dt = float(args.get('dt', 1.0 / 60.0))
                inputs = args.get('inputs', {})
                if not isinstance(inputs, dict):
                    self._send_error(rpc_id, -32602, "Invalid arguments: 'inputs' must be a dictionary mapping channel names to values.")
                    return

                try:
                    doc = validate_and_parse(scene)
                    if len(doc.entities) > MAX_ENTITIES:
                        self._send_error(rpc_id, -32602, f"Entity count ({len(doc.entities)}) exceeds cloud limit of {MAX_ENTITIES}.")
                        return

                    state = engine.init_simulation(doc)
                    for _ in range(ticks):
                        state = engine.step(state, dt=dt, inputs=inputs)

                    output_entities = [
                        {
                            'id': e.id,
                            'type': e.type,
                            'position': {'x': round(e.position.x, 6), 'y': round(e.position.y, 6)},
                            'velocity': {'vx': round(e.velocity.vx, 6), 'vy': round(e.velocity.vy, 6)},
                            'active': e.active
                        }
                        for e in state.entities
                    ]

                    res = {
                        'simulation_ticks': ticks,
                        'requested_ticks': requested_ticks,
                        'applied_ticks': ticks,
                        'clamped': clamped,
                        'min_ticks_limit': 1,
                        'max_ticks_limit': MAX_TICKS,
                        'total_time': round(state.time, 6),
                        'state_variables': state.state_variables,
                        'entities': output_entities,
                        'playable_url': make_playable_url(scene)
                    }
                    if warning_msg:
                        res['warning'] = warning_msg

                    self._send_tool_text(rpc_id, json.dumps(res, indent=2))
                except Exception as e:
                    self._send_tool_text(rpc_id, json.dumps({'success': False, 'error': str(e)}, indent=2))
                return

            self._send_error(rpc_id, -32601, f"Unknown tool: '{tool_name}'")
            return

        self._send_error(rpc_id, -32601, f"Unknown method: '{method}'")

    def _send_result(self, rpc_id, result):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        payload = {'jsonrpc': '2.0', 'id': rpc_id, 'result': result}
        self.wfile.write(json.dumps(payload).encode('utf-8'))

    def _send_tool_text(self, rpc_id, text):
        result = {'content': [{'type': 'text', 'text': text}]}
        self._send_result(rpc_id, result)

    def _send_error(self, rpc_id, code, message):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        payload = {'jsonrpc': '2.0', 'id': rpc_id, 'error': {'code': code, 'message': message}}
        self.wfile.write(json.dumps(payload).encode('utf-8'))
