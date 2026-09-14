# JupyterLab with VNC Desktop

## Quick Start

### Access Desktop in JupyterLab

**Method 1: Launcher Icon (Easiest)**
1. Open JupyterLab at http://localhost:8888
2. Click the **"Desktop"** icon in the Launcher
3. Desktop opens in a new tab within JupyterLab!

**Method 2: Direct URL**
Navigate to: http://localhost:8888/desktop/

**Method 3: Terminal Command**
```bash
launch-desktop
```

## Using the Desktop

The desktop provides a full XFCE environment with:
- Applications menu (top-left)
- Firefox web browser
- Gedit text editor
- File manager
- Terminal emulator
- Multiple workspaces

## Running Applications from Jupyter

### From Terminal:
```bash
export DISPLAY=:1
firefox &
gedit myfile.txt &
xterm &
```

### From Notebook:
```python
import os
import subprocess

os.environ['DISPLAY'] = ':1'
subprocess.Popen(['firefox'])
```

## Troubleshooting

### Desktop won't load?
```bash
# Check if VNC is running
ps aux | grep Xvnc

# Restart VNC
vncserver -kill :1
sleep 2
vncserver :1 -geometry 1920x1080 -depth 24

# Check logs
cat ~/.vnc/*.log
```

### Applications won't start?
```bash
export DISPLAY=:1
export USER=jovyan
export HOME=/home/jovyan
```

## Installed Applications

- Firefox - Web browser
- Gedit - Text editor
- XFCE Terminal - Terminal emulator
- Xterm - Simple terminal
- File Manager - Browse files
- X11 apps - xeyes, xclock, xcalc

## Password

If prompted for VNC password: **password**