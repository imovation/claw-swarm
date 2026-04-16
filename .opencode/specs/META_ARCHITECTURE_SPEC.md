# 通用智能体底座系统架构规格 (Meta-Architecture Spec)

> **意图账本双向锚定 (Bidirectional Traceability)**
> 📌 **原始意图溯源**：[2026-04-14 意图 1] 平台与业务解耦的三态智能体架构 (INTENTS.md)
> 🔄 **修订历史 (Changelog)**：
> - v1 (2026-04-14): 初始创建，剥离双轨模式，建立三态演进模型。
> - v2 (2026-04-16): 确立“诊因向事实，求解分内外”认知边界。

---

## 1. 核心意图 (Core Intent)
将 Agent 项目的职责从单体结构（Monolith）拆分为 **"三态演进模型" (3-Stage Agent Continuum)**，彻底解决上下文污染（Context Poisoning）问题。使 `.opencode/` 成为一个高度内聚、可复用的"通用 Agent 兵工厂"底座。

## 2. 边界约束 (Constraints)
- 🚫 **物理隔离禁区**：Platform Dev 严禁修改业务代码；Biz Dev 严禁修改 `.opencode/` 基建规则；App 绝对只读，严禁修改任何源码。
- 🚫 **认知隔离禁区**：诊断根因必须“只向事实”；求解方案时，Dev 模式必须首选“向内求解”（改代码），App 模式必须首选“向外求解”（改环境/提工单），严禁越界代庖。
- 🚫 **架构自洽禁区**：Onebot 自身的组件必须采用高内聚微模块形式，严禁在根目录散落孤魂野鬼脚本。

## 3. 状态契约 (State Contract)
- **前置依赖 (Inputs)**：底层的 `opencode.json` 仅保留极简物理配置。
- **预期副作用 (Side Effects)**：用户按 Tab 键切换 Agent 时，系统通过 `@file` 精确注入对应层级的红线规则（Rules）与系统架构（Specs）。
- **反哺流转 (Feedback Loop)**：App 报错 -> 写入 `INTENTS.md` -> 交给 Biz Dev；Biz Dev 受限 -> 写入 `.opencode/INTENTS.md` -> 交给 Platform Dev。

## 4. 验收标准 (Acceptance Criteria)
- [ ] **标准 1**：在 App 模式下要求修改代码，Agent 必须明确拒绝并提示用户提交工单。
- [ ] **标准 2**：`opencode.json` 中不存在任何与特定业务相关的 `instructions`。
