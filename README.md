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
使用内置的编排脚本 `clawctl.sh`。例如，为新朋友 Bob 创建一个实例：
```bash
./clawctl.sh bob 18781 my-secure-token-888
```
**脚本会自动完成：**
- 创建 `~/.openclaw-bob/` 隔离目录。
- 物理拷贝 `openclaw-lark` 插件副本（断绝依赖污染）。
- 自动生成并启用 Systemd 用户服务 `openclaw-bob.service`。
- 设置独立端口与 Token。

### 2. 实例管理 (Lifecycle)
每个实例都是一个独立的 Systemd 服务：
- **查看所有 Pod 状态**：`systemctl --user status "openclaw-*"`
- **重启 Aimee**：`systemctl --user restart openclaw-aimee.service`
- **追踪日志**：`journalctl --user -fu openclaw-aimee.service`

### 3. 架构规范 (Specs)
请务必阅读 [ARCHITECTURE.md](./ARCHITECTURE.md) 以了解“防杀/隔离/环境变量注入”的底层设计逻辑，防止在手动修改配置时破坏隔离性。

### 4. 演进路线 (Roadmap)
查看 [ROADMAP.md](./ROADMAP.md) 了解未来的 ACP 代理互联、Opencode 联动等 Phase 1-4 计划。
