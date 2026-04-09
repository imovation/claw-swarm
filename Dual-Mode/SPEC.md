# Claw-Swarm Dual-Mode (双轨模式) 规格说明书

## 〇、 原始需求 (Original Requirements)
> claw-swarm的定位是一个基于opencode的agent。它支持开发和应用两种模式。两种模式的使用场景都是将claw-swarm项目目录作为opencode 工作空间，在opencode tui中交互。
> 1. 应用模式不能迭代修改claw-swarm本身，只有开发模式才可以。
> 2. 开发模式开发完成某个功能后需要提交更新github仓库；
> 3. 应用模式在使用claw-swarm过程中需要归纳总结改进建议，并按GitHub issue的规范提交Issue（需要包含应用场景信息，即具体执行的任务）来反馈；
> 4. 开发模式支持处理GitHub issue 内容，处理逻辑是先核实，然后综合评估是否需要解决，需要解决的分析并制定解决方案。
> 5. 当用户在项目的根目录（即工作空间）启动 Opencode的第一件事就是强制用户确定模式，模式一旦确定整个会话不能切换模式，且会话名中必须包括模式信息便于提醒用户。

## 一、 核心定位与背景
Claw-Swarm 作为基于 Opencode 运行的 Agent 项目，其工作空间需要严格区分“使用反馈”与“代码开发”两种场景。
为了防止 Agent 在长对话中因为上下文漂移而误修改项目核心代码，同时提供标准化的 Issue 提报与处理能力，引入 **Dual-Mode (双轨模式)** 工作流。

核心特性：**基于 Agent 会话生命周期的状态隔离与流程锁**。

## 二、 模式定义

### 1. 强制拦截与会话锁定机制 (Gatekeeper)
- **拦截器**：用户开启新会话（`/new`）后的第一次交互，Agent 必须挂起用户原始指令，强制用户进行模式选择。
- **视觉固化**：确认模式后，Agent 的第一条回复必须以 `# [应用模式 APP MODE] 已锁定` 或 `# [开发模式 DEV MODE] 已锁定` 开头，以诱导 Opencode 生成带有模式标识的会话名称。
- **隔离墙**：会话一旦确定模式，绝对禁止中途切换。如试图切换，Agent 应拒绝并引导用户使用 `/new`。

### 2. 应用模式 (App Track)
**定位**：供用户在日常应用、测试、部署 Claw-Swarm 节点时使用。
- **权限安全**：绝对禁止使用文件写入/编辑工具（Write/Edit）修改项目源码。仅允许读取或修改 `swarm.yaml` 等配置文件。
- **反馈闭环**：当用户在应用过程中遇到 Bug 或提出改进建议时，Agent 自动收集上下文（刚执行的任务、命令输出、现象），按照标准化模板归纳，并调用 GitHub CLI (`gh issue create`) 提交规范的反馈。

### 3. 开发模式 (Dev Track)
**定位**：供开发者迭代、扩展和修复 Claw-Swarm 逻辑时使用。
- **权限全开**：允许 Agent 自由阅读、修改代码及执行相关构建/测试命令。
- **开发提交流程**：所有功能开发完毕后，Agent 必须引导用户进行 `git add`, `git commit`, `git push` 的完整提交流程。
- **Issue 驱动修复**：
  1. 接收 Issue ID。
  2. 调用 `gh issue view` 提取上下文。
  3. 结合代码库搜索评估问题，制定《诊断与修复预案》。
  4. 用户同意后执行代码修改。
  5. 提交带有 `Fixes #<ID>` 标记的 Commit 并推送，实现自动关闭 Issue。

## 三、 实施方案 (Implementation Details)
1. **指令重构**：在项目的 `AGENTS.md` (Agent 顶层宪法) 最顶部注入强指令（CRITICAL 级别），作为该模式的守门人规则。
2. **Issue 模板**：创建 `.github/ISSUE_TEMPLATE/app_feedback.md` 规范 Issue 提报格式。
3. **工具链要求**：依赖并默认调用 `gh` 工具与 `git` CLI。