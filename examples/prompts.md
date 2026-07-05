# Prompt Examples

On Claude Code and OpenCode you can just ask naturally — the skill triggers
from its description. On Codex, referencing `$blindspot-audit` explicitly is
the most reliable.

Wondering what the output should look like? See
[sample-reports/](./sample-reports/) for synthetic examples.

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

A focus run narrows the whole audit machinery onto one domain — use it
when a full audit flagged a weak-domain surface it only skimmed, or when
you already know where your blind spots cluster:

```text
Use $blindspot-audit with focus: ux-ui on this project. I'm a backend developer — walk the user-facing surface with the ux-ui pack and tell me what I never knew to decide (states, devices, dark mode, keyboard access). Append the findings to the existing ledger.
```

A context-rich prompt gets a sharper first audit (everything here is
optional — the intake asks for what it needs and every question is
skippable):

```text
Use $blindspot-audit in planning mode. Context: public, non-commercial indie project; I'm strong at programming, weak at publishing, legal, and accessibility. Never put the project's name into web searches — category-only. Give me the top 3-5 blind spots plus what's safe to ignore for now, and store this context in the ledger so you don't ask again.
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

포커스 런은 감사 전체 기계를 한 도메인에 집중시킨다 — 전체 감사가 "이
영역은 훑기만 했다"고 알려줬을 때, 또는 자기 약점이 어디 몰려 있는지 이미
알 때 쓰면 된다:

```text
$blindspot-audit를 focus: ux-ui로 이 프로젝트에 돌려줘. 나는 백엔드 개발자야 — ux-ui 팩으로 사용자 표면을 걸어보고, 내가 결정해야 하는지도 몰랐던 것들(상태, 기기, 다크모드, 키보드 접근)을 알려줘. 발견은 기존 원장에 추가해줘.
```

맥락을 함께 주면 첫 감사가 훨씬 정확해진다 (전부 선택 사항 — 스킬이 필요한
것만 묻고, 모든 질문은 패스할 수 있다):

```text
$blindspot-audit를 planning 모드로 돌려줘. 맥락: 공개 예정인 비상업 개인 프로젝트고, 나는 구현은 익숙하지만 출시/법무/접근성은 잘 몰라. 웹 검색할 때 프로젝트 이름은 넣지 말고 카테고리로만 찾아줘. 중요한 blind spot 3~5개와 지금은 무시해도 되는 것을 나눠서 알려주고, 이 맥락은 원장에 기록해서 다음엔 다시 묻지 마.
```
