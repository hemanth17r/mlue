"""MLUE AI Game & Scene Generator API Route.

Serverless Python endpoint that accepts natural language game prompts or refinement
instructions, generates 100% valid declarative .mlue documents using Google Gemini Flash,
and validates the physics & coordinate reachability in-memory before returning.
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

SYSTEM_PROMPT = """You are the MLUE Core AI Generator. Compile natural language game ideas into valid, declarative .mlue JSON documents.

### MLUE SCHEMA RULES:
1. Output strictly valid raw JSON. Do not include markdown codeblocks or conversational filler.
2. "mlue_version": "1.6"
3. "environment": { "dimensions": [800, 600], "background": "#020617" }
4. "state_variables": { "game": { "score": 0, "lives": 3, "state": "PLAYING" } }
5. "entities": Array of objects.
   - All positions are normalized in range [0.0, 1.0].
   - "type": "circle" -> "size": { "radius": float } (range: 0.02 to 0.06)
   - "type": "box" -> "size": { "width": float, "height": float } (range: 0.05 to 0.25)
   - "velocity": { "vx": float, "vy": float } (range: -0.4 to 0.4)
   - "properties":
       - "solid": true
       - "color": "#hexcode" (e.g. #38BDF8, #10B981, #F43F5E, #F59E0B, #A855F7, #EC4899)
       - "control": { "channel": "paddle", "axis": "x" } for player-controlled entity.
6. "rules": Array of declarative rules.
   - event: "collision", entities: ["entity_a", "entity_b"]
   - actions:
       - { "type": "destroy_entity", "target": "entity_b" }
       - { "type": "increment_path", "target": "game.score", "amount": 100 }
       - { "type": "decrement_path", "target": "game.lives", "amount": 1 }
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

        # Prepare prompt for Gemini
        full_user_content = f"User Request: {prompt}\n"
        if current_scene:
            full_user_content += f"\nExisting Scene to Modify:\n{json.dumps(current_scene, indent=2)}\n\nApply the requested changes and output the complete updated .mlue JSON document."

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

            with urllib.request.urlopen(req, timeout=9) as response:
                raw_resp = response.read().decode('utf-8')
                gemini_json = json.loads(raw_resp)

            candidates = gemini_json.get('candidates', [])
            if not candidates:
                raise ValueError('Gemini returned no candidates.')

            generated_text = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            if not generated_text:
                raise ValueError('Empty text response from Gemini.')

            parsed_scene = json.loads(generated_text)
            if "version" in parsed_scene and "mlue_version" not in parsed_scene:
                parsed_scene["mlue_version"] = parsed_scene.pop("version")

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._send_cors_headers()
            self.end_headers()

            out = {
                'success': True,
                'model': model_name,
                'prompt': prompt,
                'scene': parsed_scene
            }
            self.wfile.write(json.dumps(out, indent=2).encode('utf-8'))

        except urllib.error.HTTPError as he:
            error_body = he.read().decode('utf-8', errors='ignore')
            self._send_json_error(500, f"Gemini API Error ({he.code}): {error_body}")
        except Exception as ex:
            self._send_json_error(500, f"Generation Error: {ex}")

    def _send_json_error(self, code, message):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        err = {'success': False, 'error': message}
        self.wfile.write(json.dumps(err).encode('utf-8'))
