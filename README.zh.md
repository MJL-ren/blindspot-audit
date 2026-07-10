# Blindspot Audit

[English](./README.md) | [한국어](./README.ko.md) | [日本語](./README.ja.md) | [简体中文](./README.zh.md) | [Español](./README.es.md)

![Blindspot Audit 主图](./docs/assets/readme/en/hero.png)

Blindspot Audit 是一个可移植的 AI agent 技能，用来发现项目负责人还没有意识到的盲点：
unknown unknowns、隐藏风险、缺失的决策、过期的假设，以及还没有人想到要问的问题。它会把结果记录到
`BLINDSPOT_LEDGER.md`。

它适用于各种项目：软件、游戏、小说和创作、研究、内容、商业计划等。它可以在 Claude Code、Codex、
OpenCode、Claude 桌面应用和普通聊天中使用。审计核心流程是共享的；不同宿主只调整提问方式和结果写入方式。

## 60 秒安装

| 你在用的工具 | 一行命令 |
| --- | --- |
| 任意 coding agent — Claude Code、Codex、OpenCode、Cursor 等约 70 种 | `npx skills add MJL-ren/blindspot-audit` |
| Claude Code（带受管更新） | 先 `/plugin marketplace add MJL-ren/blindspot-audit`，再 `/plugin install blindspot-audit@blindspot-audit` |
| Claude 桌面应用 / Cowork — 无需终端 | 下载 [blindspot-audit.skill](https://github.com/MJL-ren/blindspot-audit/releases/latest/download/blindspot-audit.skill)，附加到聊天中，点击 **Save skill** |

装好后，试试第一个提示词：

```text
Run a blindspot audit on this project. What am I missing that I don't even know to ask about?
```

`npx` 路线使用 [vercel-labs/skills](https://github.com/vercel-labs/skills)：
它会安装整个技能文件夹，并发送匿名安装统计（用 `DISABLE_TELEMETRY=1` 可关闭）。
技能本身绝不会自行访问网络 — 见 [SECURITY.md](./SECURITY.md)。其余路线 —
按项目安装、Codex 市场、离线脚本、交给 agent 安装 — 见 [安装](#安装) 一节。

## 它会做什么

![四类未知框架](./docs/assets/readme/en/four-unknowns.png)

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
- 需要时可以收窄深挖：`focus: ux-ui` 运行会加载该领域专用的深度探针包；全量审计如果只是略过了
  所有者薄弱领域的表面（工程师的 UI、设计师的运维），不会默默放过，而是作为发现如实报告。
  探针包会逐步增加。
- 维护一个持久的 `BLINDSPOT_LEDGER.md`（审计留在项目里的笔记文件）。后续运行会和旧台账比较，只报告新增或变化的内容，让复查更像进展跟踪，
  而不是重复提醒。如果没有任何变化，运行不会空手而归，而是向下深入一层（未运行的探针包、
  观察清单复审、检查最浅的子系统，依此顺序）。

![Blindspot Audit 审计流程](./docs/assets/readme/en/audit-flow.png)

## 发现长什么样

弱的审计会写"缺少 GDPR 第 13 条隐私告知"。这个技能被设计成让负责人能看懂、
能行动的写法：

```markdown
1. The site collects email addresses but never tells people what happens
   to them
   - In plain terms: when a site stores personal data like emails, most
     regions require a short public note (a "privacy policy") saying what
     is collected and how to get it deleted. It is a page, not a lawsuit -
     but its absence can become one.
   - Why it matters: the signup form is live and EU visitors can reach it;
     this is the kind of gap that is cheap now and expensive after launch.
   - Cheapest check: read one privacy-policy generator's output (10 min)
     and confirm with a professional before launch - this audit is a
     scout, not a lawyer.
```

完整的合成示例报告有 5 份，见
[examples/sample-reports/](./examples/sample-reports/)。建议先读
[weak-vs-strong.md](./examples/sample-reports/weak-vs-strong.md)：同样三个发现，
分别用"不合格"和"合格"两种写法各写一遍。实际报告会用你工作时使用的语言来写，
只有 ID 和 status 值保持英文。

## 第一次审计会发生什么

1. 用平常的话提出请求（提示词示例见 [使用方式](#使用方式)）。
2. 首次运行会问 1–2 个简短的背景问题 — 每个都可以跳过。
3. 你会收到 3–7 个按优先级排序的发现，外加"已经覆盖得不错的部分"和
   "现在可以先跳过的部分"。
4. 它会问你哪些发现其实早就知道 — 已知的缺口得到的是一条待办，而不是
   一段说教。
5. 只留下一个文件：`BLINDSPOT_LEDGER.md`，项目里的审计笔记。下次运行读它，
   只报告变化。文件是你的 — 提交它，或加进 `.gitignore` 都行。

## 直接问"我漏了什么?"不行吗？

裸提示词每次都从零开始：重新"发现"你已经在跟踪的事，在一条待办就够的地方
开始说教，到了下一个会话又全忘了。这个技能会把项目自己的跟踪文档从发现里
过滤掉，通过访谈区分"已知缺口"和"真盲点"并给出不同处方，还会和台账做 diff，
让复查变成进展跟踪而不是重复提醒。

如何判断它在起作用：复查报告的是增量，而不是同一份清单再来一遍；每个发现
都有具体后果和最便宜的下一步检查，而不是泛泛的最佳实践；每个版本都用真实
项目运行打分 — 见 [evals/RUNS.md](./evals/RUNS.md)。

## Focus: UX/UI

![Blindspot Audit UX/UI 聚焦](./docs/assets/readme/en/ux-ui-focus.png)

`focus: ux-ui` 适用于有真实用户界面的项目。普通的广泛审计往往只能略看界面，
而这个模式会更窄、更深地检查 UI/UX 表面：屏幕、输入、状态、流程、可访问性和反馈。
它把这些当作盲点问题来处理：哪些事情从来没有被决定，用户可能卡在哪里，
以及用什么最便宜的检查就能把问题看见。

当完整审计指出 UX/UI 仍是覆盖债，或者负责人在其他领域很强、但想更认真地检查用户表面时，
就适合使用它。

这不是通用质量检查表。它回答的问题是：

> 针对这个具体项目，我们现在最可能还没有看到什么？

## Ledger Triage

`mode: ledger-triage` 用于整理已经积累了较多内容的 `BLINDSPOT_LEDGER.md`。
它不会运行新的审计，而是读取现有台账，把未处理行分成快速清理、安全接受、合并决策、
需要负责人细节判断、需要外部确认，以及需要更简单解释的项目。

在没有结构化选择 UI 的宿主中，如果要处理的决策很多，可以在 `.blindspot-tmp/` 下生成一个临时的
self-contained HTML decision board。负责人在浏览器里完成选择后，agent 验证 response JSON，
只应用被选择的台账更新，然后删除这个临时 board。board 里的推荐选项在负责人选择前不会被应用。

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

三条推荐路线在上面的 [60 秒安装](#60-秒安装) 里。下面是完整菜单，任何一条
路线都不依赖其他路线。

### 任意 coding agent — 一行命令 (npx)

[vercel-labs/skills](https://github.com/vercel-labs/skills) 会检测已安装的
agent（Claude Code、Codex、OpenCode、Cursor 等约 70 种），并为每个安装完整的
技能文件夹：

```bash
npx skills add MJL-ren/blindspot-audit
```

匿名安装统计可以用 `DISABLE_TELEMETRY=1` 关闭。

### 交给 agent 安装

把下面这段提示词复制到 Codex、Claude Code、OpenCode 或其他 coding agent 中。agent 会阅读这个仓库，
然后为当前宿主或项目安装技能。

```text
Install and configure Blindspot Audit for this agent environment:
https://github.com/MJL-ren/blindspot-audit

Read the repository README.md and AGENTS.md first, then install using the documented skill route that fits this host and scope: the installer script, the Claude desktop .skill, or a safe manual copy. If a permission or safety guard blocks writing the skill into the agent's config directory, don't silently stop - ask me to approve the permission, or offer the plugin marketplace route as a managed fallback.

Do not modify unrelated project files. After installation, tell me which route you used, the installed path or plugin name, how to update it later, and the exact prompt I can use to run a deep blindspot audit.
```

### Claude Code — 插件市场（一行安装 + 自动更新）

在 Claude Code 中运行：

```text
/plugin marketplace add MJL-ren/blindspot-audit
/plugin install blindspot-audit@blindspot-audit
```

无需克隆仓库，之后用 `/plugin marketplace update blindspot-audit` 获取更新。
（`blindspot-audit@blindspot-audit` 的写法是 `<插件>@<市场>` — 这里两者恰好
同名，不是笔误。）

### Codex — 插件市场

在 Codex 中添加 Git marketplace 并安装插件：

```bash
codex plugin marketplace add MJL-ren/blindspot-audit --ref main
codex plugin add blindspot-audit@blindspot-audit
```

在 ChatGPT 桌面应用中，打开 `Codex > Plugins > Installed` 可查看和管理已安装的插件。
如果使用 CLI，或想强制刷新 marketplace，请运行：

```bash
codex plugin marketplace upgrade blindspot-audit
codex plugin add blindspot-audit@blindspot-audit
```

安装或更新后，请开启新的 Codex 任务，让插件技能被加载。

### 脚本安装（需要克隆）

下面的脚本路线需要本地克隆。所有安装脚本都有 PowerShell (`.ps1`) 和 Bash
(`.sh`) 版本。在 macOS/Linux 上使用 `.sh` 脚本（首次可能需要运行
`chmod +x scripts/*.sh`）；在 Windows 上用 PowerShell 运行 `.ps1`，或在
Git Bash / WSL 中使用 `.sh`。

```bash
git clone https://github.com/MJL-ren/blindspot-audit.git
cd blindspot-audit
```

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

默认安装到当前 Codex 用户技能目录 `~/.agents/skills`。也可以通过参数传入自定义
目标路径。如果旧的 `~/.codex/skills` 或 `$CODEX_HOME/skills` 中仍有同名技能，
安装脚本会发出警告，但不会自动删除它。

```powershell
.\scripts\install-codex.ps1
```

```bash
./scripts/install-codex.sh
```

### Claude 桌面应用 / Cowork

直接下载最新包 —
[blindspot-audit.skill](https://github.com/MJL-ren/blindspot-audit/releases/latest/download/blindspot-audit.skill)
（有克隆的话也可以用 `dist/blindspot-audit.skill`）— 在 Claude 桌面应用里
把它附加到聊天中，然后点击 **Save skill**。不需要终端，这是非开发者最简单的方式。

如果你是在桌面应用内以市场**插件**方式安装的，仅重启应用不会完成更新。请在插件管理界面点击
**Update**，或在 Claude Code 等兼容插件 CLI 中运行 `/plugin marketplace update blindspot-audit`。

### 手动安装

把 `skills/blindspot-audit` 文件夹复制到以下任一位置：

```text
~/.claude/skills/blindspot-audit                    # Claude Code 个人 + OpenCode
<project>/.claude/skills/blindspot-audit            # Claude Code 项目 + OpenCode
~/.agents/skills/blindspot-audit                    # Codex 个人
<project>/.agents/skills/blindspot-audit            # Codex 项目
<project>/.opencode/skills/blindspot-audit          # OpenCode 原生项目安装
~/.config/opencode/skills/blindspot-audit           # OpenCode 原生全局安装
```

当前 Codex 官方文档使用 `.agents/skills`。某些旧环境可能仍会显示
`~/.codex/skills` 或 `$CODEX_HOME/skills` 中的副本，但把同一个技能同时放在
两个位置可能会出现重复项。

然后开启新的 agent 会话，或刷新当前环境，让技能被加载。

## 更新

按你最初安装时使用的同一路径更新：

- Claude Code 插件市场：运行 `/plugin marketplace update blindspot-audit`，
  然后打开新的 Claude Code 会话。
- ChatGPT 桌面应用的 Codex 插件市场：在 `Codex > Plugins > Installed` 中查看和
  管理插件。若要通过 CLI 强制刷新，请运行 `codex plugin marketplace upgrade
  blindspot-audit`，再运行 `codex plugin add blindspot-audit@blindspot-audit`，
  然后开启新的 Codex 任务。
- Claude 桌面应用市场插件：在应用的插件管理界面点击 **Update**；仅重启应用不会更新。
  兼容 CLI 路径是 `/plugin marketplace update blindspot-audit`。
- 脚本安装：先在仓库里 `git pull`，再重新运行你之前使用的同一个安装脚本。脚本会替换整个
  已安装的 `blindspot-audit` 文件夹，而不是合并复制，所以改名或删除过的旧文件不会继续残留。
- Claude 桌面应用 `.skill`：获取最新的 `dist/blindspot-audit.skill`，然后在应用里重新保存。
- 手动安装：替换整个 `skills/blindspot-audit` 文件夹。不要只复制 `SKILL.md`；这个技能还需要
  `references/`、`scripts/` 和 `templates/`。

```bash
git pull
./scripts/install-claude-user.sh      # 或者你之前使用的安装脚本
```

```powershell
git pull
.\scripts\install-claude-user.ps1     # 或者你之前使用的安装脚本
```

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

![BLINDSPOT_LEDGER 与重复审计](./docs/assets/readme/en/ledger-diff.png)

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

## 参与贡献

欢迎 bug 报告和真实运行记录 —
请使用[问题表单](https://github.com/MJL-ren/blindspot-audit/issues/new/choose)，
它会一开始就询问宿主、技能版本和模式。新技能、新探针包或大型功能的 PR
原则上不接受：审计核心保持小巧、经过实地验证。如果你觉得缺了什么，请先开
issue。

## 致谢

本项目受到 Claude Code 团队 Thariq (@trq212) 的
[A Field Guide to Fable: Finding Your Unknowns](https://x.com/trq212/status/2073100352921215386)
中 unknown unknowns 工作流的启发。本仓库中的实现、文字、模板和脚本均为原创。

`ux-ui` 聚焦包的探针结构参考了以下开源项目。参考用本地克隆放在
`external_repos/`（不纳入 git 跟踪），探针包的文字均为原创：

- [mistyhx/frontend-design-audit](https://github.com/mistyhx/frontend-design-audit)
  (MIT) - 具备 15 条可用性启发式、代码级违规模式与严重度模型的前端审计技能。
- [raintree-technology/hig-doctor](https://github.com/raintree-technology/hig-doctor)
  (结构/工具为 MIT，HIG 正文版权归 Apple，未复制) - 外观、无障碍与设备检查的
  检测类别分类体系。
- [Community-Access/accessibility-agents](https://github.com/Community-Access/accessibility-agents)
  (MIT) - 无障碍审计代理模式。

## 安全

脚本做什么、哪些部分不接触网络、以及如何私下报告问题，见
[SECURITY.md](./SECURITY.md)。

## 许可证

MIT License。请查看 [LICENSE](./LICENSE)。
