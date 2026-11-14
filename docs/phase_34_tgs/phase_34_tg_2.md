## Phase 3.4 — Task Group 2 Active Recall

### Question 1
What is a delayed outcome label, how does a previously unlabeled production prediction become a labeled prediction event, and why does this allow RMSE or MAE to answer a question that PSI cannot?

**Best sections to review: 2A–2C — Delayed Labels, Labeled Events, and PSI vs. Performance**

*A delayed outcome label is a label that was not available at the time of prediction. A sequence of events occurs where a prediction is made, time passes, then the event that was predicted actually occurs and only then do we have a label.*

*As for how a previously unlabeled production prediction becomes a labeled prediction event, the event associated with our prediction needs to actually occur. Once an engine has used up all of its RUL we then have a situation where we can compare `y_pred` and `y_true`.*

*And finally, this allows RMSE or MSE to answer a question that PSI cannot by providing a measure of how accurate our predictions are. And from the accuracy of our predictions we can determine if any predictive degradation is occurring in our model.*

prediction made
-> truth unavailable
-> outcome occurs later
-> historical prediction can be labeled

PSI -> Did a distribution change? 

RMSE/MAE -> How wrong were the predictions? 

A delayed outcome label is ground truth that becomes available only after the prediction was made. Once the eventual outcome lets us reconstruct the true RUL at the original prediction cycle, we can pair `y_pred` with `y_true` to calculate RMSE or MAE. PSI can detect distribution change without labels, but it cannot directly measure prediction error. 

### Question 2
What is the difference between `label_quality_failure`, `insufficient_labels`, `performance_stable`, `performance_degraded`, and `eligible_to_retrain`, and why does `performance_degraded` not immediately authorize retraining?

**Best sections to review: 2E–2G — Performance Policy, States, and Investigation Checks; 2T — TG2 Exit State**

*`label_quality_faliure` is when we cannot trust `y_true`, in which case we do not move on to evaluating model performance.*

*`insufficient_labels` is when there are fewer than 30 trustworthy labeled predictions available, which means we cannot make performance classifications yet.*

*`performance_stable` means enough trustworthy labels exist and RMSE remains below our degradation threshold.*

*`performance_degraded` means enough trustworthy labels exist and RMSE has crossed above the 10% performance degradation threshold.*

*`eligible_to_retrain` is when we've make a series of quality checks to confirm there is enough evidence to justify retraining a challenger. The checks include verifying the identity of the serving model, verifying the feature pipeline, verifying the data quality, etc.*

*As for why `performance_degrdaded` does not immediately authorize retraining, after measuring a performance degradation we still need to conduct the series of checks mentioned directly above. Just because we've observed a degradation signal does not guarantee that it's real or that we should go thorugh the trouble of training a challenger.*

`label_quality_failure` -> `y_true` cannot be trusted

`insufficient_labels` -> trustworthy labels exist, but fewer than 30

`performance_stable` -> enough labels and RMSE below threshold

`performance_degraded` -> enough labels and RMSE reaches degradation threshold

`eligible_to_retrain` -> degradation + investigation checks support fitting a challenger

A measured RMSE increase could still originate from:
* bad labels
* bad input data 
* wrong served artifact 
* feature-pipeline problem
* unrepresentative sample

Metric degradation is evidence; investigation determines whether the model itself is the appropriate target of intervention.

### Question 3
Why must production outcome labels and performance-reference observations preserve the same target and observation semantics used by the model, and what kinds of false retraining decisions could result from bad labels or mismatched reference sampling?

**Best sections to review: 2B — Labeled Prediction Events, 2D — Compatible Performance Reference, 2Q — Label Quality Before Metric Quality**

*The production outcome lables and performance-reference observations must preserve the same target and observation semantics used by the model because it's not okay to invent a different target at monitoring time. For a true performance comparison to be measured, we need to match the same target semantics that were used during development. Otherwise we could risk having an apples to oranges comparison on our hands.*

*As for what kinds of false retraining decisions could result form bad labels or mismatched reference sampling, we could have a situation on our hands where we have a bad ground truth, which can make RMSE skyrocket or mask a performance degradation. We need to embody the idea that label quality must come before metric quality.*

We don't get to invent a different target at monitoring time.

Label quality must come before metric quality.

A corrupted `y_true` can either make a healthy model look terrible or conceal genuine degradation.

### Help Needed

* I still don't quite understand the concept of "match observations, not information." Could you please walk me through an example of how we're embodying that here? 

*The information needed to create one observation contains many rows. The entire history associated with an RUL prediction is the information, the observation is the RUL prediction that gets made off of that history.*

* What does the `cov` part of our pytest calls from the command line mean? 

*`cov` means coverage.*

*While running the tests, measure how much code inside the `predictive_maintenanc` package actually gets executed.*

* What does observation semantics mean? Is it the way we record observations in the form of tabular data? 

*Observation semantics means what one observation actually represents in the real-world/problem context and how that observation is produced. "Semantics" here means meaning.*

*Observation semantics describes what one data point represents, when it is created, and what information was allowed to contribute to it.*

### Ideas to Retain 

* Delayed labels convert historical predictions into direct performance evidence. 

* A performance reference should use observation semantics compatible with the production events being evaluated. 

* PSI needs no labels; RMSE and MAE require a trustworthy `y_true`. 

* Bad labels block performance conclusions because corrupted ground truth can falsely implicate the model.

* `performance_degraded` means invesigate; `eligible_to_retrain` means fitting a challenger is authorized. 

* Retraining eligibility still does not authorize promotion or deployment.

### More Ideas to Retain 

* Delayed labels turn predictions into directly measureable errors. 

* PSI means distribution change; RMSE/MAE measure prediction error. 

* A 10% greater relative RMSE increase is our project's operational degradation threshold.

* `performance_degraded` is evidence; `eligible_to_retrain` requires additional investigation checks.

* Target semantics and observation semantices must both match before performance comparisons are trustworthy.