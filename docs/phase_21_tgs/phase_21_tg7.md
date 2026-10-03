## Phase 2.1 — Task Group 7 Active Recall

### Question 1
What is the Phase 2.1 public interface that Phase 2.2 should depend on, and why should FastAPI call that interface instead of directly orchestrating validation, temporal feature construction, artifact loading, feature selection, and prediction?

**Best sections to review: 7A — What “Handoff” Means and 7B — Public Interface vs Internal Implementation**

*A definition worth noting there is that a public interface is the small set of things another part of the application is expected to use. `create_default_inference_pipeline()` could be thought of as the public interface that Phase 2.2 should depend on. FastAPI could call that interface instead of handling things like temporal feature construction on its own because we have already gone through the process of validating that public interface. Those would be considered implementation details behind the inference boundary and they have been proven reliable, so recreating the work that went into it might lead errors.*

We've tested the subsystem's important contracts and behaviors. 

FastAPI should depend on the capability Phase 2.1 exposes, not reconstruct how Phase 2.1 implements that capability. 

### Question 2
What is encapsulation, and how does exposing a narrow operation such as `pipeline.predict(engine_history)` reduce coupling between Phase 2.1 and future application layers?

**Best sections to review: 7C — Why a Narrow Interface Is Valuable and 7L — An Important New Concept: Encapsulation**

*Before definiting encapsulation, it might be better to define tight coupling, which is when two different functionalities within a software system will both need to be made aware of any changes that happend to an underlying function that they both depend on. Encapsulation is the process of hiding internal complexities behind a controlled interface. We can think of a case where the outside world only sees a simple function call, but behind the function call is a series of complex other function calls that the outside world doesn't need to be aware of. Exposing the narrow operation mentioned above reduces coupling between Phase 2.1 and future application layers because if we want to edit any of the functions being called on behind the scenes with `pipeline.predict(engine_history)`, then the future application layers won't need to be aware of it and account for it by making changes to their own source code.*

Tight coupling means one component depends heavily on the internal details, structure, or behavior of another component, so changes to one frequently force changes to the other. 

We want to create loose coupling through encapsulation. 

### Question 3
Why do we audit that the inference package contains neither model-fitting calls nor FastAPI dependencies, and what architectural guarantees do those two checks protect?

**Best sections to review: 7I — Why Audit “No `.fit()`”? and 7J — Why Audit “No FastAPI”?**

*Because we want to make sure that Phase 2.1 isn't doing anything beyond its scope. Phase 2.1 has one job, and it's inference. If we found any instances of `.fit()` in the Phase 2.1 code, that would indicate that it's involved in training, which would be an error. The same could be said about any calls to FastAPI. We want to make that building the architecture of the software system is proceeding to be build with Phase 2.1 exclusively handling inference.*

We're auditing for FastAPI dependencies/imports.

### Question 4
What is the intended dependency direction between FastAPI and the Phase 2.1 inference subsystem, and why is that direction preferable to making the inference code depend on the HTTP framework?

**Best sections to review: 7J — Why Audit “No FastAPI”? and 7Q — Phase 2.1 Final Architecture**

*The indended dependency direction is that Phase 2.2 FastAPI depends on Phase 2.1 inference, not the other way around. We do not want the inference code to depend on the HTTP framework because our goal is to let the lower-level inference system remain transport-independent. HTTP concerns should be resolved and come before the application's inference capabilities get called on.* 

The transport layer actually surrounds the inference call: HTTP request parsing, then inference, then HTTP response formatting. The inference system remains blissfully unaware that HTTP was involved.

### Question 5
What can we legitimately claim after completing Phase 2.1, and what major production/MLOps capabilities are still outside its scope?

**Best sections to review: 7O — Define Phase 2.1 “Done” and 7P — What Phase 2.1 Does NOT Claim**

*Now that we have completely Phase 2.1, we can claim that we have finalized and tested contracts for input, features, artifacts, predictions, failures, tests, and the system architecture. The frozen Phase 1 predictive model now has a reusable, validated, tested, production-style Python inference pathway. As for what we cannot yet claim, we cannot claim that production deployment is complete. We do not yet have anything from the following list: HTTP service, container, CI pipeline, authentication, cloud deployment, monitoring, Streamlit front end. Also, it's worth noting that no retraining took place, so we cannot claim that the model became more accurate.*

Phase 2 didn't improve the model's predictive performance; it improved how safely and reproducibly we can use the already frozen model. 

### Follow-up Questions 

* What does CI mean in this context? 

*Instead of relying on you to remember to run the test suite after every code change, a remote automation system runs important checks whenever code is integrated into the repository.*

*Historically and conceptually, developers are continually integrating code changes into a shared codebase.*

### Ideas to Retain 

* A subsystem is ready for handoff when its consumer can use the capability through a small stable interface without needing to understand or duplicate the machinery behind it.

* Encapsulation hides internal complexity behind a stable public interface. 

* FastAPI depend on inference; inference does not depend on FastAPI. 

* Phase 2.1 owns prediction capability. Phase 2.2 will own HTTP exposure of that capability. 

* CI = Continuous Integration: automatically verify integrated code changes, commonly whenever code is pushed. 

* pytest performs tests; CI automatically decides when and where to run them. 

* Phase 2.1 is now conceptually complete. The next major phase is Phase 2.2 — Model Serving with FastAPI.