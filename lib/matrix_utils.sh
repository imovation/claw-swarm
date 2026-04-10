#!/bin/bash
# lib/matrix_utils.sh — 共享 Matrix 工具函数库
# 提供 Matrix 配置解析和验证的辅助函数
#
# ⚠️  [待迁移 PENDING MIGRATION] 本库的逻辑归属：
#     modules/matrix-channel/account-manager/  → 配置读取与验证
#     本文件作为过渡兼容层保留，供 bin/claw-matrix-* 等遗留 Bash 脚本调用。
#     请勿在此处添加新逻辑，新功能请直接在 modules/ 对应层编写。
#
# 使用方法：
#   source "$SCRIPT_DIR/../lib/matrix_utils.sh"
#
# 函数：
#   matrix_enabled <profile>         检查 Pod 是否启用 Matrix
#   matrix_get_config <profile>      获取 Matrix 配置 JSON
#   matrix_validate_config <json>    验证 Matrix 配置完整性

CLAW_USER_HOME="${HOME:-/home/imovation}"

matrix_enabled() {
    local profile="$1"
    local config_file
    
    if [[ "$profile" == "default" || "$profile" == "main" || "$profile" == "gateway" ]]; then
        config_file="$CLAW_USER_HOME/.openclaw/openclaw.json"
    else
        config_file="$CLAW_USER_HOME/.openclaw-$profile/openclaw.json"
    fi
    
    if [ ! -f "$config_file" ]; then
        return 1
    fi
    
    local enabled
    enabled=$(python3 -c "
import json
import sys
try:
    with open('$config_file', 'r') as f:
        config = json.load(f)
    matrix = config.get('channels', {}).get('matrix', {})
    print('true' if matrix.get('enabled') else 'false')
except:
    print('false')
" 2>/dev/null)
    
    [ "$enabled" = "true" ]
}

matrix_get_config() {
    local profile="$1"
    local config_file
    
    if [[ "$profile" == "default" || "$profile" == "main" || "$profile" == "gateway" ]]; then
        config_file="$CLAW_USER_HOME/.openclaw/openclaw.json"
    else
        config_file="$CLAW_USER_HOME/.openclaw-$profile/openclaw.json"
    fi
    
    if [ ! -f "$config_file" ]; then
        echo "{}"
        return
    fi
    
    python3 -c "
import json
try:
    with open('$config_file', 'r') as f:
        config = json.load(f)
    matrix = config.get('channels', {}).get('matrix', {})
    print(json.dumps(matrix))
except:
    print('{}')
" 2>/dev/null
}

matrix_validate_config() {
    local json="$1"
    
    local homeserver token
    homeserver=$(echo "$json" | python3 -c "import json,sys; print(json.load(sys.stdin).get('homeserver',''))" 2>/dev/null)
    token=$(echo "$json" | python3 -c "import json,sys; print(json.load(sys.stdin).get('accessToken',''))" 2>/dev/null)
    userid=$(echo "$json" | python3 -c "import json,sys; print(json.load(sys.stdin).get('userId',''))" 2>/dev/null)
    password=$(echo "$json" | python3 -c "import json,sys; print(json.load(sys.stdin).get('password',''))" 2>/dev/null)
    
    if [ -z "$homeserver" ]; then
        echo "错误: 缺少 homeserver 配置"
        return 1
    fi
    
    if [ -z "$token" ] && [ -z "$userid" ] && [ -z "$password" ]; then
        echo "错误: 缺少认证信息 (accessToken 或 userId+password)"
        return 1
    fi
    
    return 0
}

matrix_get_homeserver() {
    local profile="$1"
    local config
    
    config=$(matrix_get_config "$profile")
    echo "$config" | python3 -c "import json,sys; print(json.load(sys.stdin).get('homeserver','N/A'))" 2>/dev/null
}

matrix_get_user_id() {
    local profile="$1"
    local config
    
    config=$(matrix_get_config "$profile")
    echo "$config" | python3 -c "import json,sys; print(json.load(sys.stdin).get('userId','N/A'))" 2>/dev/null
}

matrix_is_encrypted() {
    local profile="$1"
    local config
    
    config=$(matrix_get_config "$profile")
    local enc
    enc=$(echo "$config" | python3 -c "import json,sys; print(json.load(sys.stdin).get('encryption',False))" 2>/dev/null)
    [ "$enc" = "True" ]
}