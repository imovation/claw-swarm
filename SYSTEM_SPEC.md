# Claw-Swarm 业务系统架构规范 (System Specification)

> **意图账本双向锚定 (Bidirectional Traceability)**
> 📌 **原始意图溯源**：[2026-04-10 意图 1] 声明式 Kubernetes/Swarm 容器化编排 (INTENTS.md)
> 🔄 **修订历史 (Changelog)**：
> - v1 (2026-04-10): 初始创建，实现声明式自动化。
> - v2 (2026-04-16): 接入 Onebot 底座，精简出纯业务架构。

## 1. 核心意图 (Core Intent)
为 OpenClaw 实例提供类 Kubernetes/Swarm 容器化编排能力的底层系统。实现声明式配置管理（基于 `swarm.yaml`）和绝对的 Pod 物理隔离。

## 2. 边界约束 (Constraints)
- 🚫 **物理隔离禁区**：每个实例必须拥有独立的目录、环境变量 (Virtual Home) 和进程生命周期，严禁交叉污染或软链接共享插件。
- 🚫 **业务范畴禁区**：所有平台对齐准则、通用架构方法论（金字塔分层、Spec 驱动、渐进式披露、反哺闭环）均由 `onebot` 的 `.opencode/specs/SPEC_PYRAMID.md` 接管，严禁在此重复声明基建规则。

## 3. 状态契约 (State Contract)
- **前置依赖 (Inputs)**：系统的唯一真理来源为根目录的 `swarm.yaml`。
- **预期副作用 (Side Effects)**：`claw apply` 会根据 YAML 定义的期望状态，通过 Systemd 服务实例化进行精确 Diff 与幂等调和，并自动清理孤儿 Pod。

## 4. 验收标准 (Acceptance Criteria)
- [ ] 标准 1：所有通过 `bin/claw` 统一路由的命令行工具必须是幂等的。
- [ ] 标准 2：`claw apply` 连续执行两次，第二次必须输出无状态变更。
- [ ] 标准 3：TUI 终端必须自动挂载对应实例的专属环境变量。

---

## 5. 架构细节实现 (Implementation Details)

### 核心愿景与架构准则

Claw-Swarm 是一个为 OpenClaw 实例提供类 Kubernetes/Swarm 容器化编排能力的底座系统。

1. **声明式意图 (Declarative Intent)**：系统的唯一真理来源为 `swarm.yaml`。一切变更均由预期状态驱动。
2. **绝对物理隔离 (Pod Isolation)**：每个实例必须拥有独立的目录、环境变量 (Virtual Home) 和进程生命周期，严禁交叉污染。

> 平台对齐准则（opencode 原生优先）和通用架构方法论（金字塔分层、Spec 驱动、渐进式披露等）已提取至 `.opencode/specs/SPEC_PYRAMID.md`，通过 biz-dev agent 自动注入。

---

## 二、 CLI 入口层

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

## 三、 模块路由索引树 (Routing Map)
*Agent 提示：当需要了解或修改某一具体领域逻辑时，请严格按以下路径寻找对应的 `MODULE_SPEC.md` 以获取上下文。*

### 1. orchestration 模块 ✅
负责读取与解析 `swarm.yaml`，执行状态对比 (Diff) 并在宿主机驱动 Systemd 进行最终的调和 (Reconciliation)。
- `config-parser/` — 配置解析与校验
- `reconciler/` — 调和控制器 (精确 Diff + dry-run)
- `pod-provisioner/` — Pod 供应器 (provision.py, repair.py, remove.py)
- `status.py` — 集群状态看板
- `ps.py` — 精细进程监控
- `tui.py` — 交互式终端
- `templates/` — Jinja2 模板引擎

### 2. network-mesh 模块 ✅
负责全局代理配置注入、端口分配与实例网络通信机制。
- `proxy-injector/` — 代理环境变量幂等注入
- `port-manager/` — 端口变更管理

### 3. matrix-channel 模块 ✅
负责 Matrix E2EE 加密、账号认证、群组和私信等渠道通讯保障。
- `account-manager/` — 账号凭证写入
- `e2ee-verifier/` — E2EE 加密状态验证
- `device-manager/` — 设备与配对管理