## Phase 3.3 — Task Group 4 Active Recall

### Question 1
Why does the Phase 3.3 closeout explicitly verify that the TG1 telemetry and TG2 reference baseline identify the same actually served model artifact and locked feature specification, and what misleading monitoring result could occur if those identities differed?

**Best sections to review: 4A–4B — Closeout Invariants and Model-Identity Reconciliation**

*The Phase 3.3 closeout explicitly verifies that the TG1 telemetry and TG2 reference baseline identify the same actually served model artifact and locked feature specification because we need the evidence to tell one coherent story. In Task Group 1 we developed a way of stating that a particular artifact actually generated the production-style prediction. In Task Group 2 we developed a way of generating a monitoring baseline using a particular artifact. Those should be the same artifact.*

*As for what misleading monitoring result could occur if those identities differed, there could be a situation where production telemetry was created with Random Forest and the reference baseline was created with Extra Trees. This would lead to inaccurate readings of PSI, among other data we plan on monitoring. Differences in distributions due to using different models will be interpreted as drift.*

Telemetry tasks and reference baseline tasks need to tell one coherent story about the system actually being monitored.

Telemetry -> What artifact actually produced predictions?

Reference baseline -> What artifact established the reference baseline?

Those identities should agree.

different estimator -> prediction baseline may be invalid

different feature specification and/or feature pipline -> feature baseline may also be invalid

The telemetry and baseline must correspond to the same deployed artifact and feature contract so that observed differences represent changes in the monitored population rather than changes in the system itself. A different estimator can invalidate the prediction-distribution baseline, while a different feature contract can invalidate the input-distribution comparison entirely.

### Question 2
Why can Phase 3.3 legitimately be considered complete even though we cannot yet calculate live production RMSE or MAE, and what additional information must eventually become available before direct performance monitoring is possible?

**Best sections to review: 4G — Direct Performance Monitoring Is Still Delayed, 4I — Final Architecture**

*Phase 3.3 can legitimately be considered complete even though we cannot yet calculate live production RMSE or MAE because live production RMSE and/or MAE requires labels. To calculate those quantities we would need to wait until data was available from actual instances of engines using up all their RUL.*

*As for what additional information must eventually become available before direct performance monitoring is possible, we need to gain access to true RUL than can be included in a calculation of RMSE with our predicted RUL.*

RMSE/MAE requires prediction and truth.

Not having immediate labels is normal for delayed-outcome ML systems and does not make unlabeled drift monitoring incomplete.

### Question 3
What is the conceptual boundary between drift detection, investigation, and retraining, and why should Phase 3.4 receive drift alerts as evidence rather than treating an `alert` as an automatic command to train and deploy a new model?

**Best sections to review: 4F — Handoff Rather Than Deployment, 4I — Final Architecture, Phase 3.3 claim boundaries**

*Drift detection is the process of calculating a population stability index and then determining if the current population has drifted from the reference population.*

*Investigation is the process of determining the root cause of drift detection.*

*Retraining is the process of updating a model in response to a drift that is lowering predictive accuracy.*

*As for why Phase 3.4 should receive drift alerts as evidence rather than treating an `alert` as an automatic command to train and deploy a new model, receiving an `alert` only means that drift was detected. That means investigation is warranted, but to justify retraining we need proof of a drop in RMSE. Drift does not imply a drop in accuracy, therefore drift alone is not sufficient for a decision for retraining.*

drift detection -> observe that a distribution changed

investigation -> determine why it changed and whether it matters

Retraining is fitting a new candidate model using updated or revised training data because sufficient evidence suggests the current model may no longer be appropriate.

Drift alone is insufficient; retraining should require additional evidence that the change is relevant to model usefulness or that updated data meaningfully justifies a new candidate.

retraining != deployment

### Ideas to Retain 

* Phase closeout reconciles evidence; it should not silently add new capabilities. 

* A monitoring reference should be bound to the artifact and feature contract it is intended to monitor. 

* Hashes provide evidence identity and integrity; they do not prove that the monitoring methodology itself is scientifically correct. 

* A dirty Git flag weakens "commit alone reproduces this state," but does not automatically invalidate evidence. 

* Drift detection produces evidence for investigation. Retraining is a separate governed decision. 

* Direct performance monitoring requires delayed truth labels; a mature system should acknowledge missing truth rather than fabricate it.

### More Ideas to Retain

* Monitoring evidence is only interpretable when the reference and runtime system identities are compatible. 

* A model change primarily invalidates the prediction baseline; a feature contract change can invalidate the input baseline. 

* Delayed outcomes are the missing ingredient for direct MAE/RMSE monitoring. 

* Drift detection asks, "Did something change?" Investigation asks, "Why, and does it matter?" Retraining asks, "Is there enough evidence to justify fitting a new candidate?"

* Retraining creates a candiate; it does not authorize promotion or deployment.