# pod-provisioner 功能规范 (Feature Spec)

## 一、 功能定位
Pod 供应器 (Provisioner) 是编排模块的执行器。它接收 reconciler 的指令，负责在宿主机上完成
Pod 的物理创建、环境注入、插件同步和 Systemd 服务的生命周期管理。

## 二、 职责边界
- **目录结构**：创建并维护 `~/.openclaw-<NAME>/runtime/` 下的完整隔离运行时目录。
- **环境注入**：生成 `runtime/env` 文件，写入所有必要的环境变量。
- **插件同步**：从全局 node_modules 物理拷贝插件到 Pod 内部 `extensions/` 目录（禁止 symlink）。
- **Systemd 管理**：通过 `systemctl --user enable/restart/stop` 管理 Pod 进程。
- **健康检查**：启动后执行 Systemd 状态 + HTTP API 探活检查。

## 三、 关键约束 (来自系统层)
- 插件**必须**物理拷贝，**严禁** `ln -s`。
- 必须注入 `OPENCLAW_STATE_DIR`, `OPENCLAW_CONFIG_PATH`, `OPENCLAW_PROFILE`, `TMPDIR`, `XDG_*`。
- 服务命名规范：`openclaw-gateway@<PROFILE>.service`（Systemd 实例化模板）。

## 四、 环境变量完整清单
| 变量名 | 说明 |
|---|---|
| `OPENCLAW_PORT` | 实例监听端口 |
| `OPENCLAW_TOKEN` | 访问令牌 |
| `OPENCLAW_PROFILE` | Profile 名称 |
| `OPENCLAW_STATE_DIR` | Pod 根目录路径 |
| `OPENCLAW_CONFIG_PATH` | openclaw.json 的绝对路径 |
| `TMPDIR` | 隔离的临时目录 |
| `XDG_CONFIG_HOME` | 隔离的配置目录 |
| `XDG_CACHE_HOME` | 隔离的缓存目录 |
| `XDG_DATA_HOME` | 隔离的数据目录 |
| `PUPPETEER_USER_DATA_DIR` | 浏览器数据目录（dedicated 模式）|
| `HTTP_PROXY` / `HTTPS_PROXY` | 全局代理注入 |

## 五、 当前实现
- **文件**：`bin/clawctl`（Bash 脚本，待迁移至本目录 `provisioner.py`）。