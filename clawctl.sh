#!/bin/bash
# claw-swarm: Provisioner Script (Like kubectl apply -f pod.yaml)
set -e

if [ "$#" -lt 3 ]; then
  echo "Usage: ./clawctl.sh <PROFILE_NAME> <PORT> <TOKEN>"
  echo "Example: ./clawctl.sh bob 18781 mysecuretoken"
  exit 1
fi

PROFILE=$1
PORT=$2
TOKEN=$3
DIR="/home/imovation/.openclaw-$PROFILE"
SERVICE="/home/imovation/.config/systemd/user/openclaw-$PROFILE.service"

# Pre-flight checks
if [ -d "$DIR" ]; then
  echo "❌ Error: Profile '$PROFILE' already exists at $DIR"
  exit 1
fi

if [ -f "$SERVICE" ]; then
  echo "❌ Error: Systemd service 'openclaw-$PROFILE.service' already exists"
  exit 1
fi

if ss -tuln | grep -q ":$PORT "; then
  echo "❌ Error: Port $PORT is already in use on this system"
  exit 1
fi

echo "🚀 [1/5] Initializing Pod: $PROFILE..."
openclaw --profile "$PROFILE" setup > /dev/null 2>&1 || true

echo "📂 [2/5] Creating Physical Workspace & Extensions..."
mkdir -p "$DIR/workspace"
mkdir -p "$DIR/extensions"
# Assuming we use Aimee's as a safe template since main might not have it anymore
if [ -d "/home/imovation/.openclaw-aimee/extensions/openclaw-lark" ]; then
    cp -r /home/imovation/.openclaw-aimee/extensions/openclaw-lark "$DIR/extensions/"
fi

echo "⚙️ [3/5] Applying Configuration (Port: $PORT, Token: $TOKEN)..."
openclaw --profile "$PROFILE" config set gateway.port $PORT
openclaw --profile "$PROFILE" config set gateway.auth.mode "token"
openclaw --profile "$PROFILE" config set gateway.auth.token "$TOKEN"
openclaw --profile "$PROFILE" config set agents.defaults.workspace "$DIR/workspace"
openclaw --profile "$PROFILE" config set plugins.allow "[\"openclaw-lark\"]"

echo "🔧 [4/5] Generating Systemd User Service..."
cat << SYSTEMD_EOF > "$SERVICE"
[Unit]
Description=OpenClaw Gateway ($PROFILE Profile)
After=network-online.target
Wants=network-online.target

[Service]
WorkingDirectory=/home/imovation/.openclaw-$PROFILE
ExecStart=/home/imovation/.nvm/versions/node/v24.14.0/bin/node /home/imovation/.nvm/versions/node/v24.14.0/lib/node_modules/openclaw/dist/index.js --profile $PROFILE gateway run --port $PORT
Restart=always
RestartSec=5
TimeoutStopSec=30
TimeoutStartSec=30
SuccessExitStatus=0 143
KillMode=control-group
Environment=HOME=/home/imovation
Environment=TMPDIR=/tmp
Environment=HTTP_PROXY=http://127.0.0.1:7897/
Environment=HTTPS_PROXY=http://127.0.0.1:7897/
Environment=NO_PROXY=localhost,127.0.0.1,192.168.0.0/16,10.0.0.0/8,172.16.0.0/12,::1
Environment=ALL_PROXY=socks://127.0.0.1:7897/
Environment=http_proxy=http://127.0.0.1:7897/
Environment=https_proxy=http://127.0.0.1:7897/
Environment=no_proxy=localhost,127.0.0.1,192.168.0.0/16,10.0.0.0/8,172.16.0.0/12,::1
Environment=all_proxy=socks://127.0.0.1:7897/
Environment=PATH=/home/imovation/.nvm/versions/node/v24.14.0/bin:/home/imovation/.local/bin:/home/imovation/.npm-global/bin:/home/imovation/bin:/home/imovation/.volta/bin:/home/imovation/.asdf/shims:/home/imovation/.bun/bin:/home/imovation/.fnm/current/bin:/home/imovation/.local/share/pnpm:/usr/local/bin:/usr/bin:/bin
Environment=OPENCLAW_SYSTEMD_UNIT=openclaw-$PROFILE.service
Environment=OPENCLAW_SERVICE_MARKER=openclaw
Environment=OPENCLAW_SERVICE_KIND=gateway
Environment=OPENCLAW_PROFILE=$PROFILE
Environment=OPENCLAW_STATE_DIR=$DIR
Environment=OPENCLAW_CONFIG_PATH=$DIR/openclaw.json

[Install]
WantedBy=default.target
SYSTEMD_EOF

echo "⚡ [5/5] Deploying and Starting Pod..."
systemctl --user daemon-reload
systemctl --user enable --now openclaw-$PROFILE.service

echo "✅ Pod '$PROFILE' deployed successfully on port $PORT!"
echo "   TUI: openclaw --profile $PROFILE tui --token $TOKEN"
echo "   Logs: journalctl --user -fu openclaw-$PROFILE.service"
