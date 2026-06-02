#!/usr/bin/env python3
"""Patch the upstream Hermes WebUI container init for Railway.

Railway's runtime injects environment variables whose values can contain
newlines. The upstream init (`/hermeswebui_init.bash`) preserves the
environment across its root->user privilege drop by serializing `env | sort`
to a file and re-importing it line by line:

    while IFS='=' read -r key value; do
      ...
      if [ -z "${!key}" ]; then        # <-- crashes here
      ...
      export "$key=$value"

A newline inside a value yields a line with an empty key. Bash indirect
expansion `${!key}` with an empty `key` fails with "invalid variable name",
and under `set -e` that kills the init, so the container restart-loops
forever and never serves.

Fix: skip any line whose key is not a valid POSIX shell identifier at the very
top of the loop, before any `${!key}` expansion or `export`. The build aborts
if the loop header is not found, so a silently broken patch can never ship.
"""
import re
import sys

PATH = "/hermeswebui_init.bash"
src = open(PATH, encoding="utf-8").read()

# Diagnostic: show the load_env region in the build log.
lines = src.splitlines()
print("----- /hermeswebui_init.bash lines 142-182 -----")
for i in range(141, min(182, len(lines))):
    print(f"{i+1:>4}: {lines[i]!r}")
print("------------------------------------------------")

# Insert an identifier guard right after the `while IFS='=' read -r key value; do`
# loop header. \g<0> re-emits the matched header line; the guard follows it.
header = re.compile(r"^(?P<indent>[ \t]*)while IFS='=' read -r key value; do$", re.MULTILINE)
guard = (
    r'\g<0>\n\g<indent>  [[ "$key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]] '
    r'|| continue  # railway: skip malformed (empty) keys'
)
new_src, n = header.subn(guard, src)
print(f"guarded {n} env-reimport loop(s)")

if n != 1:
    sys.exit(f"PATCH FAILED: expected exactly 1 `while IFS='=' read` header, found {n}")

open(PATH, "w", encoding="utf-8").write(new_src)
print("init env-reimport patch applied OK")
