## Phase 3.3 — Task Group 2 Active Recall

### Question 1
Why do we build the reference population by simulating latest-cycle prediction events from full engine-history prefixes instead of simply using every eligible training row, and how does this implement the principle of “match observations, not information”?

**Best sections to review: 2A–2C — Reference Population, Sampling Policy, and Historical Data**

*We build the reference population by simulating latest cycle prediction events from full engine history prefixes instead of simply using evey eligible training row because we do not want to compare all eligible training rows to production prediction events. This is because those populations were sampled differently. We instead want to create a situation where if the application had received an engine's full history through a particular cycle, we ask what 36 features and RUL prediction would the currently served system have produced? And we do this by creating a prediction event once every 10 cycles.*

*As for how this implements the principle of "match observations, not information," we are not treating this situation like another model evaluation. Instead of investigating how good the model is, we're investigating the expected behavior of the population that established the parameters of the model. We're also ensuring a deterministic sampling policy, i.e., making sure future information associated with an observation does not leak into the simulations.*

every eligible historical cycle != one production prediction event at a requested cycle

The unit and sampling process used in the reference population should resemble the unit and sampling process that produces real monitoring observations.

The full cycles 1-N may be necessary information to construct a prediction at cycle N, but the resulting cycle-N prediction is still one monitoring observation. 

We construct the reference set from historical engine prefixes because production telemetry consists of latest-cycle prediction events, not arbitrary training rows. Matching those observation semantics prevents apparent drift from being caused merely by different lifecycle sampling. Each reference event uses only information available through that cycle, preserving temporal causality.

### Question 2
What does PSI measure, why must its bin boundaries be created from the reference population and then frozen, and what do our `stable`, `warning`, and `alert` thresholds actually mean?

**Best sections to review: 2D–2F — PSI, Frozen Reference Bins, and Thresholds; 2Q — PSI Is Not a Hypothesis Test**

*PSI measures how much the distribution across a set of fixed bins changed between the reference population and the current population.*

*As for why its bin boundaries must be created from the reference population and then frozen, we don't want to allow new incoming data to affect the bins. Otherwise the bins themselves could move with the drifting data and partially hide*

*Our `stable` threshold means PSI < 0.01. The closer to 0 PSI is, the more similar the distributions look.*

*Our `warning` threshold means 0.10 <= PSI < 0.25. This could be described as a medium-intensity distribution difference.*

*Our `alert` threshold means PSI >= 0.25. This indicates a significant distribution difference.*

PSI measures how much the current distribution across a set of fixed bins changed between the reference population and the current population.

reference data -> establish a measuring stick

current data -> measured against that same stick

If current data were allows to redefine its own bins, the measuring instrument would move along with what we're trying to measure.

PSI < 0.10 -> stable

0.10 <= PSI < 0.25 -> warning

PSI >= 0.25 -> alert

### Question 3
Why do we separately monitor PSI for the 36 model-input features and for `predicted_rul`, why can neither prove that RMSE worsened, and why might deploying a different model require rebuilding at least part of the monitoring baseline?

**Best sections to review: 2G — What We Monitor, 2P — Model Changes and Baselines, and Phase 3.3 TG0 drift semantics**

*We keep PSI for the 36 model-intput features and PSI for `predicted_rul` separate because these components of the application provide answers to different questions. Feature PSI let's us answer the question of, "Has `P(X)` changed?" Prdiction PSI let's us answer the question of, "Has `P(y_pred)` changed?" One let's us gauge change in the input distribution and one let's us gauge change in the output distribution.*

*As for why neither can prove that RMSE worsened, in order to calculate RMSE we need `y_actual`. The two quantities above are intertwined with `y_pred`, but do not provide the actual ground-truth labels associated with the input data. To calculate changes in RMSE, we need to obtain the actual RUL and retroactively compare it to what we predicted.*

*Finally, deploying a different model might require rebuilding at least part of the monitoring baseline because a model change invalidates part of the baseline. Our model-ready feature distribution is unaffected by a change to the models we're using. But! Changing our model creates a situation where our `y_pred` distribution from the first model will not be identical to the `y_pred` distribution from the second model. So we likely need to rebuild a new `y_pred` model.*

Feature PSI -> change in P(X)

Prediction PSI -> change in P(y_pred)

RMSE requires y_pred and y_actual.

same feature pipeline + new estimator
-> existing X baseline may remain meanigful
-> prediction baseline should be reconsidered and/or rebuilt

new feature pipeline or schema
-> X baseline must also be rebuilt

### Ideas to Retain

* A monitoring baseline should match production observation semantics, not merely reuse whatever rows happened to exist during training. 

* Reference bins are learned from the reference population once and then frozen; current data does not get to redefine the measuring stick. 

* Feature PSI changes in `P(X)` and prediction PSI measures changes in `P(y_pred)`; neither proves accuracy degradation. 

* Monitoring thresholds should be specified before looking at the drift scenario being evaluated.

* A prediction distribution baseline is model-dependent, so changing the actually served model can require a new monitoring baseline. 

### More Ideas to Retain 

* "Match observations, not information" means the reference and production populations should contain comparable observation units produced by comparable sampling processes.

* Temporal causality is a separate requirement: a simulated cycle-t event may use information only up through cycle t.

* PSI uses a fixed measuring stick: reference bins are created once and frozen. 

* Our PSI categories are operational thresholds, not statistical significance statements. 

* Feature PSI monitors `P(X)`; prediction PSI measures `P(y_pred)`; performance metrics require actual `y`.

* Changing the model can invalidate the prediction distribution baseline even when the feature distrubtion baseline remains valid.