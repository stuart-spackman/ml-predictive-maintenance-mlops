## Phase 3.1 — Task Group 4 Active Recall

### Question 1
What information should a useful experiment-tracking record preserve, and what is the difference between experiment tracking and a model registry? Why is saving only a final RMSE insufficient for reproducibility?

**Best sections to review: 4A — What Is Experiment Tracking?, 4B — Experiment Tracking Is Not a Model Registry, 4D — Provenance, and 4L — Tracking Results vs. Reproducing Results**

*A useful experiment tracking record preserves the relationship among the following aspects of the experimental testing process: experiment identity, configuration, data/evaluation procedure, metrics, artifacts/evidence, and code/environment provenance. We seek to do a lot more than make a simple statement like, "Extra Trees did pretty well compared the the baseline model."*

*Experiment tracking refers to a system where we can store answers to the following questions:*
* What did we try? 
* What parameters did we use? 
* What metrics resulted? 
* Which files contain the evidence? 

*Model registry is more geared towards lifecycle questions such as:*
* Which fitted model version is a candidate? 
* Which is the incumbent? 
* Which version was promoted? 
* Which artifact should serving load? 

*Saving only a final RMSE is insufficient for reproducibility because all that does is indicate that we measured a result. In reproducing something we need to be able to reconstruct the sequence of events that lead to obtaining that number.*

Core experiment tracking bundle: 
* experiment identity
* configuration
* evaluation procedure
* metrics 
* artifacts/evidence
* code/environment provenance

Experiment tracking -> What did we try and what happened? 

Model registry -> What model version occupies what lifecycle state?

A score alone gives us the outcome, but not enough information to reconstruct the process that produced it.

### Question 2
Why should the TG1 default-model RMSEs, TG2 nested-tuning RMSE, and TG3 fixed-recipe RMSE not simply be sorted into one universal leaderboard? What additional evaluation context must accompany a metric before we interpret it?

**Best sections to review: 4C — Don't Flatten Different Experiments Into One Ranking, 4I — Inspect the Ledger, and 4N — What Do Our Experiments Actually Say So Far?**

*The TG1 default model RMSEs, TG2 nested-tuning RMSE, and TG3 fixed-recipe RMSE should not simply be sorted into one universal leaderboard because those metrics describe different experimental procedures. Putting them into a leaderboard would only show the metrics, but a ledger needs to preserve metrics plus evaluation contexts.*

*As for what additional evaluation context must accompany a metric before we interpret it, we need to be able to see the experiment type and the evaluation procedure.*

A metric is meaningful only in the context of the procedure that generated it.

TG1 Extra Trees RMSE -> fixed default recipe under grouped CV

TG2 Extra Trees RMSE -> nested tuning procedure

TG3 Extra Trees RMSE -> one fixed recipe under grouped CV

In addition to needing experiment type and evaluation procedure, we also need: 
* model configuration
* feature representation
* training objective
* selection procedure

### Question 3
What do the Git commit, dirty-working-tree flag, environment versions, and SHA-256 file hashes each contribute to experiment provenance? What do they still not prove about model quality or perfect reproducibility?

**Best sections to review: 4D–4F — Provenance, Git State, and Hashes, 4M — Reproducibility Is Never Absolute, and 4Q–4R — Quality Gate and Completion Standard**

*When discussing the different components of provenance, we have:*
* Git commit contributes knowledge of the code that was recently created or changed in the project.
* Dirty working tree flag contributes knowledge of an experiment script having been modified after a commit.
* Environment versions contribute knowledge of what specific software packages were being used at the time of the experimental results getting generated and recorded.
* SHA-256 file hashes contribute file identities and integrity.

*As for what they still do not prove about model quality or perfect reproducibility, we cannot use any of these components of provenance to draw conclusions about scientific correctness.*

A Git commit identifies a particular committed repository snapshot. Git commit hash -> exact committed project state

A dirty working tree flag means at least one tracked or untracked working tree change exists beyond the recorded commit.

Environment versions -> help reconstruct the software runtime

SHA-256 hashes -> identify exact file contents and/or detect changes

The Git commit identifies the committed source snapshot, while the dirty working tree flag tells us whether uncommitted state also contributed to the run. Environment versions help reconstruct the software runtime, and SHA-256 hashes identify exact file contents and detect changes. Together these improve provenance and reproducibility, but they do not establish scientific validity, model quality, or guarantee bit-for-bit reproducibility across all environments.

### Ideas to Retain

* Experiment tracking records evidence; a model registry governs lifecycle state.

* A metric without its evaluation procedure is incomplete evidence. 

* Git commit + clean working tree is stronger provenance than Git commit alone.

* Hashes tell you "same file or different file," not "good model or bad model."

* Reproducibility is reconstruction of process and context, not merely preservation of a score. 
