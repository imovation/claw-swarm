# Claw-Swarm 系统层架构规范 (System Specification)

## 一、 核心愿景与架构准则

Claw-Swarm 是一个为 OpenClaw 实例提供类 Kubernetes/Swarm 容器化编排能力的底座系统。

1. **声明式意图 (Declarative Intent)**：系统的唯一真理来源为 `swarm.yaml`。一切变更均由预期状态驱动。
2. **绝对物理隔离 (Pod Isolation)**：每个实例必须拥有独立的目录、环境变量 (Virtual Home) 和进程生命周期，严禁交叉污染。
3. **平台对齐 (Platform Alignment)**：本项目以 opencode 为运行平台（Agent 入口、规则注入、权限控制、Skill 发现、命令注册均依赖 opencode 原生机制）。任何项目层面的功能或约束，必须先查阅 https://opencode.ai/docs/ 确认平台是否原生支持，只有原生不支持时才另设方案。

---

## 二、 金字塔架构 (Pyramid Architecture)

本项目采用"系统-模块-功能"三层金字塔架构，采用渐进式披露机制。

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
| 系统层 | `SYSTEM_SPEC.md`, `AGENTS.md`, `agents/` | 全局规范、模块路由、核心准则 |
| 模块层 | `modules/*/MODULE_SPEC.md` | 模块边界、对外接口 |
| 功能层 | `modules/*/*/` | 具体功能实现 |

### 功能层组织 (借鉴 Skill 模式)

```
功能目录/
├── SPEC.md              # 功能规范 (Agent 指令)
├── REQUESTS.md          # 原始需求记录 (人类意图)
├── *.py                 # 可执行代码 (主逻辑)
├── scripts/             # 辅助脚本 (可选)
├── templates/           # 模板文件 (可选)
└── references/          # 参考文档 (可选)
```

**触发规则**：开发模式下，用户提出需求时 → 创建/更新 REQUESTS.md → 迭代 SPEC.md → 编写代码

### 约束关系

1. **自顶向下约束**：下层必须服从上层，不可违背核心准则
2. **高内聚低耦合**：同层内 Spec 与代码归置到一起
3. **渐进式披露**：Agent 按需加载，而非一次性加载全部

## 二.一 ~ 二.三 核心开发规范

> 6 条始终生效的硬规则已提取为 @agents/core-rules.md（通过 opencode.json 每次会话自动注入）。
> 以下保留设计原理供深入理解。

### 面向 Agent 编程 (AOP)

1. **Spec 驱动 (Spec-Driven)**：Spec 既是给人类看的需求，也是 Agent 必须执行的提示词代码。
2. **高内聚低耦合**：特定功能的 `SPEC.md` 必须与其可执行代码存放在同一目录下，同生同灭。
3. **自顶向下约束**：功能层服从模块层，模块层服从系统层。

### 设计原则

1. **意图导向 (Intent-Driven)**：一切变更始于意图（YAML/Config）。代码仅作为实现意图的执行器，意图定义期望状态。
2. **幂等同步 (Idempotent Reconciliation)**：`claw apply` 必须幂等。意图未变时，状态不应发生非必要震荡。
3. **状态闭环 (Closed-Loop)**：系统必须感知当前状态，并始终以弥合与期望状态的差距为唯一任务。
4. **迭代追溯 (Iterative Traceability)**：意图 → Spec → 代码 → 验证，严格按序执行。

---

## 三、 渐进式加载规范 (Progressive Disclosure)

### Agent 启动流程

```
1. 始终注入（opencode.json instructions）→ gatekeeper.md + core-rules.md
2. 模式锁定 → 用户 Tab 切换 dev-mode / app-mode agent（权限由 opencode permission 机械强制）
3. 任务处理 → 按需 AGENTS.md @file 引导 → SYSTEM_SPEC.md → MODULE_SPEC.md → SPEC.md
```

始终注入的内容（无需手动 Read）：
- `agents/gatekeeper.md` — 双轨模式守门人
- `agents/core-rules.md` — 6 条核心开发红线

opencode agent 选择（Tab 键切换）：
- `dev-mode` — 完整权限，遵循 Spec 驱动 + git 闭环
- `app-mode` — 所有编辑/命令需用户确认，禁止修改源码

### 各层 Spec 大小限制

| 层级 | 文件 | 建议行数 | 加载时机 | 加载机制 |
|------|------|----------|----------|----------|
| 守门人 | agents/gatekeeper.md | ~11 | 每次会话 | opencode.json instructions 自动注入 |
| 核心红线 | agents/core-rules.md | ~25 | 每次会话 | opencode.json instructions 自动注入 |
| 系统层 | SYSTEM_SPEC.md | < 100 | 按需 | AGENTS.md @file 引导 Read |
| 模块层 | MODULE_SPEC.md | < 50 | 任务进入模块 | AGENTS.md @file 引导 Read |
| 功能层 | SPEC.md | < 30 | 理解/修改功能 | AGENTS.md @file 引导 Read |

---

## 四、 CLI 入口层
**统一入口 `bin/claw`**：项目采用 kubectl 风格的子命令路由。
```bash
claw apply               # modules/orchestration/reconciler/
claw status              # modules/orchestration/status.py
claw ps                  # modules/orchestration/ps.py
claw tui <NAME>          # modules/orchestration/tui.py
claw port <NAME> <PORT>  # modules/network-mesh/port-manager/
claw repair <NAME>       # modules/orchestration/pod-provisioner/repair.py
claw rm <NAME>           # modules/orchestration/pod-provisioner/remove.py
claw matrix add          # modules/matrix-channel/account-manager/
claw matrix verify       # modules/matrix-channel/e2ee-verifier/
claw matrix devices      # modules/matrix-channel/device-manager/
claw matrix pairing      # modules/matrix-channel/device-manager/
```

## 五、 模块路由索引树 (Routing Map)
*Agent 提示：当需要了解或修改某一具体领域逻辑时，请严格按以下路径寻找对应的 `MODULE_SPEC.md` 以获取上下文。*

### 1. core-agent 模块 ✅
负责 Agent 交互逻辑、双轨模式 (Dual-Mode) 的控制、以及用户 Issue 提报与反馈流程。
- `dual-mode/` — 双轨模式核心逻辑
- `model-manager/` — 模型配置诊断与修复

### 2. orchestration 模块 ✅
负责读取与解析 `swarm.yaml`，执行状态对比 (Diff) 并在宿主机驱动 Systemd 进行最终的调和 (Reconciliation)。
- `config-parser/` — 配置解析与校验
- `reconciler/` — 调和控制器 (精确 Diff + dry-run)
- `pod-provisioner/` — Pod 供应器 (provision.py, repair.py, remove.py)
- `status.py` — 集群状态看板
- `ps.py` — 精细进程监控
- `tui.py` — 交互式终端
- `templates/` — Jinja2 模板引擎

### 3. network-mesh 模块 ✅
负责全局代理配置注入、端口分配与实例网络通信机制。
- `proxy-injector/` — 代理环境变量幂等注入
- `port-manager/` — 端口变更管理

### 4. matrix-channel 模块 ✅
负责 Matrix E2EE 加密、账号认证、群组和私信等渠道通讯保障。
- `account-manager/` — 账号凭证写入
- `e2ee-verifier/` — E2EE 加密状态验证
- `device-manager/` — 设备与配对管理