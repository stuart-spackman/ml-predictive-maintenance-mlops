## Phase 3.2 — Task Group 0 Active Recall

### Question 1
What is a model-promotion contract, why should its decision rules be established before we fit/register the Phase 3.2 candidate artifact, and what five broad gates must our Extra Trees challenger pass before promotion?

**Best sections to review: 0B — What Is a Promotion Contract?, 0D — The Five Promotion Gates, and 0M — Why Not Start MLflow Immediately?**

*A model promotion contract is documentation of the conditions that must be true before a challenger can replace the incumbent. We need to create a situation where we define the decision rules, and then evaluate the candidate against them.*

*As for why the model promotion contract's decision rules should be established before we fit and/or register the Phase 3.2 candidate artifact because we want to avoid situations where we fit a challenger, become excited about the result, and then invent criteria that justify promoting it. This can be avoided by creating a model promotion contract ahead of time.*

*The five broad gates that our Extra Trees challenger must pass before promotion are:*
* Candidate identity - the model being evaluated must exactly match the Phase 3.1 handoff
* Predictive performance - the frozen challenger must have better reference grouped-CV primary performance than the incumbent
* Artifact and feature compatibility - the fitted candidate must load successfully, predict successfully, expect exactly 36 model features, use the locked feature names and/or order, and produce finite predictions
* Software/serving quality - the candidate must not break the existing system
* Provenance and versioning - the candidate must have a series of valid and traceable historical components

The idea of governance is that we define the rules first, then judge the candidate against those rules.

There are five promotion gates: 
1. Candidate identity
2. Predictive performance
3. Artifact/feature compatibility
4. Software/serving quality
5. Provenance/versioning

### Question 2
What is the difference among a challenger/candidate, an incumbent/champion, an MLflow model version, a model alias, and a model-version tag? How would the `champion` alias and `validation_status` tag behave before and after a successful promotion?

**Best sections to review: 0E–0H — MLflow Lifecycle Design, Candidate vs. Champion, and Tags vs. Aliases, plus 0O — Phase 3.2 State Machine**

*A challenger/candidate is a specific registered model version being evaluated.*

*An incumbent/champion is the model version currently designated as the accepted production version.*

*An MLflow model version is a model that has been registered in MLflow so distinct model versions can be held and tracked.*

*A model alias is a named pointer associated with a model; it's worth noting that it can later be assigned to another version.*

*A model-version tag is a recording of metadata; this is a tool for tracking aspects of the model such as its validation status.*

*Finally, as for how the `champion` alias and `validation_status` tag would behave before and after a successful promotion, we would need to associate the `champion` alias to the newly promoted model and the `validation_status` of the promoted model would need to be switched from `pending` to `passed`.*

challenger -> experimental recipe/model trying to replace incumbent

candidate -> specific version entering promotion evaluation

incumbent -> currentl accepted model

champion -> registry alias identifying the version currently occupying that role

model version -> individually registered model artifact/version

alias -> movable named pointer to a version

tag -> metadata attached to a version

Moving the alias does not delete or overwrite the previous model version. 

### Question 3
Why are we prohibiting new hyperparameter, feature, and weighting experiments during Phase 3.2, and why does a challenger with lower grouped-CV RMSE still need artifact, serving, testing, and provenance checks before the `champion` reference can move to it?

**Best sections to review: 0C–0D — Selection vs. Promotion and Promotion Gates, 0I–0J — Official Test and No New Tuning, and 0O — Phase 3.2 State Machine**

*In Phase 3.2 we are prohibiting new hyperparameter, feature, and weighting experiments because we have moved out of the selection phase of figuring out if we want to put in a new model and we are now in the promotion phase. Once our criteria for deciding if a model has been promoted has been decided, we cannot make edits or run new experiments on the candidate model. Otherwise we would risk inventing criteria to justify promoting a model or we would risk fitting the model to the contract instead of applying the contract to the model.*
 
*As for why a challenger with lower grouped-CV RMSE still needs aritfact, serving, testing, and provenance checks before the `champion` reference can move to it, we need to enforce the five gates to promotion that were described above.*

We freeze the candidate during Phase 3.2 because promotion is supposed to evaluate a specific model, not continue optimizing it. Any substantive recipe change creates a new candidate and should restart the evaluation process. Lower grouped-CV RMSE establishes predictive evidence, but promotion additionally requires artifact compatibility, serving correctness, regression-test success, and traceable provenance so that the model is both statistically better and operationally governable. 

### Ideas to Retain

* Model selection identifies a challenger; model promotion governs whether a specific candidate may replace the incumbent.

* A promotion contract prevents us from changing the decision rules after seeing whether a candidate passes them.

* A candidate must pass predictive, artifact, serving, software-quality, and provenance/versioning gates—not merely have lower RMSE. 

* An MLflow model version is an identifiable model instance; an alias such as `champion` is a mutable reference to the version currently occupying a lifecycle role.

* Tags describe model version metadata/status; aliases point to model versions.

* Changing the frozen candidate during promotion creates a new experiment rather than completing the promotion evaluation.

### Ideas to Retain

* A promotion contract is a precommitted decision policy. 

* Candidate identity must remain stable while promotion gates are evaluated. 

* An alias points to a lifecycle role; a tag describes metadata/status. 

* Promotion moves the `champion` reference—it does not erase the former incumbent. 

* If the candiate recipe changes, you have created a new candidate rather than "fixing" the old one mid-evaluation.

* Predictive superiority and production suitability are separate requirements.