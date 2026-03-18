#!/bin/bash
# claw-swarm: Repair Script (Fixes common profile/port/dependency issues)
set -e

PROFILE=$1
if [ -z "$PROFILE" ]; then
    echo "Usage: ./claw-repair.sh <PROFILE_NAME>"
    exit 1
fi

SERVICE_DIR="/home/imovation/.config/systemd/user"
SERVICE="$SERVICE_DIR/openclaw-$PROFILE.service"
[ "$PROFILE" == "gateway" ] && SERVICE="$SERVICE_DIR/openclaw-gateway.service"

if [ ! -f "$SERVICE" ]; then
    echo "❌ Error: Service for '$PROFILE' not found at $SERVICE"
    exit 1
fi

echo "🔧 [1/3] Repairing Systemd Unit for $PROFILE..."
# 修复 PATH
sed -i "s|/home/imovation/.nvm/current/bin|/home/imovation/.nvm/versions/node/v24.14.0/bin|g" "$SERVICE"

# 强行注入环境变量以确保物理隔离
DIR="/home/imovation/.openclaw-$PROFILE"
[ "$PROFILE" == "gateway" ] && DIR="/home/imovation/.openclaw"

# 删除旧的隔离变量并重新注入
sed -i "/Environment=OPENCLAW_STATE_DIR/d" "$SERVICE"
sed -i "/Environment=OPENCLAW_CONFIG_PATH/d" "$SERVICE"
sed -i "/\[Service\]/a Environment=OPENCLAW_CONFIG_PATH=$DIR/openclaw.json" "$SERVICE"
sed -i "/\[Service\]/a Environment=OPENCLAW_STATE_DIR=$DIR" "$SERVICE"

# 修正启动命令
if [ "$PROFILE" == "gateway" ]; then
    sed -i "s|ExecStart=.*|ExecStart=/home/imovation/.nvm/versions/node/v24.14.0/bin/node /home/imovation/.nvm/versions/node/v24.14.0/lib/node_modules/openclaw/dist/index.js gateway run --port 18789|" "$SERVICE"
else
    # 强制从配置文件提取端口，并在命令行显式指定以统一 HTTP/WS 端口
    PORT=$(grep -oP '"port":\s*\K[0-9]+' "$DIR/openclaw.json" || echo "18780")
    sed -i "s|ExecStart=.*|ExecStart=/home/imovation/.nvm/versions/node/v24.14.0/bin/node /home/imovation/.nvm/versions/node/v24.14.0/lib/node_modules/openclaw/dist/index.js --profile $PROFILE gateway run --port $PORT|" "$SERVICE"
fi


# 确保有 WorkingDirectory
if ! grep -q "WorkingDirectory" "$SERVICE"; then
    if [ "$PROFILE" == "gateway" ]; then
        DIR="/home/imovation/.openclaw"
    else
        DIR="/home/imovation/.openclaw-$PROFILE"
    fi
    sed -i "/\[Service\]/a WorkingDirectory=$DIR" "$SERVICE"
fi

echo "♻️  [2/3] Reloading Systemd and Restarting..."
systemctl --user daemon-reload
systemctl --user restart "openclaw-$PROFILE.service"

echo "🩺 [3/3] Health Check..."
sleep 3
if systemctl --user is-active "openclaw-$PROFILE.service" > /dev/null; then
    echo "✅ Pod '$PROFILE' repaired and running successfully."
else
    echo "⚠️  Pod '$PROFILE' still has issues. Check logs: journalctl --user -u openclaw-$PROFILE.service"
fi
