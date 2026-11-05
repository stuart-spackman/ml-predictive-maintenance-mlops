## Phase 3.2 — Task Group 2 Active Recall

### Question 1
Why do we call the Random Forest MLflow run a historical “bootstrap/import” run rather than its training run, and why could the older incumbent legitimately receive a higher MLflow version number than the newer Extra Trees challenger?

**Best sections to review: 2A–2C — Registering the Incumbent, Historical Bootstrap, and Registry Version Numbers**

*We call the Random Forest MLflow run a historical "bootstrap/import" run rather than its training run because we are importing a previously created incumbent into our registry. We don't want to create a situation where it's incorrectly implied that an MLflow run originally trained the Random Forest.*

*As for why the older incumbent could legitimately receive a higher MLflow version number than the newer Extra Trees challenger, version numbers reflect when the model was added to MLflow, not the date that it was created. Because we are adding our incumbent to MLflow after our challenger was registered, we could expect it to have a higher version number.*

historical training != MLflow boostrap/import run

The bootstrap run says, "This existing artifact was imported into MLflow here."
It does not claim, "This run trained the artifact."

### Question 2
What does the `champion` alias represent, how is it different from a fixed model version number, and why can `models:/fd001-rul@champion` continue to represent the accepted production role even if the underlying version changes later?

**Best sections to review: 2D — What Does `champion` Actually Do?, 2J–2L — Registry Inspection and Alias Demonstration**

*The `champion` alias represents the best performing model according to promotion gates, which can also be assumed to be the active production model.*

*As for how it is different from a fixed model version number, the `champion` alias is a mutable reference. We can change where it points to, but we can't use it to change any of the models themselves.*

*Finally, `models:/fd001-rul@champion` can continue to represent the accepted production role even if the underlying version changes later because MLflow is not set up to hard-code versions for roles. With an alias, the consumer can keep asking for the same logical role and they can keep getting it as a result of the `champion` pointer being changed to a different model.*

`champion` represents the model version currently accepted for the champion/incumbent lifecycle role.

fixed version -> immutable identity

champion alias -> moveable role reference

### Question 3
Why does the Extra Trees candidate remain `validation_status=pending` after passing the candidate-identity and predictive-performance gates, and what would it mean if TG3 found that the candidate had better RMSE but failed the artifact or serving-compatibility gate?

**Best sections to review: 2E–2F — The First Two Gates and Pending Status, 2N — Why Performance Is Only One Gate, and 2Q–2S — Boundaries and Completion Standard**

*The Extra Trees candidate remains `validation_status=pending` after passing the candidate-identity and predictive-performance gates because there are still more gates that need to be passed. Once candidate identity and predictive performance have been confirmed, there is still each of the items on the following list: artifact compatibility, serving compatibility, software quality gate, and provenance/versioning completion.*

*As for what it would mean if TG3 found that the candidate has better RMSE but failed the artifact or serving-compatibility gate, that would mean that the model would either need to switch to having a failed status or remain in pending status. Either way, no promotion could be allowed to happen.*

`rejected` means evaluation reached a decision, and this candidate is not promotable under the current contract.

### Ideas to Retain

* Bootstrapping a model into a registry creates registry lineage from the import forward; it does not retroactively recreate the model's original training lineage.

* MLflow version numbers describe registry version order, not training chronology or model quality. 

* An alias such as `champion` represents a lifecycle role independently of a particular version number. 

* The registered candidate should be inspected directly—not merely trusted because the tags say it is the correct model.

* A better validation RMSE can advance a candidate through one gate without authorizing promotion.  

### More Ideas to Retain

* A bootstrap run imports historical truth; it does not manufacture historical lineage. 

* MLflow version numbers reflect registry ordering, not model chronology or superiority. 

* `champion` means the currently accepted lifecycle role, not automatically the numerically best model. 

* Aliases move between versions; versions themselves remain distinct historical identities. 

* `pending` means evaluation is incomplete. `passed` or `rejected` means the promotion decision has been resolved. 

* A candidate can beat the incumbent on RMSE and still be rejected from promotion.