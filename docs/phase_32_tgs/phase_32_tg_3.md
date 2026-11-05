## Phase 3.2 — Task Group 3 Active Recall

### Question 1
Why is checking only `candidate_model.n_features_in_ == 36` insufficient to establish feature compatibility, and what additional feature-schema property must match the locked inference contract?

**Best sections to review: 3B–3C — Compatibility vs. Equal Predictions and Feature Compatibility**

*Only checking `candidate_model.n_features_in_ == 36` is insufficient to establish feature compatibility because our models have a distinct schema they have to adhere to, with the ordering and names of features being fundamentally important.*

*The additional feature-schema property that must match the locked inference contract is `candidate.feature_names_in_`, which can be verified directly. Our models were trained with a pandas DataFrame, so scikit-learn should preserve the list of feature names.*

We're not just dealing with a count constraint. The stronger contract is: 
same 36 features + same exact names + same exact order

Feature-count compatibility is necessary but not sufficient; semantic identity and ordering of the features must also match.

### Question 2
Why is successfully calling `candidate_model.predict()` on an already-engineered 36-feature dataframe weaker evidence than successfully passing raw engine history through `RULInferencePipeline` with the registered Extra Trees candidate?

**Best sections to review: 3D — Raw History → Candidate Prediction, 3H — Pipeline vs. Direct Prediction, and 3I — Existing Pytest Suite**

*Successfully calling `candidate_model.predict()` on an already engineered 36-feature dataframe is weaker evidence than successfully passing raw engine history through `RULInferencePipeline` with the registered Extra Trees candidate because a successful call to `candidate_model.predict()` proves only that the model accepts already-engineered model features. The actual application that we built has several steps in its functionality before the model gets fed engineered features. A successful run through `RULInferencePipeline` is much stronger evidence of good functioning because there are more components that are reflective of actual production/runtime.*

Direct prediction validates estimator compatibility; end-to-end pipeline prediction validates system compatibility.

### Question 3
If TG3 passes the artifact, feature, inference, and software-quality checks, why does `validation_status` still remain `pending`, why does the Random Forest retain the `champion` alias, and what decision remains for TG4?

**Best sections to review: 3E — We Are NOT Changing Production Serving Yet, 3J — Why Validation Remains Pending, and 3O — What Comes Next**

*If TG3 passes the artifact, feature, inference, and software-quality checks, `validation_status` remains pending because we still will not have completed the final provenance/promotion decision yet. This situation represents having passed four of the five promotion gates.*

*As for why the Random Forest retains the `champion` alias, changing that alias to a different model is reserved for a situation where all five quality gates have passed, which we have not achieved yet.*

*Finaly, the decision that remains for TG4 is the final decision on promoting the Extra Trees model. Task Group 4 will be the provenance review step, in which we make our final decision, change the validation status, and transition the `champion` pointer if approved.*

* PASS: candidate identity
* PASS: predictive performance
* PASS: artifact/feature compatibility
* PASS serving/software compatibility
* REMAINING: provenance + promotion decision

The final step is the governance/reconciliation step where we ask, "Do all the evidence, provenance, registry state, and promotion-contract requirements jointly authorize promotion?"

### Ideas to Retain

* Serving compatibility means preserving the input/output contract, not preserving identical predictions. 

* Feature count alone is insufficient; feature identity and order matter. 

* Testing the model on engineered `X` is weaker than testing raw history through the actual inference pipeline.

* Candidate-specific integration checks and whole-project regression tests answer different questions, and both matter. 

* Individual gates may all pass while overall validation remains pending until the formal promotion decision is made.

### More Ideas to Retain

* Feature compatibility means exact schema compatibility, not merely matching dimensionality. 

* Estimator compatibility is weaker than end-to-end system compatibility

* Raw-history inference tests the actual serving path and therefore catches integration failures that direct model prediction can miss. 

* Passing several individual gates does not imply promotion until the governance decision is complete. 

* The champion alias moves only after the candidate has satisfied the entire promotion contract.