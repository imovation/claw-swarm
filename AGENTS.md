# Claw-Swarm Agent Entry Point

## 渐进式加载指令

CRITICAL: 本文件使用 `@file` 语法标注按需加载的文档。当任务涉及对应领域时，你必须使用 Read 工具加载引用文件。不要预先加载所有引用 — 仅在任务需要时按需加载。加载后，引用文件的内容视为强制指令，优先级高于默认行为。

## 核心约束

> **先查阅 Spec，再编写代码；修改逻辑前，必先更新 Spec。**
> 开发模式下提出新需求时，必须先创建 REQUESTS.md 记录原始需求（详见 @agents/meta.md）。

## 按需加载索引

| 场景 | 引用文件 | 说明 |
|------|---------|------|
| 协作任务 | @agents/collab.md | 人类-AI 协作准则、意图澄清协议 |
| 复杂任务/排错/需求 | @agents/meta.md | 渐进式检索规范、REQUESTS 流程 |
| 系统架构约束 | @SYSTEM_SPEC.md | 系统层设计原理、模块路由 |

### 模块层与功能层

当任务涉及具体模块时，按以下路径加载对应 Spec：

| 模块 | 模块 Spec | 功能层 |
|------|----------|--------|
| core-agent | @modules/core-agent/MODULE_SPEC.md | dual-mode/, model-manager/ |
| orchestration | @modules/orchestration/MODULE_SPEC.md | config-parser/, reconciler/, pod-provisioner/, templates/, status.py, ps.py, tui.py |
| network-mesh | @modules/network-mesh/MODULE_SPEC.md | proxy-injector/, port-manager/ |
| matrix-channel | @modules/matrix-channel/MODULE_SPEC.md | account-manager/, e2ee-verifier/, device-manager/ |

进入具体功能时，加载对应功能目录下的 @SPEC.md。

## CLI 路由

| 命令 | 路由目标 |
|------|---------|
| `claw apply` | modules/orchestration/reconciler/ |
| `claw status` | modules/orchestration/status.py |
| `claw ps` | modules/orchestration/ps.py |
| `claw tui <NAME>` | modules/orchestration/tui.py |
| `claw port <NAME> <PORT>` | modules/network-mesh/port-manager/ |
| `claw repair <NAME>` | modules/orchestration/pod-provisioner/repair.py |
| `claw rm <NAME>` | modules/orchestration/pod-provisioner/remove.py |
| `claw matrix add` | modules/matrix-channel/account-manager/ |
| `claw matrix verify` | modules/matrix-channel/e2ee-verifier/ |
| `claw matrix devices` | modules/matrix-channel/device-manager/ |
| `claw matrix pairing` | modules/matrix-channel/device-manager/ |