# 系统导航与渐进式检索规范 (Meta-Prompt)

**核心原理**：本项目采用"系统-模块-功能"三层金字塔架构。Agent 应采用"按需加载 (Progressive Disclosure)"工作流，避免上下文过载。

## 三层加载机制

### 第一阶：系统层 (System)
**触发条件**：新会话初始化
**加载内容**：守门人 (`agents/gatekeeper.md`) 和核心红线 (`agents/core-rules.md`) 由 opencode.json 自动注入，无需手动加载。

```bash
# Agent 初始指令（自动完成）
1. 守门人拦截 + 核心红线 — opencode.json instructions 自动注入
2. 模式锁定 — 根据用户选择进入对应模式
```

### 第二阶：模块层 (Module)
**触发条件**：用户进入具体任务领域（如 Matrix 配置、集群管理等）
**加载内容**：读取 `SYSTEM_SPEC.md` 找到对应模块 → 加载 `modules/*/MODULE_SPEC.md`

### 第三阶：功能层 (Feature)
**触发条件**：需要修改或理解具体功能时
**加载内容**：进入功能目录 → 读取 `SPEC.md` + 代码

## 检索路径

```
新任务 → 
  SYSTEM_SPEC.md (模块路由) → 
    MODULE_SPEC.md (模块边界) → 
      SPEC.md + code (功能实现)
```

## 关键约束

1. **禁止盲目编程**：禁止依赖模型记忆执行任务，必须先加载对应层级的 Spec
2. **先 Spec 再代码**：修改功能前必须先更新对应功能的 SPEC.md
3. **Skill 按需加载**：仅在规范明确要求时使用 `skill` 工具加载特定技能
4. **原始需求记录**：开发模式下，用户提出功能需求时，必须先创建 REQUESTS.md 记录原始需求，再迭代 SPEC.md，最后编写代码

## 原始需求记录规范 (REQUESTS.md)

**触发条件**：开发模式下，用户提出新功能需求或功能变更

**记录流程**：
```
用户提出需求 → 创建/更新 REQUESTS.md → 迭代 SPEC.md → 编写代码
```

### 三层 REQUESTS.md 定位

| 层级 | 位置 | 记录内容 |
|------|------|----------|
| 系统层 | `./REQUESTS.md` | 跨模块架构变更、系统规范迭代 |
| 模块层 | `modules/*/REQUESTS.md` | 模块级需求、模块接口变更 |
| 功能层 | `modules/*/*/REQUESTS.md` | 功能级需求、功能实现变更 |

### 触发规则

- **系统级需求** → 根目录 `./REQUESTS.md`
- **模块级需求** → 对应模块的 `REQUESTS.md`
- **功能级需求** → 对应功能目录的 `REQUESTS.md`

### REQUESTS.md 模板

```markdown
## [日期] 第N次迭代
**需求来源**：人类直接描述 / 人类反馈 / Issue
**需求**：具体描述
**期望结果**：预期输出或行为
**关联 Spec**：对应的 SPEC.md 版本
```

---

**加载时机**：当用户提出复杂任务时才按需加载（帮助文档性质）