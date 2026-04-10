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

## 三、 CLI 入口与路由
通过统一入口 `bin/claw` 路由至本模块：
- `claw matrix add ...` — 凭证写入
- `claw matrix verify ...` — E2EE 诊断与验证
- `claw matrix devices ...` — 设备管理
- `claw matrix pairing ...` — 配对审批
- `claw matrix profile ...` — 资料设置
- `claw matrix direct ...` — 私信修复

## 四、 下属功能树 (Features)
| 功能目录 | 状态 | 说明 |
|---|---|---|
| `account-manager/` | 待迁移 | 账号凭证写入与多账号管理 |
| `e2ee-verifier/` | 待迁移 | E2EE 加密状态验证与 bootstrap |
| `device-manager/` | 待迁移 | 设备清理与配对管理 |

## 五、 遗留脚本清单
| 文件 | 状态 |
|---|---|
| `lib/matrix_utils.sh` | 待迁移 → account-manager/ |
| `bin/claw-matrix-add` | 待迁移 → account-manager/ |
| `bin/claw-matrix-verify` | 待迁移 → e2ee-verifier/ |
| `bin/claw-matrix-devices` | 待迁移 → device-manager/ |
| `bin/claw-matrix-pairing` | 待迁移 → device-manager/ |