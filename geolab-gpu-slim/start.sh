#!/bin/bash
# =============================================================================
# EarthScope ML/GPU JupyterHub — container startup script
#
# Called as the container CMD; receives the JupyterHub-spawned command
# (e.g. jupyterhub-singleuser) as positional arguments and exec's it at
# the end so signals propagate correctly.
# =============================================================================
set -euo pipefail

# ── GPU environment ────────────────────────────────────────────────────────────
# Let CUDA see all GPUs unless the spawner has already pinned specific devices.
export NVIDIA_VISIBLE_DEVICES="${NVIDIA_VISIBLE_DEVICES:-all}"
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"

# Prevent TensorFlow from pre-allocating the entire GPU memory pool.
export TF_FORCE_GPU_ALLOW_GROWTH=true

# Match Polars thread count to available CPUs (avoids over-subscription on shared nodes).
export POLARS_MAX_THREADS="${POLARS_MAX_THREADS:-$(nproc)}"

# ── EarthScope SDK credentials ─────────────────────────────────────────────────
# Credentials are expected as env vars injected by the JupyterHub spawner
# (e.g. via KubeSpawner environment_vars or a Kubernetes secret).
#
#   c.KubeSpawner.environment = {
#       "EARTHSCOPE_USERNAME": "...",
#       "EARTHSCOPE_PASSWORD": "...",
#   }
#
if [[ -n "${EARTHSCOPE_USERNAME:-}" && -n "${EARTHSCOPE_PASSWORD:-}" ]]; then
    echo "[start.sh] Logging in to EarthScope SDK..."
    earthscope auth login \
        --username "${EARTHSCOPE_USERNAME}" \
        --password "${EARTHSCOPE_PASSWORD}" \
        --non-interactive 2>/dev/null \
        && echo "[start.sh] EarthScope SDK authenticated." \
        || echo "[start.sh] WARNING: EarthScope SDK login failed — continuing anyway."
fi

# ── Classic notebook extensions ────────────────────────────────────────────────
# Install once per user home; idempotent.
jupyter contrib nbextension install --user --sys-prefix 2>/dev/null || true

# ── Sanity check: GPU visibility ───────────────────────────────────────────────
python - <<'PYEOF'
import os, warnings
warnings.filterwarnings("ignore")
try:
    import torch
    n = torch.cuda.device_count()
    print(f"[start.sh] PyTorch sees {n} GPU(s)" + (f": {[torch.cuda.get_device_name(i) for i in range(n)]}" if n else " — CPU-only mode"))
except Exception as e:
    print(f"[start.sh] PyTorch GPU check skipped: {e}")
PYEOF

echo "[start.sh] EarthScope ML environment ready — handing off to: $*"

# Pass control to JupyterHub's singleuser server (or whatever the spawner sends).
exec "$@"
