## Phase 2.1 — Task Group 4 Active Recall

### Question 1
Why does the inference pipeline construct the canonical 60-feature representation but ultimately pass only 36 features to the frozen Random Forest, and what determines exactly which 36 features are selected?

**Best sections to review: 4A — The Pipeline We Are Building and 4J — Notice What Happened to the Other 24 Features**

*A couple of the principles at play here are some our previous efforts were dedicated to figuring out if we could reproduce the entire canonical temporal feature universe, while our current efforts are dedicated to extracting the exact portion of that universe that the frozen winner actually learned from.*

There's a missing piece here and it's what determines the 36 features. 

Task Group 2 reproduces the complete 60-feature Phase 1.6 temporal representation so serving uses the same feature universe as development. The final Random Forest, however, was trained on only 36 predictors. The ordered `feature_names` stores in the locked model specification determine exactly which 36 features are passed to the model.

### Question 2
Why are both feature identity and feature ordering part of the fitted model's inference contract, even when the number of supplied features is correct?

**Best sections to review: 4B — Why Feature Order Is Part of the Model Contract and 4H — Think Through the Three Levels of Feature Verification**

*This related to the fact that our tree nodes learned from the features when they were in a particular order. Tree inference only knows feature indices, not feature names. Giving our model data with feature columns out of order would produce an incorrect result. The main principle at play here is that the model contract we need to build into our application includes feature identity and feature ordering.*

Feature count alone is insufficient. Identity and order are part of the inference contract. 

### Question 3
Why should the fitted model and verified artifacts normally be loaded once into a persistent inference pipeline rather than reloaded for every prediction, and how is loading fundamentally different from fitting?

**Best section to review: 4N — Why Use a Persistent Pipeline Object?**

*We could write a single function for predicting rul that takes in an engine history dataframe, but this would require loading the locked model artifacts in the form of the `.joblib` every single prediction. That would wind up being very wasteful when processing a high number of HTTP requests. A far superior option is to start the application, load and verify the model just once, create an inference pipeline, and then start making predictions. Here the model remains in memory rather than getting recreated for every single HTTP request. With loading we recreate the model only once with frozen parameters. Fitting is the process of figuring out those parameters via a learning algorithm such as gradient descent. Loading reconstructs a frozen learned state, while fitting changes or creates a learned state.*

Fitting is the process by which a learning algorithm uses training data to create a learned model state. 

Loading is necesary for the process where we save the learned state and then reconstruct it in memory. 

Fitting is necesary for giving the training data to a learning algorithm and creating or updating the learned state.

### Question 4
Why should we avoid silently modifying a model's output during inference—for example, clipping a negative RUL prediction to zero—if that behavior was not part of the Phase 1 evaluated procedure?

**Best section to review: 4O — Should We Clamp the RUL Prediction?**

*Because that would create instances of development-serving mismatches. The principle at play here is that we do not want to covertly try to improve the model output during deployment because our model and its outputs should be thought of as a locked or frozen system that we're calling on. Introducing new behaviors has the potential to create new problems, plus we would not longer be using the exact system that we verified during Phase 1.*

We need to avoid situations where the deployed inference behavior no longer matches the evaluated procedure. 

The principle at play here is that deployment is not the time to start covertly or overtly trying to improve the model.

### Question 5
What is the difference between deterministic inference and predictive accuracy, and which phase of this project provides evidence for each?

**Best section to review: 4R — A Very Important Distinction: Deterministic Inference vs Accurate Inference**

*Deterministic inference refers to creating a situation where identical inputs always lead to the same outputs. This is desirable because reproducibility is a fundamental part of creating quality software. This is not synonymous with predictive accuracy; just because you get the same outputs from the same inputs doesn't mean the outputs are accurate, just that they can be reliably recreated. Predictive accuracy means the model made a prediction that was very close to the ground-truth label.*

Deterministic inference means the same input, preprocessing implementation, and frozen model state produce the same prediction repeatedly. That is a software-reproducibility property and Phase 2 provides evidence for it. Predictive performance concerns how close predictions are to ground truth, which Phase 1 evaluated using grouped cross-validation, OOF metrics, diagnostics, and the official test set. A model can be perfectly deterministic and consistently wrong.

### Ideas to Retain

* 60 features are available; the locked specification's ordered `feature_names` determines the 36 the winner actually consumes. 

* Feature count verifies dimensionality; feature identity and order verify semantic alignment. 

* Loading reconstructs learned state. Fitting creates learned state from training data. 

* Random Forest fitting does not require gradient descent; it learns trees and split thresholds from data. 

* Do not introduce unevaluated postprocessing during deployment. 

* Phase 1 provides evidence for predictive performance; Phase 2 provides evidence for reproducible inference behavior. 

* A model can be perfectly deterministic and perfectly wrong. 