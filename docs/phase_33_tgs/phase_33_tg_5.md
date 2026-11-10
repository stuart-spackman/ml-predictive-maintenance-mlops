## Phase 3.3 — Task Group 5 Active Recall

### Question 1
What is the difference between `reference_incompatible`, `insufficient_data`, and `alert`, and why would it be misleading to treat a newly deployed model that no longer matches the reference artifact as ordinary population drift?

**Best sections to review: 5A — Runtime State Machine, 5D — Identity Compatibility, 5J — `reference_incompatible` Is Not an Alert**

*`reference_incompatible` happens when a change in the actual serving artifact has occurred. This situation warrants an error because PSI should not be calculated against a baseline that was created by another system.*

*`insufficient_data` happens when not enough data has been collected to create a baseline from the input data that can be meaningfully compared to the reference population.*

*`alert` happens when a PSI change greater than 0.25 has been detected in comparison between the input data and the reference baseline.*

*As for why it would be misleading to treat a newly deployed model that no longer matches the reference artifact as ordinary population drift, a newly deployed model can expect to have different output distributions, hence it cannot give meaningful data comparisons if a different model was used for the reference baseline.*

### Question 2
How does TG5 make the distinction between telemetry, logging, and monitoring concrete in the actual project, and what happens to the runtime prediction events before the system can produce an overall `stable`, `warning`, or `alert` state?

**Best sections to review: 5G–5I — Runtime Monitor and Window Evaluation, 5K — Logging vs. Monitoring Is Now Concrete**

*TG5 makes the distinction between telemetry, logging, and monitoring concrete in the actual project by first making FastAPI feed data to `events.jsonl` to establish telemetry logging. Then, to establish monitoring, a sequence of events takes place with `events.jsonl` feeding data to `phase33_monitor_runtime.py`, which then is able to do 37 PSI calculations and establish a monitoring state.*

*As for what happens to the runtime prediction events before the system can produce an overall `stable`, `warning`, or `alert` state, a minimum number of input events need to be logged for a PSI calculation to be made, or else `insufficient_data` occurs.*

### Question 3
Why is an `insufficient_data` result after running the real runtime monitor a successful and truthful outcome rather than a failure of the monitoring system, and why should we avoid manufacturing requests merely to reach the 30-event threshold?

**Best sections to review: 5H — Running the Monitor, 5L — Runtime State, 5O — Phase 3.3 Final Architecture**

*An `insufficient_data` result after running the real runtime monitor is a successful and truthful outcome rather than a failure of the monitoring system because...*

*As for why we should avoid manufacturing requests merely to reach the 30-event threshold, ...*