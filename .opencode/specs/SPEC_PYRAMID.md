# 金字塔架构与 Spec 驱动方法论 (Pyramid Architecture & Spec-Driven Methodology)

> **意图账本双向锚定 (Bidirectional Traceability)**
> 📌 **原始意图溯源**：[2026-04-10 意图 1] 金字塔架构与 Spec 驱动开发方法论 (INTENTS.md)
> 🔄 **修订历史 (Changelog)**：
> - v1 (2026-04-10): 初始创建，确立 System-Module-Feature 三层结构。
> - v2 (2026-04-16): 引入强制自发审计与 AI 原生骨架规范。

## 1. 核心意图 (Core Intent)
规范所有基于 Onebot 底座的业务项目的开发生命周期，通过“系统-模块-功能”三层金字塔与“渐进式披露”机制，治理大语言模型在处理复杂工程时的幻觉与发散问题。

## 2. 边界约束 (Constraints)
- 🚫 **行为禁区 1**：严禁“先写代码后补文档”。一切执行的起点必须是建立或更新 `SPEC.md`。
- 🚫 **行为禁区 2**：严禁写成无结构的散文。所有 `SPEC.md` 必须强制采用 `SPEC_TEMPLATE.md` 提供的高内聚、结构化 AI 原生骨架。
- 🚫 **行为禁区 3**：严禁未经自检即向用户交付。Agent 必须在生命周期的最后一步，自主执行 `grep`/测试命令验证自己的输出。

## 3. 状态契约 (State Contract)
- **输入 (Inputs)**：业务意图（人类发声或 App 反哺工单）。
- **流转状态 (Execution Lifecycle)**：[立项审查 Spec First] -> [代码实现 Code] -> [强制自检 Proactive Audit] -> [交付闭环 Deliver]。
- **输出 (Side Effects)**：高内聚的功能目录（包含同生同灭的 `SPEC.md` 与可执行代码）。

## 4. 验收标准 (Acceptance Criteria)
- [ ] 标准 1：项目结构严格符合 `System -> Module -> Feature -> Code` 分层。
- [ ] 标准 2：所有的 `SPEC.md` 头部均包含指向 `INTENTS.md` 的双向溯源锚点。

---

## 5. 架构细节实现 (Implementation Details)

### 金字塔架构 (Pyramid Architecture)

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
├── INTENTS.md          # 原始意图记录 (人类意图)
├── *.py / *.ts / etc.   # 可执行代码 (主逻辑)
├── scripts/             # 辅助脚本 (可选)
├── templates/           # 模板文件 (可选)
└── references/          # 参考文档 (可选)
```

**触发规则**：开发模式下，用户提出需求时 → 创建/更新 INTENTS.md → 迭代 SPEC.md → 编写代码

### 约束关系

1. **自顶向下约束**：下层必须服从上层，不可违背核心准则
2. **高内聚低耦合**：同层内 Spec 与代码归置到一起
3. **渐进式披露**：Agent 按需加载，而非一次性加载全部

## 二、 核心 Agent 编程方法论 (AOP)

### Spec 驱动
4. **双向锚定溯源 (Bidirectional Traceability)**：每个功能或模块的 `SPEC.md` 文件头部，必须强制声明它响应了 `INTENTS.md` 中的哪一条原始人类意图。让后来接手的 Agent 顺藤摸瓜，随时能够重构甚至推翻旧代码。
5. **AI 原生骨架 (AI-Native Template)**：所有的 `SPEC.md` 文件绝不能写成随意的散文，必须强制采用 `.opencode/specs/SPEC_TEMPLATE.md` 提供的标准化骨架（核心意图、边界约束、状态契约、验收标准），以便于系统化的语义解析。

1. **Spec 驱动 (Spec-Driven)**：Spec 既是给人类看的需求，也是 Agent 必须执行的提示词代码。
2. **高内聚低耦合**：特定功能的 `SPEC.md` 必须与其可执行代码存放在同一目录下，同生同灭。
3. **自顶向下约束**：功能层服从模块层，模块层服从系统层。

### 智能体执行生命周期 (Agent Execution Lifecycle)
为了根治 AI 追求快速回复而跳过架构规范的“惰性”，任何基于本底座的 Agent 必须严格遵循以下**不可逾越的四步生命周期**。任何试图跳过步骤（如跳过 Spec 直接写代码，或跳过自检直接交付）的行为，均视为严重违反架构纪律：
1. **立项审查 (Spec First)**：无论任务多小，必须先查阅或创建对应的 `SPEC.md`。一切执行的起点是更新文档，而非触碰代码。
2. **代码实现 (Code)**：严格在 Spec 划定的边界内进行代码实现。
3. **强制自检 (Proactive Audit)**：**绝不等待用户提醒！** 在代码完成后，Agent 必须自发调用系统工具（`grep`, `ls`, 等）进行深度自检，核查：文件是否高内聚？是否违背了其他层级的红线？是否遗留了业务污染？
4. **交付闭环 (Deliver)**：将自检结果与任务完成状态一并向用户汇报。

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
## 四、 底座自身的架构自洽 (Meta-Architecture Self-Consistency)

> “制造尺子的尺子，自己必须是直的。”

虽然本规格主要约束【业务项目】，但 Onebot 作为基建底座本身，也必须受到金字塔架构“精神内核”的绝对约束：

1. **物理结构的变通**：Onebot 的物理目录（`.opencode/rules/`, `agents/`）受限于底层 Opencode 运行引擎的强解析规则，无法强行套用业务层的 `modules/` 结构。这是向物理现实的妥协。
2. **精神内核的绝对服从**：Onebot 内部的任何工程化能力（如通用工具 Tool、通用技能 Skill）必须严格遵循**高内聚微模块**模式。
   - **反面教材**：在项目根目录随意丢弃一个 `script.sh`，并将它的说明文档写在 `specs/SCRIPT_SPEC.md` 里（这违背了高内聚，造成了代码与文档的撕裂）。
   - **正确示范（吃自己的狗粮）**：建立 `.opencode/tools/sync-engine/` 目录，将核心脚本 `onebot.sh` 和它的规格文档 `SPEC.md` 紧密绑定在同一目录下，同生同灭。在项目根目录仅保留一个起到路由分发作用的 Wrapper 壳子（遵循统一 CLI 入口规范）。

任何 Platform Dev 在扩展 Onebot 基建时，若违背上述“高内聚低耦合”与“统一路由入口”的内核精神，即视为破坏了底座的架构合法性。
