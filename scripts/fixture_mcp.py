#!/usr/bin/env python3
"""Small local Streamable HTTP MCP fixture for config discovery tests only."""
import argparse, json
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    calls_file = None
    def log_message(self, *_args): pass
    def _send(self, status, payload=None):
        body = b"" if payload is None else json.dumps(payload).encode()
        self.send_response(status)
        if payload is not None:
            self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body: self.wfile.write(body)
    def do_POST(self):
        if self.path != "/mcp": return self._send(404)
        msg = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
        method = msg.get("method")
        if self.calls_file:
            with open(self.calls_file, "a") as calls:
                calls.write(str(method) + "\n")
        if method == "notifications/initialized": return self._send(202)
        if method == "initialize":
            return self._send(200, {"jsonrpc":"2.0","id":msg.get("id"),"result":{"protocolVersion":"2025-11-25","capabilities":{"tools":{}},"serverInfo":{"name":"weavz-example-fixture","version":"1.0.0"}}})
        if method == "tools/list":
            return self._send(200, {"jsonrpc":"2.0","id":msg.get("id"),"result":{"tools":[{"name":"fixture_read_only","description":"Synthetic local read-only smoke tool; no external service access.","inputSchema":{"type":"object","properties":{},"additionalProperties":False},"annotations":{"readOnlyHint":True}}]}})
        if method == "tools/call":
            if msg.get("params", {}).get("name") != "fixture_read_only":
                return self._send(200, {"jsonrpc":"2.0","id":msg.get("id"),"error":{"code":-32602,"message":"Unknown fixture tool"}})
            record = {"id":"fixture-record-1","title":"Synthetic OpenCode MCP record","status":"ready"}
            return self._send(200, {"jsonrpc":"2.0","id":msg.get("id"),"result":{"content":[{"type":"text","text":json.dumps(record)}],"isError":False}})
        if method == "ping": return self._send(200,{"jsonrpc":"2.0","id":msg.get("id"),"result":{}})
        if "id" in msg: return self._send(200,{"jsonrpc":"2.0","id":msg["id"],"error":{"code":-32601,"message":"Method not found"}})
        return self._send(202)

def main():
    p=argparse.ArgumentParser(); p.add_argument("--port-file", required=True); p.add_argument("--calls-file"); a=p.parse_args()
    server=HTTPServer(("127.0.0.1",0),Handler)
    Handler.calls_file=a.calls_file
    with open(a.port_file,"w") as f: f.write(str(server.server_port))
    server.serve_forever()
if __name__ == "__main__": main()
