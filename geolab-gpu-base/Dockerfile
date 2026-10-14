# syntax=docker/dockerfile:1
# ──────────────────────────────────────────────────────────────
# Custom geolab-gpu-base -- built on pangeo/base-image
#
# GPU-enabled flavor of geolab-base: identical package set
# (environment.yml, requirements.txt, and apt.txt are unchanged,
# byte-for-byte), plus an NVIDIA driver baked into the image at
# build time (see the note below). No GPU-specific Python packages
# (PyTorch, CuPy, etc.) are added here -- for those, see geolab-gpu
# (adds a pinned CUDA-build PyTorch and seisbench) or geolab-gpu2
# (geolab-gpu plus a seismic phase-association/location toolkit).
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
#   - Ubuntu's own apt archive (used here, no separate NVIDIA repo
#     is added) only ships specific driver branches -- at the time
#     of writing that's 470, 550, 570, 575, 580, 590, and 610 -- so
#     the NVIDIA_DRIVER_VERSION=580 default below is just the
#     newest stable branch, not tied to any pinned CUDA/PyTorch
#     build the way geolab-gpu's driver version choice is (there's
#     no CUDA package installed here to pin against). Run
#     `apt-cache search nvidia-utils` inside the base image to see
#     what's currently offered, and pick whichever branch matches
#     your actual host.
#   - If you add a GPU-accelerated package later (PyTorch, CuPy,
#     etc.), pin it to a CUDA build whose minimum driver version is
#     <= NVIDIA_DRIVER_VERSION below -- see geolab-gpu's Dockerfile
#     and requirements.txt for a worked example with torch+cu126.
#   - At `docker run`, the GPU device nodes still need to be handed
#     to the container: `docker run --gpus all ...` (needs
#     nvidia-container-toolkit on the host) or explicit `--device
#     /dev/nvidia0 --device /dev/nvidiactl --device /dev/nvidia-uvm`.
#   - Rebuild this image with an updated NVIDIA_DRIVER_VERSION any
#     time the host driver changes.
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
#   --build-arg IMAGE_TITLE=my-geolab-gpu-base-image \
#   --build-arg IMAGE_AUTHORS=you@university.edu \
#   --build-arg GEOLAB_VERSION=1.0.0 \
#   --build-arg NVIDIA_DRIVER_VERSION=580 \
#   -t my-geolab-gpu-base-image .
# ──────────────────────────────────────────────────────────────
# Changing this tag is a major (breaking) change under semantic versioning.
FROM pangeo/base-image:04bb14b


ARG IMAGE_TITLE="custom-geolab-gpu-base-image"  # default if user passes nothing
ARG IMAGE_AUTHORS="NoSpecifiedAuthors"          # default if user passes nothing
ARG GEOLAB_VERSION                              # no default; must be passed with --build-arg

RUN test -n "$GEOLAB_VERSION" || (echo "GEOLAB_VERSION must not be empty" >&2 && exit 1)

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
ARG NVIDIA_DRIVER_VERSION=580

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
