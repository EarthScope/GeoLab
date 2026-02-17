#!/bin/bash
set -e

echo "================================================"
echo "Starting VNC Desktop Environment"
echo "================================================"

# Set environment
export USER=${USER:-jovyan}
export HOME=${HOME:-/home/jovyan}
export DISPLAY=:1

echo "User: $USER"
echo "Home: $HOME"
echo "Display: $DISPLAY"

# Clean up any existing sessions
vncserver -kill :1 2>/dev/null || true
sleep 2
rm -f /tmp/.X1-lock /tmp/.X11-unix/X1 2>/dev/null || true

# Start VNC server
echo "Starting VNC server..."
vncserver :1 -geometry ${RESOLUTION:-1920x1080} -depth 24 -localhost no

# Wait for VNC to be ready
for i in {1..15}; do
    if [ -S /tmp/.X11-unix/X1 ]; then
        echo "✓ VNC server started successfully"
        break
    fi
    echo "Waiting for VNC... ($i/15)"
    sleep 1
done

if [ ! -S /tmp/.X11-unix/X1 ]; then
    echo "ERROR: VNC server failed to start"
    cat $HOME/.vnc/*.log 2>/dev/null || true
    exit 1
fi

echo "================================================"
echo "Desktop ready!"
echo "Access via JupyterLab Desktop launcher"
echo "================================================"

# Keep the script running
tail -f $HOME/.vnc/*.log