# 声明式部署测试指南

本指南展示了如何测试和验证 `claw-swarm` 项目中实现的声明式开发模式功能。

## 前提条件

确保您已经：
1. 克隆了 `claw-swarm` 仓库
2. 安装了所有依赖（包括 OpenClaw 和 Node.js）
   ```bash
   pip install -r requirements.txt
   ```
3. 有权限运行 systemd 用户服务

## 测试 1: 基础声明式调和 (claw apply)

此测试验证 `claw apply` 能否读取 `swarm.yaml` 并使实际状态匹配期望状态。

### 步骤:

1. 查看当前 `swarm.yaml`:
   ```bash
   cat swarm.yaml
   ```

2. 运行 claw apply:
   ```bash
   claw apply
   ```

3. 验证输出显示:
   - 所有Pod都成功同步
   - 没有错误信息
   - 集群状态看板显示所有Pod为"已同步"

4. 检查实际运行的服务:
   ```bash
   systemctl --user list-units "openclaw-gateway*" --state=active
   ```

## 测试 2: 声明式端口修改 (claw port + claw apply)

此测试验证端口修改可以通过声明方式（编辑swarm.yaml）或命令方式（claw port）进行，并且两种方式能保持同步。

### 方法A: 声明方式（推荐）

1. 编辑 `swarm.yaml` 将 aimee Pod 的端口从 18990 改为 19999:
   ```yaml
   - name: aimee
     profile: aimee
     port: 19999  # 修改这里
     token: "666666"
     resources:
       browser: dedicated
   ```

2. 运行 claw apply:
   ```bash
   claw apply
   ```

3. 验证:
   - 输出显示 aimee Pod 端口已更新
   - 集群状态看板显示 aimee 端口为 19999
   - aimee 服务实际运行在端口 19999

### 方法B: 命令方式（快捷方式）

1. 使用 claw port 将 shining Pod 端口改为 20000:
   ```bash
   claw port shining 20000
   ```

2. 验证:
   - 输出显示端口已更新并同步到 swarm.yaml
   - 检查 swarm.yaml 中 shining 的端口现在是 20000
   - 集群状态看板显示 shining 端口为 20000

3. 运行 claw apply 验证幂等性:
   ```bash
   claw apply
   ```
   - 应该显示所有Pod已同步（因为状态已经匹配）

## 测试 3: 孤儿Pod自动处理

此测试验证根据 `global.orphan_policy` 设置自动处理孤儿Pod。

### 场景1: orphan_policy = warn (默认行为)

1. 确保 swarm.yaml 中的 orphan_policy 设置为 "warn":
   ```yaml
   global:
     orphan_policy: warn
   ```

2. 创建一个孤儿Pod（不在swarm.yaml中定义）:
   使用 Pod 供应器直接创建（参考 pod-provisioner 模块）

3. 验证Pod已创建:
   ```bash
   systemctl --user list-units "openclaw-gateway-test_orphan*" --state=active
   ```

4. 运行 claw apply:
   ```bash
   claw apply
   ```

5. 验证:
   - 输出中会显示发现孤儿Pod的警告
   - 但不会自动删除孤儿Pod（因为政策是warn）
   - test_orphan Pod仍然在运行

### 场景2: orphan_policy = delete (自动清理)

1. 将 swarm.yaml 中的 orphan_policy 设置为 "delete":
   ```yaml
   global:
     orphan_policy: delete
   ```

2. 确认 test_orphan Pod仍在运行（从上一步骤）

3. 运行 claw apply:
   ```bash
   claw apply
   ```

4. 验证:
   - 输出中会显示发现孤儿Pod并正在清理它们
   - test_orphan Pod被停止、禁用、服务文件被删除、目录被清理
   - Systemd 被重载

## 测试 4: 配置漂移检测与自动修复

此测试验证当Pod配置发生漂移时，claw apply能自动检测并修复。

### 步骤:

1. 修改 aimee Pod 的openclaw.json文件（手动造成配置漂移）:
   ```bash
   echo '{"test":"manual_change"}' > /home/imovation/.openclaw-aimee/openclaw.json
   ```

2. 运行 claw apply:
   ```bash
   claw apply
   ```

3. 验证:
   - 输出显示 aimee Pod 被重新供应（因为检测到配置差异）
   - openclaw.json 被恢复为标准格式
   - 集群状态看板显示 aimee 为"已同步"

## 测试 5: Profile别名统一

此测试验证所有脚本正确处理Profile别名(default/main/gateway)。

### 步骤:

1. 测试不同别名指向相同Pod:
   ```bash
   # 这些命令应该都操作相同的Pod（main Pod）
   claw port main 22000     # 使用 main
   claw port default 22000  # 使用 default
   claw port gateway 22000  # 使用 gateway
   ```

2. 验证:
   - 所有三个命令都应该成功修改端口为 22000
   - swarm.yaml 中 main Pod 的端口应该是 22000
   - 集群状态看板显示 main 端口为 22000

## 测试 6: 服务修复功能 (claw repair)

此测试验证修复损坏的服务文件功能。

### 步骤:

1. 有意损坏一个服务文件（例如，移除关键的环境变量）:
   ```bash
   sudo sed -i '/Environment=OPENCLAW_STATE_DIR/d' /home/imovation/.config/systemd/user/openclaw-gateway-aimee.service
   ```

2. 验证服务状态异常:
   ```bash
   systemctl --user status openclaw-gateway-aimee.service
   ```

3. 运行修复脚本:
   ```bash
   claw repair aimee
   ```

4. 验证:
   - 脚本成功运行并报告修复完成
   - 服务文件恢复了OPENCLAW_STATE_DIR环境变量
   - 服务重新启动并处于活动状态

## 测试 7: 幂等性验证

此测试验证所有操作都是幂等的（多次执行结果相同）。

### 步骤:

1. 运行 claw apply 两次连续:
   ```bash
   claw apply
   claw apply
   ```

2. 验证:
   - 第二次运行应该显示所有Pod已同步（没有变更）
   - 没有错误或意外的服务重启

3. 测试端口修改的幂等性:
   ```bash
   claw port shining 20000
   claw port shining 20000  # 第二次应该报告端口已经是目标值
   ```

## 期望结果

如果所有测试都成功通过，您将看到：

1. **声明式工作流**: 通过编辑swarm.yaml和运行claw apply来管理系统状态
2. **一致性**: 实际状态总是匹配swarm.yaml中声明的期望状态
3. **自动修复**: 配置漂移和损坏会被自动检测和修复
4. **孤儿处理**: 根据策略自动处理未声明但存在的Pod
5. **幂等性**: 重复应用相同的声明不会产生副作用
6. **统一接口**: 所有管理脚本使用一致的参数和行为模式

这些特性共同实现了真正的声明式基础设施管理，类似于Kubernetes的做法，但针对的是OpenClaw Pod的管理。