# 金字塔架构与 Spec 驱动方法论 (Pyramid Architecture & Spec-Driven Methodology)

本规格定义了所有基于 Onebot 底座的业务项目应遵循的通用架构分层与开发方法论。

## 一、 金字塔架构 (Pyramid Architecture)

所有业务项目采用"系统-模块-功能"三层金字塔架构，采用渐进式披露机制。

```
System Layer (系统层)
    ↓ 约束
Module Layer (模块层)
    ↓ 约束
Feature Layer (功能层)
    ↓ 实现
Code (代码/提示词)
```

### 各层职责

| 层级 | 位置 | 职责 |
|------|------|------|
| 系统层 | `SYSTEM_SPEC.md` | 全局规范、模块路由、核心准则 |
| 模块层 | `modules/*/MODULE_SPEC.md` | 模块边界、对外接口 |
| 功能层 | `modules/*/*/` | 具体功能实现 |

### 功能层组织 (借鉴 Skill 模式)

```
功能目录/
├── SPEC.md              # 功能规范 (Agent 指令)
├── REQUESTS.md          # 原始需求记录 (人类意图)
├── *.py / *.ts / etc.   # 可执行代码 (主逻辑)
├── scripts/             # 辅助脚本 (可选)
├── templates/           # 模板文件 (可选)
└── references/          # 参考文档 (可选)
```

**触发规则**：开发模式下，用户提出需求时 → 创建/更新 REQUESTS.md → 迭代 SPEC.md → 编写代码

### 约束关系

1. **自顶向下约束**：下层必须服从上层，不可违背核心准则
2. **高内聚低耦合**：同层内 Spec 与代码归置到一起
3. **渐进式披露**：Agent 按需加载，而非一次性加载全部

## 二、 核心 Agent 编程方法论 (AOP)

### Spec 驱动

1. **Spec 驱动 (Spec-Driven)**：Spec 既是给人类看的需求，也是 Agent 必须执行的提示词代码。
2. **高内聚低耦合**：特定功能的 `SPEC.md` 必须与其可执行代码存放在同一目录下，同生同灭。
3. **自顶向下约束**：功能层服从模块层，模块层服从系统层。

### 设计原则

1. **意图导向 (Intent-Driven)**：一切变更始于意图（声明式配置）。代码仅作为实现意图的执行器，意图定义期望状态。
2. **幂等同步 (Idempotent Reconciliation)**：声明式同步操作必须幂等。意图未变时，状态不应发生非必要震荡。
3. **状态闭环 (Closed-Loop)**：系统必须感知当前状态，并始终以弥合与期望状态的差距为唯一任务。
4. **迭代追溯 (Iterative Traceability)**：意图 → Spec → 代码 → 验证，严格按序执行。

## 三、 渐进式加载规范 (Progressive Disclosure)

### Agent 上下文加载流程

```
1. 角色锁定 → 用户 Tab 切换 platform-dev / biz-dev / app
2. 上下文注入 → 各 agent 内部通过 @file 语法按需加载对应层级的 rules 和 spec
3. 任务处理 → 根据 SYSTEM_SPEC.md 路由至 MODULE_SPEC.md → SPEC.md
```

### 各层 Spec 大小限制

| 层级 | 文件 | 建议行数 | 加载时机 | 加载机制 |
|------|------|----------|----------|----------|
| 业务红线 | .opencode/rules/biz-dev-rules.md | ~25 | 业务开发时 | biz-dev 自动注入 |
| 系统架构 | SYSTEM_SPEC.md | < 100 | 业务开发时 | biz-dev 自动注入 |
| 模块层 | MODULE_SPEC.md | < 50 | 任务进入模块 | 显式 Read |
| 功能层 | SPEC.md | < 30 | 理解/修改功能 | 显式 Read |