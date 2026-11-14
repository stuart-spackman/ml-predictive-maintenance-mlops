## Phase 3.4 — Task Group 1 Active Recall

### Question 1
Why is it useful to classify production failures by layer before considering retraining, and give examples of three different failure families where retraining would be the wrong first response.

*It's useful to classify production failures by layer before considering retraining because any given ML application has several interacting layers. It's important to locate the failure before choosing the remedy. Without a system of classifying failures, development teams can fall into an unhealthy pattern of blaming the model anytime something looks wrong and then potentially wasting resources on retraining.*

*As for three examples of different failure families where retraining would be the wrong first response, first we can discuss service/infrastructure failures. These include API unavailable, HTTP 500 spike, latency becomes extreme, etc. The primary response to this is to repair the service/infrastructure. Second, there are input/contract failures. These could be missing required sensor, duplicate cycles, noncontiguous history, etc. The primary response is to reject invalid input and fix anything wrong with the upstream request/data contract. Third, there are data source sensor failures. These could be a sensor being stuck at a constant value, calibration suddenly changes, measurement scale suddenly changes, etc. The primary reponse is to investigate/repair the data source, not retrain around the broken sensor.*

The core purpose of failure taxonomy is to locate the failure before choosing the remedy. 

service/infrastructure failure -> repair service 

input/contract failure -> reject/fix input

sensor/data-source failure -> repair data source

A layered failure taxonomy prevents us from treating every production anomaly as a model problem. By identifying whether the failure originates in infrastructure, input validation, data sources, serving artifacts, labels, observability, or model performance, we can apply the correct remedy instead of reflexively retraining. 

**Best sections to review: 1A–1B — Failure Taxonomy and Failure Families, 1J — Decision Logic**

### Question 2
What is the difference between `no`, `conditional`, and `yes` retraining relevance, and why do persistent drift and confirmed performance degradation receive different classifications?

**Best sections to review: 1D — Retraining Relevance, 1F–1G — Persistent Drift vs. Performance Degradation**

*In matters of retraining, the `no` state means a failure has occurred and it's fundamentally outside the model. An example could be the API server crashed.*

*`conditional` means the signal might indicate a model problem, but diagnosis is required. An example could be a persistent feature drift, which could mean a legitimate new regime that the model needs to be updated to account for, or simply a broken sensor in need of repair.*

*`yes` means there is evidence that directly supports considering a new learned mapping. An example could be a situation where we have validated representative lables plus confirmed predictive degradation. Here it's worth noting that retraining may be authorized, but not necessarily deployment.*

*As for why persistent drift and confirmed performance degradation receive different classifications, persistent drift is not a direct indicator of a need for retraining. As stated above, this can be from the rise of a new operating regime (in which case retraining is a good idea), or it can be from a broken sensor (in which case retraining is a bad idea). Meanwhile, retraining is almost always a good idea when there is a confirmed performance degradation.*

`no` -> failure is outside of the learned mapping

`conditional` -> model relevance is plausible but diagnosis is still neededk

`yes` -> evidence directly supports considering a new learned mapping

Confirmed representative performance degradation makes retraining strongly relevant, but investigation still precedes authorization. 

retraining authorization != deployment authorization

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

Inference can continue if the failure does threaten prediction correctness. 

invalid artifact -> fail closed 

invalid feature schema -> fail closed 

NaN prediction -> fail closed 

telemetry failure -> fail open with respect to inference 

monitoring unavailable -> inference continues

insufficient monitoring data -> inference continues

candidate failure -> incumbent remains + reject/fix challenger

Fail closed when continuing the affected operation could produce an incorrect prediction. Fail open when the failed component is secondary valid inference. If a retraining candidate fails, reject the candidate while preserving the known-good incumbent. 

### Help Needed 

* What does taxonomy mean in this context?

*A structured system for classifying things into meaningful categories.*

*In this project, our failure taxonomy is the way we organize production problems according to the layer where they originate.*

*A taxonomy is an organized classification system for grouping related things according to meaningful characteristics.*

*The failure taxonomy groups production problems by the system layer that failed.*

* What does schema mean in this context? 

*A schema is a formal description of the structure the data is expected to have.*

schema -> what shape/structure the data must have

values -> the actual data inside that structure

schema validation -> "Is this data structurally acceptable?"

drift monitoring -> "Has the distribution of structurally valid data changed?"

The schema is the contract describing the expected structure, fields, and types of data.

### Ideas to Retain

* The first response to a production anomaly should be to target the layer that actually failed.

* Retraining relevance can be `no`, `conditional`, or `yes`; most production failures are not direct model learning failures. 

* Persistent drift strengthes evidence that something has changed, but does not identify the cause. 

* Bad outcome labels can make a healthy model appear degraded, so label quality must be validated before retraining decisions. 

* Fail-open/fail-closed behavior should depend on whether the failure threatens prediction correctness. 

* Even confirmed model-performance degradation authorizes consideration of retraining—not automatic promotion or deployment.

### More Ideas to Retain 

* Failure classification should identify the failing layer before determining the remedy. 

* `yes` retraining relevance means "strongly worth considering," not "mandatory."

* Persistent drift tells you that change persists; it still does not tell you why. 

* Fail closed protects prediction correctness; fail open protects availability when only a secondary capability has failed. 

* A failed challenger should fail safely back to the incumbent, not destabilize production.