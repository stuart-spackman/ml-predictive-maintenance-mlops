## Phase 3.3 — Task Group 5 Active Recall

### Question 1
What is the difference between `reference_incompatible`, `insufficient_data`, and `alert`, and why would it be misleading to treat a newly deployed model that no longer matches the reference artifact as ordinary population drift?

**Best sections to review: 5A — Runtime State Machine, 5D — Identity Compatibility, 5J — `reference_incompatible` Is Not an Alert**

*`reference_incompatible` happens when a change in the actual serving artifact has occurred. This situation warrants an error because PSI should not be calculated against a baseline that was created by another system.*

*`insufficient_data` happens when not enough data has been collected to create a baseline from the input data that can be meaningfully compared to the reference population.*

*`alert` happens when a PSI change greater than 0.25 has been detected in comparison between the input data and the reference baseline.*

*As for why it would be misleading to treat a newly deployed model that no longer matches the reference artifact as ordinary population drift, a newly deployed model can expect to have different output distributions, hence it cannot give meaningful data comparisons if a different model was used for the reference baseline.*

The situation doesn't warrant an error, it instead warrants a `reference_incompatible` monitoring state.

old model -> old `P(y_pred)` reference
new model -> potentially different `P(y_pred)`

A prediction distrubution difference might reflect the deployment change itself, not population drift.

`insufficient_data` means the current runtime window does not yet contain enough compatible prediction events to compare against the already-existing reference baseline.

`reference_incompatible` means the current serving artifact or feature contract does not match the system used to construct the monitoring baseline. `insufficient_data` means the reference is valid but fewer than 30 compatible current prediction events are available. `alert` means an evaluable monitored distribution has PSI >= 0.25 under the precommitted policy.

### Question 2
How does TG5 make the distinction between telemetry, logging, and monitoring concrete in the actual project, and what happens to the runtime prediction events before the system can produce an overall `stable`, `warning`, or `alert` state?

**Best sections to review: 5G–5I — Runtime Monitor and Window Evaluation, 5K — Logging vs. Monitoring Is Now Concrete**

*TG5 makes the distinction between telemetry, logging, and monitoring concrete in the actual project by first making FastAPI feed data to `events.jsonl` to establish telemetry logging. Then, to establish monitoring, a sequence of events takes place with `events.jsonl` feeding data to `phase33_monitor_runtime.py`, which then is able to do 37 PSI calculations and establish a monitoring state.*

*As for what happens to the runtime prediction events before the system can produce an overall `stable`, `warning`, or `alert` state, a minimum number of input events need to be logged for a PSI calculation to be made, or else `insufficient_data` occurs.*

FastAPI operational events -> telemetry

write them to events.jsonl -> logging

analyze those events with PSI -> monitoring

Before we can produce `stable`, `warning`, `alert`...

The runtime monitor does...

read prediction telemetry
-> flatten model_input fields
-> verify model/spec identity
-> if incompatible: `reference_incompatible`
-> otherwise: take the latest 30 events
-> if <30: insufficient data
-> otherwise: calculate 37 PSI values
-> classify each distribution
-> aggregate using worst state

The monitor isn't just calculating PSI; it also turns many individual distribution states into one operational state.

### Question 3
Why is an `insufficient_data` result after running the real runtime monitor a successful and truthful outcome rather than a failure of the monitoring system, and why should we avoid manufacturing requests merely to reach the 30-event threshold?

**Best sections to review: 5H — Running the Monitor, 5L — Runtime State, 5O — Phase 3.3 Final Architecture**

*An `insufficient_data` result after running the real runtime monitor is a successful and truthful outcome rather than a failure of the monitoring system because it means we're adhering to the drift contract of not making any calculations unless at least 30 datapoints have been obtained.*

*As for why we should avoid manufacturing requests merely to reach the 30-event threshold, that would likely be considered fabricating our result. A principle we want to embody here is that a correctly reported lack of evidence is better than a fabricated healthy result.*

A correctly reported lack of evidence is better than a fabricated healthy result.

30 compatible prediction events.

### Ideas to Retain

* Synthetic detector validation and actual runtime monitoring integration answer different questions: one proves the detector behaves correctly; the other proves real telemetry can flow through it.

* `reference_incompatible` means the measuring stick no longer applies; it is not evidence that the incoming population drifted.

* `insufficient_data` refuses to make a monitoring claim; `stable` is an actual claim made after evaluation.

* An operational monitoring window should have a defined selection policy—in this project, the latest 30 compatible prediction events. 

* Worst-state aggregation converts many individual monitored distributions into one actionable monitoring state without pretending to diagnose the cause.

### More Ideas to Retain

* `reference_incompatible` = wrong measuring stick.

* `insufficient_data` = valid measuring stick, but not enough current observations yet. 

* `alert` = enough observations, valid reference, and at least one monitored distribution crosses the alert threshold.

* The reference baseline is already frozen; the 30-event requirements applied to the current runtime window.

* Runtime monitoring checks identity first, sample sufficiency second, PSI third.

* Worst-state aggregation converts 37 individual classifications into one overall monitoring state. 

* Never manufacture evidence merely to obtain a preferred monitoring result.