# 需求记录 (Requests)

## 需求 1: 平台与业务解耦的三态智能体架构 (Meta-Architecture)

**日期**: 2026-04-14
**状态**: 规划中
**提出者**: User

**背景**:
当前 `claw-swarm` 项目的 opencode 配置存在严重的“上下文污染（Context Poisoning）”与角色错位问题。全局的 `instructions` 强制将开发红线（如 Spec 驱动、治本原则）注入到了所有模式（包括仅仅作为用户交互窗口的 App 模式）中。同时，平台底座（通用的 Agent 规范、工具）与具体的业务逻辑（OpenClaw 实例编排）耦合在一起，导致复用性差且经常互相干扰（如 deep-cure 方法论在业务代码修改时造成过度防御）。

**需求描述**:
构建以 opencode 为基座的通用智能体解决方案，从【平台/业务】与【开发/应用】两个维度进行正交解耦，演进为三态模型：
1. **平台开发 Agent (Platform Dev)**: 负责构建和维护底层框架（`.opencode/` 下的 rules, skills, agents），不涉足具体业务逻辑。
2. **业务开发 Agent (Biz Dev)**: 负责实现具体的业务逻辑（`claw-swarm` 的编排功能），受平台层开发红线的约束。
3. **业务应用 Agent (App)**: 纯粹的终端用户交互窗口，隔离所有开发相关的上下文，仅保留操作限制和用户手册，负责安全执行系统命令。

**核心目标**:
- **瘦配置，胖角色**: 移除 `opencode.json` 中全局冗余指令，将具体的上下文和规则下放到独立的 agent prompt 中。
- **上下文按需加载**: 利用 `@file` 语法，针对上述三个 Agent 分别注入对应层级的规则（Rules）、工具（Skills）和规格（Specs）。
- **完全解耦**: 使得 `claw-swarm` 的业务代码和 `.opencode/` 基础设施可以物理分离，`.opencode/` 目录本身成为一个可复用的"通用底座模板"。

**关联 Spec**: `.opencode/specs/META_ARCHITECTURE_SPEC.md`

## 需求 2: 跨态反哺闭环机制 (Feedback Loop)
**核心目标**: 建立自下而上的需求投递流，防止不同角色越权，同时保持系统的自进化能力。
1. **App 反哺 Biz Dev**: 用户在 App 模式反馈 Bug 或需求时，App Agent 必须记录需求到根目录 `REQUESTS.md`，并提示用户 Tab 切换至 `biz-dev` 模式处理。
2. **Biz Dev 反哺 Platform Dev**: Biz Dev 开发遇到平台工具/规则限制时，记录需求到 `.opencode/REQUESTS.md`，并提示用户切换至 `platform-dev` 模式更新基建。
