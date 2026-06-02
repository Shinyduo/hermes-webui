# Hermes WebUI — browser interface for Hermes Agent.
#
# The upstream image already binds 0.0.0.0 and runs a root->user init
# (docker_init.bash) under s6-style setup, so we keep its ENTRYPOINT/CMD and
# only configure it via env vars. Railway injects PORT=8080 and routes the
# public domain there, so the template sets HERMES_WEBUI_PORT=8080 to match.
#
# patch_init.py works around a restart loop the upstream init hits on Railway's
# env injection; see that file for the full explanation. The build aborts if
# the patch target is missing, so a broken patch can never ship.
FROM ghcr.io/nesquena/hermes-webui:latest

USER root
COPY patch_init.py /tmp/patch_init.py
RUN python3 /tmp/patch_init.py && rm -f /tmp/patch_init.py
