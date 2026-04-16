# 会话状态快照 (Session State Snapshot)

> 📌 **原始意图溯源**：INTENTS.md 需求 1 & 需求 2 — 三态架构 & 反哺闭环
> 🔄 **修订历史 (Changelog)**：
> - 2026-04-17: 初始落盘，涵盖 Phase 4 全部积累

---

## Goal

用户有两个核心目标：

1. **已完成**：从 claw-swarm 项目中提取通用智能体底座系统，命名为 **onebot**，并推送到 GitHub 仓库 https://github.com/imovation/onebot
2. **持续迭代**：基于"意图导向（Intent-Driven）"模型，持续优化 onebot 的架构哲学、认知边界、安全协议和同步机制，确保其成为可复用的通用智能体底座

---

## Instructions

### 核心准则（始终生效，通过 agent rules 自动注入）

1. **opencode 原生机制优先**：实现任何功能或约束行为前，必须先查阅 https://opencode.ai/docs/ 确认 opencode 是否原生支持
2. **替换清理准则**：引入新机制替代旧机制时，必须清理旧机制中被完全替代的部分，只加不减会导致双重声明
3. **Spec 驱动 / 意图导向**：任何代码修改前，必须先更新对应的 SPEC.md。一切执行的起点必须是建立或更新 Spec
4. **安全编辑协议 (Safe Edit Protocol)**：修改任何非空长文件时，**绝对禁止**使用全量覆盖写入（如 `cat > file`）。必须使用精确的字符串替换工具（Edit）、增量的 `sed` 或 Python 脚本进行"外科手术式"的局部修改。若必须重写，必须先创建 `.bak` 备份并用 `diff` 自证无遗漏
5. **强制自发审计 (Proactive Self-Audit)**：严禁将"全面深度自检"作为依赖用户催促的被动行为！完成任何任务后，必须自发使用工具审视全局文件，确认没有违背金字塔架构，并在回复中主动附上自检报告
6. **不可变账本原则 (Append-Only Ledger)**：`INTENTS.md` 文件记录人类的每一次原始发声。**代码是瞬态的，意图是永恒的。** 任何 Agent 绝对禁止修改、删除或精简历史意图记录，所有新意图必须以追加形式写入

### 三态 Agent 架构定义

| Agent | ID | 职责 | @file 注入 | 权限 |
|-------|-----|------|-----------|------|
| 平台开发架构师 | platform-dev | 造"造机器的机器"，维护 .opencode/ 基建 | platform-rules.md + META_ARCHITECTURE_SPEC.md + SPEC_PYRAMID.md | 满血读写 |
| 业务开发工程师 | biz-dev (默认) | 写业务代码，受平台红线约束 | biz-dev-rules.md + SPEC_PYRAMID.md + SYSTEM_SPEC.md | 满血读写 |
| 终端执行官 | app | 面向用户交互，安全执行命令 | app-rules.md + SYSTEM_SPEC.md | file_edit: ask, shell_cmd: ask |

### 认知边界原则

- **诊因只向事实**：诊断根因时必须保持客观，不偏不倚
- **求解向内优先（Dev 模式）**：求解时首选向内求解（修改系统/代码本身），只有确定智能体本身没问题或改进自身无法解决后，才向外求解（检查外部环境）
- **求解向外优先（App 模式）**：求解时首选向外求解（调整外部环境/参数），如果外部环境没问题或改变方式非原生，则向内求解，触发反哺机制
- **反哺闭环**：App → 写入 INTENTS.md → Biz Dev；Biz Dev → 写入 .opencode/INTENTS.md → Platform Dev

### 架构哲学：维度的正交与塌缩

【平台/业务】与【开发/应用】两个维度是正交的，但【平台×应用】=【业务×开发】（因为使用平台就是开发业务），所以合并为一个 Agent (Biz Dev)，最终三态：Platform Dev → Biz Dev → App

### 元架构自洽（吃自己的狗粮）

Onebot 自身的物理目录受 Opencode 引擎强解析规则限制，无法套用业务的 `modules/` 结构（物理变通）；但精神内核绝对服从金字塔架构——所有工具/Skill 必须采用高内聚微模块形式（如 `.opencode/tools/sync-engine/`），将 SPEC.md 与可执行代码同生同灭地放在同一子目录

### 双向同步引擎 (onebot.sh)

- `pull`：从 GitHub 拉取最新 onebot 核心，安全覆盖 .opencode/agents、rules、specs、tools、skills（通用的），**绝不覆盖** opencode.json 和 INTENTS.md
- `push`：将当前项目经过验证的基建反哺到本地 onebot 母体仓库，仅覆写母体已存在的通用 Skill（防止业务 Skill 污染母体），新通用 Skill 需首次手动复制

### AI-Native Spec 模板 (SPEC_TEMPLATE.md)

所有 SPEC.md 必须强制采用此骨架：
1. **核心意图 (Core Intent)**：一句话说明存在意义
2. **边界约束 (Constraints)**：🚫 明确"什么绝对不能做"
3. **状态契约 (State Contract)**：前置依赖、预期副作用
4. **验收标准 (Acceptance Criteria)**：可物理验证的 Boolean 标准

头部必须包含**双向锚定溯源**：
```markdown
> 📌 **原始意图溯源**：[指向 INTENTS.md 中的具体日期或意图编号]
> 🔄 **修订历史 (Changelog)**：
```

### 智能体执行生命周期

[立项审查 Spec First] → [代码实现 Code] → [强制自检 Proactive Audit] → [交付闭环 Deliver]

---

## Discoveries

### 关键发现：opencode 上下文分层机制

| 层级 | 机制 | 作用域 |
|------|------|--------|
| 全局层 | `~/.config/opencode/AGENTS.md` + `opencode.json` | 所有项目 |
| 项目始终层 | 项目 `opencode.json` `instructions` + `AGENTS.md` | 当前项目每次会话 |
| 模式层 | `.opencode/agents/*.md` | Tab 切换时加载对应 agent |
| 按需层 | `.opencode/skills/*/SKILL.md` | 触发时加载 |
| 按需层 | AGENTS.md @file 引导 | 显式 Read 时加载 |

**关键限制**：opencode 的 `instructions` 对所有 primary agent 生效，无法按 agent 差异化。所以必须"瘦配置，胖角色"——把具体规则下放到 agent 的 @file 注入中。

**关键限制**：agent markdown 的 YAML frontmatter 中不支持 `permission` 字段（会导致 Zod 校验报错 `Invalid input permission`，opencode 无法启动），权限控制只能通过 rules 中的提示词红线进行软约束。

### 历次自检中发现并修复的关键 Bug 清单

1. **permission 字段导致 opencode 启动崩溃** → 移除 YAML frontmatter 中的 permission 块
2. **@file 路径错误（docs/SYSTEM_SPEC.md 不存在）** → 修正为 SYSTEM_SPEC.md
3. **claw-swarm 中残留通用内容** → 提取金字塔架构、AOP、渐进式披露等到 SPEC_PYRAMID.md；提取通用需求到 onebot/.opencode/INTENTS.md；删除 core-agent 模块；清理 README.md、ARCHITECTURE.md、ROADMAP.md 中的过时引用
4. **onebot 中的业务污染** → 移除 opencode-model-manager skill（OpenClaw 专属）；清理 app-rules.md 中的 claw 命令示例；抽象 META_ARCHITECTURE_SPEC.md 中的 claw-swarm 引用
5. **onebot 缺少 .gitignore** → 补充通用 .gitignore
6. **claw-swarm 缺少 requirements.txt** → 补充 Python 依赖声明
7. **onebot 根目录缺少 REQUESTS.md（后改名 INTENTS.md）模板** → 补充反哺机制着陆点
8. **onebot.sh 未同步 .opencode/tools/ 目录** → 补齐 tools/ 的 cp 逻辑
9. **REQUESTS.md → INTENTS.md 重命名遗漏** → 根目录模板、.opencode/ 内部、英文括号标题均需替换
10. **全量覆写导致 Spec 内容被毁灭性删除** → git revert 回滚，改用"头部注入+原有内容下沉"策略；建立安全编辑协议
11. **platform-rules.md 缺少安全编辑协议** → 因 sed 匹配标题不存在导致注入遗漏，手动追加为 §6
12. **deep-cure/INTENTS.md 缺少不可变账本声明** → 补齐
13. **onebot.sh 硬编码 deep-cure** → pull 改为全量拷贝 skills/*；push 改为仅覆写母体已存在的通用 Skill
14. **platform-dev agent 未注入 META_ARCHITECTURE_SPEC.md 和 SPEC_PYRAMID.md** → 补齐 @file
15. **app agent 未注入 SYSTEM_SPEC.md** → 补齐 @file（使其能看到业务命令列表）

---

## Accomplished

### 已完成

1. ✅ 设计并实施"三态演进模型"（Platform Dev / Biz Dev / App）
2. ✅ 实现反哺闭环机制（App→Biz Dev→Platform Dev）
3. ✅ 从 claw-swarm 提取通用底座为独立仓库 onebot (https://github.com/imovation/onebot)
4. ✅ 建立双向同步引擎 onebot.sh（pull/push）
5. ✅ 确立"诊因向事实，求解分内外"认知边界
6. ✅ 确立"维度的正交与塌缩"架构哲学
7. ✅ 实施"意图导向"范式转换（REQUESTS→INTENTS，需求→意图）
8. ✅ 建立不可变账本原则（Append-Only Ledger）
9. ✅ 建立双向锚定溯源（Bidirectional Traceability）
10. ✅ 建立 AI-Native Spec 模板（SPEC_TEMPLATE.md）
11. ✅ 用 Intent-Driven 格式重构所有核心 Spec（头部注入四大结构块，保留原有实现细节）
12. ✅ 建立安全编辑协议（Ban Full Overwrite, Incremental Edit Only）
13. ✅ 建立强制自发审计机制（Proactive Self-Audit + Execution Lifecycle）
14. ✅ 建立元架构自洽原则（Eat Your Own Dog Food）
15. ✅ 修复 agent 上下文注入遗漏（platform-dev 补齐架构 Spec，app 补齐业务 Spec）
16. ✅ 修复同步引擎硬编码问题（deep-cure → 通用 skills 同步逻辑）
17. ✅ 所有改动已 git commit 并 push 到两个 GitHub 远端仓库

### 待完成 / 未来演进方向

- **从软约束到物理硬卡点**：当前所有约束（安全编辑、自检、意图账本）均为提示词层面的软约束，依赖 Agent 自觉性。未来需引入 Git Pre-commit Hooks 等物理机制（死链检测、高内聚校验、缺失 SPEC.md 拦截）实现 100% 保障
- **claw-swarm 业务开发**：Roadmap 中的 Phase 5（资源配额与自愈）、Phase 6（代理网格）、Phase 7（控制台可视化）
- **onebot 的实战验证**：用 onebot 初始化一个全新的、非 claw-swarm 的业务项目，检验底座的通用性和可复用性

---

## Relevant files / directories

### onebot 仓库 (https://github.com/imovation/onebot)

```
onebot/
├── .gitignore
├── .github/ISSUE_TEMPLATE/app_feedback.md
├── INTENTS.md                          # 业务意图池模板（含 Append-Only 声明）
├── README.md                           # 项目说明（含三态模型、反哺闭环、同步引擎文档）
├── SYSTEM_SPEC.md                      # 业务系统架构模板
├── onebot.sh                           # 统一入口路由 Wrapper（→ .opencode/tools/sync-engine/onebot.sh）
├── opencode.json                       # 极简注册表（仅 hello 测试命令 + prettier formatter）
└── .opencode/
    ├── INTENTS.md                      # 平台基建意图池（含 3 条历史意图 + Append-Only 声明）
    ├── agents/
    │   ├── platform-dev.md             # @file: platform-rules + META_ARCHITECTURE_SPEC + SPEC_PYRAMID
    │   ├── biz-dev.md                  # @file: biz-dev-rules + SPEC_PYRAMID + SYSTEM_SPEC
    │   └── app.md                      # @file: app-rules + SYSTEM_SPEC
    ├── rules/
    │   ├── platform-rules.md           # 平台开发红线（含自检、诊因/求解、安全编辑、元架构自洽）
    │   ├── biz-dev-rules.md            # 业务开发红线（含自检、诊因/求解、Spec驱动、治本原则、安全编辑）
    │   └── app-rules.md                # 终端应用约束（含诊因/求解、只读原则、反哺机制）
    ├── specs/
    │   ├── META_ARCHITECTURE_SPEC.md   # 元架构规格（含 Intent-Driven 头部 + 完整三态定义+拓扑+反哺）
    │   ├── SPEC_PYRAMID.md             # 金字塔与方法论规格（含 Intent-Driven 头部 + 完整分层+生命周期+自洽）
    │   ├── SPEC_TEMPLATE.md            # AI-Native Spec 标准骨架模板
    │   └── ORIGIN.md                   # Onebot 起源与架构演进史
    ├── tools/
    │   └── sync-engine/
    │       ├── SPEC.md                 # 双向同步引擎规格（含 Intent-Driven 头部 + 完整功能定义）
    │       └── onebot.sh               # 同步引擎实现脚本（pull: 全量 skills；push: 仅覆写母体已有 skills）
    └── skills/
        └── deep-cure/
            ├── INTENTS.md              # 原始意图记录（含 Append-Only 声明）
            ├── SPEC.md                 # 功能规格
            └── SKILL.md                # 最终实现
```

### claw-swarm 仓库 (https://github.com/imovation/claw-swarm)

```
claw-swarm/
├── .gitignore
├── .github/ISSUE_TEMPLATE/app_feedback.md
├── INTENTS.md                          # 业务意图池（含 Append-Only 声明）
├── README.md                           # 项目说明（已清理 core-agent 等过时引用）
├── SYSTEM_SPEC.md                      # 业务系统架构（含 Intent-Driven 头部 + 声明式/Pod隔离/CLI/模块路由）
├── onebot.sh                           # 统一入口路由 Wrapper
├── opencode.json                       # 业务配置（claw apply/status/repair 等命令 + ruff formatter）
├── requirements.txt                    # Python 依赖 (PyYAML, Jinja2)
├── swarm.yaml                          # 集群声明式配置
├── bin/claw                            # 统一 CLI 入口
├── docs/
│   ├── ROADMAP.md                      # 演进路线图（含 Phase 4: Onebot 架构升级）
│   ├── TESTING.md                      # 测试指南
│   ├── USAGE.md                        # 使用手册（含 onebot sync 场景 H）
│   └── TEST_VERIFICATION_REPORT.md     # 测试验证报告
├── modules/
│   ├── orchestration/                  # 核心编排模块
│   ├── network-mesh/                   # 网络代理模块
│   └── matrix-channel/                 # Matrix 渠道模块
└── .opencode/
    ├── INTENTS.md                      # 平台基建意图池
    ├── agents/                         # 同 onebot（platform-dev, biz-dev, app）
    ├── rules/                          # 同 onebot（platform-rules, biz-dev-rules, app-rules）+ 业务专属内容
    ├── specs/                          # 同 onebot 的 specs + ORIGIN.md
    ├── tools/sync-engine/              # 同 onebot 的同步引擎
    └── skills/
        ├── deep-cure/                  # 通用排错方法论
        └── opencode-model-manager/    # 业务专属 Skill（仅 claw-swarm 有，onebot 无）
```
