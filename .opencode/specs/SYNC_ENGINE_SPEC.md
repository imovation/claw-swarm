# Onebot 双向同步引擎规格 (Bidirectional Sync Engine Specification)

## 一、 核心愿景
Onebot 并不是一个静态的模板库，而是一个具备“自进化”能力的智能体基座。为了解决基座与衍生业务项目之间“基建提取与下发”的工程问题，我们引入了轻量的源码级双向同步引擎 `onebot.sh`。

## 二、 设计哲学
本引擎彻底摒弃了 Git Submodule 或全局挂载包等复杂的依赖管理模式，而是遵循“源码即资产”的原则，确保：
1. **就地演进 (Upstreaming)**：在具体业务的战壕里打磨基建规则，一旦成熟，一键反哺至母体。
2. **安全下发 (Downstreaming)**：母体进化后，子项目可以通过一键拉取吸纳最新认知，且绝对不会覆盖子项目的业务个性化配置。

## 三、 功能规格 (Functional Spec)

### 1. `pull` - 向下同步 (Downstream)
- **触发场景**：当 `onebot` 母体仓库在远端有更新，子项目需要吸纳最新的基建规则时。
- **执行逻辑**：
  1. 通过 `curl` 从远端（`main.zip`）拉取纯净源码。
  2. 解压至临时目录。
  3. **安全覆盖**：精准提取 `.opencode/agents/`、`.opencode/rules/`、`.opencode/specs/`、`.opencode/skills/deep-cure/`。
  4. **保护红线**：严禁覆盖根目录下的 `opencode.json`（其中包含业务注册命令）和业务专属的 `REQUESTS.md`。

### 2. `push` - 向上反哺 (Upstream)
- **触发场景**：在子项目（如 `claw-swarm`）中，`platform-dev` 或 `biz-dev` 遇到了规则局限，就地修改了子项目的 `.opencode/` 基建并验证通过后。
- **执行逻辑**：
  1. 定位本地的 Onebot 母体仓库（默认 `~/opencode-workspace/onebot`）。
  2. **逆向提取**：将当前项目中经过业务验证的核心架构文件夹（`agents/`、`rules/`、`specs/`、`deep-cure/`）复制回母体仓库。
  3. **自动发布**：在母体仓库中自动执行 Git 的 Add、Commit（携带标准化提交信息）与 Push 操作。

## 四、 边界与约束
- 本引擎仅处理 `.opencode/` 目录内的“元架构”资产，不涉及任何业务代码的同步。
- 本脚本应作为业务项目的公共资产被跟踪在版本控制中，供任何开发者使用。