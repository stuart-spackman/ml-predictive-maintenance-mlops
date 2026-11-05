## Phase 3.2 — Task Group 1 Active Recall

### Question 1
What is the difference between an MLflow experiment, run, logged model artifact, registered model, and registered model version? How does the registered candidate retain lineage back to the execution that produced it?

**Best sections to review: 1A–1B — What MLflow Is Adding and Run vs. Model Version, 1O–1P — Inspecting the Run and Registry**

*An MLflow experiment is a recorded sequence of events involving a run, various logged components of the model, and a registering of the model version.*

*An MLflow run is a recording of the following executions associated with a model: code/configuration, parameters, metrics, and artifacts. It's MLflow's way of saying, "Here's what happened."*

*A logged model artifact is the collection of model components and parameters needed to reproduce the trained model.*

*A registered model is saved model that MLflow was able to run an experiment on.*

*An MLflow registered model version is an identifiable model artifact placed under a registered model name. It's MLflow's way of saying, "Here is the model produced by that particular run."*

*As for how the registered candidate retains lineage back to the execution that produced it, candidate version models save data on source run, version number, validation status, and lifecycle role.* 

An MLflow experiment can be thought of more as a container/grouping for related runs.
Experiment
-> run 1
-> run 2
-> run 3

A logged model artifact in MLflow is the serialized fitted model artifact and associated MLflow model metadata stored as part of the run.

A registered model is the named family/container while a registered model version is the specific registered artifact.

model version
-> source run and/or run_id
-> parameters + metrics + artifacts + tags

### Question 2
Why do we fit the frozen Extra Trees recipe on all eligible development engines when creating the candidate artifact, while still logging the Phase 3.1 grouped-CV RMSE as `reference_pooled_oof_rmse` rather than computing a new training RMSE and treating it as candidate performance?

**Best sections to review: 1H–1J — Frozen Candidate, Full-Development Fit, and What We Log**

*While still logging the Phase 3.1 grouped-CV RMSE as `reference_pooled_oof_rmse` rather than computing a new training RMSE and treating it as a candidate performance, we fit the frozen Extra Trees recipe on all eligible development engines when creating the candiate artifact because we want to mirror all the things we did for the final incumbent artifact. In that process we used the process of letting selection/evaluation determine the recipe first, then the final candidate artifact is fit using the full development population. While we used cross-validation during initial training, once the recipe is frozen the fitted candidate artifact should learn from all eligible development data.*

The final full development fit creates the artifact; it does not create a new unbiased estimate of predictive performance.

### Question 3
Why can the Extra Trees model be registered and tagged `validation_status=pending` without receiving the `champion` alias or changing the currently served Random Forest? What different lifecycle claims do registration, validation, and promotion make?

**Best sections to review: 1R–1V — Pending Validation, Champion Alias, Tags, and Serving Boundaries**

*The Extra Trees model can be registered and tagged `validation_status=pending` without receiving the `champion` alias or changing the currently served Random Forest because receiving the `champion` status is reserved for the situation where the Extra Trees model has beat the incumbent and we intend to swap it in as the production model. Just because a model has been registered and tagged in that way doesn't mean we need to turn it into the production model.*

*Registration makes the lifecycle claim of, "This model is identifiable and retrievable." It is not synonymous with "approved."*

*Validation makes the lifecycle claim of, "This model exists but has or has not passed promotion gates."*

*Promotion makes the lifecycle claim of, "This model passed the promotion gates and can now be labeled as the champion model."*

REGISTRATION
"This model exists, is identifiable, versioned, and retrievable."

VALIDATION
"This candidate has been evaluated against the promotion gates."

PROMOTION
"This validated candidate is now accepted as champion."

`validation_status=pending` means the registered candidate has entered the validation workflow, and the required gates have not yet all been resolved.

### Ideas to Retain

* An MLflow run records an execution; a registered model version gives the resulting model a lifecycle identity. 

* CV performance metrics describe evaluation evidence; fitting on the full development population creates the candidate artifact and does not create a new unbiased performance estimate.

* A model signature describes expected model input/output structure and completements application-level inference artifacts.

* Registration means "identifiable and retrievable," not "approve."

* `validation_status=pending` records that a model exists but has not yet passed promotion gates. 

* The candidate can be registered without changing what production/serving currently uses.

MLflow experiments organize related runs. A run records a particular execution and its parameters, metrics, artifacts, and logged models. A registered model is a named registry namespace, while a registered model version is a specific model artifact linked back to the run that produced it. We fit the frozen recipe on all development data to create the candidate artifact, but retain grouped-CV metrics as the evidence of generalization. Registration makes the candidate identifiable; validation determines whether it satisfies promotion gates; promotion changes its lifecycle role to champion.