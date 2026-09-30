#!/bin/sh
# Runs one game client on a virtual display and serves it to a browser via noVNC.
set -e
export SDL_VIDEODRIVER=x11 DISPLAY=:99
Xvfb :99 -screen 0 1024x576x24 >/dev/null 2>&1 &
sleep 1
x11vnc -display :99 -forever -shared -nopw -quiet -bg >/dev/null 2>&1
websockify --web /usr/share/novnc 6080 localhost:5900 >/dev/null 2>&1 &
exec python -m tankbattle client --host "${SERVER_HOST:-server}" --port 5555
