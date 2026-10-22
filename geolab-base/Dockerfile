# syntax=docker/dockerfile:1
# ──────────────────────────────────────────────────────────────
# Custom geolab-base -- built on pangeo/base-image
#
# Files picked up automatically by the parent's ONBUILD machinery:
#   environment.yml  → conda env "notebook" installed from this
#   conda-lock.yml   → (optional, preferred) no-solve install
#   start            → entrypoint script (becomes /srv/start)
#
# Build:
#   docker build --platform linux/amd64 \
#   --build-arg IMAGE_TITLE=my-geolab-image \
#   --build-arg IMAGE_AUTHORS=you@university.edu \
#   --build-arg GEOLAB_VERSION=1.0.0 \
#   -t my-geolab-image .
# ──────────────────────────────────────────────────────────────
# Changing this tag is a major (breaking) change under semantic versioning.
FROM pangeo/base-image:04bb14b


ARG IMAGE_TITLE="custom-geolab-image"   # default if user passes nothing
ARG IMAGE_AUTHORS="NoSpecifiedAuthors"  # default if user passes nothing
ARG GEOLAB_VERSION="0.10.1"                      # no default; must be passed with --build-arg

RUN test -n "$GEOLAB_VERSION" || (echo "GEOLAB_VERSION must not be empty" >&2 && exit 1)

LABEL org.opencontainers.image.title="${IMAGE_TITLE}" \
      org.opencontainers.image.authors="${IMAGE_AUTHORS}" \
      org.opencontainers.image.version="${GEOLAB_VERSION}"

      # Set locations of PROJ/GDAL resource directories
ENV PROJ_DATA=/srv/conda/envs/notebook/share/proj \
    PROJ_LIB=/srv/conda/envs/notebook/share/proj \
    GDAL_DATA=/srv/conda/envs/notebook/share/gdal \
    GEOLAB_VERSION=${GEOLAB_VERSION}

# ── Security updates ──────────────────────────────────────────────
# The pinned pangeo base image only carries the security fixes that
# existed when it was built. These two steps pick up fixes published
# since (found with a Trivy scan of the built image).
#   - apt-get upgrade (as root): Ubuntu's published fixes, e.g.
#     OpenSSL, wget, gnutls, util-linux/mount, tar, gzip.
#   - The base conda install (/srv/conda) only holds build tooling
#     (conda, mamba); user code runs in /srv/conda/envs/notebook.
#     conda-lock, and the libraries only it uses (GitPython, dulwich,
#     virtualenv), are removed: the parent image's ONBUILD step has
#     already used it to install the environment, and the fixed
#     dulwich can't be installed alongside conda-lock 4.0.x. The rest
#     is pinned to fixed minimum versions, so the build fails if a
#     fix isn't available rather than silently keeping the old one.
USER root
RUN apt-get update > /dev/null \
    && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
USER ${NB_USER}
RUN mamba remove -n base -y conda-lock gitpython dulwich virtualenv \
    && mamba install -n base -y \
        "certifi>=2026.10.19" "urllib3>=2.8.0" "cryptography>=50" \
        "msgpack-python>=1.2.1" "h2>=4.4.1" "hpack>=4.2.0" \
        "pip>=26.2.0" "setuptools>=83" \
    && mamba clean -yaf

# Default command for standalone use. JupyterHub spawning passes
# its own command (jupyterhub-singleuser), which start respects.
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--no-browser"]
