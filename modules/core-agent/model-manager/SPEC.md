# model-manager 功能规范 (Feature Spec)

## 一、 功能定位
负责诊断和修复 OpenClaw 实例的模型配置问题，例如实例意外回退到 `big-pickle` 基础模型、
`opencode-antigravity-auth` 插件认证过期等常见故障。

## 二、 配置层级规则
| 优先级 | 配置文件路径 | 说明 |
|---|---|---|
| 高（优先生效） | `~/.openclaw-<NAME>/openclaw.json` | Pod 本地配置 |
| 低（兜底） | `~/.config/opencode/opencode.json` | 全局默认配置 |

## 三、 常见问题与修复方案
**问题 1：实例模型锁死在 `big-pickle`**
- 原因：`opencode-antigravity-auth` 插件损坏或 Google 认证过期。
- 修复：检查 Pod 本地的插件文件：
  `~/.openclaw/node_modules/opencode-antigravity-auth/dist/src/plugin/storage.js`
  确认第一行为：`import * as lockfile from "proper-lockfile";`（非 default import）。

**问题 2：插件修复后模型仍未更新**
- 修复：在 OpenClaw 客户端执行 `/new` 重置会话上下文，然后询问 Agent："你的完整 model ID 是什么？"

## 四、 Skill 支持
- 遇到模型相关问题时，可加载 `opencode-model-manager` 技能获取详细诊断工作流。