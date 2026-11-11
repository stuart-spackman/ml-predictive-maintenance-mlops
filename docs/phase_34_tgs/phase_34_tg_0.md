## Phase 3.4 — Task Group 0 Active Recall

### Question 1
What is the conceptual difference between investigation, retraining, promotion, and deployment, and why should a retrained model be treated only as a new challenger rather than as the automatic replacement for the incumbent?

**Best sections to review: 0A–0B — Decision Ladder and Four Decisions, 0I–0J — Challenger Creation and Governance Loop**

*Investigation is the process of figuring out if something happened that deserves attention.*

*Retraining is the process of figuring out if there is enough evidence to justify fitting a new candidate model.*

*Promotion is the process of figuring out if the candidate proved to be both better than the incumbent and production-compatible.*

*Deployment is the process of figuring out if the approved model should actually replace the incumbent model.*

*As for why a retrained model should be treated only as a new challenger rather than as the automatic replacement for the incumbent, there is a series of checks needed to figure out if the application would authentically benefit from having the incumbent replaced with the challenger. Higher performing is not always synonymous with production-compatible.*

Retraining itself is fitting a new candidate model using an updated or revised training dataset.

investigation -> determine cause/relevance

retraining decision -> decide whether fitting a new candidate is justified

retraining -> actually fit the new challenger

promotion -> determine whether the challenger should become the accepted model

deployment -> actually put approved model into the serving path

Retraining produces a new challenger, not a replacement. That challenger must independently prove predictive value, compatibility, software quality, and provenance before promotion, and promotion itself remains separate from deployment.

### Question 2
Which kinds of production evidence can reasonably justify retraining, which common signals are insufficient by themselves, and why should we first determine whether the observed problem is actually a model-learning problem?

**Best sections to review: 0C–0F — Monitoring Responses, Non-Model Failures, Retraining Evidence, and Insufficient Evidence; 0N–0O — Failure Response and Evidence-Driven Retraining**

*Production evidence that can reasonably justify retraining can take a few different forms. First, there can be a real predictive degradation. Second, there can be the discovery of a real new operating regime. Third, there can be a confirmed need for making corrections to the data and/or model, such as realizing that target construction was wrong.*

*As for which common signals are insufficient by themselves, there is a long list. Examples include one PSI alert, one warning, a change in prediction distribution, and a temporary API failure.*

*Finally, we should first determine whether the observed problem is actually a model-learning problem because indicators that something somewhere in production changed is not synonymous with a model-learning problem. There are situations where a production problem gets detected and it makes sense to deliberately choose to not retrain.*

There are three major legitimate retraining paths: 
* confirmed predictive degradation
* persistent legitimate new operating regime + representative labeled data
* validated correction to data/target/model design

Signals that do not by themselves authorize retraining: 
* one PSI alert
* one warning 
* prediction drift
* temporary API failure

Indicators that something somewhere in production changed is not synonymous with a model-learning problem.

API latency spike -> infrastructure problem

sensor calibration failure -> data-source problem

incorrect outcome reconstruction -> label-pipeline degradation

artifact mismatch -> serving/governance problem

Retrain because the learned mapping needs updating, not simply because production experienced an anomaly.

### Question 3
Why are delayed outcome labels important to retraining decisions, and what data-boundary rules must still be preserved when new labeled production data is incorporated into a future retraining dataset?

**Best sections to review: 0G–0H — Outcome Labels and Retraining Data Boundaries**

*Delayed outcome labels are important to retraining decisions because they allow us to figure out if there's a real performance degradation in predictive accuracy. To figure out the PSI of the predicted RUL values, we also need the real outcome labels from production.*

*As for what data-boundary rules must still be preserved when new labeled production data is incorporated into a future retraining dataset, there is still the standard sequence of principles with the subsets of the data: train learns, validation develops, grouped evaluation selects, and test judges. The new dataset can be expected to contain original historical data and new representative labeled production data, but we still need to ensure that any future information does not leak backwards; anything that learns from data lives inside the current training boundary.*

train learns -> validation develops -> grouped evaluation selects -> test judges

Preservations: 
* engine grouping
* temporal causality
* no future leakage
* learned transformations inside training boundaries

Outcome labels matter because they let us determine whether actual predictive accuracy deteriorated.

Delayed outcome labels are important because drift in inputs or predictions can be detected without labels, but direct predictive-performance degradation cannot. Once true outcomes become available, historical predictions can be paired with their actual RUL values and used to calculate RMSE or MAE. If new labeled production data is later used for retraining, engine grouping, temporal causality, no future leakage, and training-boundary discipline must all remain intact.

### Ideas to Retain

* A production signal should first be classified and investigated before deciding whether it is a model-learning problem.

* Drift can justify investigation; it does not independently authorize retraining.

* Confirmed performance degradation is strong retraining evidence, but even then data, labels, serving identity, and pipeline correctness should be checked first.

* Retraining creates a new challenger. It does not mutate the incumbent, authorize promotion, or perform deployment. 

* The retraining loop should reuse the evaluation and governance machinery already built in Phase 3.2.

* The right reponse to some ML system failures is explicitly "do not retrain."

### More Ideas to Retain

* The retraining decision and retraining itself are different: one authorizes fitting while the other acutally fits a new challenger. 

* Retraining creates a challenger, not an incumbent. 

* A production anomaly is not automatically a model-learning problem. 

* Prediction PSI only requires predictions; RMSE and MAE require predictions plus ground-truth labels. 

* New production data does not relax the old experimental rules: grouping, temporal causality, and leakage prevention still apply.

`P(X)` drift -> no labels required

`P(y_pred)` drift -> no labels required

RMSE/MAE degradation -> outcome labels required