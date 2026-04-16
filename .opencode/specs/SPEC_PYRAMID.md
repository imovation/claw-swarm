# 金字塔架构与 Spec 驱动方法论 (Pyramid Architecture & Spec-Driven Methodology)

> **意图账本双向锚定 (Bidirectional Traceability)**
> 📌 **原始意图溯源**：[2026-04-10 意图 1] 金字塔架构与 Spec 驱动开发方法论 (INTENTS.md)
> 🔄 **修订历史 (Changelog)**：
> - v1 (2026-04-10): 初始创建，确立 System-Module-Feature 三层结构。
> - v2 (2026-04-16): 引入强制自发审计与 AI 原生骨架规范。

---

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
- [ ] **标准 1**：项目结构严格符合 `System -> Module -> Feature -> Code` 分层。
- [ ] **标准 2**：所有的 `SPEC.md` 头部均包含指向 `INTENTS.md` 的双向溯源锚点。
