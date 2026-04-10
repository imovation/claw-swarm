# device-manager 功能规范 (Feature Spec)

## 一、 功能定位
负责 Matrix 设备列表的生命周期管理，包括查看已注册设备、清理过期/僵尸设备，以及管理
配对码 (Pairing Code) 的审批流程。

## 二、 核心操作
| 操作 | 命令 | 说明 |
|---|---|---|
| 查看设备 | `claw matrix devices <PROFILE> list` | 列出所有已注册设备 |
| 清理过期设备 | `claw matrix devices <PROFILE> prune-stale` | 移除长期不活跃设备 |
| 查看配对请求 | `claw matrix pairing <PROFILE> list` | 查看待审批的配对请求 |
| 批准配对 | `claw matrix pairing <PROFILE> approve <CODE>` | 审批指定配对码 |

## 三、 当前实现
- **设备管理**：`modules/matrix-channel/device-manager/`（Python 模块）
- **配对管理**：`modules/matrix-channel/device-manager/`（Python 模块）