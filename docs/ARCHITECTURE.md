# Claw Kubernetes: 声明式解耦架构 (v1.5)

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
 └── claw-swarm/            # 控制平面 (Control Plane)
      ├── swarm.yaml             # 意图定义 (Desired State)
      ├── CONSTITUTION.md        # 项目基本宪法
      └── bin/
           ├── claw-apply        # 控制器 (Controller/Reconciler)
           ├── clawctl           # 供应执行器 (Provisioner/Actuator)
           ├── claw-status       # 实时监控看板 (Dashboard)
           └── claw-rm           # 实例销毁工具
```

## 3. 隔离全家桶：Virtual Home (虚拟家目录)
为了解决 OS 级冲突（如浏览器、缓存、临时文件），`clawctl` 为每个 Pod 注入了以下环境变量：
- `TMPDIR=$DIR/runtime/tmp`
- `XDG_CONFIG_HOME=$DIR/runtime/config`
- `XDG_CACHE_HOME=$DIR/runtime/cache`
- `XDG_DATA_HOME=$DIR/runtime/data`
- `PUPPETEER_USER_DATA_DIR=$DIR/runtime/browser` (模式为 dedicated 时)

## 4. 幂等同步逻辑 (Reconciliation Loop)
`claw-apply` 的核心逻辑：
1. **读取意图**：解析 `swarm.yaml`。
2. **感知现状**：通过 `systemctl` 探测正在运行的服务。
3. **调和补齐**：
   - 发现新定义的 Pod -> 调用 `clawctl` 创建。
   - 发现已有配置差异 -> 调用 `clawctl` 滚动重载。
   - 发现孤儿 Pod (Orphan) -> 发出人工清理警告。

## 5. 关键经验与防坑指南
- **插件拷贝**：禁止使用 `ln -s`。
- **环境变量注入**：必须注入 `OPENCLAW_PROFILE`, `OPENCLAW_STATE_DIR`, `OPENCLAW_CONFIG_PATH` 显式覆盖。
- **缓冲区刷新**：在 `claw-apply` 中显式调用 `sys.stdout.flush()` 以保证多语言脚本混合输出的顺序正确性。
