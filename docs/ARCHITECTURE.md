# Claw Swarm: 金字塔架构 (Pyramid Architecture)

本文阐述了 `claw-swarm` 项目的设计模式与架构规范。

## 1. 核心范式：Pod (蜂穴) 隔离

每个 OpenClaw 实例被视为一个完全隔离的 "Pod"。
- **状态隔离**：独立 `~/.openclaw-<name>/` 目录
- **环境隔离 (Virtual Home)**：强制注入 `XDG_*` 变量和专属浏览器路径
- **依赖隔离**：物理拷贝插件，支持 `swarm.yaml` 声明式同步
- **进程隔离**：基于 Systemd 实例化模板 (`openclaw-gateway-<name>.service`)
- **Matrix 加密隔离**：Matrix 加密状态存储在各 Pod 独立的目录 `~/.openclaw-<name>/matrix/` 中

## 2. 金字塔架构 (Pyramid Architecture)

本项目采用"系统-模块-功能"三层金字塔架构，遵循 Spec-driven 开发模式。

```
claw-swarm/
├── AGENTS.md                 # Agent 守门人协议 (双轨模式)
├── SYSTEM_SPEC.md            # 系统宪法 (模块路由索引)
│
├── modules/                  # 功能模块层
│   ├── core-agent/           # Agent 核心逻辑
│   │   ├── dual-mode/        # 双轨模式实现
│   │   └── model-manager/    # 模型配置管理
│   │
│   ├── orchestration/        # 编排模块 (核心)
│   │   ├── config-parser/    # swarm.yaml 解析
│   │   ├── reconciler/       # 状态调和 (Diff-Patch)
│   │   ├── pod-provisioner/  # Pod 物理创建
│   │   └── templates/        # Jinja2 模板引擎
│   │
│   ├── network-mesh/         # 网络与代理
│   │   ├── proxy-injector/   # 代理配置注入
│   │   └── port-manager/     # 端口声明管理
│   │
│   └── matrix-channel/       # Matrix 通信
│       ├── account-manager/  # 账号凭证管理
│       ├── e2ee-verifier/    # E2EE 验证与 bootstrap
│       └── device-manager/   # 设备与配对管理
│
└── bin/
    └── claw                  # 统一 CLI 入口
```

## 3. 声明式配置模型 (Declarative Model)

本项目受 Kubernetes 启发，采用"期望状态"驱动逻辑。

### 3.1 CLI 入口与路由

所有命令通过 `bin/claw` 统一路由：

| 命令 | 归属模块 | 功能 |
|---|---|---|
| `claw apply` | orchestration/reconciler | 调和集群状态 |
| `claw status` | orchestration/status | 查看集群看板 |
| `claw tui <NAME>` | orchestration/tui | 进入实例 TUI |
| `claw ps` | orchestration/ps | 进程状态监控 |
| `claw port <NAME> <PORT>` | network-mesh/port-manager | 变更端口 |
| `claw matrix add ...` | matrix-channel/account-manager | 添加 Matrix 账号 |
| `claw matrix verify ...` | matrix-channel/e2ee-verifier | E2EE 验证 |
| `claw matrix devices ...` | matrix-channel/device-manager | 设备管理 |
| `claw matrix pairing ...` | matrix-channel/device-manager | 配对审批 |

### 3.2 全局配置块 (swarm.yaml)

支持 `global:` 配置段：
- **网络代理统一配置**：`global.proxy` 自动注入到每个 Pod
- **孤儿 Pod 策略**：`global.orphan_policy` (warn/delete)
- **Matrix 全局配置**：`global.matrix` 默认配置

### 3.3 声明式端口管理

`claw port` 命令：
- 精确修改 Systemd 服务文件中的端口参数
- 自动同步更新 swarm.yaml 中的声明
- 保持声明式和命令式操作的一致性

### 3.4 Matrix 支持

- **声明式配置**：通过 `swarm.yaml` 的 `global.matrix` 和 `pods[].matrix` 声明
- **SecretRef 支持**：解析 `${VAR_NAME}` 和 `env:VAR_NAME` 格式
- **多账号支持**：支持 `accounts` 配置块和 `defaultAccount`
- **E2EE 验证**：`claw matrix verify` 命令进行 bootstrap/设备验证

## 4. 隔离全家桶：Virtual Home (虚拟家目录)

为解决 OS 级冲突（如浏览器、缓存、临时文件），每个 Pod 注入以下环境变量：
- `TMPDIR=$DIR/runtime/tmp`
- `XDG_CONFIG_HOME=$DIR/runtime/config`
- `XDG_CACHE_HOME=$DIR/runtime/cache`
- `XDG_DATA_HOME=$DIR/runtime/data`
- `PUPPETEER_USER_DATA_DIR=$DIR/runtime/browser` (模式为 dedicated 时)

## 5. 幂等同步逻辑 (Reconciliation Loop)

`claw apply` 的核心逻辑：
1. **读取意图**：解析 `swarm.yaml` (含全局配置)
2. **感知现状**：通过 `systemctl` 探测正在运行的服务
3. **调和补齐**：
   - 发现新定义的 Pod -> 创建
   - 发现已有配置差异 -> 滚动重载
   - 发现孤儿 Pod -> 根据 `global.orphan_policy` 执行 warn/delete
4. **状态反馈**：展示最终集群状态

## 6. 开发规范

### Spec-driven 开发模式
- 每次迭代开发先迭代 SPEC.md，再开发代码
- 模块化功能可视化，每个功能对应的 spec 和代码归置到一起

### 双轨模式 (Dual-Mode)
- **应用模式 (APP MODE)**：仅运行、测试、配置，禁止修改核心代码
- **开发模式 (DEV MODE)**：允许修改代码、修复 Issue、并提交 Git Push

## 7. 关键经验与防坑指南

- **插件拷贝**：禁止使用 `ln -s`，必须物理拷贝以确保隔离
- **环境变量注入**：必须注入 `OPENCLAW_PROFILE`, `OPENCLAW_STATE_DIR`, `OPENCLAW_CONFIG_PATH` 显式覆盖
- **版本无关性**：通过动态路径解析消除对特定 Node.js 版本的硬依赖
- **统一别名**：所有脚本统一使用 `default` 作为主 Pod 的规范名称