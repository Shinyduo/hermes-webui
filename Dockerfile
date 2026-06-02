# syntax=docker/dockerfile:1
#
# Hermes WebUI — browser interface for Hermes Agent.
#
# The upstream image already binds 0.0.0.0 and runs a root->user init
# (docker_init.bash) under s6-style setup, so we keep its ENTRYPOINT/CMD and
# only configure it via env vars. Railway injects PORT=8080 and routes the
# public domain there, so the template sets HERMES_WEBUI_PORT=8080 to match.
FROM ghcr.io/nesquena/hermes-webui:latest

# Railway's runtime injects environment variables whose values can contain
# newlines. The upstream init preserves env across its root->user privilege
# drop by serializing `env | sort` to a file and re-importing each line as
# `export "$key=$value"`. A newline in a value yields a line with an empty key,
# so the re-import runs `export "="`, which fails with "invalid variable name"
# and, under `set -e`, kills the init -> the container restart-loops forever.
# Guard the re-import so only valid shell identifiers are exported.
USER root
RUN python3 <<'PYEOF'
p = "/hermeswebui_init.bash"
s = open(p).read()
old = '        export "$key=$value"'
new = '        if [[ "$key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then export "$key=$value"; fi'
assert s.count(old) == 1, f"expected exactly one match, found {s.count(old)}"
open(p, "w").write(s.replace(old, new))
PYEOF
