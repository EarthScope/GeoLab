# syntax=docker/dockerfile:1
# ──────────────────────────────────────────────────────────────
# Custom geolab-gpu -- built on pangeo/base-image
#
# GPU-enabled flavor of geolab-base: same base image, plus a
# CUDA/ML package set (PyTorch, seisbench, scikit-learn, etc.)
# from environment.yml/requirements.txt, an NVIDIA driver baked
# into the image at build time (see the note below), a geometric
# deep learning stack (torchvision, torchaudio, torch_geometric
# from requirements.txt; torch_scatter/torch_sparse/torch_cluster
# built from source below with CUDA kernels, using a CUDA 12.6
# compiler toolkit also installed below -- no prebuilt wheel matches
# the pinned torch build), and a seismic phase-association/location toolkit
# (PyOcto, GaMMA, Pyrocko from requirements.txt; REAL, NonLinLoc,
# HypoDD, and HypoInverse built from source below -- none of the
# four have a packaged installer).
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
#   - torch is pinned in requirements.txt to a cu126 build (CUDA
#     12.6), which needs driver >=560.28.03. Ubuntu's own apt
#     archive (used here, no separate NVIDIA repo is added) only
#     ships specific driver branches -- at the time of writing that's
#     470, 550, 570, 575, 580, 590, 610 -- so the NVIDIA_DRIVER_VERSION=580
#     default below is the closest available branch above that
#     minimum, not 560 itself. If you change one, change the other
#     to match; see the comment above the torch pin in
#     requirements.txt, and check `apt-cache search nvidia-utils`
#     inside the base image for what branches are currently offered.
#   - At `docker run`, the GPU device nodes still need to be handed
#     to the container: `docker run --gpus all ...` (needs
#     nvidia-container-toolkit on the host) or explicit `--device
#     /dev/nvidia0 --device /dev/nvidiactl --device /dev/nvidia-uvm`.
#   - Rebuild this image with an updated NVIDIA_DRIVER_VERSION (and
#     a matching torch cuXXX pin) any time the host driver changes.
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
#   --build-arg IMAGE_TITLE=my-geolab-gpu-image \
#   --build-arg IMAGE_AUTHORS=you@university.edu \
#   --build-arg GEOLAB_VERSION=1.0.0 \
#   --build-arg NVIDIA_DRIVER_VERSION=580 \
#   --build-arg TORCH_CUDA_ARCH_LIST="7.5" \
#   -t my-geolab-gpu-image .
# (TORCH_CUDA_ARCH_LIST is optional and defaults to 7.5, the Tesla
# T4 the GeoLab GPU host has. Set it to your GPU's compute
# capability if that differs, see the note above the torch_scatter
# build below.)
# ──────────────────────────────────────────────────────────────
# Changing this tag is a major (breaking) change under semantic versioning.
FROM pangeo/base-image:04bb14b


ARG IMAGE_TITLE="custom-geolab-gpu-image"   # default if user passes nothing
ARG IMAGE_AUTHORS="NoSpecifiedAuthors"     # default if user passes nothing
ARG GEOLAB_VERSION                         # may be empty (no default)

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

# REAL, NonLinLoc, HypoDD, and HypoInverse are legacy Fortran/C research
# codes with no conda-forge or PyPI package, install always means building
# from source. Built into a temp dir and thrown away after the binaries
# are copied out, so the toolchain (build-essential/gfortran/cmake, already
# in apt.txt) stays but none of the source trees or object files linger
# in the image.
#
#   REAL        -- github.com/Dal-mzhang/REAL. Its Makefile defaults to a
#                  macOS compiler name (gcc-10); pass CC= to override
#                  rather than edit the checked-in Makefile. Its
#                  pick2real.o is a stale, non-Linux precompiled object
#                  file committed alongside pick2real.c -- `make` sees it
#                  already "exists" and won't recompile it unless it's
#                  removed first, which is what actually caused a build
#                  failure here (its own README doesn't mention this).
#   NonLinLoc   -- github.com/ut-beg-texnet/NonLinLoc, the repository
#                  alomax/NonLinLoc itself now redirects to. Plain CMake
#                  build, no external libraries linked despite what
#                  Grid2GMT's GMT_VER_5 compile flag might suggest (that
#                  flag only affects the *shell scripts* it generates).
#   HypoDD      -- github.com/fwaldhauser/HypoDD, Felix Waldhauser's own
#                  mirror (v2.1beta). Ships its own Dockerfile confirming
#                  `make all` is all that's needed. Its event limits are
#                  compile-time array sizes, and the defaults (hypoDD
#                  MAXEVE=6500, ph2dt MEV=12000) are too small for a full
#                  aftershock sequence (e.g. ~18,000 events for the 2017
#                  Tehuantepec catalog), so both are raised to 20000 by
#                  sed before building. The replacements keep each line's
#                  width unchanged (fixed-form Fortran), and the grep
#                  fails the build if upstream ever changes those lines
#                  and the sed silently stops matching. At MAXEVE=20000
#                  hypoDD's static arrays exceed 2 GB, which the default
#                  x86-64 memory model can't address ("relocation
#                  truncated to fit" at link time), hence -mcmodel=medium.
#                  Memory cost: hypoDD touches those arrays on every run,
#                  even a tiny one, so its peak RSS rises from ~2.0 GB
#                  (default limits) to ~3.0 GB (measured on
#                  test_notebook.ipynb's two-event test); give the
#                  session at least 4 GB of RAM to run it.
#   HypoInverse -- USGS's HYPOINVERSE-2000 v1.40. USGS itself only
#                  distributes this via a request/FTP process, no git
#                  repo; github.com/BORONG-SEIS/HypoInverse is an
#                  unofficial but clean, unauthenticated mirror of the
#                  same public-domain (US government work) source,
#                  already patched for gfortran (the original targets
#                  g77). Built binary is dynamically linked against
#                  libgfortran despite the makefile's `-Bstatic` flag,
#                  which is a no-op on modern toolchains -- fine here
#                  since gfortran (and its runtime libs) stays installed
#                  via apt.txt, but worth knowing if you ever copy just
#                  the binary into a slimmer image. Its own bundled
#                  `testone/` example (input phases, station list,
#                  crustal model, and a known-correct summary line) is
#                  copied to /opt/geolab-tests/hypoinverse/ below for
#                  test_notebook.ipynb's functional test to run offline,
#                  see the comment there for why run.hyp differs from
#                  the repo's own testone.hyp.
#
# None of the four have a --version flag; run with no arguments (or a
# missing input file) they print a usage message and exit rather than
# crash, except hypoDD/ph2dt, which prompt on stdin if it isn't
# redirected -- harmless under test_helpers.py's cli(), which always
# runs with stdin closed, but worth knowing if you invoke them by hand.
# HypoInverse is the exception: it's a REPL, always waiting on stdin;
# cli() closes stdin, which just makes it exit immediately, still a
# valid "is it on $PATH and does it run at all" check.
RUN set -eux; \
    build_dir=$(mktemp -d); \
    cd "$build_dir"; \
    git clone --depth 1 https://github.com/Dal-mzhang/REAL.git; \
    (cd REAL/src/REAL && make CC="gcc -Os -fopenmp -W"); \
    (cd REAL/src/pick2real && rm -f pick2real.o && make); \
    (cd REAL/src/VELEST && make); \
    cp REAL/bin/REAL REAL/bin/pick2real REAL/bin/velest /usr/local/bin/; \
    git clone --depth 1 https://github.com/ut-beg-texnet/NonLinLoc.git; \
    (cd NonLinLoc/src && mkdir -p bin && cmake . && make); \
    cp NonLinLoc/src/bin/NLLoc NonLinLoc/src/bin/Vel2Grid NonLinLoc/src/bin/Grid2Time /usr/local/bin/; \
    git clone --depth 1 https://github.com/fwaldhauser/HypoDD.git; \
    sed -i 's/MAXEVE=   6500,/MAXEVE=  20000,/' HypoDD/include/hypoDD.inc; \
    sed -i 's/MEV=    12000,/MEV=    20000,/' HypoDD/include/ph2dt.inc; \
    grep -q 'MAXEVE=  20000,' HypoDD/include/hypoDD.inc; \
    grep -q 'MEV=    20000,' HypoDD/include/ph2dt.inc; \
    (cd HypoDD/src && make all FC="gfortran -mcmodel=medium" CC="gcc -mcmodel=medium"); \
    cp HypoDD/src/hypoDD/hypoDD HypoDD/src/ph2dt/ph2dt /usr/local/bin/; \
    git clone --depth 1 https://github.com/BORONG-SEIS/HypoInverse.git; \
    (cd HypoInverse/hyp1.40/source && make); \
    cp HypoInverse/hyp1.40/source/hyp1.40 /usr/local/bin/; \
    mkdir -p /opt/geolab-tests/hypoinverse; \
    cp HypoInverse/hyp1.40/testone/testone.phs \
       HypoInverse/hyp1.40/testone/allseed.sta \
       HypoInverse/hyp1.40/testone/all2000seed.fmc \
       HypoInverse/hyp1.40/testone/all2000seed.cal \
       HypoInverse/hyp1.40/testone/gey.crh \
       HypoInverse/hyp1.40/testone/gey4.del \
       /opt/geolab-tests/hypoinverse/; \
    cd /; \
    rm -rf "$build_dir"

# HypoInverse's own testone.hyp intersperses setup commands with *bare*
# confirmation prompts ("PHS" alone after "PHS 'testone.phs'", meant to
# be answered with a blank line/Enter at an interactive terminal to
# accept the default; same for FIL/PRT/SUM/ARC). Piped wholesale into
# stdin with no blank-line answers, those prompts consume the *next*
# script line as their answer instead, silently corrupting everything
# after -- confirmed by running it that way first: every phase card in
# testone.phs came back "SKIP BAD PHASE CARD" because HypoInverse ended
# up in the wrong phase-file-format state. run.hyp is the same setup,
# reordered with explicit blank-line answers after PHS and FIL (the two
# that actually affect parsing; PRT/SUM/ARC don't, but get one too for
# safety) and a trailing LOC/STOP to actually run the location instead
# of just printing "type LOC to locate the earthquake" and waiting.
# Verified byte-for-byte against the repo's own testone.sum reference
# before writing this in.
RUN cat > /opt/geolab-tests/hypoinverse/run.hyp <<'EOF'
TYP 'Setting Northern California defaults'
LET 5 2 3 2 2
RMS 4 .10 2 3
ERR .10
POS 1.78
REP T F
MIN 4
NET 2
ZTR 5
DI1 1 50 3 6
DIS 4 15 3.5 7
WET 1. .5 .2 .1
ERF T
TOP F
LST 2 0 1
KPR 2
H71 2 1 3
TYP Read in stations:
STA 'allseed.sta'
FMC 'all2000seed.fmc' T 0
TYP Read in crustal model(s):
CRH 1 'gey.crh'
DEL 1 'gey4.del'
DUR -.81 2.22 0 .0011 0, 5*0, 9999 1
DU2 .005 40, .0006 350, .014 10
FC1 'D' 5 'EHZ' 'SHZ' 'HHZ' 'BHZ' 'DPZ'
CAL 'all2000seed.cal' 0
PRE 6, 3 0 3 9, 1 1 0 9, 2 1 0 9, 4 4 4 9, 3 0 0 9, 4 0 0 9
PHS 'testone.phs'
PHS

FIL

PRT 'testone.prt'
PRT

SUM 'testone.sum'
SUM

ARC 'testone.arc'
ARC

LOC
STOP
EOF

# torch_scatter, torch_sparse, and torch_cluster (PyTorch Geometric's
# older C++/CUDA extension packages -- still expected by some PyG
# algorithms/tutorials even though torch_geometric itself no longer
# requires them for most operations) have no prebuilt wheel for the
# pinned torch==2.14.0+cu126 (see requirements.txt): PyG's own wheel
# index, data.pyg.org/whl/torch-<ver>.html, only publishes as far as
# torch 2.9.x at the time of writing. Built from source here instead.
# --no-build-isolation is required: their setup.py imports torch
# directly and expects it already installed, which pip's per-package
# isolated build env otherwise wouldn't have -- this only works because
# this RUN executes after the parent image's ONBUILD step has already
# installed requirements.txt (including torch) into the env.
#
# They're compiled with CUDA kernels, using the CUDA toolkit installed
# below, so their ops (scatter/segment reductions, sparse tensor ops,
# radius/knn/farthest-point graph construction) run on the GPU.
#   - CUDA_TOOLKIT_VERSION must match torch's own CUDA version (12.6
#     for torch==2.14.0+cu126): torch's extension builder refuses a
#     mismatched nvcc major version, and a different minor version
#     risks ABI trouble. Change it together with the torch pin.
#   - Only the pieces needed to compile against torch are installed,
#     not the multi-GB cuda-toolkit-* meta-package: nvcc, the CUDA
#     runtime/driver API headers, CCCL (Thrust/CUB), and the
#     cuBLAS/cuSPARSE/cuSOLVER/cuRAND dev packages (torch's CUDA
#     headers include all four). Their versions are the same ones
#     torch's nvidia-*-cu12 pip wheels already ship. They come from
#     NVIDIA's apt repo for Ubuntu 24.04, the base image's OS; no
#     driver packages are installed from it, the driver stays the
#     Ubuntu one installed above.
#   - The toolkit stays in the image (CUDA_HOME and nvcc on PATH), so
#     users can compile their own CUDA extensions or kernels too. It
#     adds ~2.9 GB (measured), mostly the cuBLAS/cuSPARSE dev packages.
#   - No GPU is needed to compile: FORCE_CUDA=1 makes PyG's setup.py
#     build the CUDA kernels anyway (it otherwise checks
#     torch.cuda.is_available(), which is False in `docker build`),
#     and TORCH_CUDA_ARCH_LIST says which GPU architectures to emit
#     code for. The default is 7.5 only: the Tesla T4 the GeoLab GPU
#     host has. The kernels then run on a T4 and nothing else -- on
#     any other GPU these three packages' CUDA ops fail with "no
#     kernel image is available for execution on the device" (plain
#     torch is unaffected; its own wheel covers many GPUs). For a
#     different GPU, pass its compute capability (A100 is 8.0, A10 is
#     8.6, L4 is 8.9, H100 is 9.0), or a semicolon-separated list for
#     several, e.g. --build-arg TORCH_CUDA_ARCH_LIST="7.5;8.0".
#   - Compiling is slow and scales with the number of architectures:
#     ~30 minutes for a single one under emulation (measured, with
#     torch_sparse taking most of it) -- normal, not a hang.
ARG CUDA_TOOLKIT_VERSION=12.6
ARG TORCH_CUDA_ARCH_LIST="7.5"
RUN set -eux; \
    v=$(echo "${CUDA_TOOLKIT_VERSION}" | tr . -); \
    wget -q -O /tmp/cuda-keyring.deb \
        https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb; \
    dpkg -i /tmp/cuda-keyring.deb; \
    rm /tmp/cuda-keyring.deb; \
    apt-get update > /dev/null; \
    apt-get install -y --no-install-recommends \
        "cuda-nvcc-${v}" \
        "cuda-cudart-dev-${v}" \
        "cuda-driver-dev-${v}" \
        "cuda-cccl-${v}" \
        "cuda-profiler-api-${v}" \
        "cuda-nvtx-${v}" \
        "libcublas-dev-${v}" \
        "libcusparse-dev-${v}" \
        "libcusolver-dev-${v}" \
        "libcurand-dev-${v}"; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*

# TORCH_CUDA_ARCH_LIST is kept in the image too, so CUDA extensions
# users build later target the same GPU by default, and so
# test_notebook.ipynb can check the GPU it runs on is one these
# kernels were compiled for.
ENV CUDA_HOME=/usr/local/cuda-${CUDA_TOOLKIT_VERSION} \
    PATH=${PATH}:/usr/local/cuda-${CUDA_TOOLKIT_VERSION}/bin \
    TORCH_CUDA_ARCH_LIST=${TORCH_CUDA_ARCH_LIST}

RUN FORCE_CUDA=1 TORCH_CUDA_ARCH_LIST="${TORCH_CUDA_ARCH_LIST}" \
    pip install --no-build-isolation --no-cache-dir \
    torch_scatter==2.1.2 \
    torch_sparse==0.6.18 \
    torch_cluster==1.6.3 \
    && python -c "import torch, torch_scatter, torch_sparse, torch_cluster; \
assert all(getattr(torch.ops, p).cuda_version() > 0 for p in ('torch_scatter', 'torch_sparse', 'torch_cluster')), \
'torch_scatter/torch_sparse/torch_cluster were built without CUDA'"

# The root steps above run with HOME=/home/${NB_USER}, so anything they
# cache under ~/.cache (pip, or Docker Desktop's Rosetta emulator when
# building on Apple Silicon) is left root-owned, and the notebook user
# then can't create its own cache dirs there (dascore and matplotlib
# fail with PermissionError). Hand it back before switching users.
RUN mkdir -p "/home/${NB_USER}/.cache" \
    && chown -R "${NB_USER}:${NB_USER}" "/home/${NB_USER}/.cache"

USER ${NB_USER}

# Default command for standalone use. JupyterHub spawning passes
# its own command (jupyterhub-singleuser), which start respects.
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--no-browser"]
