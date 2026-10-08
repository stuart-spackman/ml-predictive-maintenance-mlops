## Phase 2.2 — Task Group 4 Active Recall

### Question 1
What is an adapter, and why do we use an API adapter between `PredictionRequest` and the Phase 2.1 dataframe instead of changing Phase 2.1 to accept Pydantic/FastAPI objects directly?

**Best sections to review: 4B — A New Concept: Adapter and 4C — Why Not Pass Pydantic Objects Into Phase 2.1?**

*An adapter is a tool for making two interfaces that weren't directly designed for communication with each other compatible. It takes the output from one interface and edits it in a way that makes it fit into the input expectations of another interface. It could be described as something that translates representations (but doesn't reimplement inference behavior). As for why the adapter is placed between the Phase 2.1 dataframe and `PredictionRequest`, we want the Phase 2.1 inference to remain usable by multiple different types of software requests (e.g., FastAPI, CLI program, Jupyternotebook, etc.). We don't want require those callers to conform to the FastAPI/Pydantic representation needed to make inference requests.* 

An adapter is a tool for making two interfaces that weren't directly designed for communication with each other adaptable. 

It translates representations but doesn't reimplement inference behavior. It translates the public API representation into the internal inference representation.

We want to maintain transport independence.

### Question 2
What responsibilities belong to `prediction_request_to_history_dataframe()`, and which seemingly related responsibilities must deliberately remain outside that adapter?

**Best sections to review: 4E — Create `adapters.py`, 4F — What This Adapter Actually Does, and 4H — Notice What the Adapter Does NOT Validate**

*`prediction_request_to_history_dataframe()` has the responsibility of converting the public API prediction request into the canonical raw engine history dataframe format that was established in Phase 2.1. `engine_id` gets repeated as `unit_no` for every row and `cycle` gets renamed to `cycles`. As for what remains outside of the adapter, inference-domain validation, feature engineering, artifact loading, and model prediction are all handled elsewhere.*

The adapter performs representation transformation, not semantic validation.

### Question 3
Why do we explicitly convert `PredictionResult` into `PredictionResponse` even though they currently contain the same three fields, and how does that preserve encapsulation between Phase 2.1 and the public HTTP contract?

**Best sections to review: 4I — Create the Response Adapter and 4J — Why Not Just Return `PredictionResult`?**

*This is part of converting the Phase 2.1 inference result into the public API response representation, and we need to establish an architectural boundary that the Phase 2.1 object is not the same thing as the HTTP response object. They belong to different contracts, and our code should account for that. This also helps for the case where Phase 2.1 adds more input fields to the prediction result if that were to happen in the future. We don't want internal changes to accidentally change the public API.*

`PredictionResult` and `PredictionResponse` may currently have identical fields, but they're still conceptually different objects. 

`PredictionResult` comes from the internal Python inference interface. 

`PredictionResponse` comes from the public HTTP API interface.

We retain encapsulation by asking which internal information should cross this boundary. 

### Question 4
Walk through the complete path of one successful `/predict` request from the client to the frozen model and back to the client. Where do Uvicorn, FastAPI, Pydantic, dependency injection, the adapter, and Phase 2.1 each participate?

**Best section to review: 4N — Trace One Request Through the Whole System**

*In Step 1, Uvicorn receives the network request and runs the FastAPI application. In Step 2, FastAPI sees the prediction request, then Pydantic validates the JSON structures and creates the prediction request. In Step 3 we have our dependency injection, FastAPI receives the inference pipeline dependency and resolves it to add it to the app state. In Step 4, the adapter creates the canonical FD001 DataFrame. In Step 5, we run `pipeline.predict(history_df)` that was created in Phase 2.1. In Step 6, the response adapter takes the prediction result and creates a prediction response. In Step 7, that response gets serialized into JSON. In Step 8, the final step, the HTTP response is sent back to the client.*

1. Client sends HTTP POST /predict.

2. Uvicorn receives the network request. 

3. FastAPI routes it to predict_rul().

4. Pydantic validation JSON and creates PredictionRequest.

5. Dependency injection retrieves the existing pipeline from app.state and supplies it to the endpoint. 

6. API adapter converts PredictionRequest into a DataFrame. 

7. Phase 2.1 pipeline validates, engineers features, selects locked features, and predicts. 

8. PredictionResult gets returned. 

9. The response adapter converts the PredictionResult into a PredictionResponse. 

10. FastAPI serializes the response to JSON. 

11. Uvicorn sends the HTTP response to the client.

### Question 5
Why can malformed JSON/schema data be rejected before Phase 2.1 runs while a structurally valid seven-cycle history reaches Phase 2.1 before being rejected, and why is the HTTP handling of the latter intentionally deferred to TG5?

**Best sections to review: 4K — Prediction Checkpoint, 4U — Test One Pydantic Failure in `/docs`, and 4V — What About a 7-Cycle Request?**

*This has to do with the cascade of quality checks we do leading up to making an inference calculation. If JSON/schema data is malformed, the Pydantic will catch it and raise an error before it makes it to Phase 2.1. A structurally valid seven-cycle history will pass through Pydantic and if there are issues then Phase 2.1 will be the step to raise an error. As for why the HTTP handling of the latter is intentionally deferred to TG5, the goal in TG4 was just to set up a successful prediction path. We're not yet at the point where we're creating production-style failure behavior.*

A malformed request such as a missing `sensor_measurement_12` violates the HTTP schema, so Pydantic catches it. 

Pydantic checks for network validity. 

Phase 2.1 checks for inference/domain validity. 

### Additional Questions 

* What is an async function? 

*An async function can volutarily pause while waiting for something, allowing the event loop to work on other tasks instead of blocking that execution path. It's for when you want a program to use waiting time productively.*

* What is Swagger? 

### Ideas to Retain

* The API endpoint shoudl orchestrate translation and delegation: convert the public request into the inference representation, delegate all model-domain work to Phase 2.1, and deliberately translate the internal result back into the public response contract. 

* An adapter translates representations; it should not duplicate the business/domain behavior of either side. 

* Dependency injection retrieves the already-existing application-scoped pipeline and supplies it to the endpoint; it does not create or store the pipeline. 

* `async` allows efficient progress during waiting; it is not a magic accelerator for CPU-bound computation. 

* OpenAPI describes an API; Swagger UI provides an interactive interface for exploring that description. 

* FastAPI automatically generates the OpenApi information that powers `/docs` Swagger UI. 