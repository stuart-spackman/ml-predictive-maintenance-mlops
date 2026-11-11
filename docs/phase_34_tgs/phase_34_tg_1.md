## Phase 3.4 — Task Group 1 Active Recall

### Question 1
Why is it useful to classify production failures by layer before considering retraining, and give examples of three different failure families where retraining would be the wrong first response.

*It's useful to classify production failures by layer before considering retraining because any given ML application has several interacting layers. It's important to locate the failure before choosing the remedy. Without a system of classifying failures, development teams can fall into an unhealthy pattern of blaming the model anytime something looks wrong and then potentially wasting resources on retraining.*

*As for three examples of different failure families where retraining would be the wrong first response, first we can discuss service/infrastructure failures. These include API unavailable, HTTP 500 spike, latency becomes extreme, etc. The primary response to this is to repair the service/infrastructure. Second, there are input/contract failures. These could be missing required sensor, duplicate cycles, noncontiguous history, etc. The primary response is to reject invalid input and fix anything wrong with the upstream request/data contract. Third, there are data source sensor failures. These could be a sensor being stuck at a constant value, calibration suddenly changes, measurement scale suddenly changes, etc. The primary reponse is to investigate/repair the data source, not retrain around the broken sensor.*

**Best sections to review: 1A–1B — Failure Taxonomy and Failure Families, 1J — Decision Logic**

### Question 2
What is the difference between `no`, `conditional`, and `yes` retraining relevance, and why do persistent drift and confirmed performance degradation receive different classifications?

**Best sections to review: 1D — Retraining Relevance, 1F–1G — Persistent Drift vs. Performance Degradation**

*In matters of retraining, the `no` state means a failure has occurred and it's fundamentally outside the model. An example could be the API server crashed.*

*`conditional` means the signal might indicate a model problem, but diagnosis is required. An example could be a persistent feature drift, which could mean a legitimate new regime that the model needs to be updated to account for, or simply a broken sensor in need of repair.*

*`yes` means there is evidence that directly supports considering a new learned mapping. An example could be a situation where we have validated representative lables plus confirmed predictive degradation. Here it's worth noting that retraining may be authorized, but not necessarily deployment.*

*As for why persistent drift and confirmed performance degradation receive different classifications, persistent drift is not a direct indicator of a need for retraining. As stated above, this can be from the rise of a new operating regime (in which case retraining is a good idea), or it can be from a broken sensor (in which case retraining is a bad idea). Meanwhile, retraining is almost always a good idea when there is a confirmed performance degradation.*

### Question 3
How should fail-open versus fail-closed behavior differ across artifact/feature failures, telemetry/monitoring failures, and retraining-candidate failures, and what general principle determines whether inference should continue?

**Best sections to review: 1C — Fail Open vs. Fail Closed, 1K — Whether Serving Should Continue**

*Across different artifact/feature failures, fail-open should occur when the operation does not create a risk for producing an incorrect result. Examples could be monitoring analysis no longer being available or having insufficient monitoring data. Fail-closed should happen when an operation stops functioning that could make the result incorrect. Examples could include the detection of an invalid model artifact, invalid feature schema, an NaN prediction, etc.*

* invalid model artifact -> fail closed 
* invalid feature schema -> fail closed
* NaN prediction -> fail closed 
* telemetry write failure -> fail open with respect to prediction
* monitoring analysis unavailable -> inference may continue
* insufficient monitoring data -> inference continues

*As for the general principle that determines whether inference can continue, inference can continue if the application is not at risk of serving incorrect predictions. If the results produced by the application are not at risk, then inference can continue and we fail open.*

### Help Needed 

* What does taxonomy mean in this context?

* What does schema mean in this context? 