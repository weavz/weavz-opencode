# OpenCode MCP setup for Weavz app integrations

<!-- weavz:discovery:start -->

Use Slack, Gmail, GitHub and Notion from OpenCode through the hosted Weavz Model Context Protocol (MCP) connector. Sign in with OAuth, select your workspace, and connect the apps you want the client to use. The hosted connector uses Code Mode MCP.

Apps become available after they are connected for the selected Weavz user and workspace:

- [Slack MCP app access](https://weavz.io/integrations/slack)
- [Gmail MCP app access](https://weavz.io/integrations/gmail)
- [GitHub MCP app access](https://weavz.io/integrations/github)
- [Notion MCP app access](https://weavz.io/integrations/notion)

Follow the client OAuth instructions below, then discover the available tools and aliases before asking the agent to act.

[MCP app and framework directory](https://github.com/weavz/mcp-examples/blob/main/docs/integrations.md) · [All examples](https://github.com/weavz/mcp-examples) · [Weavz MCP guide](https://weavz.io/docs/guides/agent-framework-examples)

<!-- weavz:discovery:end -->

Connect an AI coding client to the apps authorized in one Weavz workspace through remote MCP. This example keeps client MCP configuration separate from the model provider and from project instructions.

## Requirements

- OpenCode CLI or desktop with remote Streamable HTTP MCP support.
- A reachable Weavz platform endpoint and a Weavz account.
- A model/provider configured in your client. Weavz OAuth does not configure or pay for model access.

See the official [OpenCode MCP guide](https://opencode.ai/docs/mcp-servers) and [installation guide](https://opencode.ai/docs) for current version and command details.

## Setup

OpenCode reads project `opencode.json` / `opencode.jsonc` and project `AGENTS.md`. MCP configuration and model-provider configuration are independent. The checked-in `opencode.json` uses the V1 shape supported by OpenCode 1.17.6 and the current `opencode-ai` 1.x package. OpenCode V2 uses a different config shape, provided separately as `opencode.v2.json`. Check `opencode --version`; for V2, merge `mcp.servers.weavz` from that file into the project's config. Preserve existing settings and MCP entries.

OpenCode 1 and 2 are separate CLI distributions. The installed 1.17.6 CLI and current `opencode-ai` 1.x line use V1 behavior; current V2 docs/install use the `@opencode/cli` package and V2 config. Command defaults differ: the installed 1.17.6 `opencode mcp add` wrote user config, while current V2 docs say it writes project config by default and accepts `--global` for user config. Use the checked-in version-matched file when you need to guarantee project scope.

The project config for OpenCode 1.x is:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "weavz": {
      "type": "remote",
      "url": "https://platform.weavz.io/mcp/weavz",
      "enabled": true
    }
  }
}
```

For OpenCode V2, the server is under `mcp.servers.weavz` and does not need `enabled: true`; see [`opencode.v2.json`](opencode.v2.json).

```sh
# From this example directory; the project config is already present.
opencode mcp auth weavz
```

Complete the browser sign-in, select the intended workspace, and approve the connector. The OAuth flow stores credentials in the client's own credential store. Do not add an `Authorization` header or paste a Weavz access token for the hosted personal connector.

For self-hosted Weavz, replace `https://platform.weavz.io/mcp/weavz` with `https://<your-public-weavz-host>/mcp/weavz`. The server must be reachable over HTTPS from the client.

## Verify

```sh
opencode run --model deepseek/<model-id> --format json "Use a Weavz read/search tool to confirm access. Do not write, connect, add, remove, or modify anything."
```

The one-shot prompt is the model-mediated check: count it as passed only if the transcript shows a Weavz tool call and result. Review tool arguments and output. Do not infer live auth or a successful app action from configuration files alone.

## Project instructions

This repo includes `AGENTS.md` guidance. It does not install or configure MCP. See the client-native instruction file for rules loaded into the agent.

## Local checks

Run the dependency-free static contract checks:

```sh
python3 -m unittest discover -s tests -v
```

The Python checks validate both config shapes and the instruction/setup contract without network calls. `scripts/test-native.sh` uses the installed OpenCode CLI with a local synthetic MCP fixture and temporary XDG state. It selects the version-matched config, checks tool discovery, and captures CLI-generated config without a model/provider call. It exits 77 if the CLI is absent.

## Credentials and safety

- Keep OAuth in the client credential store. No Weavz API key, MCP access token, connected-app secret, or model key belongs in this repo.
- The endpoint scopes the connector to the workspace selected during Weavz sign-in. To change workspaces, disconnect and reauthorize.
- Tool availability follows that workspace's configuration and permissions. This example does not promise MCP App UI support.
- Before writing, sending, publishing, deleting, or changing external data, inspect the proposed action and obtain user approval.

## License

MIT. See [LICENSE](LICENSE).
