## Phase 2.2 — Task Group 7 Active Recall

### Question 1
What is the final public interface produced by Phase 2.2, and why should an external client need to understand that HTTP contract but not the internal Phase 2.1 feature-engineering or model machinery?

**Best sections to review: 7B — The Public Phase 2.2 Interface and 7C — The Final Responsibility Boundary**

*The final public interface produced by Phase 2.2 is the network interface that has now been exposed. It contains: GET /health, GET /metadata, and POST /predict. As for why an external client needs to understand the HTTP contract but not the internal Phase 2.1 feature-engineering or model machinery, it's because those internal features of our system have been encapsulated. We have done what's referred to as encapsulation at the service level.*

The final public service interface is: GET /health, GET /metadata, POST predict

An external client needs to understand: POST /predict -> what JSON to send -> what JSON will be sent back -> what status codes might be received

An external client does not need to know: rolling windows, feature lags, joblib, etc. Therefore we encapsulate our service.

### Question 2
Why do we rerun both the Phase 2.2 API tests and the earlier Phase 2.1 architectural audit before handoff, and what dependency-direction regression are we specifically trying to prevent?

**Best sections to review: 7D — First Run the Full Test Suite and 7E — Re-run the Phase 2.1 Architectural Audit**

*The principle at play here is that we added a new HTTP layer and we want to confirm it works. We need to make sure that adding it did not silently break the already established inference subsystem. As for the dependency-direction regression that we are specifically trying to prevent, we want to confirm that the inference package does not depend on FastAPI. FastAPI is expected to depend on the inference package, but not the other way around.*

We're checking that Phase 2.2 works and that Phase 2.1 still works. We need to confirm that FastAPI depends on Phase 2.2 but not the other way around. 

### Question 3
What is the difference between the detailed pytest suite, the Phase 2.2 handoff audit script, and the Uvicorn-backed smoke scripts? What distinct type of confidence does each provide?

**Best sections to review: 7P — Why Have Both Tests and an Audit Script? and 7Q — Perform One Final Real-Network Smoke Check**

*A detailed pytest suite is something that should offer detailed regression protection, many focused assertions, and perhaps most importantly should be automatically reusable by CI. As for a handoff audit, it should offer one high-level integration checkpoint, demonstrate the major service capabilities together, and its usefulness peaks before declaring a phase handoff. Test suites make us confident that our individual contracts are functioning as intended while handoff audits make us confident that the subsystem we just got done assembling is coherent (and that we're ready to move on to the next phase). Finally, the Uvicorn-backed smoke scripts test real Uvicorn/TCP wiring. Some of our tests use `TestClient`, which means our testing is done without the real API and HTTP connection being active. By using Uvicorn-backed smoke scripts, we can check the function of our application while a real connection is active.*

The FastAPI application itself is real during a `TestClient` test. What's missing is the real external server/network layer. 

TestClient: real FastAPI app, real routing, real Pydantic, etc. 

Uvicorn smoke test: real Uvicorn process, real TCP/HTTP connection, real FastAPI app

pytest gives detailed repeatable regression evidence, the handoff audit gives assembled subsystem coherence, Uvicorn smoke test gives real server/network integration.

### Question 4
What can we legitimately claim after completing Phase 2.2, and why do successful HTTP responses still provide no evidence by themselves about predictive performance or model drift?

**Best sections to review: 7S — What Phase 2.2 Can Now Legitimately Claim and 7T — What Phase 2.2 Does NOT Claim**

*With the successful completion of Phase 2.2 we can now legitimately claim that the frozen Phase 1 model can be accessed through a validated, tested FastAPI HTTP service. This service was built on top of the reusable Phase 2.1 inference subsystem. The services currently provide things like defined HTTP contracts and Pydantic request/response validation. As for why successful HTTP responses still provide no evidence by themselves about predictive performance or model drift, we have not built a contract of any sort that measures those aspects of our application's responses to the client. We have only built the application around semtantically sound inputs and outputs.*

The frozen Phase 1 model can be accessed through a validated, tested FastAPI HTTP service ... built on top of the reusable Phase 2.1 inference subsystem.

We can establish some semantic validity through Phase 2.1, but even a completely valid inference request and successful response don't tell us whether the model is performing well statistically.

Transport/software correctness is not evidence of predictive performance.

### Question 5
Describe the final dependency chain from Phase 2.2 to Phase 2.1 to Phase 1. What does each layer own, and why is keeping those responsibilities separate valuable?

**Best sections to review: 7C — The Final Responsibility Boundary and 7U — The Finished Phase 2.2 Architecture**

*Phase 2.2 receives and HTTP request and does the necessary steps to give back an HTTP response. In cases of known inference errors, it also gives back an HTTP exception translation. Phase 2.1, which Phase 2.2 depends on, does raw history validation in the input before a series of other steps that eventually leads to returning an RUL prediction. Then with Phase 1, which Phase 2.1 depends on, the selected and frozen fitted model gets chosen and put to work for our application.*

*As for describing this with more of a layerd approach, we can think of the layers as moving along: client/http layer -> Phase 2.2 FastAPI layer -> Phase 2.1 inference layer -> Phase 1 model layer. Keeping these separate is valuable because their implementations can remain encapsulated, reusable, and independently testable.*

Phase 1 tells us the model we should trust. 

Phase 2.1 tells us how we can safely use that trusted model. 

Phase 2.2 tell us how outside programs can use that inference capability over HTTP. 

The separation of these layers gives us encapsualtion, reuse, and independent testability.

### Additional Help Needed

* What is encapsulation?

*Encapsulation means hiding internal implementation complexity behind a controlled public interface.*

* What is CI? Is it usually paired in the term CI/CD?

*CI (Continuous Integration) is the practice of automatically checking code changes as they are integrated into the shared codebase.*

### Ideas to Retain

* Encapsulation = expose a controlled interface while hiding implementation complexity from consumers. 

* Encapsulation reduces coupling because consumers depend on behavior rather than internal machinery. 

* Phase 1 selects and freezes the model; Phase 2.1 safely performs inference with it; Phase 2.2 exposes that inference over HTTP. 

* Software/HTTP success is not evidence of predictive performance. 

* CI = continuous integration: automatically verify code as changes are integrated. 

* CI/CD commonly means continuous integration plus continuous delivery or continuous deployment. 

* Delivery means "ready to release"; deployment usually means "actually released automatically." 