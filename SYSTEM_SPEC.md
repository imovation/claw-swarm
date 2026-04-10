# Claw-Swarm 系统层架构规范 (System Specification)

## 一、 核心愿景与架构准则

Claw-Swarm 是一个为 OpenClaw 实例提供类 Kubernetes/Swarm 容器化编排能力的底座系统。

1. **声明式意图 (Declarative Intent)**：系统的唯一真理来源为 `swarm.yaml`。一切变更均由预期状态驱动。
2. **绝对物理隔离 (Pod Isolation)**：每个实例必须拥有独立的目录、环境变量 (Virtual Home) 和进程生命周期，严禁交叉污染。

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
| 系统层 | `SYSTEM_SPEC.md`, `AGENTS.md` | 全局规范、模块路由、核心准则 |
| 模块层 | `modules/*/MODULE_SPEC.md` | 模块边界、对外接口 |
| 功能层 | `modules/*/*/SPEC.md` + 代码 | 具体功能实现 |

### 约束关系

1. **自顶向下约束**：下层必须服从上层，不可违背核心准则
2. **高内聚低耦合**：同层内 Spec 与代码归置到一起
3. **渐进式披露**：Agent 按需加载，而非一次性加载全部

## 二.一、 核心开发规范：面向 Agent 编程 (AOP)

本项目采用大模型友好的开发范式，任何修改**必须**遵循以下准则：
1. **Spec 驱动 (Spec-Driven)**：单一事实源。任何代码修改前，必须先更新或创建对应的 `SPEC.md`。Spec 既是给人类看的需求，也是 Agent 必须执行的提示词代码。
2. **高内聚低耦合**：特定功能的 `SPEC.md` 必须与其相关的可执行代码（如 `.py`, `.sh`, `.j2`）存放在同一层级目录下，同生同灭。
3. **自顶向下约束**：功能层 (Feature) 必须服从模块层 (Module)，模块层必须服从本文件（系统层 System）。下层绝不可违背上层的核心准则与边界约束。

## 二.二、 核心开发原则

1. **意图导向 (Intent-Driven)**：一切变更始于意图（YAML/Config）。代码不应包含独立的业务逻辑，而应仅作为实现意图的"执行器（Actuator）"。意图定义了系统的**期望状态 (Desired State)**。

2. **幂等同步 (Idempotent Reconciliation)**：`claw apply` 必须是幂等的。无论运行多少次，只要意图未变，系统的物理状态就不应发生非必要的震荡或副作用。

3. **状态闭环 (Closed-Loop)**：系统必须具备感知"当前物理状态（Actual State）"的能力，并始终以**弥合与"期望状态"之间的差距**为唯一任务。

4. **迭代追溯 (Iterative Traceability)**：所有优化和功能扩展必须遵循以下严格顺序：
**迭代意图 (Update Spec) -> 迭代功能 (Update Code) -> 验证功能 (Verify)**
严禁在未更新 Spec 的前提下进行功能"偷跑"。

## 二.三、 工程质量准则

1. **治本原则 (Heal the Source, Not the Symptom)**：绝对禁止"治标不治本"！当系统出现非预期行为时，Agent **必须**首先回溯并定位产生该问题的**唯一源头**，而不是在链路末端通过脚本包装、手动导出或强制清理等手段"掩盖"症状。

2. **最小干预与 KISS 约束**：如果存在"修改一行原生配置"与"增加一段逻辑脚本"两种方案，Agent **必须**无条件选择前者。**复杂度是错误的避难所**。

3. **强制闭环验证**：任何修复任务的"成功"定义必须包含协议层/功能层的端到端验证。仅凭进程状态（Active/Running）判定成功将被视为严重失职。

4. **怀疑与回滚逻辑**：若补丁导致了二次故障，Agent 必须立即撤销所有临时逻辑，重新启动根源分析流程，严禁"补丁叠补丁"。

---

## 三、 渐进式加载规范 (Progressive Disclosure)

### Agent 启动流程

```
1. 初始化 → 读取 agents/gatekeeper.md (~30行)
2. 模式锁定 → 根据用户选择进入对应模式
3. 任务处理 → 按需加载 SYSTEM_SPEC.md → MODULE_SPEC.md → SPEC.md
```

### 各层 Spec 大小限制

| 层级 | 文件 | 建议行数 | 加载时机 |
|------|------|----------|----------|
| 系统层 | SYSTEM_SPEC.md | < 100 | 按需 |
| 模块层 | MODULE_SPEC.md | < 50 | 任务进入模块 |
| 功能层 | SPEC.md | < 30 | 理解/修改功能 |
| Agent 入口 | agents/gatekeeper.md | ~30 | 初始化 |
| Agent 协作 | agents/collab.md | ~30 | 复杂任务 |
| Agent 导航 | agents/meta.md | ~40 | 排错/开发 |

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