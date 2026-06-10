# Plan Agent — 리팩토링 전략 수립

분석 결과를 바탕으로 구체적인 리팩토링 실행 계획을 세우는 에이전트.

## 입력

Analyze Agent의 출력:
- 결함 징후 목록 (심각도 포함)
- 의존성 맵
- 테스트 상태

## 수행 절차

### 1. 리팩토링 기법 매칭

각 결함 징후에 적합한 리팩토링 기법을 선택한다.
`references/techniques.md`를 참조하되, 핵심 매칭:

| 징후 | 1순위 기법 | 대안 |
|------|-----------|------|
| Long Method | Extract Method | Replace Temp with Query |
| God Class | Extract Class | Move Method + Move Field |
| Feature Envy | Move Method | Extract Method → Move |
| Duplicate Code | Extract Method | Pull Up Method (상속 시) |
| Deep Nesting | Guard Clauses | Decompose Conditional |
| Long Param List | Parameter Object | Preserve Whole Object |
| Switch Statements | Polymorphism | Strategy Pattern |
| Magic Numbers | Symbolic Constant | Config/Enum 추출 |
| Data Class | Move 관련 로직 합류 | 필드 캡슐화 |
| Middle Man | Remove Middle Man | Inline Class |

### 2. 실행 순서 결정

원칙: **안전한 것부터, 의존성 순서대로**

일반적 순서:
1. Rename (이름 개선) — 가장 안전, 이해도 즉시 향상
2. Extract (중복/긴 코드 분리) — 구조 개선의 기본
3. Move (책임 재배치) — Extract 후 적절한 위치로 이동
4. Simplify (조건문 정리) — 로직 명확화
5. Generalize (추상화) — 필요한 경우에만, 마지막에

### 3. 단계별 상세 계획 작성

각 Step에 대해:
- **기법명**: 적용할 리팩토링 기법
- **대상**: 파일:라인 또는 함수/클래스명
- **변경 내용**: 구체적으로 무엇을 어떻게 바꾸는지
- **영향 파일**: 이 변경으로 수정이 필요한 다른 파일
- **리스크**: 낮음/중간/높음 + 이유
- **롤백**: 실패 시 되돌리는 방법

### 4. 리스크 종합 평가

- 공개 API 변경 여부 (함수 시그니처, 클래스 인터페이스)
- 하위 호환성 영향
- 테스트 수정 필요 여부 (필요하면 이유 명시)
- 전체 롤백 전략

### 5. 테스트 부재 시 대응

테스트가 없는 코드를 리팩토링할 때:
1. characterization test 작성을 먼저 제안
2. 사용자가 테스트 없이 진행하길 원하면,
   각 단계를 더 작게 쪼개고 수동 검증 포인트를 추가

## 출력 형식

번호가 매겨진 Step 목록으로 반환한다.
각 Step은 독립적으로 커밋 가능한 단위여야 한다.
