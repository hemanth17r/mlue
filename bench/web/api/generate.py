"""MLUE AI Universal Software & Simulation Substrate Generator API Route.

Serverless Python endpoint that compiles natural language specifications or refinement
instructions strictly into valid declarative .mlue JSON documents governed by the
MLUE 1.6 architecture, and statically validates them in-memory before returning.
"""

import json
import os
import re
import sys
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler
from pathlib import Path

# Add local directory to sys.path to resolve bundled runtime
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from runtime.loader import validate_and_parse, MLUEValidationError

SYSTEM_PROMPT = """You are the MLUE Core Architecture AI Generator.
Your job is to compile natural language specifications into machine-executable, declarative .mlue JSON documents conforming strictly to the MLUE 1.6 architecture.

MLUE is a UNIVERSAL SOFTWARE & SIMULATION SUBSTRATE. You can build:
1. Software & Telemetry Dashboards (Cluster monitors, load balancers, packet routers, memory pool visualizers)
2. Scientific & Physics Simulations (N-body gravity, particle pressure chambers, wave propagation)
3. Multi-Agent Swarms (Drone grids, predator-prey systems, flocking boids, traffic intersection dispatchers)
4. Industrial Control Panels & Logic Systems (Hydraulic tank controllers, digital logic gates, finite state automata)
5. Interactive Reactive Applications & Games (Emergent breakout, cyber dodge, pinball, bumper arena)

You must NEVER generate traditional JavaScript, HTML, Canvas scripts, or unstructured JSON.
You must ONLY output a valid MLUE 1.6 JSON document adhering strictly to the specifications below.

### MLUE 1.6 ARCHITECTURAL SPECIFICATION:

1. Root Keys:
   - "mlue_version": "1.6"
   - "environment": { "dimensions": [800, 600], "background": "#hexcode" }
   - "state_variables": { "system": { "metric_a": 0, "status": "ACTIVE" } } (or custom nested counters)
   - "entities": Array of discrete entities.
   - "rules": Array of declarative collision and event rules.

2. Entities (Normalized Coordinate Space [0.0, 1.0]):
   - "id": Unique alphanumeric string (e.g. "node_alpha", "packet_1", "barrier_main", "controller").
   - "type": "circle" OR "box" (STRICT: no other shapes exist in MLUE primitives).
   - "position": { "x": float in [0.05, 0.95], "y": float in [0.05, 0.95] }
   - "size":
       - For "circle": { "radius": float in [0.015, 0.08] }
       - For "box": { "width": float in [0.04, 0.40], "height": float in [0.02, 0.25] }
   - "velocity": { "vx": float in [-0.5, 0.5], "vy": float in [-0.5, 0.5] }
   - "properties":
       - "solid": true (for physical elastic collisions)
       - "color": vibrant hex string (e.g. #38BDF8, #10B981, #F43F5E, #F59E0B, #A855F7, #EC4899, #3B82F6)
       - "control": Optional player/operator controls: { "channel": "paddle", "axis": "x" | "y" | "xy", "speed": 0.85 }

3. Rules & State Mutations:
   - "trigger": Unique rule identifier string.
   - "event": "collision"
   - "entities": ["entity_id_1", "entity_id_2"]
   - "actions": Array of atomic action objects:
       - { "type": "destroy_entity", "target": "entity_id" }
       - { "type": "increment_path", "target": "system.metric_a", "amount": 1 }
       - { "type": "set_path", "target": "system.status", "value": "UPDATED" }
       - { "type": "reset_entity", "target": "packet_1", "position": { "x": 0.15, "y": 0.5 }, "velocity": { "vx": 0.3, "vy": -0.1 } }

Output strictly valid raw JSON only.
"""

MODELS_TO_TRY = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-2.5-flash",
    "gemini-1.5-pro"
]


def extract_json(text: str) -> dict:
    """Robustly extract and parse JSON from LLM response."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n", "", text)
        text = re.sub(r"```$", "", text).strip()
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        return json.loads(match.group(0))
    return json.loads(text)


class handler(BaseHTTPRequestHandler):

    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, x-gemini-key')

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        res = {
            'service': 'MLUE AI Substrate Generator',
            'status': 'online',
            'supported_models': MODELS_TO_TRY,
            'architecture': 'MLUE 1.6 Declarative Invariant Substrate',
            'supported_versions': ['1.6']
        }
        self.wfile.write(json.dumps(res, indent=2).encode('utf-8'))

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            payload = json.loads(body) if body else {}
        except Exception as e:
            self._send_json_error(400, f'Invalid JSON payload: {e}')
            return

        prompt = payload.get('prompt', '').strip()
        current_scene = payload.get('current_scene')
        api_key = self.headers.get('x-gemini-key') or payload.get('api_key') or os.environ.get('GEMINI_API_KEY')

        if not prompt:
            self._send_json_error(400, 'Missing "prompt" in request body.')
            return

        if not api_key:
            self._send_json_error(401, 'GEMINI_API_KEY not configured on server.')
            return

        full_user_content = f"User Substrate Request: {prompt}\n"
        if current_scene:
            full_user_content += f"\nExisting MLUE Scene to Modify:\n{json.dumps(current_scene, indent=2)}\n\nApply the requested changes and output the complete updated .mlue JSON document."

        last_error = None
        for model_name in MODELS_TO_TRY:
            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            gemini_body = {
                "contents": [
                    {
                        "parts": [
                            {"text": SYSTEM_PROMPT},
                            {"text": full_user_content}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "topP": 0.95,
                    "responseMimeType": "application/json"
                }
            }

            try:
                req = urllib.request.Request(
                    gemini_url,
                    data=json.dumps(gemini_body).encode('utf-8'),
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )

                with urllib.request.urlopen(req, timeout=18) as response:
                    raw_resp = response.read().decode('utf-8')
                    gemini_json = json.loads(raw_resp)

                candidates = gemini_json.get('candidates', [])
                if not candidates:
                    continue

                generated_text = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                if not generated_text:
                    continue

                parsed_scene = extract_json(generated_text)

                # Enforce MLUE 1.6 root version
                if "mlue_version" not in parsed_scene:
                    parsed_scene["mlue_version"] = parsed_scene.pop("version", "1.6")

                # Static Invariant Gate
                validate_and_parse(parsed_scene)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()

                out = {
                    'success': True,
                    'architecture': 'MLUE 1.6 Declarative',
                    'model': model_name,
                    'prompt': prompt,
                    'scene': parsed_scene
                }
                self.wfile.write(json.dumps(out, indent=2).encode('utf-8'))
                return

            except urllib.error.HTTPError as he:
                last_error = f"Gemini ({model_name}) HTTP {he.code}: {he.read().decode('utf-8', errors='ignore')}"
            except MLUEValidationError as ve:
                last_error = f"Invariant Violation ({model_name}): {ve}"
            except Exception as ex:
                last_error = f"Error ({model_name}): {ex}"

        self._send_json_error(500, f"Compilation failed: {last_error}")

    def _send_json_error(self, code, message):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        err = {'success': False, 'error': message}
        self.wfile.write(json.dumps(err).encode('utf-8'))
