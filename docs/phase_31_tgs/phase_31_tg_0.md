## Phase 3.1 — Task Group 0 Active Recall

### Question 1
What is the difference among a baseline, an incumbent, a challenger, an incumbent fitted artifact, and an incumbent recipe? Why must the incumbent recipe be refit inside the same experimental training boundaries as a challenger when we perform a fair grouped-CV comparison?

**Best sections to review: 0A — Incumbent vs. Challenger, 0B — Baseline vs. Incumbent, 0C — The Fitted Incumbent vs. the Incumbent Recipe, and 0D — Why We Refit the Incumbent During Comparisons**

*A baseline is a benchmark used during model development. Examples from earlier in the project include the cycle only predictor, the raw feature model, and the simple temporal model.*

*In incumbent is the model currently recognized as the active model of the system and has a stronger lifecycle meaning.*

*A challenger is a model that is trying to outperform the incumbent. An example could be an XGBoost model that competes against our current RandomForestRegressor.*

*An incumbent fitted artifact is the current already-trained model used by the service. In our project this takes the form of `phase_16_final_fitted_model.joblib`.*

*An incumbent recipe is the collection of instructions for constructing and fitting the incumbent in the context of an experiment. For fair experimental comparisons, we need the incumbent's recipe (i.e., model family, hyperparameters, feature recipe, etc.) and then we take that and reproduce it inside each appropriate training fold.*

*As for why the incumbent recipe must be refit inside the same experimental training boundaries as a challenger when we perform a fair grouped-CV comparison, the principle at play here is that we do not want to simply compare a performance number from an old experiment to a performance number from today's experiment. There can be differences in folds, rows, preprocessing, or evaluation population that can trick us into thinking a model improvement has occurred. To develop a proper comparison, different models must be fitted and evaluated on the same folds of the cross-validation process in parallel with each other.*

Different models must be fitted and evaluated on the same folds of the cross-validation process in parallel with each other. The goal is to obtain a matched comparison.

fitted incumbent artifact -> learned state currently used by serving

incumbent recipe -> reproducible instructions for fitting that type of model

### Question 2
Which experimental properties remain fixed by default in Phase 3.1, which dimensions are allowed to change deliberately, and why does changing model family, feature representation, weighting, folds, and evaluation metric all at once make interpretation weaker?

**Best sections to review: 0E — What Must Stay Fixed, 0F — What May Change, 0G — Controlled Experiments Still Matter, and 0S — Experiment Identity**

*In Phase 3.1, the experimental properties that remain fixed by default are the dataset (NASA C-MAPSS), our grouping unit (unit_no / engine), target semantics (remaining useful life), temporal causality (no future information at a cycle t), minimum useable history (existing temporal history contract), evaluation grouping (engines stay grouped), primary comparison metric (RMSE), and our inference meaning (raw observed engine history is given as input, estimated RUL is given as output).*

*The dimensions that are allowed to change deliberately are model family, hyperparameters, feature representation, feature subset, sample weighting, training objective, and regularization.*

*As for why changing model family, feature representation, weighting, folds, and evaluation metrics all at once makes interpretation weaker, not only do we need to know which variables changed during our experiments, but ideally we would only change one at a time. If we change multiple variables and something goes right or wrong, then we will have limited ability to know which of the variables positively or negatively contributed the change.*

fixed by default -> problem definition and evaluation rules

allowed to vary deliberately -> experimental dimensions

Changing multiple variables is not automatically a bad experiment. 

### Question 3
Why must engine grouping and temporal causality remain non-negotiable during advanced experimentation, why should the already-revealed official FD001 test set not be used to select challengers, and why can repeated hyperparameter selection make an evaluation score optimistic?

**Best sections to review: 0H — Our Development Population, 0I — Grouping Remains Non-Negotiable, 0J — Hyperparameter Tuning Creates Another Boundary, and 0K — Primary Metric vs. Supporting Diagnostics**

*Engine grouping and temporal causality remain non-negotiable during advanced experimentation because, in the case of engine grouping, observations from one engine across cycles are correlated. If we took some rows from a single engine and used them for training and the remaining rows and used them for validation, that would create leakage. Similarly, if we let our training process have access to future information at a cycle t, then that would create another form of leakage.*

*The already-revealed official FD001 test set should not be used to select challengers because we still do not want to turn the test set into development data even though it's no longer pristine. We need to think of the official test result as historical context and not turn it into an optimization target. The best sequence of events will be taking the FD001 development/training engines, carrying out a grouped experimental procedure, and then choosing a challenger based on those results.*

*Repeated hyperparameter selection makes an evaluation score optimistic because the more decisions we make using an evaluation set, the less indepdendent that evaluation becomes. When trying lots of different hyperparameter combinations, the winning CV score is partly optimistic because we deliberately chose the configuration that happened to perform best on those evaluations, i.e., we made the evaluation process highly specialized, which runs the risk of creating a high variance model.*

The more decisions we make using an evaluation set, the less independent that evaluation becomes. 

Some configurations will look unusually good partly because of random variation in the evaluation procedure. Since we deliberately select the best observed result, we preferentially choose one that may have benefitted from favorable evaluation noise.

Repeatedly using the same evaluation evidence to choose among many configurations can overfit the model development process to that evaluation procedure, making the winning score optimistically based.

### Question 4
Why does Phase 3.1 deliberately stop at generating challengers and comparative evidence rather than immediately replacing the served model? Explain the difference between "numerically better" and "meaningfully better," and describe the experiment → evidence → interpretation → next-experiment loop we will use.

**Best sections to review: 0L — Statistical Improvement vs. Useful Improvement, 0M — No Promotion in Phase 3.1, 0N — Why That Separation Matters, 0T–0V — Challenger Standard, Anti-Patterns, and Scientific Loop**

*Phase 3.1 deliberately stops at generating challengers and comparative evidence rather than immediately replacing the served model because...*

*Numerically better means that one model posted an improved performance metric over another model. Here we have a term that doesn't offer any information about whether the model would be worth replacing the incumbent, i.e., if a model was slightly better numerically but significantly more complex, replacing the incumbent would be a bad idea.*

*Meaningfully better means that at a holistic level the model has aspects that warrant further consideration, e.g., magnitude of improvement, fold consistency, complexity, etc.*

*As for the [experiment -> evidence -> interpretation -> next experiment] loop that we will use, first we ask if changing a variable (or variables) could change the incumbent. Then we carry out a controlled experiment where the same evaluation conditions are paired with a deliberately changed variable. Then we collect evidence, i.e., OOF predictions, metrics, fold behavior, and metadata. Then we ask what hypotheses the resuls support or reject. Then it's time to carry out another experiment.*

Experimentation and promotion are intentionally separate decisions. Phase 3.1 asks whether we can produce a credible challenger; Phase 3.2 asks whether the accumulated evidence is strong enough to justify replacing the incumbent.

What claims does the evidence support, weaken, or leave unresolved? 

### Help Needed 

* What's the definition of semantics in this context? 

*In this context, semantics means meaning. Semantics describes what a value, field, target, feature, or operation is intended to represent—not merely its syntax or storage format.*

### Ideas to Retain

* artifact = learned state; recipe = instructions for producing learned state

* Changing several experimental dimensions at once weakens attribution, even if the overall recipe comparison is still valid.

* Hyperparameter-search optimism is primarily about overfitting the selection process to evaluation evidence, not necessarily about creating a high-variange estimator.

* Phase 3.1 creates challengers; Phase 3.2 decides whether any challenger deserves promotion.

* Semantics means the intended meaning of data or behavior; syntax means its form or representation.