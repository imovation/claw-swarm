# Claw-Kubernetes Vision & Roadmap (v1.5)

## 🌟 终极愿景 (The Ultimate Vision)
打造"面向 OpenClaw 的 Kubernetes"：一个能够在大规模单机或多节点集群上，自动供应、调度、联网隔离的 AI 代理环境（Pod）的控制平面。

---

## 📅 阶段性成果 (Milestones)

### Phase 0: 物理隔离 (Completed ✅)
- ✅ `main` 与 `aimee` 实例完全解耦。
- ✅ 插件物理拷贝（Break symlinks）。
- ✅ 迁移至 Systemd User Services。

### Phase 1: 声明式自动化 (Completed ✅)
- ✅ 实现 `swarm.yaml` 声明式配置。
- ✅ 开发 `bin/claw-apply` 控制器，实现幂等同步。
- ✅ 建立 `CONSTITUTION.md` 开发宪法。
- ✅ 引入 **Virtual Home (虚拟家目录)**：通过 XDG 变量和浏览器路径强制隔离 Pod 运行环境。
- ✅ 建立 `bin/claw-status` 看板：实时监控内存、模型和同步状态。
- ✅ 建立 `bin/claw-tui` 快捷入口：环境对齐的终端交互工具。

### Phase 2: Matrix 渠道支持 (Completed ✅)
- ✅ 声明式 Matrix 配置 (`swarm.yaml` global.matrix / pods[].matrix)。
- ✅ 6 个 Matrix CLI 工具 (`claw-matrix-add/verify/devices/pairing/profile/direct`)。
- ✅ SecretRef 支持 (环境变量引用解析)。
- ✅ 环境变量自动注入 (`MATRIX_*`)。
- ✅ 多账号支持与隔离。
- ✅ E2EE 验证封装 (bootstrap/设备验证/密钥备份)。

### Phase 3: 统一网关 (Unified Ingress) — 评估结论：暂不适用
- **调研结论**：经实际验证，Ingress 对于当前使用场景（租户飞书访问 + 运维 TUI 操作）无实际价值。
- **原因**：飞书通信走 WebSocket，无需 Web UI；运维通过 `claw-tui` 不需要端口。
- **决策**：移除 Ingress 相关工作，保持架构简洁。

---

## 🚀 未来计划 (Future Sessions)

### Phase 3: 资源配额与自愈 (Resource Limits & Self-Healing)
- **目标**：限制内存增长，提高系统稳定性。
- **任务**：
  - 支持 `resources.memory_limit` 配置注入 Systemd Cgroups (`MemoryHigh`)。
  - 实现 Liveness 存活探测，自动重启假死 Pod。

### Phase 4: 信任网格与 ACP 联网 (Agent Mesh)
- **目标**：连接实例，实现跨 Pod 任务下发。
- **任务**：
  - 利用 OpenClaw ACP 协议，在 `swarm.yaml` 中定义"信任关系"。
  - 允许 Aimee (Feishu) 通过内网 ACP 直接调用 Main (SSH) 的能力。

### Phase 5: 控制台可视化 (Control Plane UI)
- **目标**：可视化集群监控与操作。
- **任务**：
  - 开发 `Claw-Swarm Dashboard` Web 界面。
  - 支持图形化编辑 `swarm.yaml` 并热部署。
