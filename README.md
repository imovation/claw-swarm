# 🐝 Claw-Swarm: OpenClaw 集群编排底座 (Claw-Kubernetes)

## 🌟 项目愿景 (Vision)
`claw-swarm` 旨在为 OpenClaw 实例提供类似于 **Kubernetes/Swarm** 的容器化编排能力。通过“声明式意图 (Declarative Intent)”和“物理隔离 Pod (Pod Isolation)”机制，实现多用户、多场景的 100% 逻辑与进程隔离。

---

## 🏗️ 核心架构：声明式编排 (Declarative Orchestration)

本项目遵循 **《项目基本宪法》** (CONSTITUTION.md)，采用“期望状态 (Desired State)”驱动模式：

### 1. 唯一真理来源：`swarm.yaml`
所有的实例配置（端口、令牌、隔离模式）均在根目录下的 `swarm.yaml` 中定义。

### 2. 核心控制链 (Control Plane)
- **`bin/claw-apply`**：控制器 (Controller)。对比 `swarm.yaml` 与物理现状，自动执行同步补齐。
- **`bin/clawctl`**：执行器 (Actuator)。负责创建 Pod 目录、注入 **Virtual Home (虚拟家目录)** 环境变量，并生成 Systemd 用户服务。
- **`bin/claw-status`**：看板 (Dashboard)。实时监控各 Pod 的状态、内存占用、主用模型及同步健康度。

---

## 🛠️ 管理指南 (Admin Guide)

### 1. 同步配置
修改 `swarm.yaml` 后，运行以下命令一键生效：
```bash
./bin/claw-apply
```

### 2. 查看集群状态
```bash
./bin/claw-status
```

### 3. 进入实例终端 (TUI)
```bash
./bin/claw-tui <实例名>
```
此工具会自动读取 Token 并注入隔离的环境变量。

### 4. Matrix 渠道管理
Claw-Swarm 支持在 `swarm.yaml` 中声明式配置 Matrix 渠道：

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
./bin/claw-matrix-add <profile> --homeserver <url> --token <token> --encryption

# E2EE 状态检查
./bin/claw-matrix-verify <profile> status

# 引导加密 bootstrap
./bin/claw-matrix-verify <profile> bootstrap

# 设备管理
./bin/claw-matrix-devices <profile> list
./bin/claw-matrix-devices <profile> prune-stale

# 配对审批
./bin/claw-matrix-pairing <profile> list

# 资料设置
./bin/claw-matrix-profile <profile> set-name "Bot Name"
./bin/claw-matrix-profile <profile> set-avatar https://example.org/avatar.png
```

### 5. 隔离与同步特性 (Isolation & Sync)
- **进程隔离**：基于 Systemd 实例化模板 (`openclaw-gateway@.service`)，提供轻量且一致的生命周期管理。
- **环境隔离**：每个 Pod 拥有独立的 `TMPDIR`、`XDG_CONFIG_HOME` 和浏览器数据目录，彻底杜绝资源竞争。
- **依赖隔离**：插件采用物理拷贝模式，支持在 `swarm.yaml` 中声明插件清单并自动同步。
- **全局代理同步**：支持在 `global.proxy` 中统一定义代理，全集群自动注入。
- **版本自生命周期**：`claw-apply` 包含自动版本检测，支持一键交互式更新 OpenClaw 主程序。

---

## 📖 开发者文档
- [项目基本宪法](CONSTITUTION.md)
- [底层架构详述](docs/ARCHITECTURE.md)
- [Agent 操作指南](AGENTS.md) (包含 `opencode-model-manager` 技能说明)
- [演进路线图](docs/ROADMAP.md)
