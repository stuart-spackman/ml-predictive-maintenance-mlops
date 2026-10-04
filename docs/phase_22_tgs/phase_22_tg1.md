## Phase 2.2 — Task Group 1 Active Recall

### Question 1
What role does Pydantic play between incoming JSON and our Python endpoint code, and what advantage does this provide over manually validating every request field inside the endpoint?

**Best sections to review: 1A — Where We Are and 1B — What Pydantic Does**

*Pydantic is useful because it performs the network-schema work for us. It does this by describing expected data using Python classes. Pydantic and FastAPI wind up cooperating to carry out the following sequence of events: incoming JSON -> parse JSON -> validate against PredictionRequest -> construct Python object -> only then call endpoint function*

Pydantic lets us describe the structure we expect rather than manually writing procedural validation for every field.

### Question 2
Why does the public `PredictionRequest` contain the `engine_id` once at the request level while individual `EngineObservation` objects contain cycle/settings/sensors, and how will this eventually map to Phase 2.1's dataframe representation?

**Best sections to review: 1D — Design the Public Prediction Request and 1F — Define One Engine Observation**

*Because we can avoid repeating the `engine_id` many times at the `PredictionRequest` level. The client gets to put less work into the request that they send, plus we can do a simple data reformatting to make a single instance of `engine_id` get repeated on each row of data to get it in a form that will be compatible with the model.*

Instead of saying "compatible with the model," it would be an improvement to say "compatible with the Phase 2.1 inference contract."

### Question 3
What is the difference between Pydantic/API-schema validation and Phase 2.1 domain validation, and why can a request with duplicate or non-contiguous cycles legitimately pass the first layer but fail the second?

**Best sections to review: 1K — Pydantic Validation Is NOT Phase 2.1 Validation and 1L — A Concrete Two-Layer Example**

*A principle at play here is that Pydantic validation is not the same thing as Phase 2.1 validation. Pydantic can be used for things such as confirming the existence of values and checking their datatypes, but it does not come with the ability to check domain rules, e.g., no repeated cycles. In the sequences of events we're trying to create, first JSON gets sent in. Then Pydantic checks if the JSON is shaped like a prediction request in the way we need. Then Phase 2.1 validation checks if the input could be considered a fully legal engine history. If a cycle is missing, for example, that will make it through the first layer because no data shape rules were broken, but then it failes the second layer because a domain rule was broken.*

It's worth noting that Pydantic does have the capability of enforcing sophisticated domain rules, through custom validators. But the reason we don't do that is architectural. 

Pydantic is capable of domain validation, but in our architecture we deliberately use it primarily for the network schema and leave inference-domain rules to Phase 2.1. 

### Question 4
Why do we use `extra="forbid"`, and why are we deliberately avoiding duplicating rules such as the 10-cycle minimum and contiguous-cycle requirement inside Pydantic?

**Best sections to review: 1J — Why `extra="forbid"`? and 1R — Why Not Put All Domain Rules in Pydantic?**

*Because there is such a thing as a validation system that simply ignores unknown fields instead of flagging them for breaking the validation scheme. For added assurance we need to make sure any extra fields will raise a flag. Meanwhile having duplicated rules is undesirable because it creates two different rules to manage and account for whenever updates to rules are made. A failure to properly update both layers could result in a situation where a rule gets broken in one layer and isn't caught until the second layer.*

Avoid maitaining two different sources of truth for the same domain rule. 

### Question 5
What do `model_validate()`, `model_dump()`, and `model_dump_json()` do, and how will FastAPI eventually use these kinds of schema/serialization capabilities to turn network requests into Python objects and Python results back into HTTP responses?

**Best sections to review: 1M — Preview: What FastAPI Will Eventually Do and 1P — `model_validate`, `model_dump`, and `model_dump_json`**

*`model_validate()` takes raw input data that we do not trust yet and uses it to contruct a valid `PredictionRequest`, i.e., it takes a dictionary and puts it through the validation scheme so it can turn into a `PredictionRequest`. `model_dump()` takes a Pydantic object and converts it back into ordinary Python data, so if we run `response.model_dump()` a dictionary gets returned. `model_dump_json()` works similarly to `model_dump()`, only now the returned object has been serialized into JSON text.*

`model_validate()` -> untrusted/raw Python data -> validate -> PredictionRequest object
`model_dump()` -> Pydantic object -> ordinary Python representation -> usually dict
`model_dump_json()` -> Pydantic object -> serialized JSON text

It's worth noting that FastAPI will normally automate much of this for us.

### Ideas to Retain 

* Pydantic protects the HTTP boundary by verifying that incoming data has the declared network structure; Phase 2.1 remains the authoritative judge of whether that structurally valid data is a legal inference request.

* Pydantic provides declarative validation of the HTTP data contract. 

* The API representation does not have to match the internal DataFrame representation exactly; Phase 2.2 can translate between them. 

* Pydantic can enforce domain rules, but we deliberately leave the authoritative inference-domain rules in Phase 2.1 to avoid duplicated sources of truth. 

* `extra="forbid"` prevents clients from silently sending fields outside the documented contract. 

* `model_validate()` moves raw data into a validated Pydantic object; `model_dump()` moves back to ordinary Python data; `model_dump_json()` serializes to JSON.

* FastAPI will automate much of the request-validation and response-serialization lifecycle using these schemas. 