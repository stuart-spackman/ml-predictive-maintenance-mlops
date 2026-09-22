## Phase 2.1 — Task Group 5 Active Recall

### Question 1
What is the difference between an expected inference failure and an unexpected software bug, and why is catching every exception as though it were bad caller input dangerous?

**Best sections to review: 5B — Expected Failures vs Unexpected Bugs and 5C — Why One Giant `except Exception` Is Dangerous**

*We should build the system to account for invalid-input conditions, which occur when the caller sends us data that violates the inference contract. An unexpected bug is when the caller provides an input that meets the inference contract but an error or violation of the inference contract still occurs. Catching every exception as though it were bad caller input is dangerous because it presupposes that no software bugs can exist and that if there's an issue it was 100% caused by the caller. If there are true software bugs we would be working with a system that doesn't accoutn for them and provide ways of catching them. The principle at play here is that you want to catch an exception at the time you know what it means at the layer it's occurring at.*

An unexpected bug is when the caller provides an input that meets the inference contract but an error or violation of the inference contract still occurs. 

Expected failures are conditions we deliberately anticipate and classify, such as insufficient engine history. Unexpected failures are implementation, dependency, or asummption failutes we did not intentionally define as part of normal operation. Catching everything as caller error can hide genuine software defects and misidentify who or what caused the failure.

### Question 2
Why is an inference exception hierarchy useful, and what advantage do we get from having specific errors such as `InferenceInputError`, `InferenceArtifactError`, and `InferenceModelContractError` all inherit from a common `InferenceError`?

**Best sections to review: 5D — Create an Inference Error Hierarchy and 5E — Why Have a Common Base Exception?**

*Inference exception hierarchies are useful because they give different failure categories explicit meanings, i.e., when we encounter them in live situations we'll have to do less work to know exactly what went wrong. When a set of errors all inherit from a common error we get the advantage of knowing the category of error and the specific type of error within that category, and the errors still get to retain their distinct types.*

Sometimes a caller only needs to know if a known inference-system failure occurred. Inheritance lets us choose the level of specificity, e.g., at the specific level we're dealing with an InferenceArtifactError and at the broader level we're dealing with an inference error. At the same time there's also the fact that an unrelated error doesn't automatically get swept into the known-inference category, also providing an architectural advantage.

### Question 3
What does it mean for this inference system to “fail closed,” and why is refusing to produce a prediction generally safer than guessing when an integrity or feature-contract check fails?

**Best section to review: 5M — “Fail Closed” Rather Than Guess**

*Failing closed is a paradigm where if we encounter a failure during runtime, instead of patching the failure so inference can still run, we simply stop and report the error. The principle at play here is that when we fail an important contract or integrity check, we refuse to proceed instead of producing a potentially lower quality output due to our patching process. If we are given an uncertain or inconsistent model input, then we refuse to give an output.*

Failing closed doesn't mean eveyr possible runtime failure must always terminate the whole application. It means when the system cannot establish an important integrity, identity, or validity guarantee, it refuses the affected operation rather than weakening the guarantee to get an answer.

### Question 4
Why are a finite but potentially poor prediction such as a negative RUL and a software-invalid prediction such as `NaN` conceptually different?

**Best sections to review: 5N — Important Edge Case: Negative RUL Is NOT Currently a Failure and 5O — Another Edge Case: Extreme Sensor Values**

*The principle at play here is that input validation is not the same as distribution monitoring. Our current system is built to check if a request is structurally and contractually valid. It is not yet build to confidently state that no input values are outside of statistical expectations, which is what a negative RUL value would be. Software invalid values include NaNs, infinities, wrong prediction shapes, and missing features. These we can currently catch. Model output that may be poor includes negative but finite RUL values and large errors. These we currently do not monitor for.*

A negative RUL is not input data at all. It is model output. 

A finite negative RUL can still satisfy the software-level output contract: the model returned exactly one numeric, finite prediction. It may be undesirable model behavior, but it is not inherently an inference-system malfunction. `NaN`, infinity, or an incorrect prediction shape violate the software contract itself and therefore should raise an inference error.

### Question 5
What is exception chaining with `raise ... from error`, and why is it useful to preserve both the high-level application meaning of a failure and its original low-level technical cause?

**Best section to review: 5L — Preserve the Original Cause When Wrapping Errors**

*The principle at play here is that when errors are encountered it's desirable to have a information about the try low-level problem and the application-level meaning of the error. Exception chaining is a technique that allows you to get both of these concepts in the same error detection.*

Exception chaining allows us to know both the application meaning (what operation failed?) and the technical cause (what low-level exception triggered it?).