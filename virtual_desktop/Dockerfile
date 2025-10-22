FROM quay.io/jupyter/minimal-notebook:2024-06-24

USER root

COPY setup-scripts /opt/setup-scripts/

# Set DISPLAY env variable, so processes know where to open GUI windows.
# Allows python processes running in notebooks to open windows in the GUI.
ENV DISPLAY=":1.0"

# Setup Linux Desktop
RUN /opt/setup-scripts/setup-linux-desktop.bash

COPY startup-scripts /usr/local/bin/start-notebook.d/

# env variables used by downstream images for setting up desktop files or
# mime associations. Consumed by the startup-scripts in startup-scripts/
ENV DESKTOP_FILES_DIR /opt/desktop-files
ENV MIME_FILES_DIR /opt/mime-files
RUN mkdir -p ${DESKTOP_FILES_DIR} ${MIME_FILES_DIR}

USER ${NB_UID}

COPY environment.yml /tmp/

RUN mamba env update --name ${CONDA_ENV} -f /tmp/environment.yml \
    && pip cache purge \
    && mamba clean -afy
RUN conda install awscli==2.27.0

# Pin jupyterhub and pydantic to older version
# because of https://github.com/NASA-IMPACT/veda-jupyterhub/issues/52#issuecomment-2277453902
RUN python -m pip install --no-cache "jupyterhub<5.0.0" "pydantic<2.0"
RUN python -m pip install --no-cache jupyter-remote-desktop-proxy
# RUN python -m pip install --no-cache git+https://github.com/sunu/jupyter-remote-qgis-proxy@e1a49e0ba98700c2f49fc092d5fc1e43ca5442eb