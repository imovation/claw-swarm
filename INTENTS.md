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


## [2026-05-10] 主实例 Matrix 双账号配置及 account-manager 模块双缺陷修复 ✅ 已修复
**意图来源**：用户直接配置需求  
**意图**：为主实例（main）配置 Matrix 双账号 shiningbot 和 tianerbao；在过程中发现并反哺修复 account-manager 模块的两个关键缺陷  
**期望结果**：  
1. 主实例 Matrix 双账号成功启动并运行  
2. account-manager 模块恢复 claw matrix add 可用性并支持多账号  
**关联 Spec**：SYSTEM_SPEC.md v2, MODULE_SPEC.md (matrix-channel)  

### 问题背景
用户请求为 main 实例配置两个 Matrix 账号。尝试使用 `claw matrix add` 时发现：
1. 命令直接崩溃，错误为 KeyError: 'config'  
2. 即使命令正常，每次调用只能配置单个账号，后调用会覆盖前一次，无法实现真正的双账号共存  

### 诊断过程
- 错误源头：`modules/matrix-channel/account-manager/account_manager.py` 中多处使用 `pod_info["config"]`  
- 根因：`modules/orchestration/config-parser/utils.py` 的 `resolve_pod()` 函数返回字典缺少 `config` 键，尽管 `PodInfo` TypedDict 已声明该字段  
- 进一步检查发现：account-manager 设计仅支持单账号模式，与 MODULE_SPEC.md 声明的「通过 `accounts:` 字段可为单个 Pod 配置多个 Matrix 账号」相矛盾  

### 修复方案（由 biz-dev 执行）
**Bug 1 - 修复 config 缺失**  
- 文件：`modules/orchestration/config-parser/utils.py`  
- 修改：在 `resolve_pod()` 返回字典中添加 `"config"` 键  
  - default/main/gateway profile → `~/.openclaw/openclaw.json`  
  - 其他 profile → `~/.openclaw-{profile}/openclaw.json`  

**Bug 2 - 实现多账号支持**  
- 文件：`modules/matrix-channel/account-manager/account_manager.py`  
- 修改：重写 CLI 参数处理，新增：  
  - `--account <id>`：指定账号 ID，写入 `config.channels.matrix.accounts.<id>`  
  - `--default-account <id>`：设置全局 `defaultAccount`  
  - 自动多账号检测：未显式指定 `--account` 时，若已存在 `accounts` 对象则自动推导 account key 并采用多账号格式  
  - 新增 `list` 子命令：`claw matrix list <profile>` 列出该 Pod 的所有 Matrix 账号  
- 配置分离：新增 `_split_conf()` 函数，自动将混合配置拆分为顶层共享字段（enabled、dm、encryption、groupPolicy 等）和账号级字段（userId、password、accessToken、deviceName）  
- 向后兼容：未指定 `--account` 且无已有 `accounts` 时，保持单账号顶层写入格式  

**路由适配**  
- 文件：`bin/claw`  
  - 扩展 `MATRIX_ROUTES` 新增 `"list"` 子命令  
  - 修改 `route_matrix()` 将子命令名称作为首参传递给目标脚本  
- 文件：`modules/matrix-channel/device-manager/device_manager.py`、`e2ee-verifier/e2ee_verifier.py`  
  - 修改 argparse 主函数，新增 `subcommand` 位置参数以适配 bin/claw 的新行为  

### 验证结果
- 主实例 `openclaw-gateway@default.service` 重启后日志显示：  
  `[matrix] [shiningbot] starting provider (https://matrix.imovation.cn)`  
  `[matrix] [tianerbao] starting provider (https://matrix.imovation.cn)`  
- 配置文件 `~/.openclaw/openclaw.json` 中 channels.matrix 结构符合 OpenClaw 多账号规范  
- 所有修改过的 .py 文件均通过 `python3 -m py_compile` 语法检查  

> 本次修复通过「标本兼治」：既解决了用户当前的双账号配置需求（标），又从根源上消除了 account-manager 模块的结构性缺陷（本），确保类似问题不再复发。