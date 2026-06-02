#!/usr/bin/env python3
"""Patch the upstream Hermes WebUI container init for Railway.

Railway's runtime injects environment variables whose values can contain
newlines. The upstream init (`/hermeswebui_init.bash`) preserves the
environment across its root->user privilege drop by serializing `env | sort`
to a file and re-importing every line as `export "$key=$value"`. A newline in
a value produces a line with an empty key, so the re-import runs `export "="`,
which fails with "invalid variable name" and, under `set -e`, kills the init.
The container then restart-loops forever and never serves.

This guards the re-import so only valid POSIX shell identifiers are exported.
The build fails loudly if the expected line is not found, so a silently
broken patch can never ship.
"""
import sys

PATH = "/hermeswebui_init.bash"
OLD = '        export "$key=$value"'
NEW = '        if [[ "$key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then export "$key=$value"; fi'

src = open(PATH, encoding="utf-8").read()
count = src.count(OLD)
if count != 1:
    sys.exit(f"PATCH FAILED: expected exactly 1 match for target line, found {count}")

open(PATH, "w", encoding="utf-8").write(src.replace(OLD, NEW))

if NEW not in open(PATH, encoding="utf-8").read():
    sys.exit("PATCH FAILED: replacement not present after write")

print("init env-reimport patch applied OK")
