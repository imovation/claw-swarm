# 🐝 Claw-Swarm 快速上手手册 (Quick Start)

本手册旨在指导您如何像使用 Kubernetes 一样管理您的 OpenClaw 实例。

---

## 1. 核心操作逻辑：意图驱动 (Intent-Driven)

在这个系统中，您**不需要**手动运行复杂的命令行参数。所有的管理行为都围绕“意图”展开：
- **期望状态 (Desired State)**：定义在 `swarm.yaml` 中。
- **实际状态 (Actual State)**：由系统自动同步对齐。

---

## 2. 场景化操作指南

### 场景 A：新增一个 AI 实例 (Pod)
1.  打开 `swarm.yaml`。
2.  在 `pods` 列表下增加一段配置：
    ```yaml
    - name: mynewbot         # 实例名称 (对外标识)
      profile: mynewbot      # 配置文件名 (建议与 name 一致)
      port: 18889            # 独立端口 (不要与其他 Pod 冲突)
      token: "secret123"     # 访问令牌
      resources:
        browser: dedicated   # 浏览器隔离模式 (推荐 dedicated，防止冲突)
    ```
3.  运行同步命令：
    ```bash
    ./bin/claw-apply
    ```

### 场景 B：修改现有实例 (例如改端口、改 Token)
1.  在 `swarm.yaml` 中找到对应 Pod，直接修改 `port` 或 `token`。
2.  运行同步命令：
    ```bash
    ./bin/claw-apply
    ```
    - *结果：系统会自动重启该 Pod 并应用新配置。*

### 场景 C：进入实例的 TUI (终端交互)
如果您想直接和机器人对话或在终端中调试：
```bash
./bin/claw-tui <实例名>
```
此工具会自动从 `swarm.yaml` 读取 Token，并注入隔离的环境变量，确保 TUI 的行为与后台服务一致。

### 场景 D：查看监控看板
实时查看所有实例的内存、模型、同步健康度：
```bash
./bin/claw-status
```

### 场景 E：彻底删除一个实例
1.  从 `swarm.yaml` 中删除对应的配置块。
2.  运行 `./bin/claw-apply`，看板会提示该实例已变为 `Orphan (未纳管)`。
3.  手动运行物理清理命令：
    ```bash
    ./bin/claw-rm <实例名>
    ```

---

## 3. 运维锦囊 (Troubleshooting)

- **查看实时日志**：
  `journalctl --user -fu openclaw-gateway-<实例名>.service`
- **强制同步所有环境**：
  如果您怀疑某个 Pod 的环境被破坏（如临时目录被删），再次运行 `./bin/claw-apply` 即可一键自愈。
- **浏览器冲突处理**：
  确保 `swarm.yaml` 中的 `browser` 模式为 `dedicated`，系统会自动为该 Pod 准备独立的浏览器 UserData 目录。
