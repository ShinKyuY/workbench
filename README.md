# workbench

Claude Code 커스텀 스킬 모음 플러그인.

## 포함 스킬

| 스킬 | 설명 |
|------|------|
| `handoff` | 다음 세션/에이전트가 cold start로 이어받을 수 있는 HANDOFF.md 생성 |
| `analyze-ml-repo` | ML/AI 모델 레포 구조 분석 (데이터 흐름, 텐서 형상, 학습 파이프라인) |
| `refactor` | 코드 결함 분석 → 아키텍처 점검 → 계획 → 실행 → 검증 리팩토링 파이프라인 |
| `md2html` | 장문 Markdown을 KaTeX 수식·네이티브 플로우 다이어그램·와이어프레임·Mermaid·TOC 포함 단일 테마 HTML로 변환 |
| `parquet-viewer` | Parquet 파일을 브라우저 테이블 뷰어로 탐색 |

## 설치

```
/plugin marketplace add ShinKyuY/workbench
/plugin install workbench@shinkyuy
```

스킬은 자동으로 트리거되며, 직접 호출 시 네임스페이스가 붙습니다 (예: `/workbench:md2html`).

## 업데이트

```bash
claude plugin marketplace update shinkyuy
claude plugin update workbench@shinkyuy
```

업데이트 후 새로 시작하는 세션부터 적용됩니다.

## 전역 지침 (CLAUDE.md / AGENTS.md)

[`CLAUDE.md`](./CLAUDE.md)(Claude Code용)와 [`AGENTS.md`](./AGENTS.md)(Codex CLI 등 기타 에이전트용)는
플러그인 설치와 **무관하게 동봉만** 된 파일입니다.
설치해도 자동 적용되지 않으며, 원하는 사람만 본인 전역 지침에 복사해서 사용하세요.

```bash
# 전체를 그대로 쓰려면 (기존 파일이 있다면 백업 후)
cp CLAUDE.md ~/.claude/CLAUDE.md
cp AGENTS.md ~/.codex/AGENTS.md
```

또는 필요한 섹션만 골라 붙여넣어도 됩니다.

## 라이선스

`md2html`은 [haidang1810/md2html](https://github.com/haidang1810/md2html) 기반이며
해당 디렉터리의 LICENSE를 따릅니다.
