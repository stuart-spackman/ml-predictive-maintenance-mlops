## Phase 2.3 — Task Group 2 Active Recall

### Question 1
What is boundary-value testing, and why is testing `minimum_cycles - 1` versus `minimum_cycles` more informative than testing two values far away from the minimum-history boundary?

**Best sections to review: 2B — Boundary-Value Testing and 2C — Protect the Minimum-History Boundary**

*Boundary value testing is when we test values that occur directly before a behavior change is expected to take place in a program, e.g., testing if an expected error occurs at 9 cycles of input data because the inference contract requires 10. As for why testing `minimum_cycles - 1` versus `minimum_cycles` is more informative than testing two values away from the minimum history boundary, bugs occur more frequently close to the spot where the behavior change occurs, not far away from it.*

Boundary-value testing usually examines both sides of the point where behavior changes, not merely the value immediately before it.

### Question 2
What is metamorphic testing? Explain why both row-order invariance and prefix invariance are examples of metamorphic tests even though they protect different properties.

**Best sections to review: 2G — Introduce Metamorphic Testing, 2H — Row-Order Normalization Is Another Metamorphic Property, and 2J — Strengthen Prefix Invariance Only If Necessary**

*Metamorphic testing is a type of testing that checks how output should behave when input is transformed in a way whose effect is known. We ask if a meaning-preserving transformation should change the result. As for why row-order invariance is a metamorphic test, our inference contract accepts a complete history and normalizes chronology. So, an ordered history and a shuffled version should produce the same output, which we can test. (I'm not able to confidently answer the one about prefix invariance.)*

Metamorphic testing is testing the protects an invariant, e.g., a shuffled dataset that is expected to give the same prediction as its ordered counterpart.

Prefix invariance refers to situations where an engineered feature does not change upon having the size of the dataset that it belongs to extended. 

### Question 3
Why is engine isolation a particularly important invariant for temporal feature engineering, and why might cross-engine contamination escape ordinary happy-path checks?

**Best sections to review: 2L — Engine Isolation Is a High-Value Feature Invariant and 2M — Why Engine Isolation Is Especially High Value**

*The underlying principle here is that features for an engine should be the same whether that engine is processed in isolation or alongside other engines, assuming the same observations are included in the payload. As for why engine isolation is particularly important, if rolling calculations accidentally ceoss an engine boundary, one engine could inherit the historical values of another engine. This would be really bad for our application's ability to return accurate predictions, but subtle and difficult to catch. When it comes to why cross-engine contamination might escape ordinary happy-path checks, it's because the feature semantics would be wrong but much of the other quality checks would still pass: feature matrix still numberic, shape still correct, `model.predict()` still runs, RUL still finite.*

"assuming the same engine observations/history are supplied"

The bug can be silent. But still cause big issues for the reliability of our predictions. It could have correct: numeric, shape, model accepts it, finite RUL. But! Semantic meaning wouldn't be correct. 

### Question 4
Why should negative tests generally assert a meaningful exception category such as `InferenceInputError` instead of broad `Exception`, and why should we be cautious about asserting exact internal exception-message wording?

**Best sections to review: 2Q — Negative Tests Should Assert the Right Error Boundary and 2R — Be Careful With Exception Message Assertions**

*When we assert a broad `Exception` category, we are only offering an indicator that something went wrong. When we assert a narrower, more meaningful category such as `InferenceInputError`, we offer an indicator that the system classified the failure at the correct architectural boundary. As for why we should be cautious about asserting exact internal exception-message wording, we don't want to create a situation where harmless wording changes break tests.*

A broad error only proves that something blew up. A narrow/descriptive error proves that the failure was classified as a caller/input-contract problem.

### Help Needed 

* What is parameterization? 

*Parameterization means running the same test logic against multiple input cases without writing multiple copies of the test.*

* What is a fixture?

*A pytest fixture is a pytest-managed dependency or piece of setup that a test can request by name.*

*A fixture can provide: model/pipeline, DataFrame, TestClient, temporary path, configuration, fake dependency.*

*Its scope determines how long it lives. Function means one per test, module means one per test file, and session means one per entire pytest run.*

* What are the "-m" and "-v" commands we're putting into the test calls from the command line? 

*`python -m pytest` means, "Use this python interpreter to locate the installed `pytest` module" and execute it.*

*`-v` means we're telling the program to be verbose and give individual test names.*

### Ideas to Retain

* Prefix invariance means a past cycle's features cannot change merely because future observations were later appended. 

* Previx invariance is evidence that temporal feature engineering is causal rather than future-leaking. 

* Parameterization runs the same behavioral test against multiple representative cases. 

* Fixtures are pytest-managed dependencies/setup supplied to tests by name. 

* In `python -m pytest`, `-m` belongs to Python and means "run module."

* `-v` belongs to a pytest and means "verbose output."