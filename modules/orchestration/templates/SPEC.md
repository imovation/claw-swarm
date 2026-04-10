# templates 功能规范 (Feature Spec)

## 一、 功能定位
统一管理所有需要动态生成的配置文件模板，包括 Systemd 服务文件和 Pod 初始配置。
将模板从脚本的 Heredoc 字符串中抽离，实现"逻辑与配置声明彻底解耦"。

## 二、 当前模板清单
| 模板文件 | 用途 | 渲染模块 |
|---|---|---|
| `systemd.service.j2` | Systemd 用户服务模板 | orchestration/templates/ |
| `openclaw.json.j2` | Pod 初始配置文件 | orchestration/templates/ |

## 三、 实现方式
- 所有 Heredoc 模板已提取为独立的 `.j2` 文件存放于本目录
- 使用 Python `Jinja2` 渲染引擎替代 Bash 字符串拼接
- 模板变更只需修改 `.j2` 文件，无需触碰核心逻辑脚本