# Network-Mesh (网络与代理) 模块规范

## 一、 模块定位
本模块负责 Claw-Swarm 集群中所有与**网络通信**相关的基础设施：包括全局代理的统一注入、Pod 间的端口分配与变更管理，以及 Feishu/Lark 等对外渠道的接入配置。

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
- `claw port <NAME> <PORT>` — 变更端口（同步更新 Systemd 服务文件与 swarm.yaml 声明）

## 四、 下属功能树 (Features)
| 功能目录 | 状态 | 说明 |
|---|---|---|
| `proxy-injector/` | ✅ 已迁移 | 代理配置解析与幂等注入（纯 Python 实现） |
| `port-manager/` | 待迁移 | 端口声明与变更管理 |

## 五、 遗留脚本清单
| 文件 | 状态 |
|---|---|
| `bin/claw-port` | 待迁移 → port-manager/ |

## 六、 Feishu/Lark 渠道 (暂未迁移)
- `bin/claw-lark` — Feishu 机器人接入配置
- `bin/claw-bot-add` — Bot 添加与绑定
- `bin/claw-agent-create` — Agent 创建与绑定