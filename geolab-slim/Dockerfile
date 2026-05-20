# syntax=docker/dockerfile:1
# ──────────────────────────────────────────────────────────────
# geolab-slim — built on pangeo/base-image.
#
# Files picked up automatically by the parent's ONBUILD machinery:
#   environment.yml  → conda env "notebook" installed from this
#   conda-lock.yml   → (optional, preferred) no-solve install
#   start            → entrypoint script (becomes /srv/start)
#
# Build:
#   docker build --platform linux/amd64 -t geolab-slim .
# ──────────────────────────────────────────────────────────────
FROM pangeo/base-image:latest

LABEL org.opencontainers.image.title="geolab-slim" \
      org.opencontainers.image.authors="sophia.parafina@earthscope.org"

# Default command for standalone use. JupyterHub spawning passes
# its own command (jupyterhub-singleuser), which start respects.
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--no-browser"]
