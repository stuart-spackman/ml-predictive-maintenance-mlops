## Phase 2.2 — Task Group 2 Active Recall

### Question 1
Why do we create the Phase 2.1 inference pipeline during FastAPI application startup instead of creating it inside every `/predict` request, and why is startup-time loading not the same thing as model training?

**Best sections to review: 2A — Why We Need an Application-Lifetime Pipeline and 2B — Loading Is Not Predicting**

*An important principle here is that the model we created is an application-level dependency, not a request-level dependency. By loading it when the application starts instead of loading it every time our `/predict` endpoint is called on, we avoid a lot of repeated heavy computational tasks. As for why startup-time loading is not the same thing as model training, when we load the model at startup, we are recreating a frozen artifact whose parameters had already been saved after the original training process. No updates are being made to those parameters and we are making no calls to the `.fit()` function.*

The learned parameters already exist in the saved artifact; startup reconstructs that frozen state rather than learning a new state. 

### Question 2
What does the FastAPI lifespan function do, what is the significance of the code before and after `yield`, and why is model-loading failure before `yield` desirable?

**Best sections to review: 2D — The FastAPI Application Lifespan and 2H — Why Startup Should Fail If the Model Cannot Be Trusted**

*The lifespan function handles loading the pipeline at starup, serving requests while the application is running, and cleaning up the processing enviroments that was in use at the time of shutdown. This is done with an asynchronous context manager that contains a `yield` keyword in the code. Before `yield` is where the code for startup work gets called on, and after `yield` is where the code for the cleanup work gets called on. As for why model-loading failing before `yield` is desirable, what we distinctly don't want is the possibility of the application starting up and appearing read to take inference requests without having successfully loaded the model.*

The lifespan function establishes resources before `yield`, then yields control back to FastAPI, which serves requests during that period. 

We do not want the service to appear healthy and ready if the essential model dependency could not be loaded or trusted.

### Question 3
What is the difference between `app.state`, the `get_inference_pipeline()` dependency getter, and FastAPI's `Depends()` mechanism?

**Best sections to review: 2F — What Is `app.state`?, 2I — Create the FastAPI Dependency Getter, and 2M — Dependency Injection Is Not the Same as Application State**

*`app.state` is where the FastAPI's application object stores the specific runtime state. This is also where the inference pipeline object lives, which facilitates having the pipeline not being owned by one particular request and instead belonging to the running application. `app.state` is there to provide a location for where the persistent pipeline lives.*

*As for the `get_inference_pipeline()` dependency getter, this function is needed to facilitate two things: `get_inference_pipeline()` defines how to retrieve the dependency while `InferencePipelineDependency` creates a convenient reusable type annotation for future endpoints.*

*As for FastAPI's `Depends()` mechanism, this is in place to create a way for the endpoint code to receive the pipeline without constructing it or going through the trouble of locating it itself.*

*To provide a summary, application state stores the dependecy, the dependency getter retrieves the dependency, and the FastAPI dependency injection provides the dependency to the endpoint.*

Application state stores the dependency, the dependency getter retrieves the dependency, and FastAPI dependency injection provides the dependency to the endpoint. app.state tells us where it lives. get_inference_pipeline() tells us how we are supposed to retrieve it. `Depends(...)` tells us how FastAPI supplies it.

### Question 4
What does it mean to say that the inference pipeline is application-scoped rather than request-scoped, and why does “persistent” mean once per application process rather than one globally unique model object forever?

**Best sections to review: 2G — Persistent Does Not Mean Globally Eternal and 2T — Request-Scoped vs Application-Scoped**

*"Persistent" in this context is used to say that the pipeline persists for the length of one running application's lifetime. It is not meant to imply that one model object exists forever. As for the inference pipeline being application-scoped rather than request-scoped, this means the inference pipeline object is shared throughout the application lifetime instead of belonging to a single request.*

persistent for the lifetime of one application process

application-scoped -> shared across requests for one running app process

request-scoped -> created specifically for one HTTP request

Each process has its own memory: 4 worker processes -> potentially 4 separate pipeline objects

### Question 5
Why is sharing one frozen inference pipeline across many requests compatible with keeping the requests independent, and what would be fundamentally different if our request handling were calling `.fit()` and mutating learned model state?

**Best sections to review: 2U — One Important Concurrency Clarification and 2V — TG2 Does Not Implement `/predict` Yet**

*The principle at play here is that reusing the same model object across requests does not mean requests share their input data. While using the same model repeatedly and not calling the `.fit()` function, each call can build its own validated DataFrame, temporal table, model-ready X, and PredictionResult. We can share the read-only frozen model capability wihtout mixing the histories together.*

### Additional Questions 

What is a dependency injection? I was sick an unable to work on this project for a few days. I forgot what a dependency injection is. 

*Dependency injection means giving a function or object the thing it depends on from the outside, instead of making it construct or locate the dependency itself.*

### Ideas to Retain

* Dependency = something a function/object needs in order to do its job. 

* Dependency injection = supply that dependency from the outside rather than constructing it internally. 

* In our project, the endpoint depends on `RULInferencePipeline`. 

* `app.state` stores it, `get_inference_pipeline()` retrieves it, and `Depends()` injects it into the endpoint. 

* Dependency injection reduces coupling and makes testing easier because real dependencies can be replaces with controlled test dependencies. 

* The model is application-scoped, which request data is request-scoped.