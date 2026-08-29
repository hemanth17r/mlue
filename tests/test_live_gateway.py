"""Live Remote MCP Gateway Production Contract Smoke Test"""
import json
import unittest
import urllib.request
import urllib.error

ENDPOINT = "https://mlue-bench.vercel.app/api/mcp"

class TestLiveRemoteMCPGateway(unittest.TestCase):

    def _post(self, payload):
        req = urllib.request.Request(
            ENDPOINT,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def test_01_get_health(self):
        req = urllib.request.Request(ENDPOINT)
        with urllib.request.urlopen(req, timeout=10) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data["status"], "healthy")
            self.assertEqual(data["version"], "0.7.0")

    def test_02_initialize(self):
        res = self._post({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
        self.assertEqual(res["result"]["serverInfo"]["name"], "mlue-remote-mcp-gateway")
        self.assertEqual(res["result"]["serverInfo"]["version"], "0.7.0")

    def test_03_tools_list(self):
        res = self._post({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        tool_names = [t["name"] for t in res["result"]["tools"]]
        self.assertIn("mlue_get_schema", tool_names)
        self.assertIn("mlue_validate_scene", tool_names)
        self.assertIn("mlue_simulate_scene", tool_names)

    def test_04_schema_version_07(self):
        res = self._post({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "mlue_get_schema", "arguments": {}}
        })
        schema = json.loads(res["result"]["content"][0]["text"])
        self.assertEqual(schema["mlue_version"], "0.7")

    def test_05_simulate_normal(self):
        scene = {
            "mlue_version": "0.7",
            "environment": {"dimensions": [400, 400], "background": "#000000"},
            "entities": [
                {"id": "b", "type": "circle", "position": {"x": 0.5, "y": 0.5}, "size": {"radius": 0.05}, "velocity": {"vx": 0.1, "vy": 0.0}}
            ]
        }
        res = self._post({
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "mlue_simulate_scene", "arguments": {"scene": scene, "ticks": 10}}
        })
        data = json.loads(res["result"]["content"][0]["text"])
        self.assertEqual(data["simulation_ticks"], 10)
        self.assertFalse(data["clamped"])
        self.assertAlmostEqual(data["entities"][0]["position"]["x"], 0.516667, places=5)

    def test_06_ticks_clamping_transparency(self):
        scene = {
            "mlue_version": "0.7",
            "environment": {"dimensions": [400, 400], "background": "#000000"},
            "entities": [
                {"id": "b", "type": "circle", "position": {"x": 0.5, "y": 0.5}, "size": {"radius": 0.05}}
            ]
        }
        res = self._post({
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"name": "mlue_simulate_scene", "arguments": {"scene": scene, "ticks": 501}}
        })
        data = json.loads(res["result"]["content"][0]["text"])
        self.assertEqual(data["simulation_ticks"], 500)
        self.assertEqual(data["requested_ticks"], 501)
        self.assertEqual(data["applied_ticks"], 500)
        self.assertTrue(data["clamped"])
        self.assertEqual(data["min_ticks_limit"], 1)
        self.assertEqual(data["max_ticks_limit"], 500)
        self.assertIn("warning", data)

    def test_07_ticks_zero_rejected(self):
        scene = {"mlue_version": "0.7", "entities": []}
        res = self._post({
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {"name": "mlue_simulate_scene", "arguments": {"scene": scene, "ticks": 0}}
        })
        self.assertIn("error", res)
        self.assertEqual(res["error"]["code"], -32602)
        self.assertIn("must be >= 1", res["error"]["message"])

    def test_08_unexpected_argument_rejected(self):
        scene = {"mlue_version": "0.7", "entities": []}
        res = self._post({
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {"name": "mlue_simulate_scene", "arguments": {"scene": scene, "unexpected_arg": True}}
        })
        self.assertIn("error", res)
        self.assertEqual(res["error"]["code"], -32602)
        self.assertIn("Unexpected argument 'unexpected_arg'", res["error"]["message"])

if __name__ == "__main__":
    unittest.main()
