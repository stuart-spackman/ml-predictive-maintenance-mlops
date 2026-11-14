## Phase 3.4 — Task Group 3 Active Recall

### Question 1
Why does `eligible_to_retrain` authorize only the creation of a new challenger, and why should the incumbent artifact remain immutable throughout retraining, evaluation, and promotion?

*`eligible_to_retrain` authorizes only the creation of a new challenger because there is a series of governance checks that need to take place after training and before the decision is made to replace the incumbent. Successfully completing the training process for a new model does not imply anything about the new model's accuracy or production compatibility.*

*As for why the incumbent artifact should remain immutable throughout retraining, evaluation, and promotion, we do not want to deal with the consequences of overwriting the `.joblib` file associated with the incumbent model. Doing so would destroy several important parts of the production process such as rollback target, artifact identity, historical provenance, comparison boundary, and auditability. Challenger and incumbent should both contiue to exist independently of each other.*

Successful training does not establish either predictive superiority or production compatibility.

incumbent artifact -> preserve

challenger artifact -> create separately

promotion -> Should the challenger become approved/champion? 

deployment -> Should serving actually cut over? 

`eligible_to_retrain` permits fitting a separate challenger. The challenger must still pass predictive evaluation, compatibility, software, and provenance gates before promotion, and deployment remains a further separate decision. The incumbent stays immutable so it remains an identifiable comparison and rollback target.

**Best sections to review: 3A–3E — Retraining Handoff, Incumbent Preservation, and Evaluation Boundaries; 3O — Rollback**

### Question 2
Why does this portfolio project deliberately return `workflow_validated_but_real_fit_blocked` instead of actually fitting and claiming a production-retrained model, and what additional evidence would have to exist before a genuine retraining event could occur?

**Best sections to review: 3B — Why We Do Not Fake Retraining, 3I–3N — Project-Reality Boundary and Future Real Production Case**

*This portfolio project deliberately returns `workflow_validated_but_real_fit_blocked` instead of actually fitting and claiming a production-retrained model because we don't currently have new/real representative labeled production data. We do not currently have a way of truthfully stating that we retrained a model because predictive accuracy in production degraded. We instead need to embody the principle that we validate machinery with controlled scenarios without claiming those scenarios happened in production. `workflow_validated_but_real_fit_blocked` let's us distinguish simulation evidence from actual production evidence.*

*As for what additional evidence would have to exist before a genuine retraining event could occur, we would need to obtain actual production evidence of degradation and then use real labeled production data to train a new model.*

Validate machinery with controlled scenarios without claiming those scenarios happend in production.

Retraining can be justified by: 
* confirmed predictive degradation
* presistent legitimate new operating regime + representative labeled data
* validated correction to training data/target construction

Real production degradation is not universally required. 

A genuine retraining event requires real evidence that justifies updating the learned mapping and suitable trustworthy data from which to train the challenger. 

### Question 3
If a future challenger is promoted and deployed, how should rollback and monitoring-reference management work, and why are registry promotion, deployment cutover, and the actually served model still separate concepts?

**Best sections to review: 3O–3Q — Rollback, Monitoring References, and Registry vs. Deployment**

*If a future challenger is promoted and deployed, rollback and monitoring reference management should work, we need to embody the principle that rollback isn't something you invent after deployment goes wrong. Before deployment can happend, we need to preserve the previous known-good artifact, the previous model identity, the previous feature contract, and the previous deployment configuration. As for monitoring reference management, input reference monitoring might remain applicable, but output reference monitoring will need to be rebuilt due to the model change.*

*As for why registry promotion, deployment cutover, and the actually served model are all still separate concepts, registry promotion still does not mean deployment. We still need to account for the fact that the champion alias does not necessarily point to the actual artifact used in serving by FastAPI. The current API still has its own actual serving-loader boundary that we need to account for.*

Before cutover: 
* preserve known-good artifact
* preserve model identity
* preserve feature contract
* preserve deployment configuration

Only if the estimator changes and the exact feature pipline, feature schema, and observation semantics remain in place: 
* `P(X)` baseline -> may remain usable
* `P(ŷ)` baseline -> should be rebuilt/versioned

registry promotion != deployment
deployment intent != proof of actual serving
actual served artifact -> determined at the serving boundary

### Ideas to Retain 

* Retraining authorization is permission to fit a challenger, not permission to replace the incumbent.

* A real retraining claim requires real new evidence; workflow simulation should be clearly labeled as simulation. 

* Incumbent artifacts should remain immutable so comparison, provenance, and rollback remain possible. 

* A challenger trained on newer data still has to pass the same evaluation and production gates as any other candidate. 

* Rollback capability is created by preserving the prior known-good state before deployment occurs. 

* After a model deployment, monitoring references must be reconsidered becuase prediction distributions are model-dependent. 

### More Ideas to Retain

* A retrained model is born as a challenger, not as a replacement. 

* Preserving the incumbent makes rollback, comparison, provenance, and auditability possible.

* Workflow simulation can prove machinery works without pretending a real production event occurred. 

* Real retraining requires real evidence supporting a change to the learned mapping plus suitable trustworthy training data; confirmed degradation is one important path, not the only one.

* Changing only the estimator primarily invalidates the prediction-distribution baseline; changing the feature pipeline can invalidate both input and prediction baselines. 

* Registry state, deployment state, and actual runtime serving identity are three separate facts. 