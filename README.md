# Hermes WebUI (Railway)

One-click [Railway](https://railway.app) template for **[Hermes WebUI](https://github.com/nesquena/hermes-webui)** — a self-hosted browser interface for [Hermes Agent](https://hermes-agent.nousresearch.com) with streaming chat, persistent memory, a workspace file browser, session management, scheduling, and optional password/passkey auth.

This template deploys **two services**:

1. **hermes-gateway** — Hermes Agent running `gateway run`, exposing its OpenAI-compatible API server on private port `8642`. Holds your LLM API key and persistent state.
2. **hermes-webui** — the browser UI (public), wired to the gateway over Railway private networking via `HERMES_WEBUI_CHAT_BACKEND=gateway`.

## How to use

1. Click **Deploy on Railway**.
2. Add your LLM provider key on the gateway service (`ANTHROPIC_API_KEY` or `OPENAI_API_KEY`).
3. (Recommended) Set `HERMES_WEBUI_PASSWORD` on the WebUI service to protect the public URL.
4. Open the WebUI's public domain and start chatting.

## Key variables (WebUI service)

| Variable | Value | Notes |
| --- | --- | --- |
| `HERMES_WEBUI_HOST` | `0.0.0.0` | Bind all interfaces |
| `HERMES_WEBUI_PORT` | `8080` | Matches Railway's injected `PORT` |
| `HERMES_WEBUI_CHAT_BACKEND` | `gateway` | Route chat through the gateway API server |
| `HERMES_WEBUI_GATEWAY_BASE_URL` | `http://${{hermes-gateway.RAILWAY_PRIVATE_DOMAIN}}:8642` | Private gateway address |
| `HERMES_WEBUI_GATEWAY_API_KEY` | `${{hermes-gateway.API_SERVER_KEY}}` | Must match the gateway's `API_SERVER_KEY` |
| `HERMES_WEBUI_PASSWORD` | _your password_ | Optional but recommended for public access |

Attach a volume at `/home/hermeswebui/.hermes` to persist WebUI sessions and state.
