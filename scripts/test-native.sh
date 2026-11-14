#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
if ! command -v opencode >/dev/null 2>&1; then echo "SKIP: opencode CLI is not installed"; exit 77; fi
tmp="$(mktemp -d)"
server_pid=""
cleanup() { if [[ -n "$server_pid" ]]; then kill "$server_pid" 2>/dev/null || true; wait "$server_pid" 2>/dev/null || true; fi; rm -rf "$tmp"; }
trap cleanup EXIT INT TERM
mkdir -p "$tmp/project" "$tmp/xdg"
version="$(opencode --version | head -n 1)"
if [[ "$version" =~ ^1\. ]]; then
  config="$root/opencode.json"
elif [[ "$version" =~ ^2\. ]]; then
  config="$root/opencode.v2.json"
else
  echo "Unsupported OpenCode version output: $version" >&2
  exit 1
fi
python3 "$root/scripts/fixture_mcp.py" --port-file "$tmp/port" --calls-file "$tmp/calls" &
server_pid=$!
for _ in $(seq 1 100); do [[ -s "$tmp/port" ]] && break; sleep 0.05; done
[[ -s "$tmp/port" ]] || { echo "fixture did not start" >&2; exit 1; }
python3 - "$config" "$tmp/project/opencode.json" "$(cat "$tmp/port")" <<'PY'
import json, sys
src,dest,port=sys.argv[1:]
cfg=json.load(open(src))
servers=cfg["mcp"].get("servers",cfg["mcp"])
fixture=servers.pop("weavz")
fixture.update({"url":f"http://127.0.0.1:{port}/mcp","oauth":False})
if "servers" in cfg["mcp"]:
    cfg["mcp"]["servers"]={"fixture":fixture}
else:
    cfg["mcp"]={"fixture":fixture}
json.dump(cfg,open(dest,"w"))
PY
out="$(cd "$tmp/project" && XDG_CONFIG_HOME="$tmp/xdg" opencode mcp list 2>&1)" || { printf '%s\n' "$out"; exit 1; }
printf '%s\n' "$out"
grep -q 'fixture' <<<"$out"
for _ in $(seq 1 100); do grep -q '^tools/list$' "$tmp/calls" 2>/dev/null && break; sleep 0.05; done
grep -q '^tools/list$' "$tmp/calls" || { echo "OpenCode connected but did not request the fixture tool catalog" >&2; exit 1; }

# Keep generated config under temporary XDG state; never touch the user's configuration.
add_out="$(cd "$tmp/project" && XDG_CONFIG_HOME="$tmp/xdg" opencode mcp add generated-fixture --url "http://127.0.0.1:$(cat "$tmp/port")/mcp" 2>&1)" || { printf '%s\n' "$add_out"; exit 1; }
printf '%s\n' "$add_out"
python3 - "$tmp/project" "$tmp/xdg/opencode" <<'PY'
import json, pathlib, sys
roots=[pathlib.Path(value) for value in sys.argv[1:]]
paths=[root/name for root in roots for name in ("opencode.json", "opencode.jsonc") if (root/name).exists()]
assert paths, "OpenCode CLI did not write a project or isolated XDG config"
loaded=[(path,json.loads(path.read_text())) for path in paths]
match=next(((path,cfg) for path,cfg in loaded if "generated-fixture" in cfg["mcp"].get("servers",cfg["mcp"])),None)
assert match is not None, "generated server missing from project and isolated XDG configs"
path,cfg=match
servers=cfg["mcp"].get("servers",cfg["mcp"])
server=servers["generated-fixture"]
print("Generated native config:", path, json.dumps(cfg.get("mcp"), sort_keys=True))
assert server["type"] == "remote" and server["url"].endswith("/mcp")
PY
echo "PASS: OpenCode $version loaded its version-matched project config and generated its CLI config inside temporary XDG state; fixture discovery used no model/provider."
