#!/usr/bin/env python3
"""Patch the upstream Hermes WebUI container init for Railway.

Railway's runtime injects environment variables whose values can contain
newlines. The upstream init (`/hermeswebui_init.bash`) preserves the
environment across its root->user privilege drop by serializing `env | sort`
to a file and re-importing every line as a dynamic `export`. A newline in a
value produces a line with an empty key, so the re-import runs `export "="`,
which fails with "invalid variable name" and, under `set -e`, kills the init.
The container then restart-loops forever and never serves.

The shipped image can differ from the repo `main` branch, so we patch by
regex (every dynamic `export "$key=..."` inside load_env gets an identifier
guard) rather than by an exact-string match, and print the relevant region to
the build log for visibility.
"""
import re
import sys

PATH = "/hermeswebui_init.bash"
src = open(PATH, encoding="utf-8").read()
lines = src.splitlines()

# Diagnostic: show the load_env region so the build log reveals the real file.
print("----- /hermeswebui_init.bash lines 150-185 -----")
for i in range(149, min(185, len(lines))):
    print(f"{i+1:>4}: {lines[i]!r}")
print("------------------------------------------------")

# Guard every dynamic `export "$key=$value"` (any leading whitespace) so only
# valid POSIX identifiers are exported; an empty/invalid key is skipped.
pattern = re.compile(r'^(?P<indent>[ \t]*)export "\$key=\$value"[ \t]*$', re.MULTILINE)
guard = (
    r'\g<indent>if [[ "$key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then '
    r'export "$key=$value"; fi'
)
new_src, n = pattern.subn(guard, src)
print(f"guarded {n} dynamic export line(s)")

if n == 0:
    sys.exit("PATCH FAILED: no `export \"$key=$value\"` line found to guard")

open(PATH, "w", encoding="utf-8").write(new_src)
print("init env-reimport patch applied OK")
