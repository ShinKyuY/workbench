# Refactoring Technique Catalog (리팩토링 기법 카탈로그)

Based on Martin Fowler's refactoring catalog.
Key techniques per category, and when to apply them.

## 1. Composing Methods

| Technique | When to apply |
|-----------|---------------|
| **Extract Method** | A function is too long, or a code block needs a comment |
| **Inline Method** | The method body is as clear as its name |
| **Extract Variable** | Decomposing a complex expression |
| **Inline Temp** | A temp is used once and only gets in the way |
| **Replace Temp with Query** | Replace a temp variable with a method call |
| **Split Temporary Variable** | One variable is used for multiple purposes |
| **Remove Assignments to Parameters** | A parameter gets reassigned |
| **Replace Method with Method Object** | A long method's locals block Extract Method |
| **Substitute Algorithm** | Replace with a clearer algorithm |

## 2. Moving Features Between Objects

| Technique | When to apply |
|-----------|---------------|
| **Move Method** | A method uses another class more than its own |
| **Move Field** | A field is used more by another class |
| **Extract Class** | One class carries two responsibilities |
| **Inline Class** | A class barely does anything |
| **Hide Delegate** | Clients call the delegate object directly |
| **Remove Middle Man** | A class does nothing but delegate |

## 3. Organizing Data

| Technique | When to apply |
|-----------|---------------|
| **Encapsulate Field** | Protect a public field behind getter/setter |
| **Replace Magic Number with Constant** | Meaningless numeric literals |
| **Replace Type Code with Class** | The type code does not affect behavior |
| **Replace Type Code with Subclasses** | The type code affects behavior |
| **Replace Type Code with Strategy** | The type code changes at runtime |

## 4. Simplifying Conditionals

| Technique | When to apply |
|-----------|---------------|
| **Decompose Conditional** | Split complex conditionals into well-named functions |
| **Consolidate Conditional** | Merge conditions that produce the same result |
| **Consolidate Duplicate Fragments** | The same code appears in every branch |
| **Replace Nested Conditional with Guard Clauses** | Nested conditionals → early returns |
| **Replace Conditional with Polymorphism** | Conditionals that branch on type |
| **Introduce Null Object** | Null checks repeated everywhere |

## 5. Simplifying Method Calls

| Technique | When to apply |
|-----------|---------------|
| **Rename Method** | The name does not reveal intent |
| **Introduce Parameter Object** | A group of parameters that travel together |
| **Preserve Whole Object** | Extracting several values from an object to pass along |
| **Separate Query from Modifier** | A method returns a value and also mutates state |
| **Replace Parameter with Method Call** | The caller pre-computes a value the method could compute itself |
| **Replace Error Code with Exception** | Error codes → exceptions |

## 6. Generalization

| Technique | When to apply |
|-----------|---------------|
| **Pull Up Method/Field** | The same code exists in subclasses → move to the parent |
| **Push Down Method/Field** | A parent feature is used by only some subclasses → move down |
| **Extract Subclass** | Features used by only some instances |
| **Extract Superclass** | Two classes with similar features |
| **Extract Interface** | Clients use only part of the surface |
| **Collapse Hierarchy** | Parent and child barely differ |
| **Replace Inheritance with Delegation** | A subclass uses only part of the parent's interface |
| **Replace Delegation with Inheritance** | Delegation has become excessive |
