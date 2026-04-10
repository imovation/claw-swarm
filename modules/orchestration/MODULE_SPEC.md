# Orchestration (编排) 模块规范

## 一、 模块定位
本模块是 Claw-Swarm 的心脏，负责将声明式的意图 (`swarm.yaml`) 转化为具体的系统状态 (Systemd 进程、环境变量、物理目录隔离)。

## 二、 核心架构原则 (The Pod Isolation)
1. **绝对隔离**：每个 Profile 必须拥有独立的运行时目录 (`~/.openclaw-<NAME>`)。
2. **插件隔离**：绝不允许对 `extensions/` 目录使用软链接 (symlink)。必须硬拷贝 (`cp -r`) 以防依赖泄漏。
3. **环境注入**：必须在 Systemd Unit 中强制注入 `OPENCLAW_STATE_DIR`, `OPENCLAW_CONFIG_PATH` 和 `TMPDIR`。
4. **命名约定**：系统服务必须以 `openclaw-gateway-<name>.service` 命名，并部署在 `~/.config/systemd/user/` 下。

## 三、 CLI 入口与路由
通过统一入口 `bin/claw` 路由至本模块：
- `claw apply` — 调和集群状态 (核心入口，解析 yaml 并同步至 Systemd)
- `claw status` — 查看集群看板
- `claw tui <NAME>` — 进入实例 TUI (自动注入对应实例的环境变量)

## 四、 下属功能树 (Features)
| 功能目录 | 状态 | 说明 |
|---|---|---|
| `config-parser/` | ✅ 已迁移 | 负责读取并校验 swarm.yaml，使用 Pydantic 风格校验 |
| `reconciler/` | ✅ 已迁移 | 执行精确 Diff-Patch，支持 dry-run 预览 |
| `pod-provisioner/` | ✅ 已迁移 | 负责物理创建、环境注入、插件同步、Systemd 管理 |
| `templates/` | ✅ 已迁移 | Jinja2 模板引擎（Systemd 服务模板、openclaw.json 模板） |

## 五、 遗留脚本清单
| 文件 | 状态 |
|---|---|
| `bin/clawctl` | ⚠️ 已废弃，推荐使用 `modules/orchestration/pod-provisioner/provisioner.py` |
| `bin/claw-apply` | ⚠️ 已废弃，推荐使用 `modules/orchestration/reconciler/reconciler.py` |
| `bin/claw-repair` | 待迁移 |
| `bin/claw-rm` | 待迁移 |