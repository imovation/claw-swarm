# 🐝 Claw-Swarm: OpenClaw 集群编排底座

## 🌟 项目愿景 (Vision)
`claw-swarm` 旨在为 OpenClaw 实例提供类似于 **Kubernetes/Swarm** 的容器化编排能力。通过物理隔离的 `--profile` 机制，将每一个 OpenClaw 实例视为一个独立的 **Pod (蜂穴)**，实现多用户、多渠道（飞书/命令行/ACP）的 100% 逻辑与进程隔离。

---

## 📖 面向使用者 (User Guide)

如果你是这个集群的**普通用户**（如朋友 Aimee），你通常通过以下方式接入：

### 1. 接入渠道 (Access Channels)
*   **飞书 (Feishu/Lark)**：直接在飞书搜索对应的机器人名称即可开始对话。
*   **网页控制台 (Web UI)**：访问 `http://<服务器IP>:18780/?token=666666` (以 Aimee 实例为例)。
*   **命令行 (TUI)**：如果您有服务器 SSH 权限，运行：
    ```bash
    openclaw --profile aimee tui --token 666666
    ```

### 2. 隔离特性 (Isolation)
*   你的对话记忆、文件、设置与主实例及其他用户**完全独立**。
*   你的机器人崩溃或重启，不会影响其他人的机器人。

---

## 🛠️ 面向开发者/管理员 (Developer & Ops Guide)

如果你是集群的**编排者**，请阅读以下内容：

### 1. 快速孵化新实例 (Provisioning)
使用内置的编排脚本 `./bin/clawctl`。例如，为新朋友 Bob 创建一个实例：
```bash
./bin/clawctl bob 18781 my-secure-token-888
```
**脚本会自动完成：**
- 创建 `~/.openclaw-bob/` 隔离目录。
- 物理拷贝 `openclaw-lark` 插件副本（断绝依赖污染）。
- 自动生成并启用 Systemd 用户服务 `openclaw-bob.service`。
- 强制统一 HTTP 与 WebSocket 端口，设置独立 Token。

### 2. 实例管理 (Lifecycle)
所有管理工具位于 `bin/` 目录下：
- **查看状态**：`systemctl --user status "openclaw-*"`
- **热改端口**：`./bin/claw-port aimee 18888`
- **一键修复**：`./bin/claw-repair aimee`
- **彻底删除**：`./bin/claw-rm aimee`

### 3. 架构规范 (Specs)
请务必阅读 [ARCHITECTURE.md](docs/ARCHITECTURE.md) 以了解底层逻辑。

### 4. 演进路线 (Roadmap)
查看 [ROADMAP.md](docs/ROADMAP.md) 了解 Phase 1-4 计划。
