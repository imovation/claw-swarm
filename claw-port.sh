#!/bin/bash
# claw-swarm: Port Modifier Script
set -e

if [ "$#" -lt 2 ]; then
  echo "Usage: ./claw-port.sh <PROFILE_NAME> <NEW_PORT>"
  exit 1
fi

PROFILE=$1
NEW_PORT=$2
DIR="/home/imovation/.openclaw-$PROFILE"
[ "$PROFILE" == "gateway" ] && DIR="/home/imovation/.openclaw"
SERVICE="/home/imovation/.config/systemd/user/openclaw-$PROFILE.service"
[ "$PROFILE" == "gateway" ] && SERVICE="/home/imovation/.config/systemd/user/openclaw-gateway.service"

# 1. 检查实例是否存在
if [ ! -d "$DIR" ]; then
    echo "❌ Error: Profile '$PROFILE' not found."
    exit 1
fi

# 2. 判定端口占用
if ss -tuln | grep -q ":$NEW_PORT "; then
    echo "❌ Error: Port $NEW_PORT is already in use."
    exit 1
fi

echo "🔧 [1/3] Updating Configuration to Port $NEW_PORT..."
# 修正：直接修改 JSON 文件，避开参数顺序不可靠的问题
sed -i 's/"port": [0-9]*/"port": '$NEW_PORT'/g' "$DIR/openclaw.json"

echo "⚙️ [2/3] Updating Systemd Service Unit..."
# 修正：确保 --profile 在前，--port 在后
sed -i "s|ExecStart=.*|ExecStart=/home/imovation/.nvm/versions/node/v24.14.0/bin/node /home/imovation/.nvm/versions/node/v24.14.0/lib/node_modules/openclaw/dist/index.js --profile $PROFILE gateway run --port $NEW_PORT|" "$SERVICE"

echo "♻️  [3/3] Restarting Service..."
systemctl --user daemon-reload
systemctl --user restart "openclaw-$PROFILE.service"

echo "✅ Port for '$PROFILE' has been successfully changed to $NEW_PORT."
