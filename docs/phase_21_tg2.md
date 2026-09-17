## Phase 2.1 — Task Group 2 Active Recall

### Question 1
What is training-serving feature parity, and why is reusing the existing Phase 1 temporal-feature functions safer than independently reimplementing the same formulas inside the inference package?

**Best sections to review: 2A — Core Question and 2C — Prediction: Reuse or Rewrite?**

*We want to prevent training-serving skew, in which the data we are serving gets put through a different mathematical process than the data we trained on. A good way to reduce the chances of training-serving skew is to reuse the functions and formulas that were used in training rather than rewriting them and risking creating differences between the two processes. The principle at play here is that reusing tested code reduces opportunities for discrepancies.*

### Question 2
Why does Task Group 2 construct the complete 60-feature temporal superset instead of immediately selecting only the exact feature columns required by the winning model?

**Best sections to review: 2E — Why Build the Full 60-Feature Superset? and 2P — Where the Locked Feature Ordering Enters**

*Because it is not yet the job of the code we're writing for this section of the project to own the locked-model artifact (but that is coming up in the next section of coding). The job of the code we're currently writing is to produce a known canonical inference representation. Right now in the project we're confirming that we can reproduce the superset-like feature universe. Coming up next in the project is the part where we account for the exact features that the locked-model artifact consumes.*

### Question 3
Why must the inference pipeline engineer temporal features from the complete legal engine history before selecting only the latest prediction row?

**Best sections to review: 2I — Concrete Example: Engine 42 Through Cycle 57 and 2J — Why Not Drop Cycles 1–9 First?**

*The principle at play here is that we need inference to follow the same rules that were applied in development. We need to engineer features from the full legal history first. Then select the latest eligible row afterward. Cycles 1-9 can be ineligible prediction rows while simultaneously being essential historical inputs.*

### Question 4
What does the prefix-invariance test demonstrate, and how could it expose an accidental future-looking feature such as `shift(-1)`?

**Best sections to review: 2M — Prefix-Invariance Returns and 2N — Why Prefix-Invariance Is So Powerful**



### Question 5
Why is `df.iloc[[-1]]` more useful than `df.iloc[-1]` when preparing one observation for a scikit-learn model?

**Best section to review: 2H — Build the Latest Eligible Feature Row**