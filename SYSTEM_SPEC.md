# Claw-Swarm 系统层架构规范 (System Specification)

## 一、 核心愿景与架构准则
Claw-Swarm 是一个为 OpenClaw 实例提供类 Kubernetes/Swarm 容器化编排能力的底座系统。
1. **声明式意图 (Declarative Intent)**：系统的唯一真理来源为 `swarm.yaml`。一切变更均由预期状态驱动。
2. **绝对物理隔离 (Pod Isolation)**：每个实例必须拥有独立的目录、环境变量 (Virtual Home) 和进程生命周期，严禁交叉污染。

## 二、 核心开发规范：面向 Agent 编程 (AOP)
本项目采用大模型友好的开发范式，任何修改**必须**遵循以下准则：
1. **Spec 驱动 (Spec-Driven)**：单一事实源。任何代码修改前，必须先更新或创建对应的 `SPEC.md`。Spec 既是给人类看的需求，也是 Agent 必须执行的提示词代码。
2. **高内聚低耦合**：特定功能的 `SPEC.md` 必须与其相关的可执行代码（如 `.py`, `.sh`, `.j2`）存放在同一层级目录下，同生同灭。
3. **自顶向下约束**：功能层 (Feature) 必须服从模块层 (Module)，模块层必须服从本文件（系统层 System）。下层绝不可违背上层的核心准则与边界约束。

## 三、 CLI 入口层
**统一入口 `bin/claw`**：项目采用 kubectl 风格的子命令路由。
```bash
claw apply               # orchestration/reconciler
claw status              # orchestration
claw tui <NAME>          # orchestration
claw port <NAME> <PORT>  # network-mesh/port-manager
claw repair <NAME>       # orchestration/pod-provisioner
claw rm <NAME>           # orchestration/pod-provisioner
claw ps                  # orchestration
claw matrix add          # matrix-channel/account-manager
claw matrix verify       # matrix-channel/e2ee-verifier
claw matrix devices      # matrix-channel/device-manager
claw matrix pairing      # matrix-channel/device-manager
```

## 四、 模块路由索引树 (Routing Map)
*Agent 提示：当需要了解或修改某一具体领域逻辑时，请勿盲目搜索代码，请严格按以下路径寻找对应的 `MODULE_SPEC.md` 以获取上下文。*

### 1. core-agent 模块 ✅
负责 Agent 交互逻辑、双轨模式 (Dual-Mode) 的控制、以及用户 Issue 提报与反馈流程。
- `dual-mode/` — 双轨模式核心逻辑 ✅
- `model-manager/` — 模型配置诊断与修复 ✅

### 2. orchestration 模块 ✅
负责读取与解析 `swarm.yaml`，执行状态对比 (Diff) 并在宿主机驱动 Systemd 进行最终的调和 (Reconciliation)。
- `config-parser/` ✅ — 配置解析与校验 (Pydantic 风格校验 + SecretRef)
- `reconciler/` ✅ — 调和控制器 (精确 Diff + dry-run)
- `pod-provisioner/` ✅ — Pod 供应器 (物理创建、环境注入、插件同步)
- `templates/` ✅ — Jinja2 模板引擎 (Systemd 服务模板、openclaw.json 模板)

### 3. network-mesh 模块 ✅
负责全局代理配置注入、端口分配与实例网络通信机制。
- `proxy-injector/` ✅ — 代理环境变量幂等注入
- `port-manager/` ✅ — 端口变更管理 (冲突检测 + swarm.yaml 同步)

### 4. matrix-channel 模块 ✅
负责 Matrix E2EE 加密、账号认证、群组和私信等渠道通讯保障。
- `account-manager/` ✅ — 账号凭证写入 (SecretRef 支持)
- `e2ee-verifier/` ✅ — E2EE 加密状态验证 (status/bootstrap/backup)
- `device-manager/` ✅ — 设备与配对管理 (list/prune/pairing)

## 五、 遗留文件标记规范
- **`[已废弃 DEPRECATED]`**：核心逻辑已重构至 modules/，仅作兼容保留。

### 遗留文件清单 (已废弃)
| 文件 | 归属模块层 |
|---|---|
| `bin/clawctl` | orchestration/pod-provisioner |
| `bin/claw-apply` | orchestration/reconciler |
| `bin/claw-port` | network-mesh/port-manager |
| `bin/claw-matrix-add` | matrix-channel/account-manager |
| `bin/claw-matrix-verify` | matrix-channel/e2ee-verifier |
| `bin/claw-matrix-devices` | matrix-channel/device-manager |
| `bin/claw-matrix-pairing` | matrix-channel/device-manager |
| `lib/pod_utils.py/sh` | orchestration/config-parser + pod-provisioner |
| `lib/matrix_utils.sh` | matrix-channel/account-manager |

*(注：所有遗留脚本已标记为废弃，但仍可通过 bin/claw 路由回退调用。)*