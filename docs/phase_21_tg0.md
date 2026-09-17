## Phase 2.1 — Task Group 0 Active Recall

### Question 1
What is the Phase 2.1 inference contract, and why does the MVP accept one engine's raw observed history rather than asking callers to submit model-ready engineered features?

**Best section to review: 0A — Core Question**

*Because that would leave open the possibility of people running their own preprocessing steps on the data rather than letting our pipeline handle it. Our pipline has already gone through a series of quality checks. Accepting one engine's raw observed history reduces the possibility of user error.*

The inference contract defines what the inference system accepts and returns. We accept raw history for one engine because model-specific preprocessing should remain owned by our test pipline. If callers had to engineer temporal features themselves, they could use different windows, incorrect feature ordering, or noncausal calculations, producing inputs that no longer match the pipeline validated during Phase 1. 

### Question 2
What is training-serving skew, and how does making temporal feature engineering an internal responsibility of the inference pipeline help prevent it?

**Best sections to review: 0A — Core Question and 0H — Define the Public Input Boundary**

*A training-serving skew occurs when software fails to serve the same model pipeline that it validated. The goal is to have inference-time preprocessing reproduce training-time preprocessing exactly. (Not sure how to confidently answer this one past that.)*

Training-serving skew means the mathematical transformation applied before prediction differs from the transformation used when the model learned.

We need to reuse the same feature-engineering impelementation rather than asking every consumer to recreate it. 


### Question 3
What is the difference between the inference contract, the locked model specification, and the final fitted model artifact?

**Best section to review: 0F — Prediction: Configuration vs Learned State**

*An inference contract specifies what inputs and outputs are allowed. A locked model specification states the model and preprocessing recipe that was used and needs to continue to be used. The final fitted model artifact states the parameters and trees were actually learned.*

An inference contract asks what a caller is allowed to send and what we are guaranteed to send them back. 

A locked model specification is the specific recipe that won during the training and development process. Model family, hyperparameters, features, target policy, etc.

A final fitted artifact is the object that resulted from using the recipe to learn from the data. Tree 1, Tree 2, ..., Tree 300. 

### Question 4
Why should the inference pipeline remain independent of FastAPI instead of putting validation, feature engineering, model loading, and prediction logic directly inside an HTTP endpoint?

**Best section to review: 0J — Prediction: Why Not Put Everything in FastAPI?**

*Our goal is to have FastAPI become one consumer of the inference pipeline while not letting it become the entire inference pipline. If we were to put all the mentioned parts of the project inside an HTTP endpoint, then model inference would be tightly coupled to HTTP. This would make the underlying inference logic harder to unit test, reuse from Streamlit, use from a command-line tool, etc.*

We want to implement a separation of concerns. 

FastAPI should worry primarily about: HTTP request -> Python objects -> call inference pipeline -> Python result -> HTTP response

The inference pipeline should not care whether the caller is a website, terminal script, automated batch process, etc.

### Question 5
Which Phase 1 guarantees must remain true during production-style inference, even though model development and cross-validation are finished?

**Best section to review: 0L — Phase 1 Guarantees We Must Carry Forward**

We must maintain temporal causality, i.e., at a cycle `t` the model only has access to information that occurred at or before `t`. We much maintain engine-boundedness, i.e., if we are examining one specific engine then the model will not have access to features from any other engines. We must maintain locked feature schema, i.e., the model input must use the exact feature columns and the exact ordering that were used in model development. We must always use the locked fitted artifact, i.e., all predictions are done through `phase_16_final_fitted_model.joblib`. 

### Questions I Need Answered

* What is and endpoint in this context? I don't know what an HTTP endpoint is. 

An endpoint is a particular place in a web service that another program can send a request to in order to perform some specific operation. 

GET = give me information

POST = I'm giving you some data and I expect you to do something with it

The inference pipline provides the capability.

The HTTP endpoint exposes that capability to other software over HTTP. 

### Ideas to Retain 

Training-serving skew = production preprocessing no longer mathematically matches training preprocessing

Owning feature engineering internally gives us one authoritative implementation

Inference contract = allowed inputs/outputs

Locked specification = winning recipe

Fitted artifact = actual learned model state

An HTTP endpoint is a network-accessible doorway for a specific operation

GET /health asks for information; POST /predict submits data for prediction

FastAPI endpoint = doorway. Inference pipeline = machinery behind the doorway

FastAPI exposes the prediction capability; it should not contain the entire prediction implementation