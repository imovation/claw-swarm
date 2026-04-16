# Claw-Swarm 业务系统架构规范 (System Specification)

> **意图账本双向锚定 (Bidirectional Traceability)**
> 📌 **原始意图溯源**：[2026-04-10 意图 1] 声明式 Kubernetes/Swarm 容器化编排 (INTENTS.md)
> 🔄 **修订历史 (Changelog)**：
> - v1 (2026-04-10): 初始创建，实现声明式自动化。
> - v2 (2026-04-16): 接入 Onebot 底座，精简出纯业务架构。

---

## 1. 核心意图 (Core Intent)
为 OpenClaw 实例提供类 Kubernetes/Swarm 容器化编排能力的底层系统。实现声明式配置管理（基于 `swarm.yaml`）和绝对的 Pod 物理隔离。

## 2. 边界约束 (Constraints)
- 🚫 **物理隔离禁区**：每个实例必须拥有独立的目录、环境变量 (Virtual Home) 和进程生命周期，严禁交叉污染或软链接共享插件。
- 🚫 **业务范畴禁区**：所有平台对齐准则、通用架构方法论（金字塔分层、Spec 驱动、渐进式披露、反哺闭环）均由 `onebot` 的 `.opencode/specs/SPEC_PYRAMID.md` 接管，严禁在此重复声明基建规则。

## 3. 状态契约 (State Contract)
- **前置依赖 (Inputs)**：系统的唯一真理来源为根目录的 `swarm.yaml`。
- **预期副作用 (Side Effects)**：`claw apply` 会根据 YAML 定义的期望状态，通过 Systemd 服务实例化进行精确 Diff 与幂等调和，并自动清理孤儿 Pod（根据 `global.orphan_policy`）。

## 4. 验收标准 (Acceptance Criteria)
- [ ] **标准 1**：所有通过 `bin/claw` 统一路由的命令行工具必须是幂等的。
- [ ] **标准 2**：`claw apply` 连续执行两次，第二次必须输出无状态变更。
- [ ] **标准 3**：TUI 终端必须自动挂载对应实例的专属环境变量。

---

## 5. 业务模块路由索引树 (Routing Map)
> 当 Agent 需要修改具体业务逻辑时，必须先按以下路径读取对应的 `MODULE_SPEC.md` 获取该域的细分意图。

### 5.1 orchestration (核心编排)
- **意图**：解析配置、执行精确状态调和、宿主机 Systemd 驱动。
- `config-parser/`、`reconciler/`、`pod-provisioner/`、`templates/`、`status.py`、`ps.py`、`tui.py`。

### 5.2 network-mesh (网络代理)
- **意图**：全局代理幂等注入、实例端口动态管理。
- `proxy-injector/`、`port-manager/`。

### 5.3 matrix-channel (Matrix 渠道)
- **意图**：E2EE 账号配对审批、设备状态验证与通信。
- `account-manager/`、`e2ee-verifier/`、`device-manager/`。
