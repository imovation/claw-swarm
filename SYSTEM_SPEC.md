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
claw apply / status / tui / port / repair / rm / ps
claw matrix add / verify / devices / pairing / profile / direct
```

## 四、 模块路由索引树 (Routing Map)
*Agent 提示：当需要了解或修改某一具体领域逻辑时，请勿盲目搜索代码，请严格按以下路径寻找对应的 `MODULE_SPEC.md` 以获取上下文。*

### 1. core-agent 模块
负责 Agent 交互逻辑、双轨模式 (Dual-Mode) 的控制、以及用户 Issue 提报与反馈流程。
- `dual-mode/` — 双轨模式核心逻辑
- `model-manager/` — 模型配置诊断与修复

### 2. orchestration 模块
负责读取与解析 `swarm.yaml`，执行状态对比 (Diff) 并在宿主机驱动 Systemd 进行最终的调和 (Reconciliation)。
- `config-parser/` ✅ 已迁移 — 配置解析与校验
- `reconciler/` ✅ 已迁移 — 调和控制器 (Diff + dry-run)
- `pod-provisioner/` ✅ 已迁移 — Pod 供应器 (物理创建、环境注入、插件同步)
- `templates/` ✅ 已迁移 — Jinja2 模板引擎 (Systemd 服务模板、openclaw.json 模板)

### 3. network-mesh 模块
负责全局代理配置注入、端口分配与实例网络通信机制。
- `proxy-injector/` ✅ 已迁移 — 代理环境变量注入
- `port-manager/` — 端口变更管理

### 4. matrix-channel 模块
负责 Matrix E2EE 加密、账号认证、群组和私信等渠道通讯保障。
- `account-manager/` — 账号凭证写入
- `e2ee-verifier/` — E2EE 加密状态验证
- `device-manager/` — 设备与配对管理

## 五、 遗留文件标记规范
- **`[已迁移 MIGRATED]`**：核心逻辑已重构至 modules/，作为过渡兼容层保留。
- **`[待迁移 PENDING MIGRATION]`**：逻辑归属已知，计划迁移但尚未执行。

遗留文件清单：
| 文件 | 状态 |
|---|---|
| `bin/clawctl` | 已迁移 → pod-provisioner/provisioner.py |
| `bin/claw-apply` | 已迁移 → reconciler/reconciler.py |
| `lib/pod_utils.py` | 已迁移 → config-parser/parser.py |
| `lib/pod_utils.sh` | 已迁移 → pod-provisioner/provisioner.py |
| `lib/matrix_utils.sh` | 待迁移 → matrix-channel/account-manager/ |
| `bin/claw-port` | 待迁移 → network-mesh/port-manager/ |
| `bin/claw-repair` | 待迁移 → orchestration/pod-provisioner/ |
| `bin/claw-rm` | 待迁移 → orchestration/pod-provisioner/ |

*(注：所有遗留脚本在过渡期内仍可正常运行，控制面完全切换后将逐步废弃。)*