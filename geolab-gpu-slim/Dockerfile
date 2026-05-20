# =============================================================================
# EarthScope ML/GPU JupyterHub Image
# =============================================================================
#
# Base: pangeo/ml-notebook (Ubuntu + CUDA 12 + cuDNN + PyTorch + JAX +
#       TensorFlow + Dask + full pangeo scientific stack)
#
# ONBUILD sequence (fires automatically during `docker build`):
#   1. COPY entire build context → /home/jovyan   (as jovyan:jovyan)
#   2. conda env update -f /home/jovyan/environment.yml
#   3. bash /home/jovyan/postBuild              (if the file exists)
#
# After ONBUILD, the explicit steps below run in order:
#   4. apt-get install from apt.txt
#   5. conda remove unwanted base packages
#   6. Install start.sh as the container entrypoint wrapper
#
# Build:
#   docker build \
#     --build-arg BASE_TAG=2025.04.19 \
#     --platform linux/amd64 \
#     -t ghcr.io/earthscope/ml-notebook:2025.04.19 .
#
# Local GPU test:
#   docker run --gpus all --rm -p 8888:8888 \
#     ghcr.io/earthscope/ml-notebook:2025.04.19 \
#     /usr/local/bin/start.sh jupyter lab --ip=0.0.0.0
# =============================================================================

ARG BASE_TAG=2025.04.19
FROM pangeo/ml-notebook:${BASE_TAG}

LABEL org.opencontainers.image.title="EarthScope ML/GPU Notebook"
LABEL org.opencontainers.image.description="Pangeo ml-notebook + EarthScope seismic/GNSS ML stack (CUDA 12)"
LABEL org.opencontainers.image.source="https://github.com/spara-earthscope"
LABEL org.opencontainers.image.vendor="EarthScope Consortium"

# =============================================================================
# Step 4 — System packages
# =============================================================================
# ONBUILD already ran `conda env update` and copied all build-context files to
# /home/jovyan, so apt.txt is available at /home/${NB_USER}/apt.txt.
# Switch to root for system-level installs.
USER root

RUN apt-get update --yes \
    && xargs -a /home/${NB_USER}/apt.txt \
        apt-get install --yes --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# Step 5 — Remove unwanted packages from the pangeo/ml-notebook base
# =============================================================================
# --force bypasses the dependency solver; the packages below were deliberately
# chosen because their removal does not break any package in this image.
#
# ⚠  fsspec WARNING: fsspec is a transitive dependency of dask, distributed,
#    s3fs, gcsfs, zarr, intake, and others. It is removed here because the
#    packages that depend on it (s3fs, gcsfs, zarr …) are also being removed.
#    If you re-add any dask-based cloud I/O later, omit fsspec from this list.
USER ${NB_USER}

RUN conda remove -n ${CONDA_ENV} --force --yes \
        s3fs gcsfs obstore adlfs fsspec \
        zarr icechunk kerchunk \
        h3 lonboard \
    && conda clean -afy

# =============================================================================
# Step 6 — Startup script
# =============================================================================
# start.sh was copied to /home/jovyan by the ONBUILD COPY step.
# Move it to a system path so JupyterHub's spawner can reference it cleanly,
# and make it the default CMD (JupyterHub always overrides CMD with its own
# command, which start.sh receives as "$@" and exec's).
USER root

RUN mv /home/${NB_USER}/start.sh /usr/local/bin/start.sh \
    && chmod +x /usr/local/bin/start.sh

USER ${NB_USER}

CMD ["/usr/local/bin/start.sh"]
