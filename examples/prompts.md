# Prompt Examples

On Claude Code and OpenCode you can just ask naturally — the skill triggers
from its description. On Codex, referencing `$blindspot-audit` explicitly is
the most reliable.

## English

```text
Use $blindspot-audit in deep mode on this project. Find the unknown unknowns, create or update the BLINDSPOT_LEDGER.md, and give me only the highest-signal findings.
```

```text
Use $blindspot-audit before implementation. Interview me only if my answer would change architecture, workflow, scope, or risk.
```

```text
Use $blindspot-audit as a read-only pass. Do not edit files. Propose where the ledger should live and show the first entries.
```

```text
Re-run the blindspot audit. Read the existing ledger first and report only what changed or is new since last time.
```

```text
This folder is my novel project. Before I start publishing, run a blindspot audit — what am I missing that I don't even know to ask about?
```

## Korean

```text
$blindspot-audit를 deep 모드로 이 프로젝트에 돌려줘. 내가 아직 못 보고 있는 unknown unknowns를 찾아주고, 필요하면 BLINDSPOT_LEDGER.md를 만들거나 업데이트해줘.
```

```text
구현 전에 $blindspot-audit로 blindspot pass를 해줘. 구조, 범위, 위험이 바뀌는 질문만 물어봐.
```

```text
$blindspot-audit를 읽기 전용으로 돌려줘. 파일은 수정하지 말고, ledger를 어디에 두면 좋을지와 첫 항목만 제안해줘.
```

```text
blindspot audit 다시 돌려줘. 기존 원장을 먼저 읽고, 지난번 이후 새로 생겼거나 바뀐 것만 알려줘.
```

```text
이 폴더는 내가 쓰고 있는 소설 프로젝트야. 연재 시작 전에 내가 모르고 넘어가는 부분이 있는지 사각지대 점검 해줘.
```
