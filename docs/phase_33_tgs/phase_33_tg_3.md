## Phase 3.3 — Task Group 3 Active Recall

### Question 1
Why do we use both a known stable-control window and a deliberately drifted window to validate the monitoring system, and why is this stronger evidence than simply calculating PSI on one arbitrary production-like dataset?

**Best sections to review: 3A–3B — Controlled Synthetic Drift and Its Claim Boundaries, 3E — Large Synthetic Shift**

*We use both a known stable control window and a deliberately drifted window to validate the monitoring system because we want to avoid a scenario where we find that the PSI for a particular sensor is in the `alert` zone but we don't have a way of knowing if the detector is working correctly or the populations happened to differ. Instead we can first gauge a situation where reference values are equal to the current values and we just change row ordering, thus expecting PSI = 0. And then we do some failure injection for monitoring by deliberately shifting the current values into the `alert` zone.*

*As for why this is stronger evidence than simply calculating PSI on one arbitrary production-like dataset, when using a known stable control window along with a deliberately drifed window, we get to obtain an answer for the question, "If a distribution is obviously different, does our detector definitely notice?"*

known unchanged distribution -> detector should stay quiet

known changed distribution -> detector should react

This tests false positive behavior and true positive behavior. 

A stable control tests that the detector does not raise false alarms when the distribution is unchanged, while synthetic drift tests that it does not react when a known distribution shift is introduced. Together they validate detector behavior much more strongly then inspecting PSI on a dataset whose true drift status is unknown.

### Question 2
If a monitored feature produces PSI above 0.25 and receives an `alert`, what exactly are we justified in concluding, and what are we *not* justified in concluding about model accuracy, sensor health, or retraining?

**Best sections to review: 3I — Alert ≠ Diagnosis, 3J — Real Production Flow, and Phase 3.3 TG0 claim boundaries**

*If a monitored feature produces PSI above 0.25 and receives an `alert`, then we are justified in concluding that the current distribution for this monitored variable differs materially from its reference distribution according to our precommitted PSI policy.*

*As for what we are definitely not justified in concluding about model accuracy, sensor health, or retraining, we cannot justifiably say that the sensor is broken, the model is inaccurate, the RMSE increased, the engine fleet is unsafe, the model needs retraining, etc.*

The monitored distribution differs materially from its reference according to our precommitted policy.

A very important MLOps habit is to distinguish detection from diagnosis.

### Question 3
Why is `insufficient_data` conceptually different from `stable`, how does the 30-event minimum protect the monitoring process, and how do logging, drift detection, direct performance monitoring, and retraining fit into the larger lifecycle as distinct steps?

**Best sections to review: 3J–3K — Production Monitoring and `insufficient_data`, 3M — Phase 3.3 Exit State**

*`insufficient_data` is conceptually different from `stable` because `insufficient_data` is what we get when prediction telemetry has been accumulating but there has not been enough events to create a monitoring window. `stable` is the result of a sequence of events where we get enough events to create a monitoring window, we declare frozen reference bins, we make a PSI calculation, and we find that it is below 0.1.*

*As for how the 30-event minimum protects the monitoring process, we don't want to allow situations where a false alarm gets declared early. There needs to be a threshold level of evidence before we can truthfully state that a distribution is unstable. There might be occasions where the first 10 points cross over into the `alert` category, but the following 20 points even our the distribution back to `stable` levels.*

*And finally, logging, drift detection, direct performance monitoring, and retraining fit into the larger lifecycle as distinct steps and we can use them to tell a coherent monitoring story. The sequence of events goes something like:*
prediction request
-> actual serving system 
-> structured telemetry
-> actual served artifact identity recorded
-> 36 model inputs + prediction recorded
-> reference prediction event population
-> reference only PSI bins frozen
-> precommitted thresholds
-> current window
-> PSI
-> `stable`/`warning`/`alert`

`insufficient_data` -> not enough evidence to evaluate

`stable` -> enough evidence was collected, evaluated, and did not cross the warning threshold

We require a minimum amount of evidence before classifying the window at all.

logging -> collection evidence

drift detection -> detect distribution changes 

performance monitoring -> measure prediction error once truth exists

retraining -> action taken only after sufficient evidence and policy

### Help Needed

* What does telemetry mean in this context? Is it the process of logging events and evaluating statistics? 

*Telemetry is the operational data automatically emitted or recorded by the running application about what it is doing.*

telemetry = the operational measurements/events produced the the running system

logging = one mechanism for recording that telemetry

monitoring = analyzing that telemetry for patterns, health, drift, etc.

Telemetry is automatically collected data describing the behavior and operation of a runnign system. Monitoring is what we do with that telemetry to evaluate system health and change over time.

### Ideas to Retain 

* Failure injection is useful for monitoring systems because known synthetic drift lets us verify that detectors actually react to change

* A healthy control and a deliberately drifted control provide much stronger validation of a detector than merely looking at one arbitrary PSI value. 

* `insufficient_data` is different from `stable`; lack of observations cannot establish that a distribution is healthy.

* An alert identifies an operationally material distribution change according to policy; it does not diagnose its cause. 

* Drift monitoring detects changes in observable distributions. Performance monitoring requires truth labels, and retraining remains a separate decision.

### More Ideas to Retain 

* A detector should be tested both for sensitivity to known drift and restraint under known stability. 

* An alert is a detection result, not a root-cause diagnosis. 

* `insufficient_data` means "cannot evaluate yet," while `stable` means "evaluated and currently within policy."

* A minimum window size reduces fragile conclusions from very small samples but does not magically elimiate statistical uncertainty. 

* Logging, drift detection, performance monitoring, and retraining are separate lifecycle stages.