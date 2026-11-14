## Phase 3.4 — Task Group 4 Active Recall

### Question 1
Walk through the complete lifecycle from a production monitoring signal to a possible deployment of a retrained challenger. At which points are investigation, retraining authorization, promotion, and deployment separate decisions?

**Best sections to review: 4A — Final Decision Chain, 4F–4G — Part 3 Story and Detection vs. Decision vs. Action, 4J — Final Architecture**

*From a production monitoring signal to a possible deployment of a retrained challenger, we have in the production process*
telemetry
-> monitoring
-> drift/operational signal
-> identify failing layer
-> investigate
-> delayed outcome labels, when available
-> direct performance evidence
--> retraining justified?
no
-> fix appropriate non-model problem or continue monitoring
yes 
-> authorize challenger fit
-> new challenger artifact 
-> evaluation
-> compatibility/software/provenance gates
-> promotion decision
-> deployment decision

*As for the points where investigation, retraining authorization, promotion, and deployment are separate decisions, we can think in terms of each lifecycle not having power over all the others. Investigation cannot retrain, retraining cannot promote, and promotion cannot deploy.*

Each stage answers a different question. 

Investigation -> What actually happened, and why? 

Retraining authorization -> Is there enough evidence to justify fitting a new model? 

Promotion -> Has the challenger earned the right to become the approved model? 

Deployment -> Should the approved model actually replace the running system now? 

### Question 2
Why is it important that the final Phase 3.4 handoff explicitly preserves the statements `drift ≠ performance degradation`, `performance degradation ≠ automatic retraining`, `retraining ≠ promotion`, and `promotion ≠ deployment`?

**Best sections to review: 4A–4E — Lifecycle Boundaries and Closeout Audit**

*It is important that the final Phase 3.4 handoff explicitly preserves the statements of `drift ≠ performance degradation`, `performance degradation ≠ automatic retraining`, and `retraining ≠ promotion`, `promotion ≠ deployment` because we need to maintain boundaries along the decision chain leading up to retraining. To avoid having a kneejerk reaction of retraining anytime something somewhere the system goes wrong and wasting resources, there needs to be a series of gates and quality checks that need to be met before retraining, promotion, and deployment can occur.*

Bad reaction: something changed -> retrain

These inequalities matter not just for resource efficiency; they also protect us from making incorrect causal conclusions.

These boundaries prevent both premature action and unsupported inference.

Detection evidence does not automatically establish cause.

Cause does not automatically establish remedy. 

Remedy does not automatically authorize production change.

### Question 3
What production/retraining claims can we legitimately make about this portfolio project after Part 3, and which claims would be misleading because we used controlled simulations rather than genuine newly labeled production data and a real production retraining event?

**Best sections to review: 4H — Defensible Portfolio Claims, 4K — Part 3 Closeout**

*After Part 3, we can legitimately claim:*

* That I built an inference and monitoring architecture that records actual served-model identity and model-ready features, then evaluates current prediciton events against frozen reference distributions.

* I implemented an evidence-drive retraining policy that distinguishes service, data, artifact, observability, label, and model-performance failures instead of automatically retraining on drift.

* I implemented delayed-label performance logic that separates unlabeled drift detection from direct RMSE/MAE monitoring. 

* I designed retraining so a new model enters as a challenger while the incumbent remains immutable for comparison and rollback.

*As for which claims would be misleading because we used controlled simulations rather than genuine newly labeled production data and a real production retraining event:*

* I automatically retrained the production model. 

* I deployed a retrained model after observing real production degradation.

* I operated this against a live industrial fleet.

### Ideas to Retain 

* Detection tells us what happened; decision making determines the appropriate response; action actually changes the system. 

* The authority of each lifecycle stage should be deliberately limited; monitoring cannot retrain, retraining cannot promote, and promotion cannot silently deploy.

* A production failure should be fixed at the layer that actually failed. 

* A retrained model remains a challenger until it independently earns promotion.

* Honest project boundaries are part of good MLOps: validated simulation is not the same thing as a real production event. 

### More Ideas to Retain

* Each lifecycle state answers a different question and requires its own evidence.

* Detection does not establish cause; cause does not automatically establish remedy; remedy does not automatically authorize deployment. 

* Governance boundaries prevent bad causal reasoning as well as unecessary retraining. 

* A simulated and validated workflow is a legitimate engineering result, but it not be presented as a production event. 

* The strongest portfolio claims are specific about what was actually implemented, tested, and observed.