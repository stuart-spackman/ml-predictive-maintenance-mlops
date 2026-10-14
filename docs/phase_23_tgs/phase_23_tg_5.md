## Phase 2.3 — Task Group 5 Active Recall

### Question 1
What is the difference between test discovery, test execution, and the final quality gate? What distinct evidence does each provide?

**Best sections to review: 5B — Run the Final Test Inventory and 5C — Run the Final Quality Gate**

*Test discovery refers to the ability of our testing suite to discover all tests that were writted for the application, e.g., the actual number of tests collected when running the `--collect-only` function associated with pytest. This could be described as inventory evidence, i.e., the collection that pytest currently recognizes as part of the automated suite. Test execution is the process of actually running the tests and checking which of them pass or fail. This provides evidence of the entire test suite passing. As for the final quality gate, this gets divided into two components. All tests need to pass and coverage needs to remain above the agreed floor. If either fails to provide passing evidence, then the quality gate is considered a fail.*

*Test discovery -> inventory evidence -> What does pytest currently recognize as part of the automated suite?*

*Test execution -> does the entire current suite actually pass?*

*Final quality gate -> all tests pass + coverage remains above the agreed floor.*

Test Discovery
* What tests does pytest recognize? 
* inventory evidence 

Test Execution
* Do those tests actually pass? 
* behavioral execution evidence

Quality Gate 
* Do all tests pass and does coverage remain above the floor? 
* machine-enforceable acceptance decision

Discovery doesn't prove pytest found "all tests that were written" in an absolute sense. It proves what pytest currently discovers under its configuration and naming rules. 

### Question 2
Why should the Phase 2.3 handoff explicitly document both supported guarantees and known limitations, and why would “all tests pass” be an overreach as evidence for model accuracy, absence of drift, or universal correctness?

**Best sections to review: 5G — Record Known Limitations, 5K — What Phase 2.3 Can Now Legitimately Claim, and 5L — What Phase 2.3 Does NOT Claim**

*The principle at play here is that a good handoff states both what the evidence supports and what the evidence does not support. As for why "all tests pass" would be an overreach for model accuracy, absence of drift, or universal correctness, the main implication from all tests passing is that the current evidence supports the contracts being tested. There are still lots of conclusions that cannot be made such as no bugs exist, all possible inputs are correct, model predictions are always accurate, CI works, etc.*

The current evidence supports the contracts being tested.

### Question 3
Why does Phase 2.3 not need another large handoff-audit script merely for symmetry with Phases 2.1 and 2.2, and what serves as the executable handoff instead?

**Best sections to review: 5J — Why We Don't Need Another Big Audit Script and 5M — Final Phase 2.3 Handoff Sequence**

*In previous phases, a dedicated audit script made sense because new runtime subsystems had been added to the project. That is not the case here. For this phase, the executable artifact we're handing off it the test suite itself (paired with the quality-gate command). The executable handoff is proof of all tests in the testing strategy document now working.*

The executable handoff is the passing quality-gate command itself.

The strategy/handoff documents explain what the gate means. 

The command provides the machine-executable evidence.

documentation -> defines and explains the verification policy

quality-gate command -> executes and enforces that policy

### Question 4
What exactly is Phase 2.3 handing to Phase 2.4, and how does the responsibility change from “define what passing means” to “automatically reproduce and enforce it”?

**Best sections to review: 5I — Create the Phase 2.3 Handoff Document and 5M — Final Phase 2.3 Handoff Sequence**

*Phase 2.3 is passing a statement to Phase 2.4 that Phase 2.3 is complete. The Phase 2.1 inference subsystem and Phase 2.2 FastAPI serving layer now have a deliberate automated verification strategy and CI-ready quality gate. Phase 2.3 has now defined the contract and Phase 2.4 does not need to decide what constitutes as passing.*

Phase 2.3 -> decide what passing means

Phase 2.4 -> reproduce and automatically enforce it

Phase 2.3 is handing Phase 2.4: 
* a passing automated test suite 
* reproducible testing dependencies 
* centralized coverage configuration
* an evidence-based coverage floor
* one authoritative CI-ready quality-gate command 
* documented testing guarantees 
* documented testing limitations 
* known dependency concerns to carry forward

Phase 2.4 asks: 
* Can another clean environment reproduce this? 
* Can we package the application consistently? 
* Can GitHub Actions run the exact same gate automatically? 
* Can a failed gate block integration? 

### Ideas to Retain 

* Discovery tells us what pytests sees. Execution tells us whether those tests pass. The quality gate decides whether the project meets the agreed acceptance standard.

* Passing tests support only the contracts represented by those tests. 

* The Phase 2.3 executable handoff is the quality-gate command, not another redundant audit script. 

* Phase 2.3 hands Phase 2.4 both artifacts and policy: tests, dependencies, coverage configuration, coverage floor, gate command, guarantees, and limitations. 

* Phase 2.3 defines what passing means. Phase 2.4 makes that definition reproducible and automatic.