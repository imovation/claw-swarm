# reconciler 功能规范 (Feature Spec)

## 一、 功能定位
调和控制器 (Reconciler) 是编排模块的核心控制面。它读取 config-parser 的输出（期望状态），并与
宿主机当前 Systemd 服务的实际状态进行比对，驱动系统达到期望状态。

## 二、 职责边界
- **感知现状**：通过 `systemctl` 探测当前运行的 `openclaw-gateway*` 服务列表。
- **差量比对 (Diff)**：将期望 Pod 列表与实际服务列表进行比对，产出变更计划。
- **驱动调和**：
  - 新增 Pod → 调用 pod-provisioner 创建。
  - 配置变更 Pod → 调用 pod-provisioner 滚动更新。
  - 孤儿 Pod → 根据 `global.orphan_policy` 执行 `warn` 或 `delete`。
- **不直接操作文件系统**：文件和 Systemd 的实际写操作均委托给 pod-provisioner。

## 三、 调和循环伪代码
```
desired  = config_parser.parse("swarm.yaml")
actual   = systemd.list("openclaw-gateway*")
diff     = compute_diff(desired, actual)

for pod in diff.to_create:   provisioner.create(pod)
for pod in diff.to_update:   provisioner.update(pod)
for pod in diff.orphans:     handle_orphan(pod, policy)
```

## 四、 当前实现
- **文件**：`bin/claw-apply`（待迁移至本目录 `reconciler.py`）。
- **已知问题**：目前无精确 Diff，每次 apply 都全量执行，效率低下。

## 五、 重构目标
- 实现精确 Diff：只有真正发生变更的 Pod 才触发重启。
- 变更计划可视化：`claw apply --dry-run` 输出清晰的变更计划。