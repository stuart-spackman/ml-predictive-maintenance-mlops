## Phase 2.5 — Task Group 3 Active Recall

### Question 1
Walk through the complete successful request path from a user uploading an engine-history CSV in Streamlit to the estimated RUL being displayed. For each major layer—Streamlit, demo adapter, demo client, FastAPI, inference pipeline, and frozen model—state what that layer owns and one thing it deliberately does not own.

**Best sections to review: 3A–3E — Architectural and Boundary Audits, 3AB — Explain the Full Request Without Looking at Code, and 3AH — Final Phase 2 Handoff**

1. User uploads one engine history in the form of a CSV file. 

2. Streamlit parses the CSV file into a DataFrame.

3. The demo adapter translates the DataFrame into the API's request representation.

4. The demo client sends `POST /predict` over HTTP.

5. FastAPI validates the transport schema. 

6. The API adapter translates public request data into the inference representation.

7. The inference pipeline validates raw engine history. 

8. The pipeline constructs causal temporal features from the full observed prefix.

9. It selects the exact locked model schema. 

10. Verified frozen artifacts provide the frozen estimator. 

11. The model predicts estimated RUL. 

12. The pipeline returns a PredictionResult.

13. FastAPI serializes the public response. 

14. The demo client interprets the HTTP response.

15. Streamlit displays estimated RUL.

*Streamlit owns parsing a CSV file into a DataFrame and displaying estimated RUL. Streamlit does not own validating the dataset.*

*The demo adapter owns translating the DataFrame into the API's request representation. The demo adapter does not own editing the dataset in a way that would not be isomorphic.*

*The demo client owns sending `POST /predict` over HTTP and interpreting the HTTP response. The demo client does not own transforming the data representation.*

*FastAPI owns validating the transport schema and serializaing the public response. FastAPI does not own performing inference.*

*The inference pipeline owns validating raw engine history, constructing causal temporal features from the full observed prefix, selecting the exact locked model schema, and returning a `PredictionResult`. The inference pipeline does not own validating the shape of the dataset.*

*The frozen model state owns predicting an estimated RUL. The frozen model state does not own reporting errors of any kind.*

The inference pipeline DOES validate important structural properties of its raw-history representation, included expected columns, one engine, finite numberic data, cycle structure, and ultimately model compatibility. What it deliberately does NOT own is HTTP request/schema validation.

FastAPI / Pydantic -> Is this structurally a valid API request? 

Inference pipeline -> Is this semantically valid raw engine history for this inference contract.

The adapter my translate representation, but it must not derive new model information or change the meaning of the data.

The frozen model does not own application-level validation or public error semantics.

### Question 2
Explain the complete failure path for a structurally representable but domain-invalid request such as a seven-cycle engine history. Why is it important that the frontend can construct and send the request, the inference pipeline remains authoritative for the minimum-history rule, FastAPI translates the backend exception into HTTP, and the client creates its own local error rather than receiving the original Python exception?

**Best sections to review: 3D — Audit the Inference Boundary, 3H — Audit the Error Ownership Model, 3S — Run the Final Failure Paths, and 3AC — Explain the Failure Path**

*For a structurally representable but domain-invalid request such as a seven-cycle engine history, we first note that the Streamlit adapter can still faithfully translate that one-engine CSV into an API request (Streamlit is not build to invent or enforce a 10-cycle rule). We can expect the request to reach FastAPI, which then gets to work on validating the request structure. The inference pipeline then applies the authoritative domain contract and rejects the history because it lacks the required temporal history. That InferenceInputError is translated at the API boundary into an HTTP 422 public response. The demo client converts that HTTP response into a `DemoAPIError`. Finally, Streamlit presents it as a user-correctable warning.*

*As for why it's important that the fronend can construct and send the request, among actions taken by other layers too, the principle at play here is that across the whole system, errors should be translated as they move thorugh boundaries. This goes back to wanting to be able to report the specifics of an error. Catching `Exception` everywhere only tells us that something went wrong and makes users and developers start from zero when it comes to investigating the cause of an error.*

The client cannot literally receive an `InferenceInputError` because that Python exeception exists in the backend process.

Across the network, only the protocol representation crosses: 
`InferenceInputError` -> HTTP 422 + JSON -> network -> `DemoAPIError`

### Question 3
Distinguish the roles of `pyproject.toml`, `requirements/constraints.txt`, the Dockerfile/image/container, and GitHub Actions. What does each contribute to reproducibility or verification, and what would be an overclaim about what each one proves?

**Best sections to review: 3I–3L — Runtime, Reproducibility, Docker, and CI Audits, 3AD — Why Docker Exists, and 3AE — Why CI Exists**

*`pyproject.toml` offers a statement of what software packages the project deliberately dependes on. It contributes conceptual knowledge of what is required to reproduce the project. An overclaim about it could be that `pyproject.toml` is all that's needed to create a clean environment for building and running the system.*

*`requirements/constraints.txt` offers a list of tested, known-good software packages that the system was verified as functioning properly with. This file is highly important for reproducibility because it gives specific versions of software packages that anyone rebuilding the system should use, as going outside into different versions would require another round of verification. An overclaim about `requirements/constraints.txt` could be that if a user installs all the packages outlined on the list it provides, then no further verification will be needed.*

*The Dockerfile/image/container is the blueprint we use for creating an isolated version of the software system, built in a clean environment. The Dockerfile contains all the parameters needed to build and install the parts of the project that enable inference. The image is the blueprint created from the Dockerfile and it's what we use to instantiate containers, which are runable individual versions of our software system. The Dockerfile/image/container is important for reproducibility because it serves as a tool for confirming that the software system can be built up in a sort of cleanroom environment and still run, i.e., there weren't any bits of software in the developer/virtual environment that were unexpectedly needed to make the software system run. An overstatment is that the Dockerfile/image/container is useful for verifying our testing suite; it's only built to serve inference.*

*GitHub Actions is a CI tool for automated verification. With each push to GitHub, GitHub Actions creates the new version of the software system and puts it through the testing suite and contract verification that was created during development. Most notably, it ensures that the new codebase does not drop below a certain testing surface percentage, which would indicate that too much of our code is not going through a testing and verification process. As for an overclaim about GitHub actions, it could not be stated that GitHub Actions is able to verify the accuracy of the model.*

`pyproject.toml` -> dependency intent
It can be enough to create a runnable environment in some circumstances. What it does NOT guarantee is that you'll get the same tested resolution every time when ranges permit different versions.
Overclaim: Installing `pyproject.toml` alone guarantees reconstruction of the exact environment we tested.

`constraints.txt` -> constrains versions
does NOT request installation by itself
pyproject -> what to install
constraints -> which tested versions to resolve where applicable

Dockerfile -> build recipe / blueprint
docker build -> executes recipe
image -> built immutable-ish packaged artifact
docker run -> instantiates image
container -> runtime instance of image
The Dockerfile is the blueprint. The image is the built artifact.

Coverage tells us how much code was executed during the tests.
It does not establish that executed code was meaningfully verified.
coverage -> execution visibility
tests / assertions -> behavioral verification
Strongest CI claim: On a clean configured runner, the declared environment reconstructed and all encoded checks passed.

### Question 4
Why can this project legitimately be described as a production-style ML inference system but not a fully production-deployed platform? Give several concrete Phase 2 capabilities that support the production-style claim, then explain the `claim → evidence → test` mindset using at least two examples from the project.

**Best sections to review: 3Y — What Phase 2 Now Contains, 3Z — What “Production-Style” Means Here, 3AA — The Most Important Interview Story, 3AF — Final Claims → Evidence → Test Audit, and 3AG — Phase 2 Completion Standard**

*This project can legitimately be described as a production-style ML inference system but not a fully production-deployed platform because it has a long list of production-relevant engineering patterns, e.g., frozen artifact, explicit inference contract, artifact verification, etc. We cannot claim that it is a fully production-deployed platform because there are still several such capabilities that this project does not have, e.g., a fully production-deployed platform, a highly available service, autoscaling, etc.*

*As for several concrete Phase 2 capabilities that support the production-style claim, first, we claim that there is causal feature construction. Our feature contract and inference contract was built around changing the raw input datasets in such a way that no engineered features have access to data rows in the future. Our feature engineering was tested as guaranteeing that features are causal and group-bounded. This was included in our testing suite for the inference pipeline.*

*Second, we claim that the project uses a separate demo client. Our Streamlit interface exists at its own port and runs as a separate process from the inference and API system. Furthermore, none of the Streamlit or UI functionality was built into the Docker image.*

Missing operation capabilities: 
* no cloud deployment
* no authentication/authorization
* no autoscaling
* no redundancy/high availability
* no load testing
* no SLA
* no production observability stack
* no operational monitoring/alerting

The project does contain legitimate production-style practices: 
* explicit inference contract
* frozen artifact
* causal feature engineering
* artifact integrity checks
* FastAPI serving
* typed request/response schemas
* failure translation
* automated tests
* coverage gate
* dependency/environment specification
* Docker runtime
* CI
* configurable external client
* Streamlit demo

CLAIM: Inference at cycle t is causal.
EVIDENCE: The feature construction uses only the observed prefix.
TEST: Prefix-invariance test: Adding future cycles does not change the prediction ofr the same earlier prefix. 

CLAIM: The demo consumes the inference service rather than implementing inference itself.
EVIDENCE: `demo/client.py` communicates through HTTP, and demo code contains no model-loading, feature engineering, or `model.predict` logic.

TEST: Run Streamlit against the Dockerized API and obtain a valid prediction; then stop the API and observe `DemoConnectionError` rather than continued local prediction.

### Help Needed

* What's the difference between continuous and contiguous? 

### Ideas to Retain

* FastAPI validates the public transport contract while inference validates domain/model correctness. 

* Exceptions don't cross the network as Python objects; they become protocol representations and are reinterpreted by the client. 

* Dockerfile = recipe, image = built artifact, container = runtime instance

* Coverage measures executed code, not correctness

* `pyproject.toml` states dependency intent; constraints record a tested resolution. 

* Production-style describes the engineering patterns we've built, not an operational deployment status.

* Forevery engineering claim, ask: What evidence supports it, and what test would fail if the claim stopped being true.