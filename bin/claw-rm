#!/bin/bash
# claw-swarm: Remover Script (Like kubectl delete pod <name>)
set -e

if [ "$#" -lt 1 ]; then
  echo "Usage: ./claw-rm.sh <PROFILE_NAME>"
  echo "Example: ./claw-rm.sh bob"
  exit 1
fi

PROFILE=$1
DIR="/home/imovation/.openclaw-$PROFILE"
SERVICE="/home/imovation/.config/systemd/user/openclaw-$PROFILE.service"

echo "🗑️  [1/3] Stopping and Disabling Pod: $PROFILE..."
if systemctl --user list-units --all | grep -q "openclaw-$PROFILE.service"; then
    systemctl --user stop "openclaw-$PROFILE.service" || true
    systemctl --user disable "openclaw-$PROFILE.service" || true
fi

echo "🧹 [2/3] Removing Systemd Service File..."
if [ -f "$SERVICE" ]; then
    rm "$SERVICE"
    systemctl --user daemon-reload
fi

echo "📂 [3/3] Deleting Profile Directory: $DIR..."
if [ -d "$DIR" ]; then
    rm -rf "$DIR"
fi

echo "✅ Pod '$PROFILE' has been removed successfully."
