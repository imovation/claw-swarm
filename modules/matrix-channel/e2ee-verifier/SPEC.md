# e2ee-verifier 功能规范 (Feature Spec)

## 一、 功能定位
负责 Matrix E2EE（端到端加密）的生命周期管理，包括加密状态检查、初始化自举 (Bootstrap)、
密钥备份与恢复，以及配对验证流程的管理。

## 二、 核心操作
| 操作 | 命令 | 说明 |
|---|---|---|
| 状态检查 | `claw matrix verify <PROFILE> status` | 查看当前 E2EE 状态 |
| 详细诊断 | `claw matrix verify <PROFILE> status --verbose` | 含设备密钥信息 |
| 初始化 | `claw matrix verify <PROFILE> bootstrap` | 首次配置 E2EE |
| 备份状态 | `claw matrix verify <PROFILE> backup status` | 查看密钥备份情况 |

## 三、 加密状态隔离
每个 Pod 的 Matrix 加密状态存储在各自独立的目录中：
- 路径：`~/.openclaw-<NAME>/matrix/`
- 严禁不同 Pod 共享加密状态目录。

## 四、 当前实现
- **文件**：`bin/claw-matrix-verify`（Bash 脚本）。
- **排错 Skill**：遇到复杂的 E2EE 问题时，加载 `matrix-openclaw-troubleshooter` 技能。