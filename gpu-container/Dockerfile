# syntax=docker/dockerfile:1
# ──────────────────────────────────────────────────────────────
# gpu-container -- geolab-base plus a baked-in NVIDIA driver and
# seisbench (deep-learning seismic phase picking, via PyTorch).
#
# ** NVIDIA_DRIVER_VERSION below is load-bearing, read this **
# A container shares the host's kernel -- it never has one of its
# own -- so only the *userspace* half of an NVIDIA driver can live
# in an image; the kernel module is whatever the host already has
# loaded, and a `docker build` sandbox has no running kernel to
# build or load a module against. That means:
#   - NVIDIA_DRIVER_VERSION must exactly match the driver already
#     running on the target GPU host. A mismatch fails at container
#     *runtime* (e.g. "CUDA driver version is insufficient for CUDA
#     runtime version", or an nvidia-smi version-mismatch error),
#     not at build time, so there's nothing here to catch it early.
#   - Only nvidia-utils-* and libnvidia-compute-* are installed --
#     not the nvidia-driver-* meta-package, which pulls in DKMS and
#     tries (and fails) to build a kernel module during the build.
#   - At `docker run`, the GPU device nodes still need to be handed
#     to the container: `docker run --gpus all ...` (needs
#     nvidia-container-toolkit on the host) or explicit `--device
#     /dev/nvidia0 --device /dev/nvidiactl --device /dev/nvidia-uvm`.
#   - Rebuild this image with an updated NVIDIA_DRIVER_VERSION any
#     time the host driver is upgraded.
# If the target host isn't fixed/known ahead of time, prefer
# geolab-gpu instead: it installs CUDA-build conda packages and
# lets nvidia-container-toolkit mount whatever driver the host has
# at container start, so it isn't tied to one exact driver version.
#
# Files picked up automatically by the parent's ONBUILD machinery:
#   environment.yml  → conda env "notebook" installed from this
#   conda-lock.yml   → (optional, preferred) no-solve install
#   requirements.txt → pip packages installed into that env
#   apt.txt          → apt packages installed via apt-get
#   start            → entrypoint script (becomes /srv/start)
#
# Build:
#   docker build --platform linux/amd64 \
#   --build-arg IMAGE_TITLE=my-geolab-gpu-container \
#   --build-arg IMAGE_AUTHORS=you@university.edu \
#   --build-arg GEOLAB_VERSION=1.0.0 \
#   --build-arg NVIDIA_DRIVER_VERSION=550 \
#   -t my-geolab-gpu-container .
# ──────────────────────────────────────────────────────────────
# Changing this tag is a major (breaking) change under semantic versioning.
FROM pangeo/base-image:04bb14b


ARG IMAGE_TITLE="custom-geolab-gpu-container"  # default if user passes nothing
ARG IMAGE_AUTHORS="NoSpecifiedAuthors"         # default if user passes nothing
ARG GEOLAB_VERSION="1.0.0"                     # default if user passes nothing

LABEL org.opencontainers.image.title="${IMAGE_TITLE}" \
      org.opencontainers.image.authors="${IMAGE_AUTHORS}" \
      org.opencontainers.image.version="${GEOLAB_VERSION}"

      # Set locations of PROJ/GDAL resource directories
ENV PROJ_DATA=/srv/conda/envs/notebook/share/proj \
    PROJ_LIB=/srv/conda/envs/notebook/share/proj \
    GDAL_DATA=/srv/conda/envs/notebook/share/gdal \
    GEOLAB_VERSION=${GEOLAB_VERSION}

# Must exactly match the driver already loaded on the target GPU
# host -- see the note at the top of this file. Override at build
# time with --build-arg NVIDIA_DRIVER_VERSION=<version> if it differs.
ARG NVIDIA_DRIVER_VERSION=550

USER root

# Userspace-only NVIDIA driver install: nvidia-utils-* provides
# nvidia-smi and the CUDA driver API shim; libnvidia-compute-*
# provides libcuda.so.1. Neither pulls in nvidia-driver-*/DKMS,
# which would try (and fail) to build a kernel module here.
RUN echo "Installing NVIDIA userspace driver ${NVIDIA_DRIVER_VERSION}..." \
    && apt-get update --fix-missing > /dev/null \
    && apt-get install -y --no-install-recommends \
        "nvidia-utils-${NVIDIA_DRIVER_VERSION}" \
        "libnvidia-compute-${NVIDIA_DRIVER_VERSION}" \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && ldconfig

USER ${NB_USER}

# Default command for standalone use. JupyterHub spawning passes
# its own command (jupyterhub-singleuser), which start respects.
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--no-browser"]
