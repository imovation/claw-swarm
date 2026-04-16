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
    
    # Safe copy: 使用 rsync 实现精准镜像覆盖，清除本地可能残留的“已废弃”文件（如旧版本的 SPEC 或规则）
    # 绝不触碰 opencode.json 和业务级的 Skill 与 INTENTS.md
    rsync -a --delete onebot-main/.opencode/agents/ .opencode/agents/
    rsync -a --delete onebot-main/.opencode/rules/ .opencode/rules/
    rsync -a --delete onebot-main/.opencode/specs/ .opencode/specs/
    rsync -a --delete onebot-main/.opencode/tools/ .opencode/tools/
    
    # 对于 skills 目录，由于可能存在业务级 skill，不能使用 --delete（否则会误删业务 skill），仅做增量覆盖
    cp -r onebot-main/.opencode/skills/* .opencode/skills/
    
    rm -rf onebot-main onebot-main.zip
    echo "✅ Onebot 基建架构已成功更新至最新版本！"

elif [ "$COMMAND" == "push" ]; then
    echo "⬆️ 正在提取当前项目的架构变更，准备反哺至 Onebot 母体..."
    if [ ! -d "$ONEBOT_LOCAL_DIR" ]; then
        echo "❌ 未找到本地 Onebot 母体仓库，路径：$ONEBOT_LOCAL_DIR"
        exit 1
    fi
    
    # 提取核心通用组件回母体 (同样使用 rsync 保持一致性)
    rsync -a --delete .opencode/agents/ "$ONEBOT_LOCAL_DIR/.opencode/agents/"
    rsync -a --delete .opencode/rules/ "$ONEBOT_LOCAL_DIR/.opencode/rules/"
    rsync -a --delete .opencode/specs/ "$ONEBOT_LOCAL_DIR/.opencode/specs/"
    rsync -a --delete .opencode/tools/ "$ONEBOT_LOCAL_DIR/.opencode/tools/"
    
    # 仅反哺（覆写）母体仓库中已经存在的通用 Skill，防止业务专属 Skill 污染母体
    for skill_path in "$ONEBOT_LOCAL_DIR"/.opencode/skills/*; do
        if [ -d "$skill_path" ]; then
            skill_name=$(basename "$skill_path")
            if [ -d ".opencode/skills/$skill_name" ]; then
                cp -r ".opencode/skills/$skill_name" "$ONEBOT_LOCAL_DIR/.opencode/skills/"
            fi
        fi
    done
    echo "💡 提示：如果在此项目中开发了全新的【通用平台 Skill】，请首次手动复制到母体仓库的 skills 目录下，之后便可自动同步。"
    
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
