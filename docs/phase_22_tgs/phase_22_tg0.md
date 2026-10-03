## Phase 2.2 — Task Group 0 Active Recall

### Question 1
What different responsibilities do FastAPI and Uvicorn have, and how do they work together to make our Python application accessible over HTTP?

**Best sections to review: 0B — What FastAPI Actually Does and 0C — FastAPI vs Uvicorn**

*FastAPI is the framework responsible for the HTTP-facing portion of the application. Uvicorn is the server process that actually runs the FastAPI application and listens for network requests. Conceptually what's going on here is that the browser/client sends off HTTP text, Uvicorn notices that HTTP text has just been sent and gives the HTTP text to FastAPI, and then FastAPI gives the text to our Python code. An analogy here is that FastAPI is the restaurant operation; Uvicorn opens the building, listens at the front door, and routes arriving customers to it.*

A cleaner mental model is that Uvicorn handles the network/server side while FastAPI handles the web-application side.

FastAPI defines the web application—its routes, request handling, validation, and responses. Uvicorn is the ASGI server that listens for network requests and runs the FastAPI application. Uvicorn handles the server/network boundary, while FastAPI determines what the application should do with each request.

### Question 2
What does `predictive_maintenance.api.main:app` mean in the Uvicorn startup command, and what role does the FastAPI `app` object play?

**Best sections to review: 0G — What Is the `app` Object? and 0H — Start the Server**

*`predictive_maintenance.api.main:app` creates a situation where the command line gets told to find a Python module in the form of `predictive_maintenance.api.main` and then go looking for an object named `app` inside that module. As for the `app` object, it represents the web application that Uvicorn should run.*

There are two pieces. `predictive_maintenance.api.main` is the Python module to import. `app` is the object inside that module to serve.

### Question 3
What is an API contract, and how is the Phase 2.2 HTTP API contract different from—but layered on top of—the Phase 2.1 Python inference contract?

**Best sections to review: 0R — A New Concept: API Contract and 0S — Python Interface vs HTTP Interface**

*While Phase 2.1 had an inference contract, Phase 2.2 has an API contract. An API contract answers important questions related to the following topics: which endpoints exist, which HTTP methods they use, what input shapes /predict accepts, what output shapes /predict returns, and what error/status codes are possible. As for how the HTTP API contract is different from but layerd on top of the Phase 2.1 Python inference contract, the HTTP contract is upstream from the inference contract. The clients that are using the application don't need to know the inference contract, but they do need to know the HTTP contract. The flow is something like: client -> HTTP contract -> FastAPI -> inference contract.*

It's worth noting that some inference constraints will be reflected through the API contract.

With the Phase 2.1 contract we contained domain and model rules. Then that gets adapted into the Phase 2.2 API contract, which exposes only the portions the clients need to obey.

The HTTP contract wraps and translates the Python capability rather than exposing its internals.

### Question 4
Why are we deliberately planning a small service surface such as `GET /health`, `GET /metadata`, and `POST /predict` instead of exposing the internal feature-engineering and model machinery through many endpoints?

**Best sections to review: 0M — Why Plan Endpoints Before Implementing Them? and 0S — Python Interface vs HTTP Interface**

*The principle at play here is that more endpoints are not automatically better. Every endpoint becomes part of the service interface, and once clients start depending on an endpoint, changing it might break their process for using the application. Our goal is to expose the smallest interface that satisfies the application's current responsibilities.*

### Question 5
Why must Phase 2.2 depend on Phase 2.1 rather than allowing the Phase 2.1 inference package to depend on FastAPI?

**Best sections to review: 0A — The Architectural Transition and 0L — Define the Phase 2.2 Service Contract**

*Phase 2.2 is upstream from Phase 2.1 in the application's process for providing inferences. Our architectural goal is to have HTTP relay into FastAPI, which then relays into the contents of Phase 2.1. Having Phase 2.1 depend on FastAPI would make that process take place out of order.*

Dependency direction is less about chronological execution and more about architectural independence.

Higher-level transport/application layers may depend on the resuable inference capability, while the inference capability should remain independent of those delivery mechanisms.

Phase 2.2 should depend on Phase 2.1 because FastAPI is a delivery layer for an already-existing inference capability. Keeping Phase 2.1 independent of FastAPI makes inference transport-independent, reusable, and easier to test. If inference depended on FastAPI, model-serving logic would become unnecessarily coupled to one HTTP framework.

### Ideas to Retain

* FastAPI is becoming a network-facing adapter around the inference capability we already build—not a new place to rebuild that capability.

* FastAPI defines web-application behavior; Uvicorn runs that application and handles the server/network boundary. 

* `module:app` means "import this module and serve this application object."

* The HTTP API contract exposes only the externally relevant portions of the underlying inference behavior. 

* A small service surface reduces coupling and long-term compatibility burden. 

* FastAPI should depend on inference; inference should not depend on FastAPI. 

* Dependency direction is about reuse and architectural independence, not merely execution order.