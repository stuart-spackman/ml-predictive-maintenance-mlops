## Phase 2.1 — Task Group 3 Active Recall

### Question 1
What is the difference between the locked model specification, the serialized fitted model artifact, and the final-fit provenance record, and why does production inference need all three concepts to remain distinct?

**Best section to review: 3B — Three Things That Must Stay Distinct**

*The locked model specification is the configuration of the model than won during development. The configuration includes the model family, feature representation, hyperparameters, feature policy, weighting policy, etc. It's worth noting that the locked model specification is not the trained model.*

*The serialized fitted model contains the model in its learned state after the locked recipe was refitted on all development engines. For a fitted tree model such as ours, that includes things such as the learned tree structures.*

*The final-fit provenance record is evidence about how the fitted artifact was created in the form of a SHA-256 fingerprint that was produced in Phase 1.*

*As for why production inference needs all three concepts to remain distinct, these three concepts allow us to confirm that any input data is being put through all the steps that were used for making predictions during development and training.*

The locked specification describes the selected model recipe, the serialized fitted artifact contains the learned state produced from that recipe, and the provenance record documents evidence about how and what was produced. Keeping them distinct lets inference verify both what configuration should be deployed and whether the fitted artifact being loaded is the frozen artifact produced by Phase 1. 

### Question 2
What are serialization and deserialization, and why can the Phase 2 inference system call `predict()` on the loaded model without calling `fit()` again?

**Best sections to review: 3C — Serialization and Deserialization and 3D — Why There Must Be No `.fit()` in Production Inference**

*Serialization is the process of converting an in-memory object's state into a form that can be stored. Then, when we need it again we can pull it out of storage and reconstruct it, at which point deserialization is occurring.*

*As for why there must be no `.fit()` in production inference, we need to account for the fact that inference transforms data, which is different from retraining a locked model. Once a model has been locked, no more training can occur, otherwise we would be switching to a model that was not tested and verified during the development process.*

Once the final fitted artifact has been created and frozen, production inference does not call `.fit()` on it.

### Question 3
What does the model's SHA-256 fingerprint allow us to verify, and what important things does that fingerprint not prove about the model?

**Best sections to review: 3E — What SHA-256 Is Doing for Us and 3F — What a Hash Does NOT Prove**

*The main thing we need to have in mind here is that SHA-256 is a cryptographic hash function. It takes the data making up our model file and using it to create a fixed-size fingerprint. From there, any time we call on our model during inference we can make sure that the fingerprint of the model currently being used matched the fingerprint of the model that was locked during development. As for what that fingerprint does not prove, it doesn't prove that the model being used is statistically correct or is making highly accurate predictions, only that it matches the model that was locked as a result of the development process.*

We don't necessarily need to calculate the hash for every prediction. 

SHA-256 tells us that the bytes correspond to the frozen artifact. But there are still several things that it does not tell us.

### Question 4
Why is verifying a model artifact by filename alone weaker than verifying both its expected identity and its SHA-256 fingerprint?

**Best section to review: 3R — Artifact Identity vs Filename**

*The principle at play here is that the contents of a file can be changed without showing any evidence in the file name itself. It's possible to completely change the model being used by the inference program while keeping the file name the same, so it's best add more/better layers of precaution.*

The filename expresses the intended identity, while the fingerprint provides much stronger evidence about the artifact's actual byte-level identity. 

### Question 5
How can `n_features_in_` and, when available, `feature_names_in_` help us prevent the inference pipeline from feeding the fitted model an incompatible feature matrix?

**Best sections to review: 3O — Why `n_features_in_` Is Useful and 3P — Feature Names May Give Us an Even Stronger Check**

*`n_features_in_` can provide a distinct count associated with the model for how many features were used to train it. This provides a method for quick and simple checking on model alignment with locked model vs. current model. The principle at play here is to fail loudly at the boundary where an inconsistency can still be dianosed early in the process. `feature_names_in_` can provide an even stronger signal, as the titles of features in the form of strings are more specific than feature count.*

Fail loudly where the inconsistency can be diagnosed early.

### Extra Questions

What does the word "provenance" mean in this context? 

*In this context, provenance means the documented origin and history of an artifact. The provenance provides an evidence trail about where the thing came from.*

*The fitted `.joblib` is the model's body; the provenance record is part of its documented history/bith certificate.*

### Ideas to Retain

* Specification = selected recipe.

* Fitted artifact = actual learned state. 

* Provenance = evidence trail describing where that artifact came from. 

* SHA-256 is one piece of provenance/integrity evidence, not proof of model quality. 

* After the final artifact is frozen, inference uses `.predict()`, not `.fit()`.

* `n_features_in_` checks dimensionality; `feature_names_in_` can check feature identity and ordering.

* Filename says what a file is supposed to be; fingerprint provides stronger evidence of what file it actually is.