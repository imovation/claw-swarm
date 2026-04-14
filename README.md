# Claw Swarm: OpenClaw 集群编排底座

## 项目愿景

`claw-swarm` 旨在为 OpenClaw 实例提供类似于 **Kubernetes/Swarm** 的容器化编排能力。通过"声明式意图 (Declarative Intent)"和"物理隔离 Pod (Pod Isolation)"机制，实现多用户、多场景的 100% 逻辑与进程隔离。

---

## 核心架构：金字塔架构 (Pyramid Architecture)

本项目采用"系统-模块-功能"三层金字塔架构，遵循 Spec-driven 开发模式。

### 1. 唯一真理来源：`swarm.yaml`

所有的实例配置（端口、令牌、隔离模式）均在根目录下的 `swarm.yaml` 中定义。

### 2. 统一 CLI 入口：`bin/claw`

所有命令通过 `bin/claw` 统一路由：

| 命令 | 功能 |
|---|---|
| `claw apply` | 调和集群状态 |
| `claw status` | 查看集群看板 |
| `claw tui <NAME>` | 进入实例 TUI |
| `claw ps` | 进程状态监控 |
| `claw port <NAME> <PORT>` | 变更端口 |
| `claw matrix add ...` | 添加 Matrix 账号 |
| `claw matrix verify ...` | E2EE 验证 |
| `claw matrix devices ...` | 设备管理 |
| `claw matrix pairing ...` | 配对审批 |

### 3. 模块结构

```
modules/

├── orchestration/        # 编排模块 (核心)
│   ├── config-parser/    # swarm.yaml 解析
│   ├── reconciler/       # 状态调和
│   └── pod-provisioner/ # Pod 物理创建
├── network-mesh/         # 网络与代理
│   ├── proxy-injector/   # 代理配置注入
│   └── port-manager/     # 端口管理
└── matrix-channel/      # Matrix 通信
    ├── account-manager/  # 账号管理
    ├── e2ee-verifier/    # E2EE 验证
    └── device-manager/   # 设备管理
```

---

## 管理指南

### 1. 同步配置

修改 `swarm.yaml` 后，运行以下命令一键生效：
```bash
claw apply
```

### 2. 查看集群状态
```bash
claw status
```

### 3. 进入实例终端 (TUI)
```bash
claw tui <实例名>
```

### 4. Matrix 渠道管理

支持在 `swarm.yaml` 中声明式配置 Matrix 渠道：

```yaml
pods:
  - name: main
    matrix:
      enabled: true
      homeserver: https://matrix.org
      accessToken: "${MATRIX_TOKEN}"
      encryption: true
      dm:
        policy: pairing
      autoJoin: "allowlist"
```

Matrix CLI 工具：
```bash
# 添加/更新 Matrix 配置
claw matrix add <profile> --homeserver <url> --token <token> --encryption

# E2EE 状态检查
claw matrix verify <profile> status

# 引导加密 bootstrap
claw matrix verify <profile> bootstrap

# 设备管理
claw matrix devices <profile> list
claw matrix devices <profile> prune-stale

# 配对审批
claw matrix pairing <profile> list
```

### 5. 隔离与同步特性

- **进程隔离**：基于 Systemd 实例化模板，提供轻量且一致的生命周期管理
- **环境隔离**：每个 Pod 拥有独立的 `TMPDIR`、`XDG_CONFIG_HOME` 和浏览器数据目录
- **依赖隔离**：插件采用物理拷贝模式，支持在 `swarm.yaml` 中声明插件清单并自动同步
- **全局代理同步**：支持在 `global.proxy` 中统一定义代理，全集群自动注入

---

## 开发者文档

- [系统宪法](SYSTEM_SPEC.md)


- [演进路线图](docs/ROADMAP.md)