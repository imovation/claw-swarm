#!/bin/bash
# 统一入口包装器 (Wrapper) -> 路由至高内聚的工具目录
exec "$(dirname "$0")/.opencode/tools/sync-engine/onebot.sh" "$@"
