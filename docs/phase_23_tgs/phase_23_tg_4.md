## Phase 2.3 — Task Group 4 Active Recall

### Question 1
What is the difference between line coverage and branch coverage, and why is branch coverage particularly useful for validation, artifact-checking, and error-handling code in our project?

**Best sections to review: 4B — What Code Coverage Means and 4D — Line Coverage vs Branch Coverage**

*To begin with, code coverage measures which parts of the program execute while the test suite runs. It can be thought of as a map but not a grade. As for what branch coverage is, this asks the extent to which a test exercised all logic-branched outcomes, e.g, if the prediction path and the failure path both received testing. Line coverage, on the other hand, records which lines of code ran and which lines of code didn't. Finally, branch coverage is useful for the above-mentioned code because our project has a lot of logic for checking failure paths. We need to gauge which decision outcomes ran in our testing suite, as testing only the happy paths might execute the majority of a module while missing multiple important failure branches.*

Line coverage -> which lines executed.

Branch coverage -> which decision outcomes executes.

High line coverage can coexist with weak failure-path coverage. 

### Question 2
Why is a high coverage percentage not equivalent to a high-quality test suite, and how should we decide whether an uncovered section of code deserves another test?

**Best sections to review: 4C — Coverage Is Not Correctness, 4G — Read Coverage by Risk, 4I — Target Uncovered Important Branches, Not Files, and 4J — A Coverage Anti-Pattern**

*The principle at play here is that it's possible to achieve 100% line coverage while asserting nothing meaningful. Uncovered code may reveal a blind spot in our testing strategy, and at the same time covered code merely tells us that it the code was executed, not that we tested it well. As for how we should decide whether an uncovered section of code deserves another test, we need to be confident that a meaningful risk is being protected.*

Covered code merely tells us that the code was executed, not that we tested it well. 

What behavior is hiding on those uncovered lines? 

If it failed: 
* Would it matter? 
* Could it fail silently?
* Is it part of a public/internal contract? 
* Can we test it cheaply and deterministically? 
If yes, then it's a strong candidate for another test. 

### Question 3
What is a quality gate, how do pytest's process exit codes make the gate usable by future CI, and what two conditions will our proposed test-and-coverage gate be able to fail on?

**Best sections to review: 4O — What Is a Quality Gate?, 4P — Exit Codes Matter to CI, and 4S — Establish the CI-Ready Test Command**

*A quality gate is simply a binary condition that must be met before code can be deemed ready to move on to the next stage of a project. As for how pytest's process exit code make the gate usable by future CI, it creates a situation where future CI endeavours don't have to read English terminal output and instead can ask if a command terminated successfully. As for what two conditions our proposed test-and-coverage gate will fail on, it can come from either a test failing or coverage dropping below a certain floor value.*

A quality gate is a machine-enforceable pass/fail condition for whether code is acceptable to move forward.

pytest exits 0 -> success. pytest exits nonzero -> failure. This allows future CI to react programatically.

Two failure conditions: 
* One or more tests fail.
* Coverage drops below the agreed floor.

### Question 4
Why should we establish a coverage threshold only after measuring and inspecting the hardened suite, and what is the main purpose of that threshold going forward?

*We should establish a coverage threshold only after measuring and inspecting the hardened suite because once we have established a reasonable baseline, that threshold can assume the job of preventing future code from dramatically increasing untested surface area without anyone noticing. This could be thought of as a regression guardrail, but it's worth noting that a particular percentage does not have perfect overlap with quality.*

**Best sections to review: 4Q — Don't Choose a Coverage Threshold Arbitrarily and 4R — Coverage Thresholds Prevent Silent Backsliding**

We do not want to pick 90% because 90% sounds strong. 

We want: measure -> inspect -> harden meaningful gaps -> observe stable baseline -> set floor.

The phrase "regression guardrail" is exactly right. 

The threshold is there to prevent: new code accumulates -> tests do not keep pace -> coverage quietly errodes.

The threshold is not a proxy for overall software quality. 

### Ideas to Retain

* Line coverage asks what executed. Branch coverage asks which logical outcomes executed.

* Coverage reveals blind spots but does not prove correctness. 

* Uncovered high-risk behavior deserves attention. Uncovered trivia likely does not deserve attention. 

* A quality gate turns test policy into a binary machine-readable decision. 

* Coverage thresholds are regression guardrails, not quality scores. 