# Hermes WebUI — browser interface for Hermes Agent.
#
# The upstream image already binds 0.0.0.0 and runs a root->user init
# (docker_init.bash) under s6-style setup, so we keep its ENTRYPOINT/CMD.
# We only re-tag it here so Railway can build from this repo. Runtime
# configuration (port, gateway backend, auth) is supplied via env vars.
#
# Railway injects PORT=8080 and routes the public domain there, so the
# template sets HERMES_WEBUI_PORT=8080 to match.
FROM ghcr.io/nesquena/hermes-webui:latest
