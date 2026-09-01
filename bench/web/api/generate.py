"""MLUE AI Game & Scene Generator API Route.

Serverless Python endpoint that accepts natural language game prompts or refinement
instructions, compiles them strictly into valid declarative .mlue JSON documents
governed by the MLUE 1.6 architecture, and statically validates them in-memory before returning.
"""

import json
import os
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
Your job is to compile natural language game ideas into machine-executable, declarative .mlue JSON documents conforming strictly to the MLUE 1.6 architecture.

You must NEVER generate traditional JavaScript, HTML, Canvas scripts, or unstructured JSON.
You must ONLY output a valid MLUE 1.6 JSON document adhering to the specifications below.

### MLUE 1.6 ARCHITECTURAL SPECIFICATION:

1. Root Keys:
   - "mlue_version": "1.6"
   - "environment": { "dimensions": [800, 600], "background": "#hexcode" }
   - "state_variables": { "game": { "score": 0, "lives": 3, "state": "PLAYING" } } (or custom nested counters)
   - "entities": Array of discrete entities.
   - "rules": Array of declarative collision and event rules.

2. Entities (Normalized Coordinate Space [0.0, 1.0]):
   - "id": Unique alphanumeric string (e.g. "player_paddle", "ball", "brick_1", "obstacle_a").
   - "type": "circle" OR "box" (STRICT: no other shapes exist in MLUE primitives).
   - "position": { "x": float in [0.05, 0.95], "y": float in [0.05, 0.95] }
   - "size":
       - For "circle": { "radius": float in [0.015, 0.08] }
       - For "box": { "width": float in [0.04, 0.35], "height": float in [0.02, 0.12] }
   - "velocity": { "vx": float in [-0.5, 0.5], "vy": float in [-0.5, 0.5] }
   - "properties":
       - "solid": true (for physical elastic collisions)
       - "color": vibrant hex string (e.g. #38BDF8, #10B981, #F43F5E, #F59E0B, #A855F7, #EC4899)
       - "control": Optional player controls: { "channel": "paddle", "axis": "x" | "y", "speed": 0.6 }

3. Rules & State Mutations:
   - "trigger": Unique rule identifier string.
   - "event": "collision"
   - "entities": ["entity_id_1", "entity_id_2"]
   - "actions": Array of atomic action objects:
       - { "type": "destroy_entity", "target": "entity_id" }
       - { "type": "increment_path", "target": "game.score", "amount": 100 }
       - { "type": "increment_path", "target": "game.lives", "amount": -1 }
       - { "type": "set_path", "target": "game.state", "value": "GAME_OVER" }
       - { "type": "reset_entity", "target": "ball", "position": { "x": 0.5, "y": 0.5 }, "velocity": { "vx": 0.2, "vy": 0.3 } }

### CANONICAL EXAMPLE:
{
  "mlue_version": "1.6",
  "environment": { "dimensions": [800, 600], "background": "#020617" },
  "state_variables": { "game": { "score": 0, "lives": 3, "state": "PLAYING" } },
  "entities": [
    {
      "id": "ball",
      "type": "circle",
      "position": { "x": 0.50, "y": 0.60 },
      "size": { "radius": 0.025 },
      "velocity": { "vx": 0.25, "vy": -0.35 },
      "properties": { "solid": true, "color": "#38BDF8" }
    },
    {
      "id": "player_paddle",
      "type": "box",
      "position": { "x": 0.50, "y": 0.88 },
      "size": { "width": 0.16, "height": 0.03 },
      "velocity": { "vx": 0.0, "vy": 0.0 },
      "properties": { "solid": true, "color": "#10B981", "control": { "channel": "paddle", "axis": "x", "speed": 0.6 } }
    },
    {
      "id": "target_1",
      "type": "box",
      "position": { "x": 0.30, "y": 0.20 },
      "size": { "width": 0.12, "height": 0.04 },
      "velocity": { "vx": 0.0, "vy": 0.0 },
      "properties": { "solid": true, "color": "#F43F5E" }
    }
  ],
  "rules": [
    {
      "trigger": "hit_target_1",
      "event": "collision",
      "entities": ["ball", "target_1"],
      "actions": [
        { "type": "destroy_entity", "target": "target_1" },
        { "type": "increment_path", "target": "game.score", "amount": 100 }
      ]
    }
  ]
}

Output strictly valid raw JSON only.
"""


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
            'service': 'MLUE AI Game Generator',
            'status': 'online',
            'model': 'gemini-3.5-flash',
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

        # Build prompt grounded in MLUE architecture
        full_user_content = f"User Game Request: {prompt}\n"
        if current_scene:
            full_user_content += f"\nExisting MLUE Scene to Modify:\n{json.dumps(current_scene, indent=2)}\n\nApply the requested changes and output the complete updated .mlue JSON document."

        model_name = "gemini-3.5-flash"
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

            with urllib.request.urlopen(req, timeout=25) as response:
                raw_resp = response.read().decode('utf-8')
                gemini_json = json.loads(raw_resp)

            candidates = gemini_json.get('candidates', [])
            if not candidates:
                raise ValueError('Gemini returned no candidates.')

            generated_text = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            if not generated_text:
                raise ValueError('Empty text response from Gemini.')

            parsed_scene = json.loads(generated_text)

            # Enforce MLUE 1.6 root version
            if "mlue_version" not in parsed_scene:
                parsed_scene["mlue_version"] = parsed_scene.pop("version", "1.6")

            # Static MLUE Schema & Invariant Validation Gate
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

        except urllib.error.HTTPError as he:
            error_body = he.read().decode('utf-8', errors='ignore')
            self._send_json_error(500, f"Gemini API Error ({he.code}): {error_body}")
        except MLUEValidationError as ve:
            self._send_json_error(500, f"MLUE Architectural Invariant Violation: {ve}")
        except Exception as ex:
            self._send_json_error(500, f"Generation Error: {ex}")

    def _send_json_error(self, code, message):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        err = {'success': False, 'error': message}
        self.wfile.write(json.dumps(err).encode('utf-8'))
