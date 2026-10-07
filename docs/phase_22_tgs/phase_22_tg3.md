## Phase 2.2 — Task Group 3 Active Recall

### Question 1
What is a FastAPI route, and why are we using an `APIRouter` plus `app.include_router()` instead of putting all endpoint definitions directly inside `main.py`?

**Best sections to review: 3B — What Is a Route? and 3C — Why Use `APIRouter` Instead of Putting Everything in `main.py`?**

*In a web API, a route mixes an HTTP method and path with some sort of Python behavior, e.g., `GET + /health`. As for why we are using an `APIRouter` plus `app.include_router()` instead of putting all endpoint definitions directly inside `main.py`, we already know of three API calls this application will need to support (`/health`, `/metadata`, `/predict`) and there might be additional error-handling/configuration code. If we put all endpoint definitions inside `main.py`, then our main method would become unnecessarily heavy. It will be much cleaner if we used `main.py` to construct the application and a separate `routes.py` to describe the HTTP routes.* 

A route maps an HTTP method and URL path to a specific endpoint function. 

GET + /health -> get_health()

main.py -> construct/configure the application

routes.py -> define HTTP endpoint behavior

### Question 2
Why does `GET /health` request the injected inference-pipeline dependency even though it does not make a prediction, and what is the difference between a liveness check and a readiness check?

**Best sections to review: 3E — Implement `GET /health`, 3F — Why Inject the Pipeline Into `/health` If We Don't Use It?, and 3G — Liveness vs Readiness**

*To begin with, `GET /health` returns a report that the prediction service is operational. But to do that it's best to not only confirm that the Python web servide in question exists, but also to confirm that the inference resource expected by the service is available. We want `Get /health` be closer to a readiness check than a pure liveliness check. As for the difference between a liveliness check and a readiness check, liveliness simply asks if the application process is still alive, i.e., it expects a simple yes or no answer to if the process is running. Meanwhile, a readiness check asks if the application is actually prepared to perform its intended work.*

LIVENESS = Is the web process alive? 

READINESS = Is the service alive? AND Is if inference pipeline available? 

### Question 3
What does `response_model=HealthResponse` or `response_model=ModelMetadataResponse` accomplish, and how does this relate to Pydantic protecting both the input and output sides of an HTTP API?

**Best section to review: 3H — What Does `response_model` Do?**

*The main thing that those parameters do is create a situation where FastAPI now has an explicit response contract. By using this, our Pydantic models now protect both sides of the API boundary. The request model can determine what can come in and the response model can determine what can go out.*

The request model determines what can come in while the response model determines what can go out. 

Pydantic isn't just protecting incoming JSON anymore. We're using schemas on both sides of the network boundary. 

### Question 4
Why did we add the public read-only `model_family` and `feature_count` properties to `RULInferencePipeline` instead of either hard-coding `"RandomForestRegressor"` and `36` in the API or directly reading private attributes such as `pipeline._model` and `pipeline._feature_names`?

**Best sections to review: 3I — Implement Safe Public Model Metadata through 3M — Encapsulation Appears Again**

*The principle at play here is that we want `model_family` and `feature_count` to describe the model that was actually loaded at runtime. If we hard-coded each of those model parameters that would create a situation where a change to the frozen model would need additional updates elsewhere in the application. We want to create a situation where there's only one source of truth, i.e., the metadata should come only from the actual verified inference pipeline.*

There's a second principle here worth adding and its encapsualtion. 

The two principles at play here are a single source of truth plus encapsulation.

### Question 5
What can a successful `/health` response legitimately tell us, and why does it provide no evidence by itself that the model has good predictive performance, no drift, or appropriate predictions for some new real-world population?

**Best section to review: 3Y — Health Is Not Model Quality**

*If `/health` sends back a message that the application or model is okay, then that means the serving application is running with its required inference resources available. Nothing more. It does not imply anything about the model's accuracy, whether drift is occurring, if the model predictions are physically correct, etc.*

A successful health response means roughly that the serving application is operational and its required inference dependency is available. 

This distinction is especially important in MLOps because software can be healthy while the model is statistically poor. 

### Additional Questions 

* What is Uvicorn? I can feel the knowledge I had about it has faded. 

*Uvicorn is the server process that runs our FastAPI application and listens for incoming network requests.*

Uvicorn -> Listen for network traffic and run the application. 

FastAPI -> Decide what the web application does with that traffic.

* What is pydantic? 

*Pydantic is a Python library for defining structured data models and validating data against them.*

Pydantic guards the shape of data crossing our API boundary.

* What is an API? 

*An API is a defined interface through which one piece of software can interact with another without needing to know its internal implementation.*

### Ideas to Retain

* Health and metadata endpoints expose small, intentional views of the running service; they should report operational state without leaking or duplicating the inference system's internal machinery. 

* Idempotence means performing the same operation repeatedly should not keep changing server state as a consequence of that operation.

* Uvicorn runs the server. FastAPI defines the web application. Pydantic defines/validates structured API data. The API is the interface clients interact with.

* A route maps an HTTP method + path to endpoint behavior. 

* Uvicorn runs the FastAPI application and listens for network traffic. 

* Pydantic defines an validates structured data crossing the API boundary. 

* An API is a controlled interface that lets software use a capability without knowing its internal implementation. 

* Operational health is different from statistical model quality.