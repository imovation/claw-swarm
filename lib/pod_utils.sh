#!/bin/bash
# lib/pod_utils.sh — 声明式开发模式：共享 Pod 解析函数库
# 解决 Profile/DIR/SERVICE_NAME 在 5 个脚本中重复声明的 DRY 违规问题。
#
# 使用方法（在调用脚本顶部 source 本文件）:
#   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#   source "$SCRIPT_DIR/../lib/pod_utils.sh"
#
# 然后调用:
#   resolve_pod "aimee"    → 设置 $DIR, $SERVICE_NAME, $SERVICE, $PROFILE_ARG
#   get_node_binary        → 返回 node 可执行文件路径
#   get_openclaw_binary    → 返回 openclaw dist/index.js 路径

# ==============================================================================
# 常量：用户主目录
# ==============================================================================
CLAW_USER_HOME="/home/imovation"
CLAW_SYSTEMD_DIR="$CLAW_USER_HOME/.config/systemd/user"

# ==============================================================================
# resolve_pod <profile>
# 根据 profile 名称解析出所有路径相关变量。
# 统一处理 "default"、"main"、"gateway" 这三个历史别名 → 均指向主 Pod。
#
# 输出（通过导出变量）:
#   $RESOLVED_PROFILE   — 规范化的 profile 参数 (用于 --profile 命令行)
#   $DIR                — Pod 的根目录路径
#   $SERVICE_NAME       — Systemd 服务名（不含 .service 后缀）
#   $SERVICE            — 服务文件的完整路径
# ==============================================================================
resolve_pod() {
    local profile="$1"
    if [ -z "$profile" ]; then
        echo "错误: resolve_pod() 需要一个 profile 参数" >&2
        return 1
    fi

    # 统一别名：default / main / gateway 均指向主 Pod
    if [[ "$profile" == "default" || "$profile" == "main" || "$profile" == "gateway" ]]; then
        RESOLVED_PROFILE="default"
        DIR="$CLAW_USER_HOME/.openclaw"
        SERVICE_NAME="openclaw-gateway"
    else
        RESOLVED_PROFILE="$profile"
        DIR="$CLAW_USER_HOME/.openclaw-$profile"
        SERVICE_NAME="openclaw-gateway-$profile"
    fi

    SERVICE="$CLAW_SYSTEMD_DIR/$SERVICE_NAME.service"
    export RESOLVED_PROFILE DIR SERVICE_NAME SERVICE
}

# ==============================================================================
# get_node_binary
# 动态解析当前激活的 Node.js 可执行文件路径。
# 优先使用 nvm 的当前激活版本，其次 which node，最后降级到硬编码路径。
#
# 输出: 打印 node 可执行文件的绝对路径（供命令替换使用）
# ==============================================================================
get_node_binary() {
    # 方法 1: 从 nvm 的软链接解析真实路径
    if [ -d "$CLAW_USER_HOME/.nvm/versions/node" ]; then
        local nvm_current
        # 读取 nvm 当前使用的版本（最新修改时间的目录）
        nvm_current=$(ls -t "$CLAW_USER_HOME/.nvm/versions/node" 2>/dev/null | head -n 1)
        if [ -n "$nvm_current" ]; then
            local candidate="$CLAW_USER_HOME/.nvm/versions/node/$nvm_current/bin/node"
            if [ -x "$candidate" ]; then
                echo "$candidate"
                return 0
            fi
        fi
    fi

    # 方法 2: 通过 PATH 查找
    local node_in_path
    node_in_path=$(command -v node 2>/dev/null)
    if [ -n "$node_in_path" ]; then
        echo "$node_in_path"
        return 0
    fi

    echo "错误: 找不到 node 可执行文件，请确认 nvm 或 node 已正确安装" >&2
    return 1
}

# ==============================================================================
# get_openclaw_binary
# 动态解析 openclaw 的 dist/index.js 路径。
# 与 get_node_binary() 使用相同的版本解析策略，保持一致性。
#
# 输出: 打印 dist/index.js 的绝对路径
# ==============================================================================
get_openclaw_binary() {
    if [ -d "$CLAW_USER_HOME/.nvm/versions/node" ]; then
        local nvm_current
        nvm_current=$(ls -t "$CLAW_USER_HOME/.nvm/versions/node" 2>/dev/null | head -n 1)
        if [ -n "$nvm_current" ]; then
            local candidate="$CLAW_USER_HOME/.nvm/versions/node/$nvm_current/lib/node_modules/openclaw/dist/index.js"
            if [ -f "$candidate" ]; then
                echo "$candidate"
                return 0
            fi
        fi
    fi

    echo "错误: 找不到 openclaw dist/index.js，请确认 openclaw 已全局安装" >&2
    return 1
}

# ==============================================================================
# systemd_reload_restart <service_name>
# 统一的 Systemd 重载 + 重启序列，避免在各脚本中重复书写。
# ==============================================================================
systemd_reload_restart() {
    local svc="$1"
    systemctl --user daemon-reload
    systemctl --user restart "$svc.service"
}

# ==============================================================================
# pod_health_check <service_name> [display_profile]
# 执行健康检查并打印结果。
# ==============================================================================
pod_health_check() {
    local svc="$1"
    local display="${2:-$1}"
    sleep 3
    if systemctl --user is-active --quiet "$svc.service"; then
        echo "✅ Pod '$display' 运行正常。"
        echo "   查看日志: journalctl --user -fu $svc.service"
    else
        echo "⚠️  Pod '$display' 仍有问题，请检查日志: journalctl --user -u $svc.service"
    fi
}

# ==============================================================================
# sync_plugins <target_dir> <plugin_list_comma_separated>
# 物理同步插件到 Pod 的 extensions 目录。
# ==============================================================================
sync_plugins() {
    local target_dir="$1"
    local plugins="$2"
    local extensions_dir="$target_dir/extensions"
    local node_modules_global

    # 获取全局 node_modules 路径
    node_modules_global=$(dirname "$(get_node_binary)")/../lib/node_modules
    
    mkdir -p "$extensions_dir"

    IFS=',' read -ra ADDR <<< "$plugins"
    for plugin in "${ADDR[@]}"; do
        if [ -z "$plugin" ]; then continue; fi
        local src="$node_modules_global/$plugin"
        if [ -d "$src" ]; then
            echo "   📦 正在同步插件: $plugin..."
            # 使用 rsync 进行增量同步，如果不存在则回退到 cp
            if command -v rsync >/dev/null 2>&1; then
                rsync -rt --delete "$src/" "$extensions_dir/$plugin/"
            else
                rm -rf "$extensions_dir/$plugin"
                cp -r "$src" "$extensions_dir/$plugin"
            fi
        else
            echo "   ⚠️ 警告: 找不到全局插件 $plugin ($src)"
        fi
    done
}

# ==============================================================================
# ensure_template_service
# 检查并创建 systemd 模板服务（如果不存在）。
# 解决首次部署时缺少 openclaw-gateway@.service 模板的问题。
# ==============================================================================
ensure_template_service() {
    local template_service="$CLAW_SYSTEMD_DIR/openclaw-gateway@.service"
    
    if [ -f "$template_service" ]; then
        return 0
    fi
    
    echo "⚠️  未发现 systemd 模板服务，正在创建..."
    
    # 动态解析 node 路径
    local node_bin
    node_bin=$(get_node_binary)
    local node_dir
    node_dir=$(dirname "$node_bin")
    local node_version
    node_version=$(basename "$node_dir")
    
    # 创建模板服务文件
    mkdir -p "$CLAW_SYSTEMD_DIR"
    
    cat > "$template_service" << TEMPLATE_EOF
[Unit]
Description=OpenClaw Gateway (profile: %i, claw-swarm managed)
After=network-online.target
Wants=network-online.target

[Service]
EnvironmentFile=-%h/.openclaw/runtime/env
EnvironmentFile=-%h/.openclaw-%i/runtime/env
ExecStartPre=/bin/bash -c 'export \$(cat %h/.openclaw-%i/runtime/env 2>/dev/null || cat %h/.openclaw/runtime/env 2>/dev/null | grep -v "^#" | xargs)'
ExecStart=/bin/bash -c 'source %h/.openclaw-%i/runtime/env 2>/dev/null || source %h/.openclaw/runtime/env; export \$(grep -v "^#" %h/.openclaw-%i/runtime/env 2>/dev/null || grep -v "^#" %h/.openclaw/runtime/env 2>/dev/null | xargs); cd %h/.openclaw-%i 2>/dev/null || cd %h/.openclaw; unset OPENCLAW_SYSTEMD_UNIT; export OPENCLAW_PROFILE=%i; export OPENCLAW_STATE_DIR=\$PWD; export OPENCLAW_CONFIG_PATH=\$PWD/openclaw.json; exec ${node_bin} \${node_bin%bin}lib/node_modules/openclaw/dist/index.js --profile %i gateway run --port \${OPENCLAW_PORT} --bind loopback'

Restart=always
RestartSec=5
TimeoutStopSec=30
TimeoutStartSec=30
SuccessExitStatus=0 143
KillMode=control-group

[Install]
WantedBy=default.target
TEMPLATE_EOF
    
    # 替换占位符
    sed -i "s|\${node_bin}|$node_bin|g" "$template_service"
    sed -i "s|\${node_version}|$node_version|g" "$template_service"
    
    chmod 644 "$template_service"
    echo "✅ 模板服务已创建: $template_service"
}
