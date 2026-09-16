# geolab-base Dockerfile for JupyterLab with Embedded VNC Desktop
# temporarily pinned to the spara/geolab-s3fs:0.0.0 test build (includes the
# aiobotocore<3.0.0 fix) instead of the published geolab-base tag
FROM spara/geolab-s3fs:0.0.0 AS  stage


ENV NB_GID=100
USER root

#install packages
RUN apt-get update -qq --yes > /dev/null \
    && apt-get install gmt-dcw gmt-gshhg --yes \
    && apt-get install gedit --yes \
    && apt-get install nano --yes \
    && apt-get install man-db --yes \
    && apt-get install openjdk-11-jre-headless --yes \
    && apt-get install xdg-utils --yes \
    && apt-get install libsqlite3-0 --yes \
    && apt-get install -y openjdk-21-jre-headless \
    && apt-get clean

# Set up the environment variables
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin

# Set GMT_DATA_SERVER
ENV GMT_DATA_SERVER="oceania"

# unminimize to install man-db
RUN yes | unminimize

#install gmt and pygmt from conda-forge
RUN mamba install -n "${CONDA_ENV}" -c conda-forge --yes \
        'gmt=6.6.0' 'gdal=3.12' 'pygmt=0.19' \
    && mamba clean -yaf

# Set GDAL_DRIVER_PATH as a real Docker ENV so it applies to every process
# (JupyterLab's CMD is not a login shell, so conda's own activate.d/gdal-activate.sh
# never runs for it and GDAL_DRIVER_PATH would otherwise be unset there)
ENV GDAL_DRIVER_PATH="/srv/conda/lib/gdalplugins:/srv/conda/envs/notebook/lib/gdalplugins"

RUN gdalinfo --formats | grep -q JP2OpenJPEG || (echo "JP2OpenJPEG driver missing" && exit 1)

# install taup
WORKDIR /opt
RUN wget -P /opt/ https://zenodo.org/records/16884103/files/TauP-3.1.0.zip \
    && unzip /opt/TauP-3.1.0.zip \
    && chmod +x /opt/TauP-3.1.0/bin/taup \
    && rm /opt/TauP-3.1.0.zip

# JupyterLab's CMD is not a login shell, so /etc/profile is never sourced for it
# (see GDAL_DRIVER_PATH above) -- PATH must be set as a real Docker ENV instead.
ENV PATH="${PATH}:/opt/TauP-3.1.0/bin"

# Dockerfile for JupyterLab with Embedded VNC Desktop
# ====================================================
# This creates a JupyterLab environment with:
# - JupyterLab interface
# - VNC desktop accessible through JupyterLab
# - X server (Xvfb for virtual display)
# - Desktop applications (xterm, firefox, etc.)
# - jupyter-server-proxy for desktop integration
# - jupyter-remote-desktop-proxy for launcher button

FROM stage
# FROM jupyter/base-notebook:latest

# Switch to root for system installations
USER root

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive \
    DISPLAY=:1 \
    VNC_PORT=5901 \
    RESOLUTION=1920x1080

# Install Firefox and its dependencies
# https://support.mozilla.org/en-US/kb/install-firefox-linux
# https://www.mozilla.org/en-US/firefox/117.0/system-requirements/
RUN install -d -m 0755 /etc/apt/keyrings \
    && wget -q https://packages.mozilla.org/apt/repo-signing-key.gpg -O- | tee /etc/apt/keyrings/packages.mozilla.org.asc > /dev/null \
    && gpg -n -q --import --import-options import-show /etc/apt/keyrings/packages.mozilla.org.asc | awk '/pub/{getline; gsub(/^ +| +$/,""); if($0 == "35BAA0B33E9EB396F59CA838C0BA5CE6DC6315A3") print "\nThe key fingerprint matches ("$0").\n"; else print "\nVerification failed: the fingerprint ("$0") does not match the expected one.\n"}' \
    && echo "deb [signed-by=/etc/apt/keyrings/packages.mozilla.org.asc] https://packages.mozilla.org/apt mozilla main" | tee -a /etc/apt/sources.list.d/mozilla.list > /dev/null \
    && echo 'Package: *\nPin: origin packages.mozilla.org\nPin-Priority: 1000' | tee /etc/apt/preferences.d/mozilla \
    && apt-get update && apt-get install -y --no-install-recommends \
        libpci-dev \
        libcanberra-gtk3-module \
        libgles2-mesa-dev \
        dbus-x11 \
        firefox \
    && apt-get clean

# Install system packages
RUN apt-get update && apt-get install -y \
    # X server and utilities
    xvfb \
    x11-apps \
    x11-utils \
    # Window manager
    xfce4 \
    xfce4-goodies \
    xfce4-terminal \
    # VNC server
    tigervnc-standalone-server \
    tigervnc-common \
    # noVNC and dependencies
    novnc \
    websockify \
    python3 \
    # Applications
    xterm \
    firefox \
    gedit \
    # Utilities
    wget \
    curl \
    net-tools \
    # Fonts
    fonts-liberation \
    fonts-dejavu \
    # System utilities
    dbus-x11 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create VNC directory for the notebook user
RUN mkdir -p /home/$NB_USER/.vnc && \
    chown -R $NB_USER:$NB_GID /home/$NB_USER

# copy JP2 plugin
# COPY --chown=jovyan:jovyan --chmod=664 gdal_JP2OpenJPEG.so /srv/conda/envs/notebook/lib/gdalplugins/

# Switch to notebook user for Python package installation
USER $NB_USER

# Install JupyterLab extensions and VNC support
RUN pip install --no-cache-dir \
    jupyter-server-proxy==4.4.0 \
    jupyter-remote-desktop-proxy \
    jupyterlab-topbar-stop-server==0.1.2

# Switch back to root for VNC configuration
USER root

# Set VNC password (password: password)
RUN echo "password" | vncpasswd -f > /home/$NB_USER/.vnc/passwd && \
    chmod 600 /home/$NB_USER/.vnc/passwd && \
    chown $NB_USER:$NB_GID /home/$NB_USER/.vnc/passwd

# Create VNC xstartup script for XFCE
COPY xstartup /home/$NB_USER/.vnc/xstartup

RUN chmod +x /home/$NB_USER/.vnc/xstartup && \
    chown $NB_USER:$NB_GID /home/$NB_USER/.vnc/xstartup

# Copy desktop startup script
COPY startup-desktop.sh /usr/local/bin/start-desktop.sh

# Create a wrapper script that jupyter-remote-desktop-proxy can call
COPY vnc-startup /usr/local/bin/vnc-startup

RUN chmod +x /usr/local/bin/vnc-startup

# Copy manual launcher script for terminal use
COPY launch-desktop /usr/local/bin/launch-desktop

RUN chmod +x /usr/local/bin/launch-desktop

# Fix all permissions
RUN chown -R $NB_USER:$NB_GID /home/$NB_USER

# Switch back to notebook user
USER $NB_USER

# Expose JupyterLab and VNC ports
EXPOSE 8888 5901 6080

# Set working directory
WORKDIR /home/$NB_USER

# Copy README
COPY README.md /home/$NB_USER/README.md

# Copy demo notebook
COPY desktop-demo.ipynb /home/$NB_USER/desktop-demo.ipynb

# Start JupyterLab
# The jupyter-remote-desktop-proxy will automatically detect VNC and add the Desktop launcher
# CMD ["start-notebook.sh", "--ServerApp.token=''", "--ServerApp.password=''"]
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--no-browser", "--allow-root"]
