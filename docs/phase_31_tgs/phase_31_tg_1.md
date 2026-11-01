## Phase 3.1 — Task Group 1 Active Recall

### Question 1
What are the conceptual differences among Random Forest, Extra Trees, and Histogram Gradient Boosting, and why are Extra Trees and Histogram Gradient Boosting useful challengers for this project without adding a new external ML dependency?

**Best sections to review: 1A — Why These Two Challengers?, 1B — Why We're Not Adding XGBoost Right Now, and 1C — TG1 Is Screening, Not Tuning**

*RandomForest could be described as a bagged tree ensemble. It gets built from taking many randomized trees, fitting them independently, and averaging the predictions. There is randomized data/features and the learning algorithm searches for good split thresholds.*

*ExtraTrees is closedly related to Random Forest but injects more randomness into how tree splits are chosen. The extra randomization can reduce variance, but it might come at the cost of increased bias.*

*Histogram Gradient Boosting does not build lots of mostly independent trees and averages them. It instead creates a sequence of trees where each one improves upon the one that came before it, i.e., boosting.*

*As for why Histogram Gradient Boosting and Extra Trees are useful challengers for this project wihtout adding a new external ML dependency, in the case of Extra Trees it lets us ask whether a somewhat different tree-ensemble strategy improves performance without radically changing the rest of the problem. In the case of Histogram Gradient Boosting, it lets us use a learning algorithm where each stages focuses on correcting errors left by the ensemble so far. The goal here is simply to ask if this model family shows enough promise to deserve more attention. We don't want to go too deep on training a highly specific type of model without getting a preview of what the results will look like.*

With histogram gradient boosting, each stage is fitted to improve the ensemble as a whole.
current ensemble -> remaining error structure -> new boosting stage -> updated ensemble

### Question 2
Why do all three model families use the same locked feature matrix, engine-grouped folds, eligible rows, and primary metric in TG1? What does `sklearn.base.clone()` do, and why do we clone and refit the incumbent rather than use its already-fitted predictions?

**Best sections to review: 1D — Keep the 36-Feature Representation Fixed, 1E — Check the Incumbent Fit Policy, 1F — A Useful New Tool: `clone()`, and 1H — What This Script Is Doing**

*All three models use the same locked feature matrix, engine-grouped folds, eligible rows, and primary metric because we don't want to change too many variables at once. In this task group we're changing the model family, and as many variables as possible outside of that should remain fixed.*

*As for what `sklearn.base.clone()` does, it copies the configuration of a model without copying its fitted state. This enables us to recover the incumbent recipe rather than reusing the already-fitted artifact. We clone the model rather than use its already-fitted predictions because it allows us to train each of the models on the same folds (which are generated just once), enabling a matched comparison instead of just comparing final metric number without knowing if fold splits played a role in getting a particular performance.*

We want the model family to be the primary experimental change. 

clone(fitted_estimator)
-> same estimator configuration
-> no learned fitted state

Matched folds prevents us from mistaking fold differenes for model differences.

### Question 3
What is an out-of-fold prediction, what is the difference between pooled OOF RMSE and fold-to-fold RMSE variability, and why does a challenger with the lowest TG1 RMSE become a candidate for further experimentation rather than automatically becoming the new served model?

**Best sections to review: 1I–1J — OOF Predictions and RMSE Evidence, 1M — How to Decide What Advances to TG2, and 1O — We Are Not Saving a New `.joblib` Yet**

*An out-of-fold prediction is when an engine's RUL is predicted as a result of that engine getting its turn at not being in the training data (each engine is placed in the validation set instead of the training set once out of the 5 folds).*

*Pooled OOF RMSE is when we combine every OOF prediction and calculated a single RMSE value. Fold-to-fold RMSE is when we take each of the calculated RMSE associated with a single fold and then average those values. Fold-to-fold RMSE variability is the result of calculating the standard deviation of folds. It lets us ask if the model is reasonably consistent across different held-out engine groups.*

*As for why a challenger with the lowest TG1 RMSE becomes a candidate for further experimentation rather than automatically becoming the new served model, having the lowest RMSE only allows us to state that the model is numerically better than the incumbent. There's a lot more than RMSE measurement that factors into declaring the challenger better than the incumbent, e.g., complexity also needs to be evaluated as a trade-off.*

Each engine gets evaluated when it belongs to a held-out fold rather than the training portion.

pooled OOF RMSE
-> one RMSe over all combined held-out predictions

fold RMSE variability
-> how much fold performance changes across held-out engine groups

Mean fold RMSE and fold-to-fold RMSE variability are different quantities.

mean fold RMSE
-> average of the five fold RMSE values

fold RMSE variability
-> usually standard deviation of those five values

No challenger beat the incumbest in TG1. Extra Trees advances only because it was the strongest challenger and is close nough to justify a small tuning experiment.

### Ideas to Retain

* Bagging aggregates many mostly independent trees; boosting sequentially improves the current ensemble. 

* `clone()` preserves configuration, not learned state.

* Fair comparisons required matched rows, features, groups, folds, and metric.

* Pooled OOF RMSE measures aggregate held-out performance; fold standard deviation measures consistency across folds. 

* The strongest challenger can advance even if it has not yet beated the incumbent, because TG1 is screening and TG2 is limited tuning.

* The actual TG1 winnier was still the incumbent Random Forest. 