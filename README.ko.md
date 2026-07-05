# Blindspot Audit

Blindspot Audit는 프로젝트 주인이 "모르고 있다는 것조차 모르는" 부분을 찾아주는
AI 에이전트용 스킬이다. unknown unknowns, 숨은 위험, 빠진 결정, 오래된 가정,
아직 아무도 떠올리지 못한 질문을 찾아서 `BLINDSPOT_LEDGER.md`에 남긴다.

소프트웨어, 게임, 소설·창작, 리서치, 콘텐츠, 사업 기획 등 프로젝트 종류를 가리지
않고, Claude Code, Codex, OpenCode, Claude 데스크톱 앱, 일반 채팅에서 모두
돌아간다. 감사 핵심 흐름은 공통이고, 도구마다 질문 방식과 결과 저장 방식만
맞춘다.

[English README](./README.md)

## AI에게 복사해서 설치하기

아래 문구를 Codex, Claude Code, OpenCode 같은 코딩 에이전트에게 그대로 붙여넣으면
이 레포를 읽고 현재 환경에 맞게 설치하게 할 수 있다.

```text
Install the Blindspot Audit skill from https://github.com/MJL-ren/blindspot-audit.

Please read the repository README and AGENTS.md first, detect whether this environment is Codex, Claude Code, OpenCode, Claude desktop/Cowork, or a plain project folder, then install skills/blindspot-audit using the provided installer script or a safe manual copy.

Do not modify unrelated project files. If this is a project-local install, use the appropriate project skill folder. If this is a user/global install, use the documented user skill folder. After installation, tell me the installed path and the exact prompt I can use to run a deep blindspot audit.
```

## 무엇을 하나

- 프로젝트를 먼저 프로파일링한다(종류, 단계, 주인의 전문 분야, 취미인지
  상업인지). 이때 프로젝트가 스스로 추적 중인 문서(TODO, 체크리스트, 로드맵)를
  필터로 써서, **이미 알고 있는 항목은 절대 "발견"으로 재보고하지 않는다.**
- 프로젝트 유형별 렌즈로 내부를 훑고, 없는 것만이 아니라 잘 갖춰진 것도 증거와
  함께 기록한다.
- 웹 리서치로 최근 외부 변화(규제, 플랫폼 정책, 시장·장르 변화)를 스캔한다.
  프로젝트 문서 어디에도 있을 수 없는 정보라서, 경험상 가장 임팩트 큰 발견이
  여기서 나온다.
- 발견은 3~7개로 제한해서 순위를 매긴다. 끝없는 체크리스트를 쏟아내지 않고,
  "잘 갖춰진 것"과 "지금은 건너뛰어도 되는 것(재점검 시점 포함)" 두 섹션을
  반드시 함께 준다.
- 발견 중 주인이 이미 알고 있던 게 뭔지 인터뷰한다. 알고 있던 구멍이면 필요한 건
  긴 설명이 아니라 체크리스트 한 줄이니까, 처방이 달라진다.
- `BLINDSPOT_LEDGER.md`를 남겨서, 다음 실행부터는 원장과 비교해 새로 생겼거나
  바뀐 것만 보고한다. 재실행이 잔소리가 아니라 진행 상황 확인이 된다.

이건 일반적인 품질 체크리스트가 아니다. 핵심 질문은 이거다.

> 이 프로젝트의 현재 상태를 보면, 우리가 아직 못 보고 있는 중요한 구멍은
> 무엇인가?

## 레포 구조

```text
blindspot-audit/
  AGENTS.md
  README.md
  README.ko.md
  LICENSE
  dist/
    blindspot-audit.skill        # Claude 데스크톱 앱용 원클릭 설치 파일
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

## 설치

모든 설치 스크립트는 PowerShell(`.ps1`)과 Bash(`.sh`) 두 버전이 있다.
macOS/Linux에서는 `.sh`를 쓰고(처음 한 번 `chmod +x scripts/*.sh`가 필요할 수
있다), Windows에서는 PowerShell로 `.ps1`을 쓰거나 Git Bash/WSL에서 `.sh`를 쓰면
된다.

```bash
git clone https://github.com/MJL-ren/blindspot-audit.git
cd blindspot-audit
```

### Claude Code — 개인 설치 (추천, OpenCode까지 한 번에)

`~/.claude/skills`에 설치된다. 이 경로는 Claude Code와 OpenCode가 둘 다 읽기
때문에, 한 번 설치로 두 도구를 커버한다.

```powershell
.\scripts\install-claude-user.ps1
```

```bash
./scripts/install-claude-user.sh
```

### Claude Code — 특정 프로젝트에만

`<프로젝트>/.claude/skills`에 설치된다 (이 경로도 OpenCode가 읽는다).

```powershell
.\scripts\install-claude-project.ps1 -ProjectRoot "C:\path\to\your-project"
```

```bash
./scripts/install-claude-project.sh /path/to/your-project
```

### Codex

`CODEX_HOME`이 있으면 `$CODEX_HOME/skills`, 없으면 `~/.codex/skills`에
설치된다. 원하는 위치를 인자로 넘길 수도 있다.

```powershell
.\scripts\install-codex.ps1
```

```bash
./scripts/install-codex.sh
```

### Claude 데스크톱 앱 / Cowork

`dist/blindspot-audit.skill` 파일을 Claude 데스크톱 앱 채팅에 첨부하고 **Save
skill** 버튼을 누르면 끝. 터미널이 필요 없어서 비개발자에게 가장 쉬운 경로다.

### 수동 설치

`skills/blindspot-audit` 폴더를 아래 중 원하는 위치에 복사한다.

```text
~/.claude/skills/blindspot-audit                    # Claude Code 개인 + OpenCode
<프로젝트>/.claude/skills/blindspot-audit            # Claude Code 프로젝트 + OpenCode
~/.codex/skills/blindspot-audit                     # Codex
<프로젝트>/.opencode/skills/blindspot-audit          # OpenCode 네이티브 (프로젝트)
~/.config/opencode/skills/blindspot-audit           # OpenCode 네이티브 (전역)
```

복사 후 에이전트 세션을 새로 열면 스킬이 잡힌다.

## 사용법

Claude Code와 OpenCode에서는 그냥 자연스럽게 말하면 된다. 스킬 설명이 알아서
트리거된다.

```text
이 프로젝트 사각지대 점검 해줘. 내가 모르고 넘어가는 부분이 있는지 봐줘.
```

Codex에서는 스킬 이름을 직접 부르는 게 가장 확실하다.

```text
Use $blindspot-audit in deep mode on this project. Create or update the BLINDSPOT_LEDGER.md and give me only the highest-signal findings.
```

더 많은 예시(한국어/영어)는 [examples/prompts.md](./examples/prompts.md)에 있다.

## 관리용

`skills/blindspot-audit`를 수정한 뒤에는 Claude 데스크톱 앱용 패키지를 다시 만든다.

```powershell
.\scripts\build-skill-package.ps1
```

```bash
./scripts/build-skill-package.sh
```

## 도구별 동작 차이

- 선택지 질문 가능 (Claude Code, OpenCode): 결과가 바뀌는 질문만 짧게 묻고,
  인지 인터뷰는 다중 선택 질문 하나로 처리한다.
- Codex / 채팅 전용: 질문으로 멈추지 않는다. 안전한 가정으로 진행하고 나중에
  답할 `Decision packet`을 남긴다.
- 웹 접근 없는 환경: 외부 변화 스캔을 건너뛰되 건너뛰었다고 명시하고, 규제나
  플랫폼 관련 항목은 "미검증"으로 표시한다.
- 파일 쓰기 가능: 기본적으로 `BLINDSPOT_LEDGER.md`를 만들거나 업데이트한다.
- 읽기 전용: 원장 위치와 첫 항목을 제안만 하는 리포트를 준다.

## 출처와 영감

이 프로젝트는 Claude Code 팀 Thariq(@trq212)의
[A Field Guide to Fable: Finding Your Unknowns](https://x.com/trq212/status/2073100352921215386)에서
소개된 unknown unknowns 작업 흐름에서 영감을 받았다. 이 레포의 구현, 문장,
템플릿, 스크립트는 해당 글을 복사하지 않고 새로 작성한 것이다.

## 라이선스

MIT License. [LICENSE](./LICENSE)를 보면 된다.
