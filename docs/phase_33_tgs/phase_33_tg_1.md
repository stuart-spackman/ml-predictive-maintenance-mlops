## Phase 3.3 — Task Group 1 Active Recall

### Question 1
Why do we record a separate `service_request` event and `prediction` event for a successful `/predict` call, and what different monitoring questions can each event type answer?

**Best sections to review: 1A — Two Event Types, 1G — Request-Level Service Telemetry, and 1O — TG1 Exit State**

*We record a separate `service_request` event and `prediction` event for a successful `/predict` call because we need to embody the principle that service telemetry is not the same thing as model telemetry. We want to ensure that if a request fails before a prediction is produced, then we will still be able to log a `service_request`, event but appropriately get no successful prediction event.*

*As for the different monitoring questions that each type can answer, first, `service_request` answers the question of, "Was a service request received?" Second, `prediction` answers the question of, "Was a prediction event executed?"*

Service telemetry is not the same thing as model telemetry. 

A request may fail before any model prediction exists. 

We separate service and prediction events because application health and model behavior are different observability layers. Service events capture request success, HTTP status, and end-to-end latency even when inference fails, while prediction events exist only after successful inference and capture the actual model identity, input features, prediction, and inference-specific behavior.

### Question 2
Why does the prediction telemetry record the SHA-256 identity of the artifact actually used by the FastAPI serving path instead of simply recording `model = champion`, and what problem would the latter approach create for historical telemetry?

**Best sections to review: 1J — Artifact Identity vs. `champion`, and Phase 3.3 TG0 Section 0B**

*The prediction telemetry records the SHA-256 identity of the artifact actually used by the FastAPI serving path instead of simply recording `model = champion` because we need an immutable historical identity to serve as the record of the model we used. The `champion` pointer is mutable and recording that at the time of prediction does not offer a guarantee that the `champion` at that time was actually the model that was used in serving predictions.*

*As for the problem that just recording `model = champion` would create in later historical telemetry, it is possible that situations could occur where the `champion` pointer could be changed while the model serving predictions was not changed. So long as misalignment is a possibility, we need to record the SHA-identity of the model every time serving predictions occurs.*

immutable historical identity vs. mutable lifecycle role

The SHA-256 identifies the exact bytes of the artifact that were served.

A mutable alias such as `champion` describes a current registry role, not immutable historical runtime identity. Recording the artifact SHA-256 lets us identify the exact model bytes that produced a prediction, even if the `champion` alias later moves or was already misaligned with the deployed application.

### Question 3
Why is it acceptable in this portfolio implementation to call `build_model_input()` again after prediction, what important source-of-truth rule are we still preserving, and why should a telemetry-write failure normally fail open rather than fail the prediction request?

**Best sections to review: 1E — Fail Open for Telemetry, 1H–1I — Prediction Event and Reusing `build_model_input()`**

*In this portfolio implementation is is acceptable to call `build_model_input()` again after prediction because we are duplicating computation (which is acceptable) while not duplicating logic (which is not acceptable). Duplicating computation in this case is acceptable because it gives us the benefits of no second feature implementation, no invasive refactor of Phase 2 inference, and monitoring still uses the same source of truth.*

*As for the important source of truth rule that we are still preserving, we are keeping logic to one source, it's computation that we're duplicating. We neep to keep feature logic to one source of truth, while duplicating computation is still okay.*

*Finally, a telemetry-write failure should normally fail open rather than fail the prediction request because we want a telemtry outage to be observable but not cause a model failure. We want to avoid situations where the model correctly predicted RUL, but the customer received HTTP 500 because the telemetry file couldn't be opened.*

We are duplicating computation while not duplicating logic.

Calling `build_model_input()` is computationally redundant but semantically safe.

### Help Needed

* What exactly is telemtry? I'm unable to produce a definition and examples without help at the moment. I'd like to change that. 

*Telemetry is data that a running system automatically records about its own operation so that the system can later be observed, monitored, and investigated.*

*Telemetry is automatically collected operational data describing what a running system is doing and how it is behaving.*

* What does the `-p` mean in `mkdir` again? 

*`-p` means parent, as in, "Create the parent directories if they don't exist."*

* Could you explain the fail open/fail closed paradigm for me again? Does fail open mean we let the requestor know the details of the failure? Or, actually, is it rather that failing open breaks the application while failing closed allows the application to keep running? 

*When something goes wrong, do we allow the requested operation to continue or block it?*

*Fail closed = when in doubt, deny/block.*

*Fail open = when this component fails, permit the operation to continue.*

* What does the `-q` mean in the pytest calls? 

*`-q` means quiet, as in, "Make the output quieter than usual."*

* What is the purpose of an `__init__.py` file? Why is it okay that they've been empty? 

*`__init__.py` traditionally tells Python, "Treat this directory as a Python package."*

folder + `__init__.py` = explicit Python package

### Ideas to Retain

* Logging creates the raw evidence that the monitoring later interprets. 

* Service events and prediction events represent different layers of observability and should remain distinguishable even when linked by the same request ID. 

* Historical model identity should use the artifact that actually produced the prediction, not a mutable registry role such as `champion`.

* Monitoring should consume model-ready features from the existing inference feature path rather than implement feature engineering a second time. 

* Telemetry should normally fail open: loss of observability should be visible, but it should not turn an otherwise valid inference into a failed customer request. 

### More Ideas to Retain

* Service telemetry measure application behavior; prediction telemetry measures successful model behavior. 

* A registry alias describes a lifecycle role; an artifact has identifies exact historical bytes. 

* Duplicating computation can be acceptable; duplicating business/feature logic creates competing sources of truth. 

* Observability is important, but an observability outage should not normally become an inference outage.