# Blindspot Audit

[English](./README.md) | [한국어](./README.ko.md) | [日本語](./README.ja.md) | [简体中文](./README.zh.md) | [Español](./README.es.md)

Blindspot Audit は、プロジェクトの持ち主が「知らないことにすら気づいていない」
部分を見つけるための、持ち運びしやすい AI エージェント向けスキルです。unknown
unknowns、隠れたリスク、未決定の判断、古くなった前提、まだ誰も聞いていない問いを
`BLINDSPOT_LEDGER.md` に残します。

ソフトウェア、ゲーム、小説や創作、リサーチ、コンテンツ、事業計画など、どんな種類の
プロジェクトにも使えます。Claude Code、Codex、OpenCode、Claude デスクトップアプリ、
通常のチャットで動きます。監査の中核は共通で、ホストごとに変わるのは質問の仕方と結果の
保存方法だけです。

## AI に貼り付けてインストール

次の文を Codex、Claude Code、OpenCode などのコーディングエージェントに貼り付けると、
このリポジトリを読んで、現在の環境に合う形でスキルをインストールできます。

```text
Install the Blindspot Audit skill from https://github.com/MJL-ren/blindspot-audit.

Please read the repository README and AGENTS.md first, detect whether this environment is Codex, Claude Code, OpenCode, Claude desktop/Cowork, or a plain project folder, then install skills/blindspot-audit using the provided installer script or a safe manual copy.

Do not modify unrelated project files. If this is a project-local install, use the appropriate project skill folder. If this is a user/global install, use the documented user skill folder. After installation, tell me the installed path and the exact prompt I can use to run a deep blindspot audit.
```

## 何をするか

- プロジェクトを最初に把握します。種類、段階、持ち主の専門性、趣味か商用かを見ます。
  そのうえで、TODO、チェックリスト、ロードマップなど、すでに追跡している文書を先に読み、
  **持ち主がすでに知っている項目を「発見」として再報告しません。**
- プロジェクトの型に合わせた視点で内部を見ます。足りないものだけでなく、すでに整っている
  ものも証拠つきで記録します。
- 最近の外部変化を Web で確認します。規制、プラットフォーム方針、市場やジャンルの変化など、
  プロジェクト文書だけでは出てこない情報を拾います。
- 発見は 3〜7 個に絞って順位づけします。無限のチェックリストではなく、「よく整っているもの」
  と「今は後回しでよいもの（再確認のきっかけつき）」も必ず含めます。
- どの発見を持ち主がすでに知っていたかを確認します。知っている穴に必要なのは長い説明ではなく、
  次に動ける短いチェック項目です。
- `BLINDSPOT_LEDGER.md` を残します。次回以降はその台帳と比較し、新しく出たもの、変わったものだけを
  報告します。

これは汎用的な品質チェックリストではありません。答える問いはこれです。

> このプロジェクトの今の状態から見て、私たちがまだ見落としていそうな重要な穴は何か？

## リポジトリ構成

```text
blindspot-audit/
  .claude-plugin/
    marketplace.json / plugin.json  # Claude Code プラグインマーケットプレイス用
  AGENTS.md
  CHANGELOG.md
  README.md
  README.ko.md
  README.ja.md
  README.zh.md
  README.es.md
  LICENSE
  dist/
    blindspot-audit.skill        # Claude デスクトップアプリ用のワンクリックインストールファイル
  examples/
    prompts.md
  scripts/
    build-skill-package.py / .ps1 / .sh
    install-claude-user.ps1 / .sh
    install-claude-project.ps1 / .sh
    install-codex.ps1 / .sh
  skills/
    blindspot-audit/
      SKILL.md
      references/
      scripts/
      templates/
```

## インストール

すべてのインストーラーには PowerShell (`.ps1`) と Bash (`.sh`) があります。macOS/Linux では
`.sh` を使ってください（初回だけ `chmod +x scripts/*.sh` が必要な場合があります）。Windows では
PowerShell で `.ps1` を使うか、Git Bash / WSL で `.sh` を使えます。

```bash
git clone https://github.com/MJL-ren/blindspot-audit.git
cd blindspot-audit
```

### Claude Code — プラグインマーケットプレイス（1 行インストール + 自動更新）

Claude Code 内で次を実行します。

```text
/plugin marketplace add MJL-ren/blindspot-audit
/plugin install blindspot-audit@blindspot-audit
```

クローンは不要で、`/plugin marketplace update blindspot-audit` で更新を受け取れます。

### Claude Code — 個人インストール（推奨、OpenCode も対象）

`~/.claude/skills` にインストールします。この場所は Claude Code と OpenCode の両方が読むため、
一度のインストールで両方を使えます。

```powershell
.\scripts\install-claude-user.ps1
```

```bash
./scripts/install-claude-user.sh
```

### Claude Code — プロジェクト単位

`<project>/.claude/skills` にインストールします。この場所も OpenCode が読みます。

```powershell
.\scripts\install-claude-project.ps1 -ProjectRoot "C:\path\to\your-project"
```

```bash
./scripts/install-claude-project.sh /path/to/your-project
```

### Codex

`CODEX_HOME` が設定されていれば `$CODEX_HOME/skills`、なければ `~/.codex/skills` に
インストールします。引数で別のインストール先を渡すこともできます。

```powershell
.\scripts\install-codex.ps1
```

```bash
./scripts/install-codex.sh
```

### Claude デスクトップアプリ / Cowork

`dist/blindspot-audit.skill` を Claude デスクトップアプリのチャットに添付し、**Save skill** を
押します。ターミナルは不要なので、開発者でない人には一番簡単です。

### 手動インストール

`skills/blindspot-audit` フォルダを次のどれかにコピーします。

```text
~/.claude/skills/blindspot-audit                    # Claude Code 個人 + OpenCode
<project>/.claude/skills/blindspot-audit            # Claude Code プロジェクト + OpenCode
~/.codex/skills/blindspot-audit                     # Codex
<project>/.opencode/skills/blindspot-audit          # OpenCode ネイティブ（プロジェクト）
~/.config/opencode/skills/blindspot-audit           # OpenCode ネイティブ（グローバル）
```

その後、新しいエージェントセッションを開くか更新すると、スキルが読み込まれます。

## 使い方

Claude Code と OpenCode では、自然に頼めばスキルの説明から起動します。

```text
Run a blindspot audit on this project. What am I missing that I don't even know to ask about?
```

Codex では、スキル名を明示するほうが確実です。

```text
Use $blindspot-audit in deep mode on this project. Create or update the BLINDSPOT_LEDGER.md and give me only the highest-signal findings.
```

さらに多くの例は [examples/prompts.md](./examples/prompts.md) にあります。

## メンテナンス

`skills/blindspot-audit` を変更した後は、Claude デスクトップアプリ用パッケージを作り直します。

```powershell
.\scripts\build-skill-package.ps1
```

```bash
./scripts/build-skill-package.sh
```

## ホストごとの動き

- 選択式の質問が使えるホスト（Claude Code、OpenCode）: 結果が変わる場合だけ短く質問し、
  持ち主がすでに知っていたかの確認は 1 つの複数選択質問で行います。
- Codex / チャットのみのホスト: 質問で止まりません。安全で戻せる仮定で進め、後で答えられる
  `Decision packet` を残します。
- Web アクセスがないホスト: 外部変化スキャンを省略し、そのことを明示します。規制や
  プラットフォーム関連の項目は「未検証」として扱います。
- ファイルを書けるホスト: 既定で `BLINDSPOT_LEDGER.md` を作成または更新します。
- 読み取り専用ホスト: 台帳候補を含む持ち運び可能なレポートを返します。

## 出典と着想

このプロジェクトは、Claude Code チームの Thariq (@trq212) による
[A Field Guide to Fable: Finding Your Unknowns](https://x.com/trq212/status/2073100352921215386)
で紹介された unknown unknowns の流れに着想を得ました。このリポジトリの実装、文面、
テンプレート、スクリプトは独自に作成したものです。

## ライセンス

MIT License。詳しくは [LICENSE](./LICENSE) を見てください。
