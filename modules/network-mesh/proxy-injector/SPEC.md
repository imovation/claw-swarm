# proxy-injector 功能规范 (Feature Spec)

## 一、 功能定位
负责从 `swarm.yaml` 的 `global.proxy` 字段解析代理配置，并将其统一注入到每个 Pod 的
`runtime/env` 文件中，确保所有实例共享一致的网络出口策略，无需在每个 Pod 中单独配置。

## 二、 职责边界
- **只注入，不路由**：本功能仅负责将代理配置写入环境文件，不处理实际的网络流量路由。
- **全量覆盖**：每次 `claw apply` 执行时，重新写入代理配置，确保与声明一致。

## 三、 支持的代理变量
| 源字段 (swarm.yaml) | 注入的环境变量 |
|---|---|
| `global.proxy.http` | `HTTP_PROXY`, `http_proxy` |
| `global.proxy.https` | `HTTPS_PROXY`, `https_proxy` |
| `global.proxy.socks` | `ALL_PROXY`, `all_proxy` |
| `global.proxy.no_proxy` | `NO_PROXY`, `no_proxy` |

## 四、 SecretRef 支持
代理配置值支持 `${ENV_VAR}` 格式的环境变量引用（SecretRef），解析时从宿主机环境读取实际值。

##五、 当前实现
- **文件**：`modules/network-mesh/proxy-injector/injector.py` ✅
- **技术方案**：纯 Python 实现，无额外依赖 (无 jq)

## 六、 功能特性
- ✅ 幂等注入：先清理旧代理配置，再写入新配置
- ✅ 纯 Python 实现：无外部命令依赖
- ✅ SecretRef 解析支持