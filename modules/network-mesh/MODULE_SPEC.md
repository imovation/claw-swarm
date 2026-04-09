# Network-Mesh (网络与代理) 模块规范

## 一、 模块定位
本模块负责 Claw-Swarm 集群中所有与**网络通信**相关的基础设施：包括全局代理的统一注入、Pod 间的端口分配与变更管理，以及 Feishu/Lark 等对外渠道的接入配置。

## 二、 声明式配置入口
所有代理行为均通过 `swarm.yaml` 的 `global.proxy` 字段统一声明，由 `claw-apply` 自动注入到每个 Pod 的运行时环境。
```yaml
global:
  proxy:
    http: http://127.0.0.1:7897/
    https: http://127.0.0.1:7897/
    socks: socks://127.0.0.1:7897/
    no_proxy: localhost,127.0.0.1,...
```

## 三、 底层 CLI 工具链
- **端口变更**：`./bin/claw-port <NAME> <NEW_PORT>`（同步更新 Systemd 服务文件与 swarm.yaml 声明）
- **进程状态**：`./bin/claw-ps`（精细化进程监控）
- **Feishu 机器人接入**：`./bin/claw-lark <PROFILE> [BOT_ID] [APP_ID] [APP_SECRET]`
- **Feishu Bot 绑定**：`./bin/claw-bot-add <PROFILE> <BOT_ID> <APP_ID> <APP_SECRET>`
- **Agent 创建与绑定**：`./bin/claw-agent-create <PROFILE> <AGENT_NAME> [BOT_ID]`

## 四、 下属功能树 (待重构迁移)
- `proxy-injector/`：代理配置解析与注入逻辑。
- `port-manager/`：端口声明与变更管理。