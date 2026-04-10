# account-manager 功能规范 (Feature Spec)

## 一、 功能定位
负责 Matrix 账号凭证的声明式写入与管理。将 `swarm.yaml` 中的 Matrix 配置（包括多账号）
解析并写入到对应 Pod 的 `openclaw.json` 中，完成 Matrix 渠道的接入配置。

## 二、 支持的认证方式
1. **Token 认证**：直接使用 `accessToken` 字段，写入配置后立即生效。
2. **密码认证**：使用 `userId` + `password` 字段，OpenClaw 启动时登录并缓存令牌。

## 三、 SecretRef 解析规则
配置值支持两种环境变量引用格式：
- `${VAR_NAME}` — 从宿主机当前环境变量读取。
- `env:VAR_NAME` — 同上，备选格式。

## 四、 多账号支持
通过 `accounts:` 字段可为单个 Pod 配置多个 Matrix 账号，并通过 `defaultAccount` 指定默认账号。

## 五、 当前实现
- **文件**：`modules/matrix-channel/account-manager/`（Python 模块）。
- **调用时机**：由 `claw apply` 在每次调和时自动触发。