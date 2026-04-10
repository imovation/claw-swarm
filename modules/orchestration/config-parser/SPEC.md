# config-parser 功能规范 (Feature Spec)

## 一、 功能定位
负责读取并校验 `swarm.yaml`，将其解析为标准化的内部数据结构，供 reconciler 和 pod-provisioner 使用。
这是整个调和循环的第一步，也是最关键的防线。

## 二、 职责边界
- **只读**：本功能仅负责解析，不执行任何写操作。
- **防御性校验**：任何非法或缺失的字段必须在这里报错，不允许将非法配置传递给下游。

## 三、 输入 / 输出
- **输入**：`swarm.yaml` 文件路径。
- **输出**：`SwarmConfig` 数据结构，包含：
  - `global`：全局配置（proxy、orphan_policy、plugins、matrix）。
  - `pods[]`：Pod 配置列表（name、profile、port、token、resources、plugins、matrix）。

## 四、 当前实现
- **文件**：`modules/orchestration/config-parser/parser.py` ✅
- **技术方案**：使用 Python `yaml.safe_load()` 解析，SecretRef 解析，Pydantic 风格字段校验。

## 五、 功能特性
- ✅ SecretRef 支持 (`${VAR}` 和 `env:VAR` 格式)
- ✅ 字段级精确报错 (如 "pods[0].port 必须为整数")
- ✅ Profile 别名解析 (default/main/gateway)