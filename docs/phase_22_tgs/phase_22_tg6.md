## Phase 2.2 — Task Group 6 Active Recall

### Question 1
What does FastAPI's `TestClient` allow us to test, and how is an in-process `TestClient` API test different from the Uvicorn-backed smoke scripts we used in TG4 and TG5?

**Best sections to review: 6B — `TestClient`: HTTP Testing Without Starting Uvicorn and 6V — Manual Smoke Tests vs `TestClient`**

*The premise of `TestClient` is that automated tests shouldn't require you to manually start a server first. It let's us test responses against the FastAPI application inside the test process. No TCP connection is necessary. As for how an in-process `TestClient` API test is different from the Uvicorn-backed smoke scripts we used in TG4 and TG5, it uses a pytest process that leads into an in-process HTTP-style test client. Meanwhile, the smoke scripts we used occasionally prove real server/network wiring. `TestClient` is faster and easier to automate.*

`TestClient` gives us: pytest -> TestClient -> FastAPI application. And it does this without requiring a real network socket, 127.0.0.1:8000, or separate Uvicorn processes. 

### Question 2
Why do we create the `TestClient` with a context manager in a session-scoped fixture, and how does that relate to the lifespan and application-scoped inference pipeline from TG2?

**Best sections to review: 6C — Why the Context Manager Matters and 6E — Create Shared API Fixtures**

*We create the `TestClient` with a context manager in a session-scoped fixture because the context manager enables us to make the lifecycle explicit. And we can put that into a pytest fixture so the stages of the lifecycle are iterated through automatically. As for how this relates to the lifespan and application-scoped inference pipeline from Task Group 2, it's built to match our application-lifetime architecture. Entering `TestClient` runs lifespan startup, including loading and verifying the Phase 2.1 inference pipeline. Leaving the context runs the lifespan shutdown process.*

The context manager enables us to make the lifecycle explicit: enter context -> FastAPI lifespan startup -> tests run -> exit context -> FastAPI lifespan shutdown. 

The session-scoped fixture is the separate pieces that tells the system to do the application lifecycle once for the whole test sessions instead of once per test. 

context manager -> ensures startup/shutdown correctly

scope="session" -> reuse that one application lifetime across many tests

### Question 3
Why do we compare the `/predict` HTTP result against the Phase 2.1 pipeline's result instead of hard-coding one expected RUL number into the API test?

**Best sections to review: 6J — Verify HTTP Prediction Matches Phase 2.1 and 6K — Why Not Hard-Code the Expected RUL?**

*The principle at play here is that there's an important boundary that we need to check between the Phase 2.1 pipeline and the HTTP API. If Phase 2.1 says a prediction is a certain value, then we need to verify that the HTTP API exposes that value. As for why we don't hard-code one expected RUL number into the API test, we would be making the API do something that's outside the scope of its job. Phase 2.1 already owns model/inference correctness, and now Phase 2.2 establishes that the HTTP layer faithfully exposes whatever the authoritative Phase 2.1 pipeline produces. The goal is to compare the API output versus the Phase 2.1 output instead of duplicating a frozen number.*

The API test owns the guarantee that Phase 2.1 produces X and the HTTP layer exposes X faithfully.

We want to compare the API output versus the Phase 2.1 output instead of duplicating a frozen number. 

We want to apply the "one source of truth paradigm". 

### Question 4
What is a test double, how does `app.dependency_overrides` let us inject one into FastAPI, and why is this useful for testing a server-side inference failure without damaging the real model?

**Best sections to review: 6O — Test a Known Internal Inference Failure, 6P — What Is `dependency_overrides`?, and 6Q — What Is a Test Double?**

*The principle at play here is that, for testing purposes, we don't want to corrupt the random forrest model to trigger an HTTP 500 type of error. We instead replace our real inference pipeline with a controlled fake pipeline (i.e., a test double) and use that. To enable this phenomenon, `app.dependency_overrides` let's us give the system a controlled test replacement instead of the usual object when something asks for that dependency.*

Instead of intentionally damaging any real items in our system, we inject a controlled fake pipeline that will expectedly raise `InferencePredictionError`.

`app.dependency_overrides` tells FastAPI when an endpoint requests a particular dependency, supply the test replacement instead.

### Question 5
Why must the dependency override be removed after the test, and what kind of testing problem can occur if one test leaves shared application state modified for later tests?

**Best section to review: 6R — Why the `finally` Block Matters**

*Because we want to return the application to the state we found it in before activating the dependency override. Wihtout poppping the dependency overrides, it's possible that the failing test double would still be in place when the application moved on to another test. This could cause an unexpected failure due to something from the previous test instead of the current test.*

Wihtout a cleanup after activating a test double we would create a situation of test contamination.

Every test should leave shared state in the condition it found it.

### Additional Questions 

* What is a TCP connection? 

*TCP stands for transmission control protocol. A TCP connection is a reliable, ordered communication channel established between two network endpoints so they can exchange bytes.*

### Ideas to Retain

* `TestClient` tests FastAPI behavior in-process; Uvicorn smoke tests exercise real server/network wiring. 

* The context manager runs the FastAPI lifespan; session scope determines that this lifecycle happens once across the test session. 

* A test double is a controlled replacement for a real dependency. 

* Test cleanup prevents contamination between tests. 

* TCP provides a reliable, ordered byte channel between network endpoints. 

* HTTP gives transmitted data web/API meaning; TCP transports the underlying bytes. 