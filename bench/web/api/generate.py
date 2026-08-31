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

SYSTEM_PROMPT = """You are the MLUE Core AI Generator. You compile natural language game and interactive simulation ideas into valid, declarative .mlue JSON documents.

### MLUE SCHEMA RULES:
1. Output strictly valid raw JSON. Do not include markdown codeblocks or conversational filler.
2. "mlue_version": "1.6"
3. "environment": { "dimensions": [800, 600], "background": "#020617" }
4. "state_variables": { "game": { "score": 0, "lives": 3, "state": "PLAYING" } }
5. "entities": Array of objects.
   - All positions are normalized in range [0.0, 1.0].
   - "circle": size: { "radius": float } (e.g., 0.025 to 0.08)
   - "box": size: { "width": float, "height": float } (e.g., width: 0.16, height: 0.03)
   - "velocity": { "vx": float, "vy": float } (speeds typically 0.2 to 0.5)
   - "properties":
       - "solid": true (for physics collisions)
       - "color": "#hexcode" (vibrant cyberpunk/neon colors: #38BDF8, #10B981, #F43F5E, #F59E0B, #A855F7, #EC4899)
       - "control": { "channel": "paddle", "axis": "x" } (or "y", or "p1"/"p2") for player-controlled entities.
6. "rules": Array of declarative rules.
   - event: "collision", entities: ["entity_a", "entity_b"]
   - actions:
       - { "type": "destroy_entity", "target": "entity_b" }
       - { "type": "increment_path", "target": "game.score", "amount": 100 }
       - { "type": "decrement_path", "target": "game.lives", "amount": 1 }

Make games fun, vibrant, responsive, and physically engaging with interactive controls and clear objectives!
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
            'model': 'gemini-1.5-flash',
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
            self._send_json_error(401, 'No Gemini API Key provided. Please provide a key or enter one in the studio settings.')
            return

        # Prepare prompt for Gemini
        full_user_content = f"User Request: {prompt}\n"
        if current_scene:
            full_user_content += f"\nExisting Scene to Modify:\n{json.dumps(current_scene, indent=2)}\n\nApply the requested changes and output the complete updated .mlue JSON document."

        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

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
                "temperature": 0.3,
                "topP": 0.95,
                "responseMimeType": "application/json"
            }
        }

        try:
            req = urllib.request.Request(
                gemini_url,
                data=json.dumps(gemini_body).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                resp_data = json.loads(resp.read().decode('utf-8'))

            # Extract generated text
            candidates = resp_data.get('candidates', [])
            if not candidates:
                self._send_json_error(502, 'Gemini returned no candidates.')
                return

            text_content = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            parsed_scene = json.loads(text_content)

            # In-memory validation
            validate_and_parse(parsed_scene)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            
            res_obj = {
                'success': True,
                'scene': parsed_scene,
                'prompt': prompt
            }
            self.wfile.write(json.dumps(res_obj, indent=2).encode('utf-8'))

        except urllib.error.HTTPError as http_err:
            err_msg = http_err.read().decode('utf-8', errors='ignore')
            self._send_json_error(http_err.code, f"Gemini API Error: {err_msg}")
        except MLUEValidationError as val_err:
            self._send_json_error(422, f"Generated scene failed MLUE invariant validation: {val_err}")
        except Exception as gen_err:
            self._send_json_error(500, f"Generation failed: {gen_err}")

    def _send_json_error(self, code: int, message: str):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({'success': False, 'error': message}, indent=2).encode('utf-8'))
