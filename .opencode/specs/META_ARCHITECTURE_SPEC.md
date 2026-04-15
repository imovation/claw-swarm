# 通用智能体底座系统架构规格 (Meta-Architecture Spec)

## 一、 架构愿景
将 Agent 项目的职责从单体结构（Monolith）拆分为 **"三态演进模型" (3-Stage Agent Continuum)**，彻底解决上下文污染问题，实现**平台基础设施**与**具体业务逻辑**的物理隔离与按需加载。

本架构使 `.opencode/` 成为一个高度内聚、可复用的"通用 Agent 兵工厂"底座。

### 核心哲学：维度的正交与认知塌缩

Onebot 的架构基石建立在两个正交的维度之上：**【领域】（平台 vs 业务）** 与 **【模式】（开发 vs 应用）**。

在完美的 2x2 矩阵中，这四个象限通过“软件工程”的物理现实发生了一次奇妙的塌缩：
1. **【平台 x 开发】** = 平台开发架构师 (Platform Dev)
2. **【平台 x 应用】** 与 **【业务 x 开发】** = 完美重叠。因为使用“平台系统”的过程就是“开发业务系统”的过程。这二者合并为同一角色 (Biz Dev)。
3. **【业务 x 应用】** = 业务终端应用 (App)

这解释了为什么四个正交场景最终演化为完美的“三态模型”。

### 行为边界：向内求解 vs 向外求解
除了物理隔离（权限限制），Onebot 在认知层面严格定义了 Agent 的“求解方向”：
- **开发模式（Dev）必须“向内求解”**：当系统运行报错时，Agent 必须审视自身（源码、基建结构、业务逻辑）是否存在缺陷，通过改进系统自身来适配外部。严禁通过随意修改外部环境（如乱改宿主机配置、屏蔽报错）来掩盖代码问题。
- **应用模式（App）只能“向外求解”**：当无法满足用户需求时，Agent 在不修改系统自身的前提下，通过调用业务接口、调整用户输入、解释当前环境状态来解决特定场景。
## 二、 三态 Agent 角色定义

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
│   ├── biz-dev-rules.md          # 业务开发红线 (原 core-rules.md 演变)
│   └── app-rules.md              # 终端应用约束
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
   - 当用户提出修改需求或发现 Bug 时，将记录写入业务需求池 (`REQUESTS.md`)。
   - 回复标准话术：“已记录至业务需求单。请按 Tab 键切换至 `biz-dev` 模式进行修复/开发。”

2. **Biz Dev 阶段 (业务受困于基建)**
   - 严禁修改 `.opencode/` 目录内的规则和工具。
   - 当遇到系统红线阻碍、通用 Skill (如 deep-cure) 不满足要求时，将改进建议写入平台基建池 (`.opencode/REQUESTS.md`)。
   - 回复标准话术：“遇到平台级限制，已记录至基建需求单。请按 Tab 键切换至 `platform-dev` 模式升级平台能力。”

3. **Platform Dev 阶段 (基建迭代)**
   - 处理 `.opencode/REQUESTS.md` 中的工单，升级 Rules、Skills 或 Agent 设定。
   - 升级完成后，提示用户切换回 `biz-dev` 继续业务开发。