## Phase 2.4 — Task Group 5 Active Recall

### Question 1
Starting from a fresh clone of the repository, describe the full reproducibility chain that takes the project from source code to a verified running prediction service. What distinct roles do `pyproject.toml`, `requirements/constraints.txt`, the virtual environment, the Docker image, and GitHub Actions play?

**Best sections to review: 5A — The Core Phase 2.4 Claim, 5D — Audit the Dependency Sources of Truth, 5O — Understand the Full Reproducibility Chain, and 5Z — Final Phase 2.4 Completion Audit**

*When discussing the full reproducibility chain, from source code to a verified running prediction service, we first have the Git repository, which is accessed by a fresh environment. In the fresh environment, reconstruction takes place, followed by verification. From there, the source code is actually run. So, all without depending on an undocumented developer machine state, we need to prove that a fresh supported environment can reconstruct the project's Python dependencies, execute the established automated quality gate, build the serving image, initialize the frozen system, and run the FastAPI service.*

*`pyproject.toml` provides a distinct statement of what the project depends on by design.*

*`requirements/constraints.txt` is a more specific version of the `pyproject.toml` file, in which exact known-good dependency resolutions are given.*

*The virtual environment is one installed local realization of the specifications outlined in `pyproject.toml` and `requirements/constraints.txt`.*

*The Docker image is a packaged blueprint for instantiating a version of the service that we have built.*

*GitHub Actions embodies the CI process, providing an automated way of verifying that the application will still behave as intended after a code change.*
 
The overall chain is: 
Git repository
-> fresh supported environment
-> dependency reconstruction
-> quality verification
-> Docker image build
-> pipeline initialization
-> running FastAPI service

`pyproject.toml` and `requirements/constraints.txt` are related, but one of them isn't a more specific version of the other. `pyproject.toml` declares dependency intent, e.g., "This project needs FastAPI, pandas, sklearn..." `constraints.txt` constrains resoltion, i.e., "When those packages are installed, use these exact known-good versions."

`pyproject.toml` answers what we require; the constraints file answers which tested resolution to use when resolving those requirements.

Also, reproducibility isn't specifically about recreating what worked in the local `.venv`. The `.venv` was one experiment. The controlled repository information is the source of truth.

### Question 2
What is the difference between reproducibility, determinism, portability, and deployment? What evidence from Phase 2.4 supports each concept, and which stronger claims would still be unjustified?

**Best sections to review: 5P — Reproducibility Is Not Determinism, 5Q — Reproducibility Is Also Not Portability, 5R — Reproducibility Is Also Not Deployment, and 5S — Training Reproducibility vs Serving Reproducibility**

*Reproducibiliy is a gauge of how well we can take controlled project artifacts and use them in a fresh supported enviroment to reconstruct and operate the intended software system that we verified in our local virtual environment. In Phase 2.4 we used Docker several times to build our project in a container from an image and confirmed it had all the same functionality as in our local testing.*

*Determinism is the concept that equal inputs in a system always result in same outputs. In Phase 2.4 we tested intputs in our local version of the software system and then tested them again in the containerized version of our system build from a Docker image. Both times it resulted in the same outputs.*

*Portability is the concept that the software system we've built can operate a variety of different environments and platforms. In Phase 2.4 we confirmed that our system could run on our local Mac operating system, and that it could run on a Linux operating system in the form of the most recent version of Ubuntu via Docker.*

*Deployment is the process of buildling deployment infrastructure for the software system we've created. This has not been done yet in our project. We do not yet have things like cloud hosting, public endpoints, authentication, etc.*

*As for which stronger claims would still be unjustified, we cannot yet make a claim that we have created a production system. We can say that we've implemented a production-style system or a deployment-ready architecture, but deployment has not yet become a part of the system.*

Reproducibility is our ability to reconstruct and operated the intended system in a fresh supported environment from controlled project information. Phase 2.4 evidence for this includes fresh `.venv` reconstruction, GitHub clean-runner reconstruction, Docker image reconstruction, and fresh container recreation.

Determinism is, within environment A, we can show input X results in output Y. And then we reconstruct environment A again, and can show that once again input X results in output Y. Repeated determinism evience is given by repeated prediction in same runtime. Parity evidence is given by same prediction across runtimes.

Our Docker image uses `FROM python:3.13-slim`. That does not mean the container is Ubuntu. Our portability evidence is macOS developer environment, Linux Docker serving environment, and Ubuntu GitHub Actions verification environment.

For deployment, we can definitely claim we have a production-style system, we can kind of claim we have a deployment-ready-ish architecture, and we definitly cannot claim that we have a fully deployed production system.

### Question 3
Why is it useful to separate the development/testing environment from the serving runtime, what belongs in our Docker image, and why are notebooks, training data, pytest, and other development tools not required merely to serve predictions?

**Best sections to review: 5D — Audit the Dependency Sources of Truth, 5S — Training Reproducibility vs Serving Reproducibility, and 5T — What Belongs in the Runtime Image?**

*Because the serving runtime does not need the components of the system that were used for testing. Once testing has been carried out and confirmed that the system is working as intended, there is no need for the testing components to serve a client. It's possible for the system to be run without the testing components. The same could not be said about being able to develop the system without the testing components.*

*As for what belongs in our Docker image, it deliberately contains the items on this list: Python runtime, application package, runtime dependencies, three frozen inference artifacts, and startup configuration. On purpose, we have let it not contain the items on the following list: notebooks, training datasets, pytest, pytest-cov, development tooling, and full experiment history. This is due to a separation of concerns. The development environment allows us to build, test, and change the system. The runtime environment allows us to operate the system. We separate these because a narrow runtime image generally makes the operational contract easier to understand.*

In the development/testing environment, we build, modify, diagnose, and verify. 

In serving/runtime, we operate the already-built application.

The running production-style service does not need to carry its development verification tooling inside the serving image. CI still needs pytest; Uvicorn serving predictions does not.

### Question 4
Explain the architectural dependency chain among the inference core, FastAPI layer, Docker/CI runtime layer, and upcoming Streamlit frontend. Why should Streamlit call FastAPI rather than load the model directly, and what problems would two independent serving paths create?

**Best sections to review: 5W — The Important Architectural Separation, 5X — Phase 2.5 Handoff Contract, and 5Y — What Phase 2.5 Should Not Become**

*The principle at play here is that we now have three major architectural layers. First, we have the inference core system. This was built in Phase 2.1 and can take raw engine history as input and give estimated RUL as output. This gets used by the API/transport system, which is the second layer. This was built in Phase 2.2 and can make HTTP send data back and forth between the inference core. This gets used by the runtime/operations system, which is the third layer. This was built in Phase 2.4 and intertwines dependencies, Docker, and CI.*

*So, from the ground up, the layers are: inference core -> API/transit -> runtime/operations. And, finally, the Streamlit front end will be built on top of these three layers. As for why we need to build this in a way where Streamlit calls FastAPI rather than loads the model directly, that would create two serving paths and make our software system unnecessarily complicated with duplicate logic. The API needs to remain as the only serving boundary, and we need to create a situation where the front end could be described as an API client.*

Streamlit with HTTP client -> FastAPI with calls -> inference core with loads/uses -> frozen model.

Around that system, Docker is what packages its runtime and CI verifies its software/runtime contracts.

Keeping FastAPI as the sole serving boundary gives us one inference implementation, multiple possible clients.

### Ideas to Retain

`constraints.txt` != a more detailed `pyproject.toml`

determinism != local/container parity

`python:3.13-slim` Docker environment != Ubuntu necessarily

Docker/CI -> operational infrastructure around application layers

`pyproject.toml` declares dependency intent; constraints pin a tested resolution without requesting packages themselves.

Reproducibility asks whether the system can be reconstructed; determinism asks whether repeated execution behaves consistently; parity asks whether behavior survives an environment change; portability asks where the system can operate.

GitHub's running is Ubuntu; the Docker image is Linux but should not be casually described as Ubuntu.

Development tooling verifies the application; it does not have to ship inside the serving runtime.

FastAPI remains the single inference-serving boundary. Streamlit should become an HTTP client, not a second model-serving implementation.