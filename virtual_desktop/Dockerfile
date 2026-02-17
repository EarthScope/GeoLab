FROM public.ecr.aws/earthscope-dev/geolab/geolab-default:agu_wkshp-dc9cd124 

ENV NB_GID=100
USER root

# temporary fix
RUN pip uninstall --yes pygmt 

#install packages
RUN apt-get update -qq --yes > /dev/null \
    && apt-get install gmt-dcw gmt-gshhg --yes \
    && apt-get install gedit --yes \
    && apt-get install man-db --yes \
    && apt-get install openjdk-11-jre-headless --yes \
    && apt-get install xdg-utils --yes \
    && apt-get clean

# unminimize to install man-db
RUN yes | unminimize

#install gmt and pygmt from conda-forge
RUN conda install -c conda-forge --yes gmt pygmt 

# install taup
WORKDIR /opt
RUN wget -P /opt/ https://zenodo.org/records/16884103/files/TauP-3.1.0.zip \
    && unzip /opt/TauP-3.1.0.zip \
    &&  echo 'export PATH=$PATH:/opt/TauP-3.1.0/bin'  >> ~/.bashrc \
    && rm /opt/TauP-3.1.0.zip

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

# Switch to notebook user for Python package installation
USER $NB_USER

# Install JupyterLab extensions and VNC support
RUN pip install --no-cache-dir \
    jupyter-server-proxy==4.4.0 \
    jupyter-remote-desktop-proxy

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