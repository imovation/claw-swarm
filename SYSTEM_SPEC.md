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

## 三、 模块路由索引树 (Routing Map)
*Agent 提示：当需要了解或修改某一具体领域逻辑时，请勿盲目搜索代码，请严格按以下路径寻找对应的 `MODULE_SPEC.md` 以获取上下文。*

- **`modules/core-agent/`**：负责 Agent 交互逻辑、双轨模式 (Dual-Mode) 的控制、以及用户 Issue 提报与反馈流程。
- **`modules/orchestration/`**：负责读取与解析 `swarm.yaml`，执行状态对比 (Diff) 并在宿主机驱动 Systemd 进行最终的调和 (Reconciliation)。
- **`modules/network-mesh/`**：负责全局代理配置注入、端口分配与实例网络通信机制。
- **`modules/matrix-channel/`**：负责 Matrix E2EE 加密、账号认证、群组和私信等渠道通讯保障。

*(注：系统目前正处于金字塔架构重构期，部分遗留脚本可能仍散落在 `bin/` 和 `lib/` 目录中，在新建模块时需将其逐步迁移。)*