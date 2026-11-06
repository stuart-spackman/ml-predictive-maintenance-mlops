## Phase 3.3 — Task Group 0 Active Recall

### Question 1
What is the difference between service health, prediction/model health, and data drift, and why would detecting a shift in model-input features or RUL predictions not by itself prove that the model's RMSE has worsened?

**Best sections to review: 0A — Monitoring Targets, 0D–0E — Drift Concepts and Claim Boundaries**

*Service health is the extent to which the application is functioning. This the first layer of monitoring for this project.*

*Prediction model health is the extent to which the deployed model is producting plausible, valid predictions. This is the second layer of monitoring for this project.*

*Data drift is is the extent to which the population reaching the model has changed relative to the reference population. Zero data drift is most desirable.*

*As for why detecting a shift in model input feature or RUL predictions not by itself prove that the model's RMSE has worsened, there are at least 4 different kinds of drift. Shifts in model input features or RUL predictions are one of multiple more ways in which RMSE can worsen. The principle at play here is that we need to be acknowledging of the core monitoring rule, which states that unlabeled drift signals can tell us that the production population changed. They cannot by themselves tell us that predictive accuracy deteriorated. We need labels and/or outcomes to truthfully state that the model has become less accurate. Drift detected does not imply model failure.*

Service health -> Is the application functioning? 

Prediction/model health -> Are predictions valid and plausible? 

Data drift -> Has the population reaching the model changed? 

The goal is to detect material drift, understand it, and determine whether it matters. 

Service health monitors whether the application is operating correctly, prediction health monitors whether outputs remain valid and plausible, and data drift monitors changes in the input population. Input or prediction drift can be detected without labels, but neither proves that RMSE has worsened; direct performance degradation requires comparison against observed outcomes. 

### Question 2
Why must each telemetry event record the identity of the model that actually produced the prediction instead of simply recording that the model was `champion`, especially given the current relationship between the MLflow registry and the FastAPI serving path?

**Best sections to review: 0B — Registry Champion vs. Served Model, 0H — Prediction Telemetry**

*Instead of simply recording that the model was `champion`, each telemetry event needs to record the identity of the model that actually produced the prediction because the registry champion is not guaranteed to be the actually served model. There is the possiblity of situations where the telemetry record has "model = `champion`", to where it's pointing at Extra Trees. But the running API is still serving Random Forest. To ensure our monitoring data doesn't wind up lying, we need to implement a rule that every prediction event must record the identity of the model that actually produced that prediction. We can never infer runtime model identity solely from the current registry alias.*

registry champion != necessarily the model that produced this prediction

Telemetry says: model = champion
Current alias: champion -> Extra Trees 
But actual serving API: Random Forest

Historical telemetry must record immutable runtime identity, not a mutable role name.

### Question 3
Why is one latest-cycle inference event the correct monitoring observation for this application, and why could comparing those production events blindly against every eligible training row create a misleading drift signal?

**Best sections to review: 0F–0G — Monitoring Observation and Reference Population, 0K — Reference vs. Current Window**

*The correct monitoring observation for this application is one latest cycle inference event (i.e., the RUL prediction at the latest cycle that was supplied) because we want to embody the priciple of matching observations, not information. We should compare production prediction events with a reference population constructed using equivalent observation semantics.*

*As for why comparing those production events blindly against every eligible training row could create a misleading drift signal, we have a situation where our model training population contains many eligible cycle-level rows, but the actual API telemetry represents whatever latest cycle existed when someone requested a prediction.*

We want to embody the principle of matching observations, not information.

Training/reference candidate: many eligible cycle-level rows
Production telemetry: one event at whatever latest cycle was present when prediction was requested

There are situations where sampling drift can be caused by mismatched observation semantics rather than necessarily true observational drift. 

One monitoring observation corresponds to one latest-cycle prediction event because that is the unit the application actually emits. Comparing those events against every eligible historical training row would mix different sampling processes, so apparent drift could arise from lifecycle position differences rather than a genuine change in the population.

### Help Needed

* In regards to Question 3, predicting RUL requires the full engine history, right? We can't just take cycle 57 and map that to an RUL, we need all the cycles that came before it. Am I understanding that correctly? And because the full history in accordance with the latest cycle reported is what we take in, our observation event becomes the RUL predicted for that full history.

* What are outcome labels and how exactly are they used for direct performance monitoring? 

### Ideas to Retain

* Monitoring begins by defining what one observation means and what claims each signal can support.

* The actual served model identity must be recorded at prediction time; a mutable registry alias is not sufficient evidence of what produced a historical prediction.

* Data drift means `P(X)` changed; prediction drift means `P(y_pred)` changed; neither alone proves predictive performance worsened. 

* Direct performance monitoring generally requires outcome labels. 

* Monitoring should observed the model-ready features produced by the existing inference pipeline rather than recreate feature engineering elsewhere. 

* Drift is an investigation signal, not automatically a retraining command.

### More Ideas to Retain

* Drift is change, not automatically degradation. 

* `P(X)` changing and `P(y_pred)` changing are observable without labels; performance degradation requires truth. 

* Historical telemetry should identify the actual serving artifact/model, not a mutable alias. 

* Match production observations to a reference population with equaivalent observation semantics. 

* The history required to create a prediction is not the same thing as the unit of monitoring.