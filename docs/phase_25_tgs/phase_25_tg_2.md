## Phase 2.5 — Task Group 2 Active Recall

### Question 1
Describe the complete responsibility chain among `demo/app.py`, `demo/adapters.py`, `demo/client.py`, FastAPI, the inference pipeline, and the frozen model. Why is keeping CSV adaptation separate from both the Streamlit UI and the HTTP client useful?

**Best sections to review: 2A — What TG2 Actually Adds, 2B — Add `app.py` and an Input Adapter, 2C — Why Add `adapters.py`?, and 2AM–2AN — Why This Matters for MLOps / A Powerful Test of Architecture**

*Within our demo package, we now have:*

*`demo/app.py` is responsible for implementing the Streamlit UI.*

*`demo/adapters.py` is responsible for taking any inputs with a CSV/DataFrame representation and then converting them into the API request representation.*

*`demo/client.py` is responsible for taking an API request, sending it to the server via HTTP, and making the HTTP response available for the client to examine.*

*FastAPI is the service that takes HTTP requests and delivers them to the inference pipeline. From there, once the inference pipeline has an output, FastAPI then delivers that output back to the client.*

*The inference pipeline takes HTTP payloads that were sent as input, feeds them to the trained model, examines the output for contract violations, and then potentially sends the payload in the form of an RUL prediction back to the client.*

*The frozen model is the part of the pipeline that actually does the RUL calculations.*

*As for why keeping CSV adaptation separate from both the Streamlit UI and the HTTP client is useful, this goes back to the fact that we don't want to overload `app.py` with responsibilities. If we keep the sequence of events for getting CSV files to be `app.py` then `adapters.py` then `client.py`, we let each layer stay small. The principle at play here is that adapters translate representations without owning domain behavior.*

`app.py` -> human interaction / presentation

`adapters.py` -> representation translation

`client.py` -> HTTP communication

FastAPI -> public service contract

inference pipeline -> inference correctness

frozen model -> learned prediction mapping

The inference pipeline does not know about HTTP payloads.

HTTP JSON request
-> FastAPI/Pydantic
-> API adapter
-> raw engine-history representation
-> inference pipeline
-> feature engineering + artifact/model-contract checks + prediction
-> PredictionResult
-> FastAPI response schema
-> HTTP JSON response

The inference layer doesn't know whether its input ultimately same from Streamlit, curl, a model application, etc.

The frozen model is more precisely the component containing the learned mapping from model features to estimated RUL. 

The pipeline does substantially more than merely feed a payload into it. 

### Question 2
What is the difference between representation-level frontend validation and authoritative inference-domain validation? Why is checking that a CSV represents one engine appropriate in the adapter, while minimum-history, cycle-contiguity, and model-contract checks should remain on the backend?

**Best sections to review: 2D — The CSV Contract, 2E — CSV Representation vs API Representation, 2G — Build the CSV Adapter, 2H — Why Does the Adapter Check for One Engine?, and 2AE–2AF — Backend Rejection vs Bad CSV Representation**

*Representation-level fronend validation is checking that a CSV input represents one engine across multiple cycles. All it does is take one way of showing an engine history and changes it into another way of showing engine history without adding or removing information. We simply check that the UI did not change information.*

*Authoritative inference-domain validation is ensuring that the input data is valid within the domain of the inference pipeline. Here instead of checking representation, we go a layer deeper and confirm that the data that was provided meets the requirements stated by the inference contract (e.g., no infinite values, no cycle gaps, etc.).*

*As for why checking that a CSV represents one engine is appropriate in the adapter, while at the same time minimum-history, cycle-contiguity, and model-contract checks should remain on the backend, the fronend concerns itself with checking if the one-engine request representation can be created from the CSV file. This is different from the deeper concerns of checking for cycles not being contiguous, history being too short, or NaN/domain failures. Those should remain backend concerns wherever possible.*

Can this input be faithfully converted into the representation required by the next boundary? 

### Question 3
Explain Streamlit's role as a rerunning UI application and why we use a session-scoped cached API client. What exactly are we caching, what are we deliberately not caching in Streamlit, and why is intentional resource cleanup useful?

**Best sections to review: 2J — Streamlit's Execution Model Matters, 2K — Cache the API Client, Not the Model, 2L — Create `app.py`, and 2M — Create the Session-Scoped Client**

*To begin with, it's worth noting that Streamlit applications are Python scripts that rerun as users interact with widgets. Because of this, we don't want every rerun to unnecessarily create another long-lived HTTP client. It makes sense to cache the httpx-based API client but not anything deeper down the data process such as the RandomForest model, joblib artifacts, or the inference pipeline, which are best left inside the FastAPI process. Finally, intentional resource cleanup is useful because it fits in with good lifecycle management and keeping a synchronous HTTP client functioning properly.*

Streamlit reruns script
-> don't reconstruct unnecessary long-lived resource every rerun
-> cache HTTP client for session

Stream lit caches: 
httpx API client

Streamlit does NOT cache: 
RandomForest
joblib model
inference pipeline 
artifact state
(These belong to the FastAPI process.)

`httpx.Client` owns resources such as its connection pool. Calling `client.close()` lets it release those resources intentionally when we're finished with it.

### Question 4
Walk through how the Streamlit application should distinguish no input, CSV parsing/adaptation errors, connection failures, HTTP 422/500 responses, protocol failures, and successful predictions. Why is preserving these failure semantics better than catching every exception and displaying one generic error?

**Best sections to review: 2N–2U — Backend Status Through HTTP Error Presentation, 2AL — The User-Facing Failure Model, and 2AO — What TG2 Legitimately Establishes**

*Not having any input would keep us in the normal UI state, where no requests are currently processing.*

*CSV parsing/adaptation errors would also fall into the category of `DemoInputError`, a case where the front end couldn't construct the necessary request representation. Streamlit would be expected to treat this as a presentation/input problem.*

*In the case of a connection failure, we would expect the Streamlit application to display a 500 error code with a `DemoInputError`.*

*In the case of 422/500 responses, that would mean a user-correctable request problem was found or the service could not complete the request respectively. We would expect the Streamlit application to display each of these to the user with a `DemoAPIError`.*

*For protocol failures, we would expect a 200 return code but a `DemoProtocolError` would be paired with it.*

*As for successful predictions, here we would expect a 200 return code with a display of the estimated RUL calculated by the model.*

*Preserving these failure semantics is important because it can tell users and developers what went wrong instead of simply stating that something went wrong. It allows us to not start from zero when it comes to investigating a problem.*

CSV parser can't read file
-> pandas parsing exception
-> `app.py` handles it correctly

CSV was parsed, but can't form our API request
-> DemoInputError

A connection failure is `DemoConnectionError` and usually has no HTTP status at all.

Streamlit -> tries connection -> 127.0.0.1:8000 -> nothing listening
Therefore there cannot be HTTP 500.
transport failure != HTTP failure

The correct taxonomy is: 

No file -> normal UI state

Malformed/unreadable CSV -> parsing / presentation error

Parsed CSV can't form request -> `DemoInputError`

Connection refused / timeout / DNS problem -> `DemoConnectionError` -> potentially no HTTP status whatsoever

HTTP 422 -> `DemoAPIError` -> user request / problem

HTTP 500 -> `DemoAPIError` -> service-side problem

HTTP 200 + invalid / missing expected response -> `DemoProtocolError`

Valid HTTP 200 response -> display estimated RUL

You can only have an HTTP error status if HTTP communication succeeded far enough for the server to return an HTTP response.

### Question 5
Why should the frontend display the returned value as an estimated RUL rather than a guaranteed failure time, why should it not invent a confidence percentage or safe/warning/danger thresholds, and why must Streamlit not clamp or otherwise modify backend predictions?

**Best sections to review: 2V — Display the Prediction, 2W — Say “Estimated,” Not “Will Fail In”, 2X — Lightweight Response Validation, and 2Y — Don't Revalidate the Prediction in Streamlit**

*The front end should display the returned value as an estimated RUL rather than a guaranteed failure time because in testing our model we did not find perfect predictive accuracy across all data. Our model does not provide guarantees, only estimates based on the training data.*

*The front end display should not invent a confidence percentage or safe/warning/danger thresholds because those have not been defined or validated at this point in the project. That would create a situation where the front end would be claiming something that the model did not earn.*

*Streamlit must not clamp or otherwise modify backend predictions because any such activity would violet the contracts that were established for the back end processing. The principle at play here is that we want the UI to display the service result, nothing more. The front end doesn't get to reinterpret the model.*

The front end would be claiming something that the model did not earn.

negative prediction from service != frontend permission to change it

If we decide to enforce `RUL >= 0` that decision should be evaluated, specified, tested, and implemented at the appropriate inference / service boundary—not sliently invented in Streamlit.

### Question 6
What evidence do adapter tests, client tests, the real Streamlit-to-Dockerized-FastAPI system test, and GitHub Actions each provide? Why do we add `[demo]` to the CI development environment while deliberately keeping Streamlit out of the FastAPI Docker runtime?

**Best sections to review: 2I — Test the Adapter Before the UI, 2AG–2AK — Testing and CI, 2AC–2AF — End-to-End and Failure Tests, and 2AP — TG2 Completion Audit**

*Adapter tests, client tests, the real Streamlit-to-Dockerized-FastAPI system test, and GitHub actions each provide tests along the path of end-to-end functioning. We want to make sure our first complete human-facing prediction chain is functioning as intended.*

*We add `[demo]` to the CI development environment while deliberately keeping Streamlit out of the FastAPI Docker runtime because Streamlit is not part of the FastAPI runtime. We want to continue preserving the paradigm we've created where the CI environment tests all current source capabilities and the backend image contains only the backend runtime.*

Adapter tests
-> Does CSV / DataFrame
-> API representation behave correctly? 

Client tests wiht substituted HTTP transport
-> Does the client correctly interpret HTTP successes / failures without needed the real backend? 

Real Streamlit -> Dockerized FastAPI test
-> Does the assembled human-facing system actually work across real process / network / runtime boundaries? 

GitHub Actions
-> Can a clean machine reconstruct the declared environment and repeatedly execute our automated quality contract?

CI environment
-> needs dev + demo capabilities because it verifies repository code

FastAPI Docker image
-> needs only dependencies required to actually run FastAPI inference

### Help Needed 

* What does `-p` do when calling the `mkdir` command? Also, while we're on this topic, how do I create a directory and `cd` into that directory with the same single command? 

*The `-p` can be thought of as `parents`. Adding it creates any parent directories above the lowest child directory we're making.*

*A useful shell pattern to remember is `command_1 && command_2`, which means "Do command 2 only if command 1 succeeds."*

* What does runtime exactly mean in this context?

*In the context of this project, runtime refers to what is required while a particular application is actually executing.*

*FastAPI runtime != entire development environment*

*A runtime environment is the software, configuration, resources, and dependencies required for an application to execute its intended behavior, as distinct from tools needed for development, testing, building, or analysis.*

### Ideas to Retain

* Transport failure can occur without any HTTP status code because no HTTP response may ever have been received.

* Parsing failure and representation-adaptation failure are related but not identical.

* An inference pipeline should not know that its caller happened to use HTTP.

* Different test scopes provide different evidence; they aren't merely redundant ways to test the same thing. 

* `mkdir -p` creates missing parent directories and tolerates already-existing directories.

* `A && B` means execute B only if A succeeds.

* Runtime means what a particular application needs while actually executing; development and test tooling need not belong to that runtime.