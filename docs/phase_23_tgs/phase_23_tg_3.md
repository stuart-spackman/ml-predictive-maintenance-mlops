## Phase 2.3 — Task Group 3 Active Recall

### Question 1
Why is it useful to prove that a Pydantic-invalid request not only returns HTTP 422, but also never reaches `pipeline.predict()`? What architectural boundary does that test protect?

**Best sections to review: 3B — Think in Terms of API Boundaries, 3F — Protect `extra="forbid"`, and 3G — Stronger Boundary Test: Invalid Schema Must Not Reach Prediction**

*A strong API test suite should't just establish that giving a valid request returns a valid prediction. It also needs to establish that failures stop at the correct boundary. As for what boundary this test protects, its the `extra="forbid"` part of our architecture. We need to make sure that an unknown field causes an API-schema failure and kicks back an HTTP 422 error, thus making it never reach `pipeline.predict()`.*

Failures should stop at the correct architectural boundary. 

There are multiple schema enforcements that take place before `pipeline.predict()`. The boundary we are trying to protect is that the pipeline doesn't unecessarily get invoked with structurally invalid data. 

### Question 2
What is failure injection, why do we use a test double rather than corrupting the real Random Forest or artifacts, and what makes the resulting test deterministic?

**Best sections to review: 3H — Failure Injection and 3I — Why Failure Injection Is Valuable**

*A failure injection is when we supply a broken version of an important object in the software system to a test instead of corrupting the real version of that object. We deliberately create a controlled failure so that we can verify the system's failure behavior. We want to be able to deliberately produce an error without damaging anything real. The resulting failure could be described as deterministic because we are creating a controlled cause of the failure.*

Failure injection doesn't necessarily require a literally "broken object." It's more generally a controlled dependency configured to produce a known failure.

Determinism comes from a known controlled cause which leads to a known exception along an expected failure path. 

### Question 3
Why should an internal inference failure's diagnostic details be absent from the HTTP response but present in server logs, and how does `caplog` let us automatically verify both sides of that policy?

**Best sections to review: 3J — Strengthen the Internal-Error Test With Logging, 3K — What Is `caplog`?, and 3L — Sanitization Is a Security and Interface Concern**

*A principle at play here is that we want a test that protects both external confidentiality/sanitatization and internal observability. In cases of an error that a caller is able to fix, i.e., 4XX errors, we're okay with giving detailed reports on what went wrong. In cases of an error that the caller is not able to fix, i.e., 5XX errors, we're not okay with giving lots of details because that could send back sensitive information to the caller, e.g., it could cause a securtiy concern. As for how `caplog` let's us automatically verify both sides of that policy, all errors processed through the logger can be inspected via `caplog.text`. Here we're enforcing our observability contract.*

If we're sending out an external response, then we sanitize it!

If we're writing to internal logs, then we add lots of diagnostically useful details. 

`caplog` lets us inspect the logging side. 

Expose information that is safe and useful for the caller to correct the request. 

### Question 4
What makes the seven-cycle HTTP-500 bug a good candidate for a permanent regression test, and why should we avoid turning every typo or historical mistake into its own regression test?

**Best sections to review: 3M — The Real 422-vs-500 Bug Is Already a Regression Test, 3N — Regression Tests Preserve Lessons From Real Failures, and 3O — Don't Turn Every Historical Mistake Into a Test**

*It makes a good candidate for a permanent regression test because it deals with data that is structurally valid but domain-invalid. It gets caught with a Phase 2.1 `InferenceInputError` and needs to be translated to HTTP 422 instead of a generic HTTP 500 error code. As for why we should avoid turning every typo or historical mistake into its own regression test, regression tests are a good tool for preserving lessons from real failures. The goal is to turn a debugging experience into permanent project knowledge. Typos and historical tests aren't guaranteed to be bugs that should make us invest in creating more tests that will make them harder to reproduce. Sometimes failure don't reveal an important recurring system guarantee.*

If we encounter a structurally valid request paired with a domain-invalid history, then we send back an HTTP 422 error (instead of a generic HTTP 500 error). 

We want to determine if something is worth permanent protection. 

Not every mistake reveals an important recurring system guarantee. 

Regression tests should preserve important lessons about behavior, not create a museum of every typo we've ever made.

### Help Needed 

* What does the `-q` mean in the testing we're doing from the command line? 

`-q` means "quiet." It tells pytest to produce less terminal output. `-v` means verbose for more detail. `-q` means quiet for less detail. 

### Ideas to Retain

* Pydantic validation is a boundary before inference, not merely a mechanism for producing 422 responses. 

* Failure injection creates a controlled failure path rather than damaging real resources. 

* Safe public errors and detailed private logs serve different audiences. 

* Regression tests should preserve important behavioral lessons from real defects. 

* `-v` means verbose; `-q` means quiet. 