## Phase 2.1 — Task Group 1 Active Recall

### Question 1
What is the difference between schema validation and domain validation, and give one engine-history example of each?

**Best section to review: 1B — Schema Validation vs. Domain Validation**

*Schema validation is the process of confirming any data we're dealing with has the structure needed to proceed further down the pipline. Domain validation is the process of figuring out if any data we're dealing with make sense under the rules of our particular problem. An example of schema validation would be making sure there is a data column for all sensors that we dealth with in training and development. An example of domain validation would be making sure there are no duplicate values for cycle count for all the engines.*

### Question 2
Why does the validation layer safely sort out-of-order cycle rows but reject histories with missing or duplicate cycles?

**Best sections to review: 1E — Decide What We Normalize and What We Reject and 1H — Example: Why Missing Cycle 6 Is Different From Unsorted Rows**

*The principle at play here is that we need to automatically normalize something only when the correction is unambiguous and information-preserving. It is possible that a dataset could come to us with out of order rows, but then fit our inference contract perfectly after sorting. The same could not be said about histories with missing or duplicate cycles. Even if we put that dataset through a normalization process, we couldn't get it to match the inference contract without fabricating data.*

### Question 3
Why does the Phase 2.1 MVP accept the canonical raw FD001 schema even though the final model does not directly use every raw operating setting and sensor?

**Best section to review: 1D — Why Require Raw Columns the Model Might Not Ultimately Use?**

*The principle at play here is that the external interface of an application should be domain-oriented, while the internal domain of an application should be model-oriented. At the start of the project, the FD001 dataset had a distinct format and for ease of use we need to assume that any new observations will also have that format. We benefit from expecting the users to send one or more normal FD001 observation histories.*

The deeper reason for accepting the raw canonical schema is that we don't want callers to depend on the implementation details of today's model. We want to create a situation where the caller understands FD001 observations and the pipeline understands which variables the model actually needs.

### Question 4
Why should engine-history validation live inside the inference package rather than exclusively inside the future FastAPI endpoint?

**Best section to review: 1K — Why Do Validation Outside FastAPI?**

*The principle at play here is that domain rules belong with the domain/inference code, not with the transport layer (though I don't really know what a transport layer is).*

*We eventually want to have the software run a sequence like: POST /predict -> FastAPI -> validate_engine_history(...)*

*But the validation itself should not depend on HTTP. We want multiple types of preceeding steps to be possible before inference. If validation only existed inside the future FastAPI endpoint, then other preceeding steps not associate with FastAPI wouldn't receive validation, i.e., a Python notebook or a command-line application.*

If we're getting data from FastAPI, the validation should work. 

If we're getting data from a Jupyter Notebook, the validation should work. 

If we're getting data from a CLI, then validation should work. 

If we're getting data from a future batch process, then validation should work. 

### Question 5
What is the conceptual difference between the inference validation layer we created here and the Pydantic request validation we will later add around the HTTP API?

**Best section to review: 1L — Pydantic vs Our Validation Layer**

*The principle at play here is that Pydantic is good at figuring out if a network request does not have the expected structure or datatypes. But if someone sends data with the correct shape, Pydantic might miss the fact that it's not compatible with our inference contract. That's where inference validation picks up the slack. Pydantic or an API schema asks if a request is shaped correctly. Inference validation asks if the incoming engine history is compatible with our specific model.*

### Extra Questions

* What is a transport layer in this context? 

A transport layer is the mechanism used to move information between the outside world and your application's core logic.

HTTP is one transport mechanism. 

When dealing with a transport layer we ask how the information arrived. 

When dealing with a domain or inference layer we ask what the information means and what we should do with it.

### Ideas to Retain

Schema validation = correct structure

Domain validation = correct meaning under our problem rules

Normalize only when correction is unambiguous and information-preserving

Public interface should speak the domain; internal code can speak the model

Our MVP accepts one engine history per request

Pydantic validates request shape; inference validation validates model/domain compatibility

Transport layer tells us how the data got there

Inference/domain layer tells us what the data means and if it is legal

HTTP/FastAPI should carry requests to the inference pipeline, not contain the entire inference pipeline