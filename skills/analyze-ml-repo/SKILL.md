---
name: analyze-ml-repo
description: >
    ML/AI 모델 코드 레포지토리의 구조 분석이 필요할 때 사용하는 스킬.
    사용자가 ML 레포 분석, 모델 코드 이해, 학습 파이프라인 파악,
    데이터 흐름 추적, 텐서 형상 확인, 코드베이스 구조화 문서화를
    요청할 때 사용한다. "이 모델 어떻게 동작해?", "데이터가 어떻게
    흘러가?", "텐서 형상 알려줘", "워크플로우 정리해줘", "코드 구조
    분석해줘" 같은 요청에 반드시 트리거되어야 한다. '분석'이라는
    단어가 없어도 모델 학습/추론 코드의 동작 설명이 필요한 상황이면
    사용한다.
---

# ML Repository Analyzer

ML/AI 모델 레포지토리를 전문 subagent 팀으로 분석하여
구조화된 문서를 생성하는 스킬이다.

## 핵심 원칙

1. **코드 우선, docs 보조**: 소스코드를 먼저 읽고,
   docs/README는 보충용이다.
2. **구체적 예시 필수**: 추상적 설명 대신 실제 데이터 예시,
   텐서 형상, 코드 라인 참조를 포함한다.
3. **필요한 subagent만 병렬 투입**: 요청 범위에 맞는
   에이전트를 골라(Step 2) 동시에 투입한다.
4. **오케스트레이터 역할**: 메인 에이전트는 subagent 결과를
   종합하고, 빈 부분을 보충하고, 최종 문서를 조립한다.
5. **산출물은 파일로**: 최종 문서는 markdown으로 저장하고
   md2html 스킬로 HTML 변환까지 마친다. 채팅에는 요약만
   제시한다.

---

## Step 1: 정찰 (직접 수행)

subagent를 보내기 전에 먼저 레포의 뼈대를 파악한다.
이 정보가 있어야 subagent에게 정확한 탐색 범위를 지시할 수
있다.

직접 실행할 작업:
```
1. Glob으로 프로젝트 트리 파악:
   - **/*.py (주요 Python 파일)
   - **/config*.json, **/config*.yaml (설정 파일)
   - **/*.md (문서)

2. Grep으로 핵심 패턴 탐색:
   - "class.*Dataset" -> 데이터셋 파일 위치
   - "class.*Model\b|class.*Net\b|class.*Module" -> 모델 파일 위치
   - "def forward" -> forward pass 위치
   - "def train|class.*Trainer" -> 학습 루프 위치
   - "nn\.Embedding|nn\.Conv|nn\.Linear|nn\.LSTM|nn\.Transformer"
     -> 사용 중인 아키텍처 패턴 파악
   - "__main__" -> entry point

3. Config 파일 읽기:
   - 모델 핵심 수치 파악 (차원, 레이어 수, vocab 크기 등)
   - 어떤 아키텍처 유형인지 판별
     (CNN/RNN/Transformer/GAN/Diffusion/MLP/추천·랭킹 등)

4. 분석 범위 확정:
   - 레포에 독립적인 모델 패밀리나 서브프로젝트가 여러 개면
     (모노레포), 어느 부분을 분석할지 AskUserQuestion으로
     사용자에게 확인한다. 전체 분석은 시간·토큰이 몇 배로
     들기 때문에 범위를 먼저 좁히는 것이 낫다.
```

이 단계의 결과물: **subagent 투입 계획** — 어떤 파일을
누가 분석할지 결정한다.

---

## Step 2: 투입할 subagent 선택

모든 분석이 필요하지 않을 수 있다. 사용자 요청에 따라
투입할 subagent를 선택한 뒤 Step 3로 진행한다.

| 요청 유형 | 투입 agents |
|-----------|-------------|
| "전체 구조 분석해줘" | 5개 전체 |
| "데이터 형상 알려줘" | structure-scout + data-pipeline |
| "모델 어떻게 동작해" | structure-scout + model-architecture |
| "학습 어떻게 해" | structure-scout + training-workflow |
| "워크플로우 정리해줘" | structure-scout + data-pipeline + training-workflow + inference-analyst |
| "이 파일 분석해줘" | 없음 — 직접 수행, subagent 불필요 |

- Step 1 정찰은 어떤 경우에도 직접 수행한다.
  structure-scout는 정찰과 별개로, 최종 문서의 구조/entry
  point 섹션을 작성하는 에이전트다.
- 사용자가 이전에 분석한 결과가 대화에 있으면, 해당 부분은
  건너뛰고 새로운 부분만 분석한다.

---

## Step 3: 전문 Subagent 병렬 투입

Step 2에서 선택한 subagent를 **동시에** 투입한다.
각 subagent에게는 Step 1에서 파악한 구체적 파일 경로를
지정해준다.

에이전트 정의는 `agents/` 디렉토리에 있다.
투입 전에 해당 에이전트 파일을 Read로 읽어서 프롬프트에
포함하라.

| # | 에이전트 | 파일 | subagent_type | 역할 |
|---|---------|------|---------------|------|
| 1 | structure-scout | `agents/structure-scout.md` | Explore (very thorough) | 프로젝트 구조, entry point, 실행 흐름 |
| 2 | data-pipeline | `agents/data-pipeline.md` | general-purpose | 데이터 파이프라인, 형상 변환 |
| 3 | model-architecture | `agents/model-architecture.md` | general-purpose | 모델 구조, forward pass, 핵심 블록 |
| 4 | training-workflow | `agents/training-workflow.md` | general-purpose | 학습 루프, loss, optimizer |
| 5 | inference-analyst | `agents/inference-analyst.md` | general-purpose | 추론, 출력 스키마, 서빙 |

각 에이전트에게 전달할 프롬프트 구성:
1. 에이전트 파일의 지침 내용
2. Step 1에서 파악한 **구체적 파일 경로**
3. Config에서 읽은 **핵심 수치** (해당 시)
4. `references/diagram-rules.md`의 다이어그램/표 규칙
   — **투입하는 모든 에이전트에게 전달한다.** 각 에이전트
   지침이 D1~D6 규칙을 참조하므로, 빠뜨리면 규칙 없이
   다이어그램을 그리게 된다.
5. 보고서 형식 지시: 최종 문서에 그대로 편입할 markdown
   섹션으로 작성하게 한다 (각 에이전트 파일의 출력 규칙
   참고).

**Fallback — Agent 디스패치 도구가 없는 환경** (중첩
subagent, 일부 플랫폼): 병렬 투입 대신, Step 2에서 선택한
에이전트 정의 파일과 `references/diagram-rules.md`를 읽고
각 에이전트의 분석 절차·출력 규칙을 직접 순차 수행한다.
선택 기준과 산출물 품질 기준은 동일하게 적용된다.

---

## Step 4: 결과 종합 및 보충

모든 subagent 결과가 돌아오면:

1. **결과 검증**: 각 subagent의 결과를 빠르게 검토한다.
   형상이 맞는지, 빠진 부분이 없는지 확인한다.
2. **교차 참조**: 데이터 전문가의 "배치 출력"과
   모델 분석가의 "forward 입력"이 일치하는지 확인한다.
3. **빈 부분 보충**: subagent가 놓친 파일이나 세부사항은
   직접 읽어서 보충한다.
4. **비교 테이블**: 모델이 여러 개이면 핵심 비교 테이블을
   작성한다.

---

## Step 5: 최종 문서 조립 → HTML 변환

### 5-1. Markdown 문서 조립

subagent 결과를 아래 구조로 조립한다. 다이어그램은
`references/diagram-rules.md` 규칙(Mermaid/markdown 표)을
따르고, 각 섹션에 해당 소스 파일 경로를 마크다운 링크로
첨부한다.

```markdown
# [프로젝트명] 분석

## 전체 워크플로우
(Mermaid 다이어그램: 데이터 -> 전처리 -> 모델 -> 출력)

## 1. 데이터 파이프라인
### 1-1. 원시 데이터 스키마
### 1-2. 전처리 파이프라인
### 1-3. Dataset -> Collate 형상
### 1-4. 구체적 데이터 예시 (원시 데이터 행, 배치 텐서)

## 2. 모델 아키텍처
### 2-1. 설정값 요약 테이블
### 2-2. Forward Pass 형상 추적 (라인별)
### 2-3. 핵심 연산 블록 분석 (시각화 포함)
### 2-4. Loss 함수 (수식 + 형상)

## 3. 학습 워크플로우
### 3-1. 학습 설정 (optimizer, scheduler, precision)
### 3-2. 분산 학습 구성
### 3-3. 체크포인트 구조
### 3-4. CLI 실행 예시

## 4. 추론 & 출력
### 4-1. 추론 입출력 형상
### 4-2. 출력 스키마
### 4-3. 서빙 최적화

## 5. 핵심 비교 테이블
(모델이 여러 개이면)
```

### 5-2. 저장 및 HTML 변환

1. 조립한 문서를 `.md` 파일로 저장한다. 사용자가 경로를
   지정하지 않았으면 분석 대상 레포의
   `docs/analysis/<주제>.md`에 저장한다 (디렉토리가 없으면
   생성).
2. **md2html 스킬을 호출**하여 저장한 `.md`를 HTML로
   변환한다. Mermaid 다이어그램·표·코드 블록이 네이티브로
   렌더링된다. HTML 변환 로직을 직접 작성하지 않는다.
3. 채팅에는 핵심 요약(전체 워크플로우 + 주요 발견 몇 가지)과
   `.md`/`.html` 파일 경로만 제시한다. 전체 문서를 채팅에
   다시 붙여넣지 않는다.

---

## 분석 시 주의사항

1. **docs만 읽는 함정**: subagent에게 "소스 코드를 전체
   읽어라"고 명시적으로 지시한다.
2. **형상 추측 금지**: Embedding 테이블 크기, Linear in/out
   차원은 코드에서 직접 확인한다.
3. **예시 없는 설명 금지**: "x는 입력 텐서" 같은
   설명은 불충분. `x: shape [32, 3, 224, 224]` 같은
   구체적 예시가 필수.
4. **교차 검증**: 데이터 출력 형상과 모델 입력 형상이
   일치하는지 반드시 확인한다.
