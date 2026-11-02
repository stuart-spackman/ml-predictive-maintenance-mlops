## Phase 3.1 — Task Group 3 Active Recall

### Question 1
What is `sample_weight`, how is it different from X, y, and `groups`, and how does engine-balanced weighting change the training objective compared with giving every row equal weight?

**Best sections to review: 3A — Why Weighting Is Worth One Experiment, 3B — What `sample_weight` Actually Is, 3C — How Engine-Balanced Weighting Works, and 3D — This Changes the Training Objective**

*`sample_weight` is an item of metadata that controls how strongly observations influence the training process; it lets us tell the learning algorithm if some training observations should count more or less strongly when fitting.*

*As for how it is different from X, y, and `groups`, to being with, X contains the predictor values while y contains the target values. `groups` can be thought of as metadata that lets us distinguish which rows belong to which engines.*

*As for how engine-balanced weighting changes the training objective compared with giving every row equal weight, instead of giving each individual row equal weight, we change the a rows's weight to `1 / number of training rows for its associated engine`. Now, instead of each row exerting equal influence, each engine exerts equal influence on the training process. Before, it we had engine A with 100 rows while engine B had 200 rows, then engine B would have twice as much influence on the learning algorithm.*

X -> predictor values

y -> target values

groups -> metadata controlling which rows must stay together during splitting

sample_weight -> metadata controlling how stronly rows influence fitting

`groups` prevents observations from the same engine from being split across training and validation.

Saying each engine exerts exactly equal influence is a useful approximation, but the weightts guarantee equal total training weight, not necessarily identical influence on the fitted tree structure.

### Question 2
Why do we compare unweighted and engine-balanced training using one fixed Extra Trees recipe, the same 36 features, and the same grouped folds? Why might the unweighted TG3 RMSE differ from the 37.439 nested-CV result from TG2?

**Best sections to review: 3E–3G — Fixed Experimental Conditions and TG2 vs. TG3 Evidence, and 3N — Why We Don't Retune Again**

*We compared unweighted and engine-balanced training using one fixed Extra Trees recipe, the same 36 features, and the same grouped folds because otherwise we would be confounding our variables. Right now out hypothesis is that engine-balanced training might improve predictive performance, and we should not change any additional variables as we go about confirming or disconfirming that hypothesis.*

*As for why the unweighted TG3 RMSE might differ from the 37.439 nested-CV result from TG2, that figure was a measure of fold-specific performance from the nested tuning procedure. Here we're taking the hyperparameter configuration that appeared most frequently in `reports/phase_31_tg2_nested_fold_results.csv` and freezing it for our current experiment.*

Controlled experiment logic: 
keep fixed: model recipe, features, folds, metric
change only: weighting policy

If the result changes, weighting is the main deliberate experimental difference. 

TG2 RMSE ~= 37.439
-> performance of a tuning procedure
-> each outer fold may choose different hyperparameters

TG3 unweighted RMSE ~= 37.473
-> performance of one fixed modal Extra Trees recipe
-> same recipe used across all folds

### Question 3
What is the difference between pooled OOF RMSE and mean per-engine RMSE, why does pooled RMSE remain the primary metric even if weighting improves the per-engine diagnostic, and how should we respond if weighting provides little or no primary-metric improvement?

**Best sections to review: 3J–3L — Result Interpretation and Mean-Engine RMSE, and 3O–3Q — Scope Control and Completion Standard**

*Pooled OOF RMSE is a metric that gives every row equal evaluation influence.*

*Mean per engine RMSE is a metric that calculates the average RMSE value per engine, to where each engine contributes one value to the diagnostic.*

*Pooled RMSE remains the primary metric even if weighting improves the per engine diagnostic because our Phase 3.1 contract declared ordinary pooled OOF RMSE as the primary metric. We do not want to change the evaluation metric just because we changed the fitting objective.*

*As for how we should repond if weighting provides little or not primary metric improvement, we should defer to the parsimony principle and keep the previously existing model as the challenger.*

pooled OOF RMSE
-> every held-out row contributes to one global RMSE

mean per-engine RMSE
-> calculate RMSE separately per engine
-> average those engine-level RMSE values

We don't change the primary metric after seeing that a secondary diagnostic looks better.

We keep the unweighted fixed Extra Trees recipe as the challenger.

### Ideas to Retain

* `groups` controls split membership; `sample_weight` controls fit influence. 

* Equal total engine weight is not the same thing as adding engine identity as a feature. 

* TG2 evaluated a tuning procedure; TG3 evaluated one fixed recipe. 

* Supporting diagnostics can reveal tradeoffs without replacing the locked primary metric. 

* When an added training complication does not improve the primary metric, prefer the simpler recipe.