# Virtual Desktop Dockerfile Annotated

This Dockerfile creates a JupyterLab environment with an embedded VNC desktop for scientific computing and visualization.

## Stage 1: Base Image and Initial Setup

### Base Image
```dockerfile
FROM public.ecr.aws/earthscope-dev/geolab/geolab-default:agu_wkshp-dc9cd124
```
**Purpose:** Starts from a pre-built EarthScope geolab image that contains JupyterLab and scientific computing tools for the AGU workshop.

---

### Environment and User Configuration
```dockerfile
ENV NB_GID=100
```
**Purpose:** Sets the group ID for the notebook user to 100 (typically the 'users' group in Linux).

```dockerfile
USER root
```
**Purpose:** Switches to the root user to perform system-level installations and configurations.

---

### PyGMT Fix
```dockerfile
RUN pip uninstall --yes pygmt
```
**Purpose:** Temporarily removes pygmt package (likely due to a version conflict that will be resolved by reinstalling from conda-forge later).

---

### System Package Installation
```dockerfile
RUN apt-get update -qq --yes > /dev/null \
    && apt-get install gmt-dcw gmt-gshhg --yes \
    && apt-get install gedit --yes \
    && apt-get install man-db --yes \
    && apt-get install openjdk-11-jre-headless --yes \
    && apt-get install xdg-utils --yes \
    && apt-get clean
```
**Purpose:** Installs essential packages:
- `apt-get update -qq --yes > /dev/null` - Updates package lists quietly
- `gmt-dcw gmt-gshhg` - GMT (Generic Mapping Tools) data files for coastlines and political boundaries
- `gedit` - Text editor with GUI
- `man-db` - Manual page database for documentation
- `openjdk-11-jre-headless` - Java runtime (required for TauP)
- `xdg-utils` - Desktop integration utilities
- `apt-get clean` - Removes package cache to reduce image size

---

### Unminimize Ubuntu
```dockerfile
RUN yes | unminimize
```
**Purpose:** Restores documentation and man pages in minimized Ubuntu installations. The `yes` command automatically answers "yes" to all prompts.

---

### GMT and PyGMT Installation
```dockerfile
RUN conda install -c conda-forge --yes gmt pygmt
```
**Purpose:** Installs GMT (mapping tools) and PyGMT (Python interface to GMT) from the conda-forge channel for better compatibility.

---

### TauP Installation
```dockerfile
WORKDIR /opt
```
**Purpose:** Changes working directory to `/opt` for installing system-wide software.

```dockerfile
RUN wget -P /opt/ https://zenodo.org/records/16884103/files/TauP-3.1.0.zip \
    && unzip /opt/TauP-3.1.0.zip \
    &&  echo 'export PATH=$PATH:/opt/TauP-3.1.0/bin'  >> ~/.bashrc \
    && rm /opt/TauP-3.1.0.zip
```
**Purpose:** Installs TauP (seismic travel time calculator):
- Downloads TauP 3.1.0 zip file from Zenodo
- Unzips the archive
- Adds TauP binary directory to PATH in bashrc
- Removes the zip file to save space

---

## Stage 2: VNC Desktop Environment

### Stage Marker and Comments
```dockerfile
FROM stage
# FROM jupyter/base-notebook:latest
```
**Purpose:** Creates a new build stage from the previous stage (multi-stage build). The commented line shows an alternative base image option.

---

### User and Environment Setup
```dockerfile
USER root
```
**Purpose:** Switches back to root user for system installations.

```dockerfile
ENV DEBIAN_FRONTEND=noninteractive \
    DISPLAY=:1 \
    VNC_PORT=5901 \
    RESOLUTION=1920x1080
```
**Purpose:** Sets environment variables:
- `DEBIAN_FRONTEND=noninteractive` - Prevents interactive prompts during package installation
- `DISPLAY=:1` - Sets X display to virtual display 1
- `VNC_PORT=5901` - Sets VNC server port
- `RESOLUTION=1920x1080` - Sets default screen resolution

---

### VNC and Desktop System Packages
```dockerfile
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
```
**Purpose:** Installs complete desktop environment:
- **X server**: `xvfb` (virtual framebuffer), X utilities
- **Desktop**: XFCE4 window manager and applications
- **VNC**: TigerVNC server for remote desktop access
- **Web VNC**: noVNC and websockify for browser-based VNC access
- **Applications**: Terminal, web browser, text editor
- **Utilities**: Network tools, fonts for better display
- Cleans up package cache to reduce image size

---

### VNC Directory Creation
```dockerfile
RUN mkdir -p /home/$NB_USER/.vnc && \
    chown -R $NB_USER:$NB_GID /home/$NB_USER
```
**Purpose:** Creates VNC configuration directory in the notebook user's home and sets proper ownership.

---

### Python Packages for VNC Integration
```dockerfile
USER $NB_USER
```
**Purpose:** Switches to notebook user for Python package installation.

```dockerfile
RUN pip install --no-cache-dir \
    jupyter-server-proxy==4.4.0 \
    jupyter-remote-desktop-proxy
```
**Purpose:** Installs JupyterLab extensions:
- `jupyter-server-proxy` - Proxies web services through JupyterLab
- `jupyter-remote-desktop-proxy` - Adds Desktop launcher button to JupyterLab

---

### VNC Password Configuration
```dockerfile
USER root
```
**Purpose:** Switches back to root for VNC configuration.

```dockerfile
RUN echo "password" | vncpasswd -f > /home/$NB_USER/.vnc/passwd && \
    chmod 600 /home/$NB_USER/.vnc/passwd && \
    chown $NB_USER:$NB_GID /home/$NB_USER/.vnc/passwd
```
**Purpose:** Sets VNC password to "password" (should be changed in production):
- Creates encrypted password file
- Sets restrictive permissions (600 = read/write for owner only)
- Sets correct ownership

---

### VNC Startup Script
```dockerfile
COPY xstartup /home/$NB_USER/.vnc/xstartup
```
**Purpose:** Copies VNC startup script that launches XFCE desktop environment.

```dockerfile
RUN chmod +x /home/$NB_USER/.vnc/xstartup && \
    chown $NB_USER:$NB_GID /home/$NB_USER/.vnc/xstartup
```
**Purpose:** Makes startup script executable and sets correct ownership.

---

### Desktop Launch Scripts
```dockerfile
COPY startup-desktop.sh /usr/local/bin/start-desktop.sh
```
**Purpose:** Copies desktop startup script to system binaries.

```dockerfile
COPY vnc-startup /usr/local/bin/vnc-startup
```
**Purpose:** Copies VNC startup wrapper that jupyter-remote-desktop-proxy will call.

```dockerfile
RUN chmod +x /usr/local/bin/vnc-startup
```
**Purpose:** Makes VNC startup wrapper executable.

```dockerfile
COPY launch-desktop /usr/local/bin/launch-desktop
```
**Purpose:** Copies manual desktop launcher for terminal use.

```dockerfile
RUN chmod +x /usr/local/bin/launch-desktop
```
**Purpose:** Makes manual launcher executable.

---

### Permission Fixes
```dockerfile
RUN chown -R $NB_USER:$NB_GID /home/$NB_USER
```
**Purpose:** Ensures all files in user's home directory have correct ownership.

---

### Final User Switch
```dockerfile
USER $NB_USER
```
**Purpose:** Switches back to notebook user for running JupyterLab (security best practice).

---

### Port Exposure
```dockerfile
EXPOSE 8888 5901 6080
```
**Purpose:** Documents which ports the container uses:
- `8888` - JupyterLab web interface
- `5901` - VNC server
- `6080` - noVNC web interface

---

### Working Directory
```dockerfile
WORKDIR /home/$NB_USER
```
**Purpose:** Sets default working directory to the notebook user's home.

---

### Copy Documentation and Demo Files
```dockerfile
COPY README.md /home/$NB_USER/README.md
```
**Purpose:** Copies README documentation to user's home directory.

```dockerfile
COPY desktop-demo.ipynb /home/$NB_USER/desktop-demo.ipynb
```
**Purpose:** Copies demo Jupyter notebook showing desktop features.

---

### Container Startup Command
```dockerfile
# CMD ["start-notebook.sh", "--ServerApp.token=''", "--ServerApp.password=''"]
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--no-browser", "--allow-root"]
```
**Purpose:** Defines the default command when container starts:
- Commented line shows alternative startup method
- Active command launches JupyterLab:
  - `--ip=0.0.0.0` - Listens on all network interfaces
  - `--no-browser` - Doesn't try to open a browser
  - `--allow-root` - Allows running as root if needed

---

## Summary

This Dockerfile creates a comprehensive scientific computing environment with:
1. **Geospatial tools**: GMT, PyGMT for mapping and visualization
2. **Seismology tools**: TauP for earthquake analysis
3. **Desktop environment**: Full XFCE desktop accessible via VNC
4. **Web interface**: JupyterLab with integrated desktop launcher
5. **Accessibility**: Multiple access methods (JupyterLab, VNC, noVNC)

The image is designed for interactive scientific work with both command-line and GUI applications.