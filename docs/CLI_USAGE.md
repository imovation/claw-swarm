# Claw-Swarm CLI 使用指南

> `bin/claw` 是 Claw-Swarm 集群编排系统的统一命令行入口，采用类似 `kubectl` 的子命令设计风格。

---

## 快速概览

| 命令 | 功能描述 | 适用场景 |
|------|----------|----------|
| `claw apply` | 调和集群状态 | 修改 swarm.yaml 后同步配置 |
| `claw status` | 查看集群看板 | 实时监控所有 Pod 状态 |
| `claw ps` | 精细进程状态 | 查看详细的 Pod 运行信息 |
| `claw tui <NAME>` | 进入实例 TUI | 与指定 Pod 进行交互 |
| `claw port <NAME> <PORT>` | 变更端口 | 动态调整 Pod 监听端口 |
| `claw repair <NAME>` | 修复实例 | 重新同步配置并重启 |
| `claw rm <NAME>` | 销毁实例 | 彻底删除 Pod 及数据 |
| `claw matrix ...` | Matrix 渠道管理 | E2EE、设备、配对等操作 |

---

## 全局选项

```bash
claw -h, --help     # 显示帮助信息
claw <command> -h   # 显示指定命令的帮助
```

---

## 详细命令说明

### 1. `claw apply` — 调和集群状态

将 `swarm.yaml` 中声明的期望状态同步到实际运行环境，是所有配置变更的核心入口。

**语法**
```bash
claw apply [选项]
```

**选项**
| 选项 | 说明 |
|------|------|
| `--dry-run` | 仅预览变更，不执行实际操作 |
| `--skip-update` | 跳过版本检查 |
| `-y, --yes` | 自动确认，无需交互 |

**示例**
```bash
# 预览变更（不实际执行）
claw apply --dry-run

# 标准同步（根据 swarm.yaml 更新所有 Pod）
claw apply

# 自动确认同步
claw apply -y
```

**执行逻辑**
1. 解析 `swarm.yaml` 获取期望状态
2. 查询 Systemd 获取实际状态
3. 计算差异（Diff）：
   - **to_create**: 需新建的 Pod
   - **to_update**: 需更新的 Pod（端口/配置变更）
   - **orphans**: 孤儿 Pod（存在但不在配置中）
4. 根据 `orphan_policy` 处理孤儿：
   - `delete`: 自动停止并清理
   - `warn`: 仅提醒，不操作
5. 执行新建/更新操作

**输出示例**
```
▶️  正在同步实例: aimee...
   ✅ aimee 同步成功。
▶️  正在同步实例: bob...
   ✅ bob 同步成功。

🔍 发现 1 个孤儿 Pod: legacy-instance
🗑️  根据 orphan_policy: delete，正在清理...
   ✅ 孤儿 Pod 'legacy-instance' 已清理。
```

---

### 2. `claw status` — 集群状态看板

显示所有 Pod 的运行状态、资源占用、配置同步情况，类似 `kubectl get pods`。

**语法**
```bash
claw status
```

**输出字段**
| 字段 | 说明 |
|------|------|
| 实例 (POD) | Pod 名称，来自 swarm.yaml |
| 状态 | 运行中/已离线/failed |
| 端口 | 实际监听端口 |
| 内存占用 | RSS 内存使用 |
| 启动时间 | 服务启动时间 |
| 主用模型 | 当前配置的 LLM 模型 |
| 生效渠道 | 启用的通信渠道 |
| Matrix | E2EE 加密状态 |

**输出示例**
```
实例 (POD)                状态       端口      内存占用      启动时间       主用模型            生效渠道         Matrix
-----------------------------------------------------------------------------------------------------------------
aimee                     运行中     11434     156.2 MB      Apr 14 10:23   kimi-k2.5          matrix           E2EE
bob                       运行中     11435     142.8 MB      Apr 14 10:25   claude-3.5         matrix           E2EE
legacy-test               已离线     N/A       0 MB          N/A            N/A                none             未启用
```

**颜色说明**
- 🟢 绿色：正常/已同步
- 🔴 红色：异常/离线
- 🟡 黄色：警告/配置漂移
- 🔵 青色：未纳管/孤儿

---

### 3. `claw ps` — 精细进程状态

显示更详细的进程级信息，包括插件状态。

**语法**
```bash
claw ps
```

**输出字段**
| 字段 | 说明 |
|------|------|
| INSTANCE | 实例名称 |
| STATUS | 服务状态 (active/inactive) |
| PORT | 监听端口 |
| MODEL | 主用模型 |
| CHANNELS | 启用的渠道 |
| PLUGINS | 加载的插件 |

**输出示例**
```
INSTANCE     STATUS   PORT     MODEL                     CHANNELS     PLUGINS
-----------------------------------------------------------------------------------------------
aimee        active   11434    kimi-k2.5                 matrix       openclaw-webfetch
bob          active   11435    claude-3.5                matrix       openclaw-webfetch
main         active   10086    gpt-4o                    matrix       none
```

---

### 4. `claw tui <NAME>` — 进入实例 TUI

进入指定 Pod 的交互式终端界面（Text User Interface），自动注入正确的环境变量。

**语法**
```bash
claw tui <实例名>
```

**参数**
| 参数 | 说明 | 必填 |
|------|------|------|
| `实例名` | swarm.yaml 中定义的 Pod 名称 | 是 |

**示例**
```bash
# 进入名为 aimee 的 Pod 的 TUI
claw tui aimee

# 进入 main Pod
claw tui main
```

**环境注入**
进入 TUI 时，以下环境变量会被自动设置：
- `TMPDIR`: `{pod_dir}/runtime/tmp`
- `XDG_CONFIG_HOME`: `{pod_dir}/runtime/config`
- `XDG_CACHE_HOME`: `{pod_dir}/runtime/cache`
- `XDG_DATA_HOME`: `{pod_dir}/runtime/data`
- `OPENCLAW_STATE_DIR`: Pod 状态目录
- `OPENCLAW_CONFIG_PATH`: Pod 配置文件路径
- `PUPPETEER_USER_DATA_DIR`: 浏览器数据目录（如配置为 dedicated）

---

### 5. `claw port <NAME> <PORT>` — 变更端口

动态修改指定 Pod 的监听端口，自动更新配置并重启服务。

**语法**
```bash
claw port <实例名> <新端口号> [--skip-yaml]
```

**参数**
| 参数 | 说明 | 必填 |
|------|------|------|
| `实例名` | Pod 名称 | 是 |
| `新端口号` | 1024-65535 范围内的端口 | 是 |

**选项**
| 选项 | 说明 |
|------|------|
| `--skip-yaml` | 仅修改服务文件，不更新 swarm.yaml |

**示例**
```bash
# 将 aimee Pod 的端口从 11434 改为 20000
claw port aimee 20000

# 仅修改服务文件（不修改 swarm.yaml）
claw port aimee 20000 --skip-yaml
```

**执行流程**
1. 验证端口号（1024-65535）
2. 冲突检测（检查端口是否被占用）
3. 更新 `swarm.yaml`（除非使用 `--skip-yaml`）
4. 更新 Systemd 服务环境变量文件
5. 重载 Systemd 并重启服务

---

### 6. `claw repair <NAME>` — 修复实例

对存在问题的 Pod 进行手术式修复，重建配置并重启。

**语法**
```bash
claw repair <实例名>
```

**参数**
| 参数 | 说明 | 必填 |
|------|------|------|
| `实例名` | Pod 名称 | 是 |

**示例**
```bash
# 修复 aimee Pod
claw repair aimee
```

**修复流程**
1. 验证 Systemd 模板服务存在
2. 检查并启动服务（如未运行）
3. 从 `swarm.yaml` 读取期望配置
4. 重建 `runtime/env` 环境变量文件
5. 重建 `openclaw.json`（如损坏或缺失）
6. 重启服务并进行健康检查

**适用场景**
- 环境变量文件损坏
- 配置文件与声明不一致
- 服务启动失败但配置正确

---

### 7. `claw rm <NAME>` — 销毁实例

彻底删除指定 Pod，包括停止服务、移除服务文件、删除数据目录。

**语法**
```bash
claw rm <实例名>
```

**⚠️ 警告**
此操作不可逆！将删除：
- Systemd 服务文件
- Pod 配置目录（含 openclaw.json）
- 运行时数据（浏览器数据、缓存等）

**示例**
```bash
# 彻底删除 aimee Pod
claw rm aimee
```

**执行流程**
1. 停止并禁用 Systemd 服务
2. 移除 Systemd 服务文件
3. 删除配置目录（`~/.openclaw-<profile>/`）

---

### 8. `claw matrix ...` — Matrix 渠道管理

管理 Matrix 渠道的账号、E2EE 加密、设备和配对。

#### 8.1 `claw matrix add`

配置或更新 Matrix 账号。

**语法**
```bash
claw matrix add <profile> [选项]
```

**参数**
| 参数 | 说明 |
|------|------|
| `profile` | Pod 的 profile 名称 |

**选项**
| 选项 | 说明 |
|------|------|
| `--homeserver <url>` | Matrix Homeserver URL |
| `--token <token>` | Access Token |
| `--encryption` | 启用 E2EE 加密 |
| `--dm-policy <policy>` | DM 策略 (pairing/verify/public) |
| `--auto-join <mode>` | 自动加入模式 (allowlist/blacklist/all) |

**示例**
```bash
claw matrix add aimee \
  --homeserver https://matrix.org \
  --token "syt_xxxx" \
  --encryption \
  --dm-policy pairing
```

#### 8.2 `claw matrix verify`

E2EE 端到端加密验证工具。

**语法**
```bash
claw matrix verify <profile> <action>
```

**Actions**
| Action | 说明 |
|--------|------|
| `status` | 检查 E2EE 状态 |
| `bootstrap` | 引导加密密钥初始化 |
| `rotate` | 轮换密钥 |
| `backup` | 备份密钥 |

**示例**
```bash
# 检查 E2EE 状态
claw matrix verify aimee status

# 初始化加密
claw matrix verify aimee bootstrap
```

#### 8.3 `claw matrix devices`

设备管理工具。

**语法**
```bash
claw matrix devices <profile> <action>
```

**Actions**
| Action | 说明 |
|--------|------|
| `list` | 列出所有设备 |
| `prune` | 清理过期设备 |
| `revoke <device_id>` | 撤销指定设备 |

**示例**
```bash
# 列出设备
claw matrix devices aimee list

# 清理过期设备
claw matrix devices aimee prune
```

#### 8.4 `claw matrix pairing`

配对审批管理。

**语法**
```bash
claw matrix pairing <profile> <action>
```

**Actions**
| Action | 说明 |
|--------|------|
| `list` | 列出待审批请求 |
| `approve <request_id>` | 批准配对请求 |
| `reject <request_id>` | 拒绝配对请求 |
| `block <user_id>` | 屏蔽用户 |

**示例**
```bash
# 列出待审批请求
claw matrix pairing aimee list

# 批准配对
claw matrix pairing aimee approve req_12345
```

---

## 典型工作流

### 工作流 1：新建 Pod

```bash
# 1. 编辑 swarm.yaml 添加新 Pod
vim swarm.yaml

# 2. 预览变更
claw apply --dry-run

# 3. 执行同步
claw apply

# 4. 验证状态
claw status
```

### 工作流 2：修改 Pod 配置

```bash
# 1. 修改 swarm.yaml
vim swarm.yaml

# 2. 应用变更
claw apply

# 3. 如有问题，进入 TUI 排查
claw tui <pod_name>
```

### 工作流 3：迁移 Pod 到新端口

```bash
# 1. 修改 swarm.yaml 中的端口
vim swarm.yaml

# 2. 应用或直接修改端口
claw port <pod_name> <new_port>

# 3. 验证状态
claw status
```

### 工作流 4：清理集群

```bash
# 1. 查看当前状态
claw status

# 2. 识别孤儿 Pod（未在 swarm.yaml 中定义）
# 3. 确保 orphan_policy 设置为 delete

# 4. 执行清理
claw apply

# 5. 或直接删除特定 Pod
claw rm <pod_name>
```

### 工作流 5：配置 Matrix 渠道

```bash
# 1. 在 swarm.yaml 中启用 Matrix
vim swarm.yaml
# 添加:
# matrix:
#   enabled: true
#   homeserver: https://matrix.org
#   encryption: true

# 2. 应用配置
claw apply

# 3. 添加/验证账号
claw matrix add <pod_name> --homeserver https://matrix.org --token "xxx" --encryption

# 4. 检查 E2EE 状态
claw matrix verify <pod_name> status

# 5. 初始化加密（首次启用时）
claw matrix verify <pod_name> bootstrap
```

---

## 故障排查

### 问题 1：`claw apply` 后 Pod 未启动

```bash
# 检查服务状态
systemctl --user status openclaw-gateway@<profile>

# 查看详细日志
journalctl --user -u openclaw-gateway@<profile> -f

# 尝试修复
claw repair <pod_name>
```

### 问题 2：端口冲突

```bash
# 检查端口占用
ss -tlnp | grep <port>

# 更换端口
claw port <pod_name> <new_port>
```

### 问题 3：配置不同步

```bash
# 查看配置漂移
claw status
# 注意 "同步健康度" 列显示 "配置漂移"

# 强制重新同步
claw repair <pod_name>
```

### 问题 4：Matrix E2EE 失败

```bash
# 检查状态
claw matrix verify <pod_name> status

# 重新引导加密
claw matrix verify <pod_name> bootstrap

# 查看日志
journalctl --user -u openclaw-gateway@<profile> | grep -i matrix
```

---

## 配置文件参考

### swarm.yaml 示例

```yaml
global:
  proxy:
    http: "http://proxy.example.com:8080"
    https: "http://proxy.example.com:8080"
    no_proxy: "localhost,127.0.0.1"
  plugins:
    - openclaw-webfetch
    - openclaw-fileops

orphan_policy: delete  # 或 warn

pods:
  - name: main
    profile: default
    port: 10086
    token: "${MAIN_TOKEN}"
    browser: shared
    matrix:
      enabled: false

  - name: aimee
    profile: aimee
    port: 11434
    token: "${AIMEE_TOKEN}"
    browser: dedicated
    matrix:
      enabled: true
      homeserver: "https://matrix.org"
      encryption: true
      dm:
        policy: pairing
      autoJoin: "allowlist"
```

---

## 相关文档

- [系统架构](SYSTEM_SPEC.md)
- [模块规范](MODULE_SPEC.md)
- [测试验证报告](docs/TEST_VERIFICATION_REPORT.md)
- [演进路线图](docs/ROADMAP.md)
