## Phase 3.1 — Task Group 5 Active Recall

### Question 1
What does it mean to “freeze” the Extra Trees challenger at the end of Phase 3.1, what exact parts of its recipe are being frozen, and why would continuing to change its hyperparameters, features, or weighting during Phase 3.2 undermine the meaning of the promotion evaluation?

**Best sections to review: 5B — Challenger vs. Incumbent, 5C — What Does “Freeze the Challenger” Mean?, and 5A — What Phase 3.1 Actually Established**

*"Freezing" the Extra Trees challenger at the end of Phase 3.1 means we distinctly stop changing the recipe while we evaluate whether this exact candidate deserves promotion. It does not mean fit it once and declare it production ready.*

*The exact parts of its recipe that are being frozen are:*
* model family
* hyperparameters
* feature schema
* training policy
* evaluation evidence
* provenance
* known limitations

*Continuing to change its hyperparameters, features, or weighting during Phase 3.2 would undermine the meaning of the promotion evaluation because that would create a situation where we would no longer be evaluating the same challenger.*

Stop changing the candidate while determining whether that exact candidate deserves a promotion.

Frozen recipe: 
* model family
* hyperparameters
* featuer feature contract
* training policy

phase 3.1 handoff = frozen challenger recipe + frozen/recorded evidence package

### Question 2
Why is the fixed TG3 Extra Trees RMSE of roughly 37.473 the more appropriate reference metric for the challenger handoff than the roughly 37.439 TG2 result? What different claim does each number support?

**Best sections to review: 5A — What Phase 3.1 Actually Established and 5E — Why We Use the TG3 Fixed Recipe Score**

*The fixed TG3 Extra Trees RMSE of roughly 37.473 the more appropriate reference metric for the challenger handoff than the roughly 37.439 TG2 result because the first RMSE gives reference evidence for the actual candidate recipe. We need to match the type of RMSE that was stated in our comparison contract.*

*The TG3 Extra Trees RMSE supports the claim that we should keep the unweighted recipe.*

*The TG2 result supports the claim that the nested tuning procedure slightly beat the incumbent.*

TG2 RMSE
-> performance of the nested tuning procedure
-> outer folds could select different recipes

TG3
-> performance of one specific Extra Trees recipe
-> the recipe we're acutally handing to Phase 3.2

TG2's 37.439 estimates the performance of a nested tuning procedure, whereas TG3'2 37.473 estimates the grouped-CV performance of the specific fixed recipe being handed forward. Because Phase 3.2 evaluates a concrete challenger, the fixed-recipe score is an appropriate reference.

### Question 3
What is the difference between model selection and model promotion, and why does a lower grouped-CV RMSE not by itself authorize replacing the served Random Forest? What additional concerns will Phase 3.2 need to evaluate?

**Best sections to review: 5H — What Phase 3.1 Is NOT Claiming, 5I — Why We Don't Fit a Challenger `.joblib` Yet, and 5J — Promotion Is More Than “Lowest RMSE Wins”**

*Model selection is what Phase 3.1 is primarily handling, it entails conducting experiments and deciding which model should be chosen to move on to the final round of deciding if we have sufficient information on it beating the incumbent. Model promotion is the process of swapping out the incumbent with the new model if it was beat in the comparison and it is determined to be deployable.*

*As for why a lower grouped CV RMSE does not by itself authorize replacing the served Random Forest, there are many aspects of a model aside from RMSE that factor in to deciding to promote a model. Having an impressively high RMSE alone does nothing to indicate if the model can be reliably reproduced, if it requires unavailable features, if it breaks inference, or if it fails tests.*

*Phase 3.2 will need to evaluate the additional concerns associated with creating a production candidate artifact and fit a challenger `.joblib`. We'll need to establish a model version, then an evaluation record, then a registry state, and then make a promotion decision.*

MODEL SELECTION -> Which experimental candidate warrants further consideration? 

MODEL PROMOTION -> Should this exact candidate actually replace the incumbent? 

Operational examples: 
* Can it be reproduced? 
* Does it use available/compatible features? 
* Does it work through inference? 
* Does it pass tests? 
* Can we create and identify the artifact? 
* Does is satisfy promotion governance? 

Fitting the artifact is only one step in a larger governed process: 
Frozen challenger recipe
-> fit identifiable candidate artifact
-> version it
-> record evaluation evidence
-> validate serving compatibility and/or tests
-> register lifecycle state
-> apply promotion criteria
-> PROMOTE or REJECT

### Ideas to Retain

* A challenger is an experimentally supported candidate; an incumbent is the currently accepted model. 

* Freezing a challenger means fixing its recipe so subsequent evaluation refers to one identifiable candidate. 

* The best score from a tuning procedure and the score of a fixed model recipe answer different questions. 

* Model selection asks which candidate looks better; model promotion asks whether that candiate is sufficiently validated and operationally suitable to replace the incumbent. 

* A modest improvement can justify promotion evaluation without automatically justifying promotion.

### Ideas to Retain

* A model recipe consists of what determines how the model is built and trained; evidence, provenance, and limitations accompany the model in the handoff. 

* TG2 evaluated a tuning procedure; TG3 evaluated the particular recipe Phase 3.2 can govern. 

* Selection identifies a challenger. Promotion determines whether that challenger is worthy and operationally safe enough to become the incumbent. 

* Lower RMSE is better, but lower RMSE alone is not a deployment authorization. 

* Promotion should operate on a fixed, identifiable candidate. Otherwise the object being evaluated keeps moving.