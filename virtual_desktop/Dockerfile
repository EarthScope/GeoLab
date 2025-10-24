FROM pangeo/base-notebook

USER root

# COPY setup-scripts /opt/setup-scripts/

# Set DISPLAY env variable, so processes know where to open GUI windows.
# Allows python processes running in notebooks to open windows in the GUI.
ENV DISPLAY=":1.0"

# Setup Linux Desktop
# RUN /opt/setup-scripts/setup-linux-desktop.bash
## Move everything from the setup scrip to this Dockerfile
# RUN set -exuo pipefail
# Requirements:
# - Run as the root user

# Install baseline packages to get X and xfce working
RUN apt-get update -qq --yes > /dev/null
RUN apt-get install --yes --no-install-recommends -qq \
    xfce4 \
    xorg \
    dbus-x11 \
    xubuntu-icon-theme \
    > /dev/null

# Install tigervnc from apt repos - these are newer and more architecture
# appropriate than whatever is bundled with jupyter-remote-desktop-proxy
RUN apt-get install --yes --no-install-recommends -qq \
        tigervnc-standalone-server \
        tigervnc-xorg-extension > /dev/null

# Install add-apt-repositories so we can add PPA for latest firefox
RUN apt-get install --yes --no-install-recommends -qq \
    software-properties-common gpg-agent > /dev/null

# Install Firefox from a PPA - default Ubuntu's Firefox no longer
# provides it via apt, using snap instead. That does not work inside
# containers. We do this before our apt update in the script so that
# needs to run only once.
RUN add-apt-repository ppa:mozillateam/ppa

# Install Firefox from the PPA explicitly
RUN apt-get update -qq --yes > /dev/null
RUN apt-get install -qq --yes -t 'o=LP-PPA-mozillateam' --yes firefox

# Cleanup apt-get update side effects
RUN rm -rf /var/lib/apt/lists/*

# Install packages required for linux desktop VPN setup to work
# websockify and jupyter-server-proxy available from conda-forge, but
# jupyter-remote-desktop-proxy is not.
# Temporarily install nbgitpuller too, while we work on getting it upstream
# RUN mamba install -c conda-forge --yes \
#       websockify \
#       jupyter-server-proxy \
#       nbgitpuller

RUN fix-permissions "${CONDA_DIR}"
RUN fix-permissions "/home/${NB_USER}"


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

# # Pin jupyterhub and pydantic to older version
# # because of https://github.com/NASA-IMPACT/veda-jupyterhub/issues/52#issuecomment-2277453902
# RUN python -m pip install --no-cache "jupyterhub<5.0.0" "pydantic<2.0"
# RUN python -m pip install --no-cache jupyter-remote-desktop-proxy
# # RUN python -m pip install --no-cache git+https://github.com/sunu/jupyter-remote-qgis-proxy@e1a49e0ba98700c2f49fc092d5fc1e43ca5442eb