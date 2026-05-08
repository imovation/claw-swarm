> ⚠️ **不可变账本原则 (Append-Only Ledger)** ⚠️
> 本文件是系统的第一性原理来源，记录了人类的每一次原始发声。**代码是瞬态的，意图是永恒的。**
> 任何 Agent 绝对禁止修改、删除或精简历史意图记录。所有新意图必须以追加（Append）的形式写在文件最末尾或最顶端。
>
# Claw-Swarm 业务意图记录 (Business Intents)

本文件记录 Claw-Swarm 业务层面的需求迭代历史。

---

### 模板

```markdown
## [日期] 第N次迭代
**意图来源**：人类直接描述 / 人类反馈 / Issue
**意图**：具体描述
**期望结果**：预期输出或行为
**关联 Spec**：对应的 SPEC.md 版本
```

---

## [2026-05-08] Profile 错位导致 Gateway 端口冲突与重启风暴 ✅ 已修复
**意图来源**：运行时诊断发现  
**意图**：`swarm.yaml` 中 pod `main` 声明 profile=default，但实际运行的是 `openclaw-gateway@main.service`（profile=main）。`claw apply` 会创建 `openclaw-gateway@default.service` 与运行中的 main-profile 网关争抢同一个端口 18789，导致 default 服务陷入无限重启循环（已达 104 次）。手动禁用 default 服务后恢复。  
**根因**：`reconciler.py::compute_diff()` 仅按 pod name 进行 diff，未检查实际运行服务的 profile 是否与 swarm.yaml 声明的 profile 一致。当实际服务 profile 与期望不一致时（如 @main vs @default），reconciler 无法检测出来，直接在旧服务占端口的情况下创建新服务，导致冲突。  
**修复**：
1. `compute_diff()` 增加 profile 匹配检查：通过 `resolve_pod()` 解析期望 profile_arg，与 systemd 实际 profile 对比，不匹配时标记为 orphan + to_create
2. `reconcile()` 将 `handle_orphans()` 移至 provision 循环之前执行，确保旧服务先被停止释放端口
3. 执行 `claw apply` 清理残留的 `openclaw-gateway@main.service`，成功创建正确的 `openclaw-gateway@default.service`
**期望结果**：`claw apply` / `claw repair` 应正确识别 pod 的实际 profile 归属，避免创建端口冲突的服务实例。`swarm.yaml` 中的 profile 字段与实际运行的 gateway 实例 profile 应保持一致。  
**关联 Spec**：SYSTEM_SPEC.md v2