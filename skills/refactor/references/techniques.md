# 리팩토링 기법 카탈로그

Martin Fowler의 리팩토링 카탈로그 기반.
각 카테고리별 주요 기법과 적용 시점.

## 1. 메서드 구성 (Composing Methods)

| 기법 | 적용 시점 |
|------|----------|
| **Extract Method** | 함수가 너무 길거나, 코드 블록에 주석이 필요할 때 |
| **Inline Method** | 메서드 본문이 이름만큼 명확할 때 |
| **Extract Variable** | 복잡한 표현식을 분해할 때 |
| **Inline Temp** | 임시 변수가 한 번만 쓰이고 방해될 때 |
| **Replace Temp with Query** | 임시 변수 대신 메서드 호출로 대체 |
| **Split Temporary Variable** | 하나의 변수가 여러 용도로 쓰일 때 |
| **Remove Assignments to Parameters** | 파라미터에 값을 재할당할 때 |
| **Replace Method with Method Object** | 긴 메서드의 지역 변수가 Extract를 방해할 때 |
| **Substitute Algorithm** | 더 명확한 알고리즘으로 교체 |

## 2. 객체 간 기능 이동 (Moving Features)

| 기법 | 적용 시점 |
|------|----------|
| **Move Method** | 메서드가 다른 클래스를 더 많이 사용할 때 |
| **Move Field** | 필드가 다른 클래스에서 더 많이 쓰일 때 |
| **Extract Class** | 하나의 클래스가 두 개의 책임을 가질 때 |
| **Inline Class** | 클래스가 하는 일이 거의 없을 때 |
| **Hide Delegate** | 클라이언트가 위임 객체를 직접 호출할 때 |
| **Remove Middle Man** | 클래스가 단순 위임만 할 때 |

## 3. 데이터 조직 (Organizing Data)

| 기법 | 적용 시점 |
|------|----------|
| **Encapsulate Field** | public 필드를 getter/setter로 보호 |
| **Replace Magic Number with Constant** | 의미 없는 숫자 리터럴이 있을 때 |
| **Replace Type Code with Class** | 타입 코드가 동작에 영향을 주지 않을 때 |
| **Replace Type Code with Subclasses** | 타입 코드가 동작에 영향을 줄 때 |
| **Replace Type Code with Strategy** | 타입 코드가 런타임에 바뀔 때 |

## 4. 조건문 단순화 (Simplifying Conditionals)

| 기법 | 적용 시점 |
|------|----------|
| **Decompose Conditional** | 복잡한 조건문을 의미 있는 이름의 함수로 분해 |
| **Consolidate Conditional** | 같은 결과를 내는 조건들을 합침 |
| **Consolidate Duplicate Fragments** | 조건 분기마다 같은 코드가 있을 때 |
| **Replace Nested Conditional with Guard Clauses** | 중첩 조건문 → 이른 반환 |
| **Replace Conditional with Polymorphism** | 타입에 따라 분기하는 조건문 |
| **Introduce Null Object** | null 체크가 반복될 때 |

## 5. 메서드 호출 단순화 (Simplifying Method Calls)

| 기법 | 적용 시점 |
|------|----------|
| **Rename Method** | 이름이 의도를 드러내지 않을 때 |
| **Introduce Parameter Object** | 함께 다니는 파라미터 그룹이 있을 때 |
| **Preserve Whole Object** | 객체에서 여러 값을 꺼내 전달할 때 |
| **Separate Query from Modifier** | 값을 반환하면서 상태도 변경하는 메서드 |
| **Replace Parameter with Method Call** | 호출자가 미리 계산하는 값을 메서드 내부에서 계산 |
| **Replace Error Code with Exception** | 에러 코드 → 예외 |

## 6. 일반화 (Generalization)

| 기법 | 적용 시점 |
|------|----------|
| **Pull Up Method/Field** | 서브클래스에 같은 코드가 있을 때 → 부모로 |
| **Push Down Method/Field** | 부모의 기능이 일부 서브클래스만 쓸 때 → 자식으로 |
| **Extract Subclass** | 일부 인스턴스만 사용하는 기능이 있을 때 |
| **Extract Superclass** | 비슷한 기능의 클래스가 둘 있을 때 |
| **Extract Interface** | 클라이언트가 일부 기능만 사용할 때 |
| **Collapse Hierarchy** | 부모/자식 차이가 거의 없을 때 |
| **Replace Inheritance with Delegation** | 서브클래스가 부모 인터페이스 일부만 쓸 때 |
| **Replace Delegation with Inheritance** | 위임이 과도할 때 |
