#!/bin/bash
# Onebot Meta-Architecture Sync Tool (双向同步引擎)

COMMAND=$1
ONEBOT_REPO="https://github.com/imovation/onebot/archive/refs/heads/main.zip"
ONEBOT_LOCAL_DIR="$HOME/opencode-workspace/onebot"

print_help() {
    echo "Onebot 同步引擎 (Sync Tool)"
    echo "用法: ./onebot.sh [pull | push]"
    echo ""
    echo "  pull  - (向下同步) 从 GitHub 拉取最新的 Onebot 核心架构，安全覆盖当前项目的 .opencode 目录。"
    echo "  push  - (向上反哺) 将当前项目中经过业务验证的 .opencode 核心架构，反向推送合并至本地 Onebot 母体仓库并提交。"
}

if [ "$COMMAND" == "pull" ]; then
    echo "⬇️ 正在从 GitHub 拉取最新的 Onebot 架构基建..."
    curl -sL $ONEBOT_REPO -o onebot-main.zip
    unzip -q onebot-main.zip
    
    # Safe copy: 只覆盖核心通用组件，绝不触碰 opencode.json 和业务级的 Skill
    cp -r onebot-main/.opencode/agents/* .opencode/agents/
    cp -r onebot-main/.opencode/rules/* .opencode/rules/
    cp -r onebot-main/.opencode/specs/* .opencode/specs/
    cp -r onebot-main/.opencode/skills/deep-cure .opencode/skills/
    
    rm -rf onebot-main onebot-main.zip
    echo "✅ Onebot 基建架构已成功更新至最新版本！"

elif [ "$COMMAND" == "push" ]; then
    echo "⬆️ 正在提取当前项目的架构变更，准备反哺至 Onebot 母体..."
    if [ ! -d "$ONEBOT_LOCAL_DIR" ]; then
        echo "❌ 未找到本地 Onebot 母体仓库，路径：$ONEBOT_LOCAL_DIR"
        exit 1
    fi
    
    # 提取核心通用组件回母体
    cp -r .opencode/agents/* "$ONEBOT_LOCAL_DIR/.opencode/agents/"
    cp -r .opencode/rules/* "$ONEBOT_LOCAL_DIR/.opencode/rules/"
    cp -r .opencode/specs/* "$ONEBOT_LOCAL_DIR/.opencode/specs/"
    cp -r .opencode/skills/deep-cure "$ONEBOT_LOCAL_DIR/.opencode/skills/"
    
    cd "$ONEBOT_LOCAL_DIR"
    git add .opencode/
    
    if git diff --cached --quiet; then
        echo "⚠️ Onebot 核心基建没有任何变更，无需提交。"
    else
        git commit -m "feat: upstream architecture evolution from downstream project"
        git push
        echo "✅ 架构变更已成功提取并反哺至 Onebot 远端母体！"
    fi
else
    print_help
fi
