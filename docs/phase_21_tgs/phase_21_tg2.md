## Phase 2.1 — Task Group 2 Active Recall

### Question 1
What is training-serving feature parity, and why is reusing the existing Phase 1 temporal-feature functions safer than independently reimplementing the same formulas inside the inference package?

**Best sections to review: 2A — Core Question and 2C — Prediction: Reuse or Rewrite?**

*We want to prevent training-serving skew, in which the data we are serving gets put through a different mathematical process than the data we trained on. A good way to reduce the chances of training-serving skew is to reuse the functions and formulas that were used in training rather than rewriting them and risking creating differences between the two processes. The principle at play here is that reusing tested code reduces opportunities for discrepancies.*

Training-serving feature parity means that inference-time inputs are transformed using the same mathematical definitions that were used during model training and validation. Reusing the existing Phase 1 temporal-feature lag functions reduces training-serving skew because there is only one implementation of the lag, rolling, slope, grouping, and windowing rules instead of separate training and inference implementations that could drift apart.

### Question 2
Why does Task Group 2 construct the complete 60-feature temporal superset instead of immediately selecting only the exact feature columns required by the winning model?

**Best sections to review: 2E — Why Build the Full 60-Feature Superset? and 2P — Where the Locked Feature Ordering Enters**

*Because it is not yet the job of the code we're writing for this section of the project to own the locked-model artifact (but that is coming up in the next section of coding). The job of the code we're currently writing is to produce a known canonical inference representation. Right now in the project we're confirming that we can reproduce the superset-like feature universe. Coming up next in the project is the part where we account for the exact features that the locked-model artifact consumes.*

Instead of superset-like feature universe we could better say the canonical 60-feature Phase 1.6 temporal superset.

### Question 3
Why must the inference pipeline engineer temporal features from the complete legal engine history before selecting only the latest prediction row?

**Best sections to review: 2I — Concrete Example: Engine 42 Through Cycle 57 and 2J — Why Not Drop Cycles 1–9 First?**

*The principle at play here is that we need inference to follow the same rules that were applied in development. We need to engineer features from the full legal history first. Then select the latest eligible row afterward. Cycles 1-9 can be ineligible prediction rows while simultaneously being essential historical inputs.*

### Question 4
What does the prefix-invariance test demonstrate, and how could it expose an accidental future-looking feature such as `shift(-1)`?

**Best sections to review: 2M — Prefix-Invariance Returns and 2N — Why Prefix-Invariance Is So Powerful**

*The principle at play here is the need to implement a behavioral test of causality. Instead of reading every line of feature code and asking if it looks causal, we can ask the stronger behavioral question of if the future can change the past. This is done by calculating a subset of features in the pipeline and then confirming that all those values remain identical when we build up the full set of features in the pipeline.*

We're not comparing the subset of features with the full feature set. 

We're comparing the same features at the same cycle under two different amounts of available future history.

Prefix invariance is a behavioral test of temporal causality. We compute the same features at some cycle `t` once using history only through `t`, and again using a longer history containing future cycles. The features at `t` must remain identical. A future-looking transformation such as shift(-1) would fail because the feature at cycle `t` would depend on cycle `t + 1`. 

### Question 5
Why is `df.iloc[[-1]]` more useful than `df.iloc[-1]` when preparing one observation for a scikit-learn model?

**Best section to review: 2H — Build the Latest Eligible Feature Row**

*This has to do with Pandas data types. `df.iloc[-1]` returns a Pandas Series while `df.iloc[[-1]]` returns a one-row DataFrame. There will be an upcoming point in this project where our sklearn model expects an input with a particular shape in the form of `(number of examples, number of features)`. For a single prediction, the input data will have shape `(1, n_features)`, which is more like a vector or a Pandas DataFrame, as opposed to `(n_features,)`, which is more like an array or a Pandas Series.*

The clearner distinction here is dimensionality, because noth vectors and arrays can be described in several ways. 

### Ideas to Retain

* Training-serving parity means preserving the mathematical meaning of model inputs between development and inference. 

* The safesty way to preserve parity is usually to reuse the same implementation rather than recreate equivalent-looking code. 

* Task Group 2 creates the canonical feature universe; the locked model specification later decides which exact columns are consumed. 

* Prediction-ineligile history can still be feature-essential history. 

* Prefix invariance compares the same cycle and same features with versus without future rows. 

* If the future changes features at cycle `t`, the transformation is not causal.

* `iloc[-1]` is 1D; `iloc[[-1]]` preserves the 2D `(samples, features)` structure sklearn expects. 