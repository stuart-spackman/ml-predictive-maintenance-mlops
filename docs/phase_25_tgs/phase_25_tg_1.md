## Phase 2.5 — Task Group 1 Active Recall

### Question 1
What responsibility does the demo API client own, why should it communicate through real HTTP rather than import FastAPI route functions or the inference pipeline, and why do we separate `demo/client.py` from the eventual Streamlit `demo/app.py`?

**Best sections to review: 1A — What Is an API Client?, 1B — Why Not Put HTTP Calls Directly in `app.py`?, 1C — Reuse the Existing API Contract, Not Its Implementation, and 1D — Should the Frontend Import the Backend's Pydantic Schemas?**

*The demo API client has the responsibility of using its public interface to communicate with the inference service that we created in the previous phases of this project. It should communicate through real HTTP rather than import FastAPI route functions or the inference pipeline because we don't want `app.py` to get overloaded with responsibilities. The best delegation is one where `demo/client.py` is built to communicate with FastAPI and `demo/app.py` is built to interact with the user. A goal here is to make sure the client experiences the backend the same way any external consumer would.*

`demo/app.py` -> interacts with the human

`demo/client.py` -> interacts with FastAPI

FastAPI -> interacts with inference

HTTP is the service boundary that we intentionally created.

The client experiences the backend the same way any external consumer would.

### Question 2
What are the differences among a transport failure, an HTTP/API failure, and a protocol/response failure? Give an example of each and explain why collapsing all three into a generic "connection error" would produce misleading frontend behavior.

**Best sections to review: 1I — Timeouts Are Part of the Client Contract, 1J — Three Failure Layers, 1Q — Transport Error Translation, 1R — HTTP Errors Are Not Connection Errors, and 1U — JSON Parsing on Success**

*A transport failure occurs when the client could not successfully complete communication with the service. Examples are in the following list: connection refused, DNS failure, timeout, network unavailable.*

*An HTTP/API failure occurs when the client was able to establish communication but the backend rejected the input that was provided. Examples included 422, 500, and 404 errors. This is distinctly not a case where nothing was listening to the client and the connection attempt was refused.*

*A protocol response failure occurs when communication was established and a successful status code was achieved, but the response violated what the client was expecting via the contract/protocol. An example could be server returning HTTP 200 but the response not being in the form of valid JSON.*

*As for why collapsing all three into a generic "connection error" would produce misleading frontend behavior, we need to distinguish HTTP failures from successful HTTP status paired with an unusable response. Collapsing all three into a single error classification would make us unable to distinguish failure semantics.*

Transport failure: 
-> couldn't successfully communicate
-> connection refused, timeout, DNS failure

HTTP/API failure: 
-> communication succeeded; server returned 4xx/5xx
-> 422, 404, 500

Protocol failure: 
-> communication succeeded and status looked successful, but the response violated the expected contract
-> 200 + invalid JSON

HTTP/API failure doesn't necessarily mean the backend rejected the input (but that is true for 422 errors). 
404 -> resource/path problem
500 -> server-side failure
The server successfully returned an HTTP response whose status represents failure.

### Question 3
Why do we define a demo-specific error hierarchy rather than reuse `InferenceError` classes in the frontend client? Explain what happens conceptually when a backend `InferenceInputError` becomes an HTTP response and then a client-side error.

**Best sections to review: 1K — Client Error Taxonomy, 1L — Why Not Reuse `InferenceError`?, 1S — Parse Public Error Responses, and 1T — Pydantic's Default 422 Is a Special Case**

*In the frontent client we define a demo-specific error hierarchy rather than reuse `InferenceError` classes because there's a service boundary we want to respect. `InferenceError` error classes are a for backend domain errors. For the demo we are on the frontend where the client sees network behavior, HTTP status, and public response body. Dealing with different domains warrants creating different error classes.*

*As for what happens conceptually when a backend `InferenceInputError` becomes an HTTP response and then a client-side error, an architectural issue gets created. A remote client cannot catch `InferenceInputError` if it is thrown inside another process. A remote client sees `HTTP 422` paired with a response body. The principle at play here is that exceptions do not magically cross process/network boundaries.*

`InferenceError` hierarchy -> backend/domain language

`DemoClientError` hierarchy -> client/network/API language

The client does not catch the original `InferenceInputError` because that Python exception exists inside a different process.

Exceptions do not cross process/network boundaries. Their meaning must be represented through the protocol.

### Question 4
Why should API location and timeout be configurable at the client boundary, what role does `create_default_api_client()` play relative to `PredictiveMaintenanceAPIClient`, and how is this similar to the factory pattern already used for the Phase 2.1 inference pipeline?

**Best sections to review: 1G — Client Configuration, 1H — Base URL Normalization, 1I — Timeouts Are Part of the Client Contract, 1Z — Configuration Factory, and 1AA — Why a Factory Helps**

*API location should be configurable because we want to remain flexible for modifications in future build locations without modifying source code. API timeout should be configurable at the client boundary because we want to embody the principle that a UI-facing network request should never be allowed to wait forever.*

*When dicussing `PredictiveMaintenanceAPIClient`, the role played by `create_default_api_client()` is that the former can be thought of as a class or a configurable implementation while the later can be thought of as a factory with default application wiring. As for how this is similar to the factory pattern already used for the Phase 2.1 inference pipeline, classes are configurable implementations while factories are default application wirings.*

`PredictiveMaintenanceAPIClient` -> configurable capability

`create_default_api_client()` -> default application wiring

### Question 5
How should the client be tested before Streamlit is introduced, why should client tests substitute the HTTP transport rather than instantiate the real inference pipeline, and what additional evidence is provided by a real client-to-Dockerized-FastAPI smoke test?

**Best sections to review: 1AC — Test the Client Without Real FastAPI First, 1AD — Mock at the Network Boundary, Not the Inference Boundary, 1AE–1AH — Success and Failure Tests, and 1AL–1AM — Real Integration Smoke Tests**

*Before Streamlit is introduced, the client should be tested from the network boundary, not the inference boundary. The boundary directly beneath the demo client is the HTTP transport system. Confirming that the HTTP transport system is working does not require invoking the inference pipeline, so we don't want to make the client's tests unnecessarily dependent on the inference pipeline either.*

*As for why the client tests should substitute the HTTP transport rather than instantiating the real inference pipeline, that would make the client unit test dependent on artifacts, features, the model, and inference. Those parts of the system have already been tested and validated and we don't want to add another layer of testing that becomes dependent on systems that were already verified. The scope of our client testing can remain narrow enough to not include those components of the system.*

*A real client-to-Dockerized-FastAPI smoke test provides correct input-to-output evidence. When a CSV of raw engine history is provided, a payload of valid RUL is sent to the client. The sequence of events we want evidence for proper functioning is:*
*known-valid API payload -> `PredictiveMaintenanceAPIClient.predict()` -> read HTTP gets sent -> containerized API -> valid prediction response* 

System under tests -> demo client

Immediate lower boundary -> HTTP transport

We substitute/mock the HTTP behavior when doing narrow client tests.

The client sends engine history request data and receives a prediction response containing the estimated RUL.

Mocked client test -> Does the client interpret controlled HTTP behavior correctly? 

real smoke test -> Can this client actually communicate across the real network boundary with our containerized service? 

### Help Needed

* What is `httpx`? 

*`httpx` is a Python HTTP client library. It lets Python code act like a client that sends HTTP requests to web services and recieves HTTP responses.*

*`PredictiveMtaintnanceAPIClient` -> uses -> httpx -> sends HTTP -> FastAPI*

*httpx -> general-purpose HTTP client*

*FastAPI -> HTTP server/application framework*

*httpx asks; FastAPI answers*

* What does the `-m` mean in Python command line code?

*The `-m` means run a Python module as a program.*

*`python -m X` means "use this Python interpreter to execute module X."*

* What is a factory in this context?

*A factory is code whose job it is to construct and configure another object for you.*

* What is a factory pattern? 

*The factory pattern is the broader software design idea of moving object-construction decisions into a dedicated factory instead of requiring every consumer to know how to build the object.*

*Centralize default object construction so callers depend on the capability rather than duplicating its wiring.*

### Ideas to Retain

* `httpx` lets Python act as an HTTP client; FastAPI acts as the HTTP service.

* `python -m X` means use this specific Python interpreter to execute module `X`.

* A factory contructs/configures an object; the object itself provides the capability.

* A factory pattern centralizes construction knowledge so every consumer does not have to duplicate wiring.

* Backend exception -> public HTTP representation -> client-side exception is intentional translation across a service boundary.

* Mocked client tests establish client behavior; the real Docker smoke test establishes that the new client works across the actual HTTP/runtime boundary.