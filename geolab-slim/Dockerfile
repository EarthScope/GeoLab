# syntax=docker/dockerfile:1

# ── Build stage: compile pyrocko and install conda env ───────────────────────
FROM quay.io/jupyter/base-notebook:latest AS builder

USER root

RUN apt-get update --quiet && \
    apt-get install --quiet --yes --no-install-recommends \
        git \
        python3-dev \
        build-essential \
        gcc \
        gfortran \
        g++ \
        make && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER ${NB_UID}

RUN git clone https://git.pyrocko.org/pyrocko/pyrocko.git /tmp/pyrocko && \
    cd /tmp/pyrocko && \
    python install.py deps conda --yes && \
    python install.py user --y && \
    rm -rf /tmp/pyrocko

COPY --chown=${NB_UID}:${NB_GID} environment.yaml /tmp/environment.yaml

RUN mamba env update --name base --file /tmp/environment.yaml && \
    pip install gnss-lib-py --ignore-requires-python && \
    mamba clean --all --yes && \
    find /opt/conda -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /opt/conda -name '*.pyc' -delete 2>/dev/null || true

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM quay.io/jupyter/base-notebook:latest

LABEL maintainer="your-name <your@email.com>"
LABEL description="Geoscience JupyterLab environment"

USER root

RUN apt-get update --quiet && \
    apt-get install --quiet --yes --no-install-recommends \
        git \
        gmt-dcw gmt-gshhg \
        libgfortran5 \
        libgomp1 \
        ftp && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /home/joyvan/work

COPY --from=builder /opt/conda /opt/conda
COPY --from=builder --chown=${NB_UID}:${NB_GID} /home/jovyan /home/jovyan
COPY --chown=${NB_UID}:${NB_GID} test_suite.py /etc/tests/test_suite.py

USER ${NB_UID}

ENV JUPYTER_ENABLE_LAB=yes
CMD ["start-notebook.py"]
