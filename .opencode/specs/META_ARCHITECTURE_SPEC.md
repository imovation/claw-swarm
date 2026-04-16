# 通用智能体底座系统架构规格 (Meta-Architecture Spec)

> **意图账本双向锚定 (Bidirectional Traceability)**
> 📌 **原始意图溯源**：[2026-04-14 意图 1] 平台与业务解耦的三态智能体架构 (INTENTS.md)
> 🔄 **修订历史 (Changelog)**：
> - v1 (2026-04-14): 初始创建，剥离双轨模式，建立三态演进模型。
> - v2 (2026-04-16): 引入意图导向（Intent-Driven）结构与认知边界。

## 1. 核心意图 (Core Intent)
将 Agent 项目的职责从单体结构（Monolith）拆分为 **"三态演进模型" (3-Stage Agent Continuum)**，彻底解决上下文污染（Context Poisoning）问题。使 `.opencode/` 成为一个高度内聚、可复用的"通用 Agent 兵工厂"底座。

## 2. 边界约束 (Constraints)
- 🚫 **物理隔离禁区**：Platform Dev 严禁修改业务代码；Biz Dev 严禁修改 `.opencode/` 基建规则；App 绝对只读，严禁修改任何源码。
- 🚫 **认知隔离禁区**：诊断根因必须“只向事实”；求解方案时，Dev 模式必须首选“向内求解”（改代码），App 模式必须首选“向外求解”（改环境/提工单），严禁越界代庖。
- 🚫 **架构自洽禁区**：Onebot 自身的组件必须采用高内聚微模块形式，严禁在根目录散落孤魂野鬼脚本。

## 3. 状态契约 (State Contract)
- **前置依赖 (Inputs)**：底层的 `opencode.json` 仅保留极简物理配置。
- **预期副作用 (Side Effects)**：用户按 Tab 键切换 Agent 时，系统通过 `@file` 精确注入对应层级的红线规则（Rules）与系统架构（Specs）。
- **反哺流转 (Feedback Loop)**：App 报错 -> 写入 `INTENTS.md` -> 交给 Biz Dev；Biz Dev 受限 -> 写入 `.opencode/INTENTS.md` -> 交给 Platform Dev。

## 4. 验收标准 (Acceptance Criteria)
- [ ] 标准 1：在 App 模式下要求修改代码，Agent 必须明确拒绝并提示用户提交工单。
- [ ] 标准 2：`opencode.json` 中不存在任何与特定业务相关的 `instructions`。

---

## 5. 架构细节实现 (Implementation Details)

### 三态 Agent 角色定义

### 1. 平台开发架构师 (Platform Dev)
- **ID**: `platform-dev`
- **职责**: 负责"造机器的机器"。专门开发通用工具 (Skills)、制定通用规则 (Rules) 和系统架构。
- **作用域**: 仅限于 `.opencode/` 目录及底层基础设施。严禁修改业务代码。
- **注入上下文**: `@file .opencode/rules/platform-rules.md` (平台级准则：通用性、高内聚等)
- **权限**: 满血读写与命令执行权限。

### 2. 业务开发工程师 (Biz Dev)
- **ID**: `biz-dev` (默认 Agent)
- **职责**: 在平台框架的约束下，编写和维护具体的业务逻辑。
- **作用域**: 项目的业务代码目录（根目录及除 `.opencode/` 外的所有子目录）。
- **注入上下文**: 
  - `@file .opencode/rules/biz-dev-rules.md` (业务开发红线：Spec驱动、治本原则、KISS等)
  - `@file SYSTEM_SPEC.md` (业务系统架构)
- **权限**: 满血读写与命令执行权限。

### 3. 终端执行官 (App)
- **ID**: `app`
- **职责**: 面向终端用户的交互入口，响应自然语言指令并安全调用系统工具。
- **作用域**: 全局只读，或执行受限的 CLI 业务命令。禁止触碰任何源码和 Spec。
- **注入上下文**: `@file .opencode/rules/app-rules.md` (应用限制与终端操作规范)
- **权限**: `file_edit: "ask"`, `shell_cmd: "ask"`（需配置强制拦截）。

## 三、 目录拓扑与文件路由

底座系统采用标准化的目录结构，基于金字塔式的 `@file` 按需加载：

```text
.opencode/
├── opencode.json                 # 极简注册表（工具、Agent 路由），无全局业务 instruction
├── agents/                       # 三态角色定义层
│   ├── platform-dev.md           
│   ├── biz-dev.md                
│   └── app.md                    
├── rules/                        # 上下文红线库 (Context Payloads)
│   ├── platform-rules.md         # 平台开发红线
│   ├── biz-dev-rules.md          # 业务开发红线
│   └── app-rules.md              # 终端应用约束
├── specs/                        # 底座规范 (META, PYRAMID, ORIGIN)
├── tools/                        # 工程工具微模块 (如 sync-engine)
└── skills/                       # 能力武器库
    ├── deep-cure/                # 平台级排错 (供 platform/biz-dev 调用)
    ├── skill-creator/            
    └── ...
```

## 四、 实施重构路径 (Transition Path)

1. **配置瘦身**: 清空 `opencode.json` 中臃肿的 `instructions`，仅保留底层环境配置。
2. **规则入库**: 将开发红线迁移重构入 `.opencode/rules/biz-dev-rules.md`，并新设平台和应用规则。
3. **角色实例化**: 在 `.opencode/agents/` 下建立三态 Markdown 文件，使用 `@file` 精确引入对应的 `rules/`。
4. **遗留清理**: 删除项目根目录下不再使用的旧代理配置和全局说明。

## 五、 反哺闭环机制 (Feedback Loop)

为保持系统的自进化能力与角色物理边界，严格实施跨态投递：

1. **App 阶段 (终端发现问题)**
   - 严禁自行修改源码。
   - 当用户提出修改需求或发现 Bug 时，将记录写入业务意图池 (`INTENTS.md`)。
   - 回复标准话术：“已记录至业务意图单。请按 Tab 键切换至 `biz-dev` 模式进行修复/开发。”

2. **Biz Dev 阶段 (业务受困于基建)**
   - 严禁修改 `.opencode/` 目录内的规则和工具。
   - 当遇到系统红线阻碍、通用 Skill (如 deep-cure) 不满足要求时，将改进建议写入平台基建池 (`.opencode/INTENTS.md`)。
   - 回复标准话术：“遇到平台级限制，已记录至基建意图单。请按 Tab 键切换至 `platform-dev` 模式升级平台能力。”

3. **Platform Dev 阶段 (基建迭代)**
   - 处理 `.opencode/INTENTS.md` 中的工单，升级 Rules、Skills 或 Agent 设定。
   - 升级完成后，提示用户切换回 `biz-dev` 继续业务开发。