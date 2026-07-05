# Blindspot Audit

[English](./README.md) | [한국어](./README.ko.md) | [日本語](./README.ja.md) | [简体中文](./README.zh.md) | [Español](./README.es.md)

Blindspot Audit 是一个可移植的 AI agent 技能，用来发现项目负责人还没有意识到的盲点：
unknown unknowns、隐藏风险、缺失的决策、过期的假设，以及还没有人想到要问的问题。它会把结果记录到
`BLINDSPOT_LEDGER.md`。

它适用于各种项目：软件、游戏、小说和创作、研究、内容、商业计划等。它可以在 Claude Code、Codex、
OpenCode、Claude 桌面应用和普通聊天中使用。审计核心流程是共享的；不同宿主只调整提问方式和结果写入方式。

## 复制给 AI 安装

把下面这段提示词复制到 Codex、Claude Code、OpenCode 或其他 coding agent 中。agent 会阅读这个仓库，
然后为当前宿主或项目安装技能。

```text
Install and configure Blindspot Audit for this agent environment:
https://github.com/MJL-ren/blindspot-audit

Read the repository README.md and AGENTS.md first, then choose the documented install route that fits this host and install scope: marketplace/plugin, Claude desktop .skill, installer script, or safe manual copy.

Do not modify unrelated project files. After installation, tell me which route you used, the installed path or plugin name, how to update it later, and the exact prompt I can use to run a deep blindspot audit.
```

## 它会做什么

- 先对项目进行画像：项目类型、阶段、负责人的专业领域、是兴趣项目还是商业项目。它会优先读取项目自己的
  TODO、检查表、路线图等跟踪文档，**已经被负责人跟踪的内容不会被重新包装成“发现”。**
- 首次运行时会收集影响审计的最少项目背景（公开/商业意图、目标用户与地区、阶段、负责人的强项——每个问题
  都可以跳过），并保存到台账的 `Project Context` 区块；之后的运行直接读取，不再重复询问。
- 用适合项目类型的不同视角扫描项目。它不仅记录缺失项，也会记录已经做得不错的部分，并附上证据。
- 执行 fresh-eyes Web 扫描，寻找最近的外部变化，例如法规、平台政策、市场或类型变化。这些通常不会出现在
  项目文档里，却往往影响很大。
- 输出 3 到 7 个按重要性排序的发现，而不是无限长的清单。报告里始终包含两个信任区块：“已经检查且覆盖良好”
  和“现在可以跳过（附重新检查触发条件）”。
- 询问负责人哪些发现其实早就知道。已知的缺口需要的是一条待办，而不是一段长篇解释。
- 维护一个持久的 `BLINDSPOT_LEDGER.md`。后续运行会和旧台账比较，只报告新增或变化的内容，让复查更像进展跟踪，
  而不是重复提醒。

这不是通用质量检查表。它回答的问题是：

> 针对这个具体项目，我们现在最可能还没有看到什么？

## 仓库结构

```text
blindspot-audit/
  .agents/
    plugins/marketplace.json     # Codex 插件市场配置
  .claude-plugin/
    marketplace.json / plugin.json  # Claude Code 插件市场配置
  AGENTS.md
  CHANGELOG.md
  README.md
  README.ko.md
  README.ja.md
  README.zh.md
  README.es.md
  LICENSE
  dist/
    blindspot-audit.skill        # Claude 桌面应用的一键安装文件
  evals/
    fixtures/                    # 行为回归测试夹具（含 EXPECTED 标准）
  examples/
    prompts.md
    sample-reports/              # 展示目标输出形态的合成示例报告
  scripts/
    build-skill-package.py / .ps1 / .sh
    install-claude-user.ps1 / .sh
    install-claude-project.ps1 / .sh
    install-codex.ps1 / .sh
    sync-codex-plugin.py / .ps1 / .sh
    verify-codex-plugin.py
  plugins/
    blindspot-audit/
      .codex-plugin/plugin.json  # Codex 插件 manifest
      skills/blindspot-audit/
  skills/
    blindspot-audit/
      SKILL.md
      references/
      scripts/
      templates/
```

## 安装

所有安装脚本都有 PowerShell (`.ps1`) 和 Bash (`.sh`) 版本。在 macOS/Linux 上使用 `.sh`
脚本（首次可能需要运行 `chmod +x scripts/*.sh`）；在 Windows 上用 PowerShell 运行 `.ps1`，
或在 Git Bash / WSL 中使用 `.sh`。

```bash
git clone https://github.com/MJL-ren/blindspot-audit.git
cd blindspot-audit
```

### Claude Code — 插件市场（一行安装 + 自动更新）

在 Claude Code 中运行：

```text
/plugin marketplace add MJL-ren/blindspot-audit
/plugin install blindspot-audit@blindspot-audit
```

无需克隆仓库，之后用 `/plugin marketplace update blindspot-audit` 获取更新。

### Codex — 插件市场

在 Codex 中添加 Git marketplace 并安装插件：

```bash
codex plugin marketplace add MJL-ren/blindspot-audit --ref main
codex plugin add blindspot-audit@blindspot-audit
```

之后如需更新：

```bash
codex plugin marketplace upgrade blindspot-audit
codex plugin add blindspot-audit@blindspot-audit
```

安装或更新后，请开启新的 Codex 线程，让插件技能被加载。

### Claude Code — 个人安装（推荐，也适用于 OpenCode）

安装到 `~/.claude/skills`。Claude Code 和 OpenCode 都会读取这个路径，一次安装即可覆盖两个宿主。

```powershell
.\scripts\install-claude-user.ps1
```

```bash
./scripts/install-claude-user.sh
```

### Claude Code — 单个项目

安装到 `<project>/.claude/skills`。OpenCode 在该项目中也会读取这个路径。

```powershell
.\scripts\install-claude-project.ps1 -ProjectRoot "C:\path\to\your-project"
```

```bash
./scripts/install-claude-project.sh /path/to/your-project
```

### Codex — 手动技能安装

如果设置了 `CODEX_HOME`，会安装到 `$CODEX_HOME/skills`；否则安装到 `~/.codex/skills`。
也可以通过参数传入自定义目标路径。

```powershell
.\scripts\install-codex.ps1
```

```bash
./scripts/install-codex.sh
```

### Claude 桌面应用 / Cowork

在 Claude 桌面应用里打开 `dist/blindspot-audit.skill`（把它附加到聊天中），然后点击
**Save skill**。不需要终端，这是非开发者最简单的方式。

如果你是在桌面应用内以市场**插件**方式安装的，插件默认不会自动更新：请在应用的插件管理界面手动执行
更新检查，或在其中关联 GitHub 账号以启用与本仓库的自动同步。

### 手动安装

把 `skills/blindspot-audit` 文件夹复制到以下任一位置：

```text
~/.claude/skills/blindspot-audit                    # Claude Code 个人 + OpenCode
<project>/.claude/skills/blindspot-audit            # Claude Code 项目 + OpenCode
~/.codex/skills/blindspot-audit                     # Codex
<project>/.opencode/skills/blindspot-audit          # OpenCode 原生项目安装
~/.config/opencode/skills/blindspot-audit           # OpenCode 原生全局安装
```

然后开启新的 agent 会话，或刷新当前环境，让技能被加载。

## 使用方式

在 Claude Code 和 OpenCode 中，自然地提出请求即可。技能会根据描述触发。

```text
Run a blindspot audit on this project. What am I missing that I don't even know to ask about?
```

在 Codex 中，显式提到技能名最可靠：

```text
Use $blindspot-audit in deep mode on this project. Create or update the BLINDSPOT_LEDGER.md and give me only the highest-signal findings.
```

更多示例见 [examples/prompts.md](./examples/prompts.md)。

## 维护者

修改 `skills/blindspot-audit` 后，请重新构建 Claude 桌面应用包：

```powershell
.\scripts\build-skill-package.ps1
```

```bash
./scripts/build-skill-package.sh
```

然后同步并验证 Codex 插件副本：

```powershell
.\scripts\sync-codex-plugin.ps1
python .\scripts\verify-codex-plugin.py
```

```bash
./scripts/sync-codex-plugin.sh
python3 scripts/verify-codex-plugin.py
```

## 不同宿主中的行为

- 支持选择题的宿主（Claude Code、OpenCode）：只在答案会改变工作结果时问一个短问题，并用一个多选问题确认负责人是否已知这些发现。
- Codex / 纯聊天宿主：不会因为问题而停住。它会用安全、可回退的假设继续，并留下 `Decision packet` 供之后回答。
- 没有 Web 访问的宿主：跳过 fresh-eyes 扫描，并明确说明跳过原因，而不是假装知道最新法规或平台变化。
- 可写文件的宿主：默认创建或更新 `BLINDSPOT_LEDGER.md`。
- 只读宿主：返回可复制的报告和建议的台账条目。

## 致谢

本项目受到 Claude Code 团队 Thariq (@trq212) 的
[A Field Guide to Fable: Finding Your Unknowns](https://x.com/trq212/status/2073100352921215386)
中 unknown unknowns 工作流的启发。本仓库中的实现、文字、模板和脚本均为原创。

## 许可证

MIT License。请查看 [LICENSE](./LICENSE)。
