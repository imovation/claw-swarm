# 🛑 Claw-Swarm Agent 入口 (Agent Entry Point)

本文件是 Agent 的总入口，仅负责引导。根据任务类型按需加载子文档。

---

## 快速索引

| 场景 | 加载文件 | 说明 |
|------|---------|------|
| 新会话初始化 | `agents/gatekeeper.md` | 双轨模式拦截 (~30行) |
| 协作任务 | `agents/collab.md` | 人类-AI 协作准则 |
| 复杂任务/排错 | `agents/meta.md` | 渐进式检索规范 |
| 模块层 | `modules/*/MODULE_SPEC.md` | 模块边界 |
| 功能层 | `modules/*/*/SPEC.md` | 功能规范 |

---

## 初始化流程

1. 读取 `agents/gatekeeper.md` - 执行双轨模式拦截
2. 根据用户选择，锁定会话模式
3. 仅在需要时按需加载其他文档

---

## 核心约束

> **先查阅 Spec，再编写代码；修改逻辑前，必先更新 Spec。**

详细规范请参阅 `agents/meta.md`。