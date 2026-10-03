## Phase 2.2 — Task Group 1 Active Recall

### Question 1
What role does Pydantic play between incoming JSON and our Python endpoint code, and what advantage does this provide over manually validating every request field inside the endpoint?

**Best sections to review: 1A — Where We Are and 1B — What Pydantic Does**

*Pydantic is useful because it performs the network-schema work for us. It does this by describing expected data using Python classes. Pydantic and FastAPI wind up cooperating to carry out the following sequence of events: incoming JSON -> parse JSON -> validate against PredictionRequest -> construct Python object -> only then call endpoint function*

### Question 2
Why does the public `PredictionRequest` contain the `engine_id` once at the request level while individual `EngineObservation` objects contain cycle/settings/sensors, and how will this eventually map to Phase 2.1's dataframe representation?

**Best sections to review: 1D — Design the Public Prediction Request and 1F — Define One Engine Observation**

*Because we can avoid repeating the `engine_id` many times at the `PredictionRequest` level. The client gets to put less work into the request that they send, plus we can do a simple data reformatting to make a single instance of `engine_id` get repeated on each row of data to get it in a form that will be compatible with the model.*

### Question 3
What is the difference between Pydantic/API-schema validation and Phase 2.1 domain validation, and why can a request with duplicate or non-contiguous cycles legitimately pass the first layer but fail the second?

**Best sections to review: 1K — Pydantic Validation Is NOT Phase 2.1 Validation and 1L — A Concrete Two-Layer Example**

### Question 4
Why do we use `extra="forbid"`, and why are we deliberately avoiding duplicating rules such as the 10-cycle minimum and contiguous-cycle requirement inside Pydantic?

**Best sections to review: 1J — Why `extra="forbid"`? and 1R — Why Not Put All Domain Rules in Pydantic?**

### Question 5
What do `model_validate()`, `model_dump()`, and `model_dump_json()` do, and how will FastAPI eventually use these kinds of schema/serialization capabilities to turn network requests into Python objects and Python results back into HTTP responses?

**Best sections to review: 1M — Preview: What FastAPI Will Eventually Do and 1P — `model_validate`, `model_dump`, and `model_dump_json`**

### Ideas to Retain 

* Pydantic protects the HTTP boundary by verifying that incoming data has the declared network structure; Phase 2.1 remains the authoritative judge of whether that structurally valid data is a legal inference request.