# Claw Kubernetes: 声明式解耦架构 (v2.0)

本文阐述了 `claw-swarm` 项目的底层设计模式。

## 1. 核心范式：Pod (蜂穴) 隔离
每个 OpenClaw 实例被视为一个完全隔离的“Pod”。
- **状态隔离**：独立 `~/.openclaw-<name>/` 目录。
- **环境隔离 (Virtual Home)**：强制注入 `XDG_*` 变量和专属浏览器路径，锁定软件的所有读写行为到 Pod 内部。
- **依赖隔离**：物理拷贝插件，杜绝符号链接导致的污染。
- **进程隔离**：封装为 Systemd User Services (`openclaw-gateway-<name>.service`)。

## 2. 声明式配置模型 (Declarative Model)
本项目受 Kubernetes 启发，采用“期望状态”驱动逻辑。

### 目录与拓扑布局
```text
/home/imovation/
 ├── .openclaw/                  # Pod: main (Default Profile)
 │    ├── runtime/               # Virtual Home: tmp, config, cache, data, browser
 │    └── openclaw.json          
 │
 ├── .openclaw-aimee/            # Pod: aimee
 │    ├── runtime/               # Virtual Home (XDG/Puppeteer Isolated)
 │    └── openclaw.json          
 │
 ├── .openclaw-shining/          # Pod: shining
 │    ├── runtime/               # Virtual Home (XDG/Puppeteer Isolated)
 │    └── openclaw.json          
 │
 └── claw-swarm/            # 控制平面 (Control Plane)
      ├── swarm.yaml             # 意图定义 (Desired State) + 全局配置
      ├── CONSTITUTION.md        # 项目基本宪法
      ├── lib/                   # 共享库 (声明式模式的基础)
      │    ├── pod_utils.sh      # Bash 共享函数
      │    └── pod_utils.py      # Python 共享函数
      └── bin/
           ├── claw-apply        # 控制器 (Controller/Reconciler) ← 支持孤儿自动清理
           ├── clawctl           # 供应执行器 (Provisioner/Actuator) ← 使用共享库
           ├── claw-repair       # 修复器 ← 修复了逻辑双执行Bug
           ├── claw-port         # 端口变更器 ← 实现了完整功能
           ├── claw-rm           # 实例销毁工具
           ├── claw-ps           # 精细进程状态监控
           ├── claw-status       # 实时监控看板 (Dashboard)
           ├── claw-tui          # 终端交互快捷入口
           └── claw-lark         # 飞书插件一键配置向导
```

## 3. 声明式增强特性

### 3.1 全局配置块 (swarm.yaml)
新增 `global:` 配置段，支持：
- **网络代理统一配置**：避免在每个服务文件中重复声明 8 行代理环境变量
- **孤儿 Pod 策略**：
  - `warn` (默认)：仅提醒不采取行动
  - `delete`：自动清理在 swarm.yaml 中未定义但仍在运行的 Pod

### 3.2 共享库消除重复逻辑
引入 `lib/` 目录包含：
- `pod_utils.sh`：解决 Bash 脚本中 Profile/DIR/SERVICE_NAME 重复解析问题 (5处 → 1处)
- `pod_utils.py`：解决 Python 脚本中路径解析和服务度量重复问题 (3处 → 1处)

### 3.3 声明式端口管理
`claw-port` 脚本现在：
- 精确修改 Systemd 服务文件中的端口参数
- 自动同步更新 swarm.yaml 中的声明
- 保持声明式和命令式操作的一致性

### 3.4 自我修复能力增强
- `claw-repair`：修复了逻辑被错误分割执行两遍的严重Bug
- 动态路径解析：消除了硬编码的 Node.js 版本号，自适应 nvm 环境变更

## 4. 隔离全家桶：Virtual Home (虚拟家目录)
为了解决 OS 级冲突（如浏览器、缓存、临时文件），`clawctl` 为每个 Pod 注入了以下环境变量：
- `TMPDIR=$DIR/runtime/tmp`
- `XDG_CONFIG_HOME=$DIR/runtime/config`
- `XDG_CACHE_HOME=$DIR/runtime/cache`
- `XDG_DATA_HOME=$DIR/runtime/data`
- `PUPPETEER_USER_DATA_DIR=$DIR/runtime/browser` (模式为 dedicated 时)

## 5. 幂等同步逻辑 (Reconciliation Loop)
`claw-apply` 的核心逻辑：
1. **读取意图**：解析 `swarm.yaml` (含全局配置)。
2. **感知现状**：通过 `systemctl` 探测正在运行的服务。
3. **调和补齐**：
   - 发现新定义的 Pod -> 调用 `clawctl` 创建。
   - 发现已有配置差异 -> 调用 `clawctl` 滚动重载。
   - 发现孤儿 Pod (Orphan) -> 根据 `global.orphan_policy` 执行 warn/delete。
4. **状态反馈**：调用 `claw-status` 展示最终集群状态。

## 6. 关键经验与防坑指南
- **插件拷贝**：禁止使用 `ln -s`，必须物理拷贝以确保隔离。
- **环境变量注入**：必须注入 `OPENCLAW_PROFILE`, `OPENCLAW_STATE_DIR`, `OPENCLAW_CONFIG_PATH` 显式覆盖。
- **缓冲区刷新**：在多语言脚本中显式调用刷新以保证输出顺序正确性。
- **版本无关性**：通过动态路径解析消除对特定 Node.js 版本的硬依赖。
- **统一别名**：所有脚本现在统一使用 `default` 作为主 Pod 的规范名称，历史别名 `main`/`gateway` 在内部被透明映射。