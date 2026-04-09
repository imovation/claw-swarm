# Matrix Channel 模块规范

## 一、 模块定位
本模块负责 Claw-Swarm 实例与 Matrix 协议通信的完整生命周期管理，重点解决 E2EE 端到端加密、设备验证、以及复杂的多账号/多房间策略。

## 二、 声明式配置入口
推荐所有 Matrix 行为均通过 `swarm.yaml` 中的 `matrix:` 字段声明。
支持的功能包括：
- `accessToken` 认证与密码认证。
- `encryption` 状态与启动验证 (`startupVerification`)。
- 私信门控 (`dm.policy`) 与自动加群 (`autoJoin`)。
- 线程绑定 (`threadBindings`) 与操作审批 (`execApprovals`)。

## 三、 底层 CLI 工具链
*遇到 Matrix 相关问题时，Agent 可通过以下底层脚本排查和配置：*

1. **凭证写入**：`./bin/claw-matrix-add <PROFILE> --homeserver <URL> --token <TOKEN> --encryption`
2. **E2EE 诊断与验证**：
   - 查看状态：`./bin/claw-matrix-verify <PROFILE> status`
   - 初始化自举：`./bin/claw-matrix-verify <PROFILE> bootstrap`
   - 密钥备份：`./bin/claw-matrix-verify <PROFILE> backup status`
3. **设备与配对**：
   - 清理死设备：`./bin/claw-matrix-devices <PROFILE> prune-stale`
   - 审批配对码：`./bin/claw-matrix-pairing <PROFILE> approve <CODE>`
4. **私信异常修复**：`./bin/claw-matrix-direct <PROFILE> repair --user-id @user:server`