# Network-Mesh (网络与代理) 模块规范

## 一、 模块定位
本模块负责 Claw-Swarm 集群中所有与**网络通信**相关的基础设施：包括全局代理的统一注入、Pod 间的端口分配与变更管理。

## 二、 声明式配置入口
所有代理行为均通过 `swarm.yaml` 的 `global.proxy` 字段统一声明，由 `claw apply` 自动注入到每个 Pod 的运行时环境。
```yaml
global:
  proxy:
    http: http://127.0.0.1:7897/
    https: http://127.0.0.1:7897/
    socks: socks://127.0.0.1:7897/
    no_proxy: localhost,127.0.0.1,...
```

## 三、 CLI 入口与路由
通过统一入口 `bin/claw` 路由至本模块：
- `claw port <NAME> <PORT>` — 变更端口 (port-manager)

## 四、 下属功能树 (Features)
| 功能目录 | 状态 | 说明 |
|---|---|---|
| `proxy-injector/` | ✅ 已完成 | 代理配置解析与幂等注入 (纯 Python) |
| `port-manager/` | ✅ 已完成 | 端口声明与变更管理 (冲突检测 + swarm.yaml 同步) |

## 五、 遗留文件清单 (已废弃)
| 文件 | 归属模块层 |
|---|---|
| `bin/claw-port` | port-manager |