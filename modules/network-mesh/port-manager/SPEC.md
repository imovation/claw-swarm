# port-manager 功能规范 (Feature Spec)

## 一、 功能定位
负责管理 Pod 的端口声明与变更，确保 `swarm.yaml` 中的端口声明与宿主机 Systemd 服务的
实际监听端口始终保持一致（双向同步）。

## 二、 职责边界
- **声明式变更**：通过修改 `swarm.yaml` 中的 `pods[].port` 字段触发变更，再执行 `claw apply` 生效。
- **命令式变更**：通过 `claw port <NAME> <PORT>` 命令直接变更端口，工具自动回写 `swarm.yaml`，保持声明一致性。
- **冲突检测**：变更前检查目标端口是否已被占用。

## 三、 变更流程
```
claw port <NAME> <NEW_PORT>
  ├─ 1. 检查 <NEW_PORT> 是否被占用 (ss -tlnp)
  ├─ 2. 修改 swarm.yaml 中对应 Pod 的 port 字段
  ├─ 3. 更新 Pod 的 runtime/env 文件中的 OPENCLAW_PORT
  └─ 4. 重载并重启对应的 Systemd 服务
```

##四、 当前实现
- **文件**：`modules/network-mesh/port-manager/port_manager.py` ✅

## 五、 功能特性
- ✅ 端口冲突检测
- ✅ swarm.yaml 双向同步
- ✅ Systemd 服务文件自动更新
- ✅ 自动重载与重启