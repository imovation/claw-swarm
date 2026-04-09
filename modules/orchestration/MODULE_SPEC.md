# Orchestration (编排) 模块规范

## 一、 模块定位
本模块是 Claw-Swarm 的心脏，负责将声明式的意图 (`swarm.yaml`) 转化为具体的系统状态 (Systemd 进程、环境变量、物理目录隔离)。

## 二、 核心架构原则 (The Pod Isolation)
1. **绝对隔离**：每个 Profile 必须拥有独立的运行时目录 (`~/.openclaw-<NAME>`)。
2. **插件隔离**：绝不允许对 `extensions/` 目录使用软链接 (symlink)。必须硬拷贝 (`cp -r`) 以防依赖泄漏。
3. **环境注入**：必须在 Systemd Unit 中强制注入 `OPENCLAW_STATE_DIR`, `OPENCLAW_CONFIG_PATH` 和 `TMPDIR`。
4. **命名约定**：系统服务必须以 `openclaw-gateway-<name>.service` 命名，并部署在 `~/.config/systemd/user/` 下。

## 三、 当前可用 CLI 命令清单 (遗留)
*注：目前逻辑仍由 Bash 和 Python 脚本混合实现，未来将统一重构入本模块。*

- **集群配置调和**：`./bin/claw-apply` (核心入口，解析 yaml 并同步至 Systemd)
- **状态监控**：`./bin/claw-status`
- **交互式调试**：`./bin/claw-tui <NAME>` (自动注入对应实例的环境变量)
- **底层供应 (被 apply 调用)**：`./bin/clawctl <NAME> <PORT> <TOKEN>`
- **修复与销毁**：`./bin/claw-repair <NAME>`, `./bin/claw-rm <NAME>`

## 四、 下属功能树 (待重构迁移)
- `config-parser/`：计划用于解析 `swarm.yaml`。
- `reconciler/`：计划用于执行 Diff-Patch 和 Systemd 重启。