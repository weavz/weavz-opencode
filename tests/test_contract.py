import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class OpenCodeContract(unittest.TestCase):
    def test_v1_remote_mcp_shape_and_oauth_default(self):
        cfg = json.loads((ROOT / "opencode.json").read_text())
        server = cfg["mcp"]["weavz"]
        self.assertEqual(cfg["$schema"], "https://opencode.ai/config.json")
        self.assertEqual(server["type"], "remote")
        self.assertEqual(server["url"], "https://platform.weavz.io/mcp/weavz")
        self.assertTrue(server["enabled"])
        self.assertNotIn("oauth", server)
        self.assertNotIn("headers", server)

    def test_v2_remote_mcp_shape(self):
        cfg = json.loads((ROOT / "opencode.v2.json").read_text())
        server = cfg["mcp"]["servers"]["weavz"]
        self.assertEqual(server["type"], "remote")
        self.assertEqual(server["url"], "https://platform.weavz.io/mcp/weavz")
        self.assertNotIn("enabled", server)

    def test_instructions_separate_from_mcp_and_no_credentials(self):
        text = (ROOT / "AGENTS.md").read_text()
        self.assertIn("Do not commit credentials", text)
        self.assertIn("wait for my approval", text)
        self.assertNotIn("wvz_", text)
        self.assertNotIn("mcp_", text)

if __name__ == "__main__":
    unittest.main()
