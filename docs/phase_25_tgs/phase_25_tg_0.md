## Phase 2.5 — Task Group 0 Active Recall

### Question 1
What is the architectural role of Streamlit in this project, why should it be treated as an API client rather than another inference implementation, and what problems would arise if Streamlit loaded the model or called the inference pipeline directly?

**Best sections to review: 0A — What Is the Demo Actually For?, 0B — The Demo Is a Client, 0C — Why Not Let Streamlit Import the Inference Pipeline?, and 0D — Single Source of Truth Applies to Behavior Too**

*The primary role of the frontend of this project is to make the existing engineering work visible and usable. We're adding presentation over existing capability, not new ML capability. As for why it should be treated as an API client rather than an existing implementation, we want to create a situation where FastAPI is the boundary that needs to be crossed via sending engine history to get an prediction. Allowing a second path to getting RUL predictions would duplicate logic and make the prediction process unnecessarily complicated. We only want there to be one way to access inference.*

*When it comes to what problems would arise if Streamlit loaded the model or called the inference pipeline directly, it might work for getting valid RUL prediction initially. But we want to enforce just one API contract, one inference implementation, and allow for many possible clients. If we were to create multiple paths to inference, then if we added new functionality to the application, e.g., new API validation, authentication, rate limiting, then we would need to account for those changes in all paths to inference instead of just one. The principle at play here is that we want to have just one source of truth in matters of getting access to inference.*

many possible clients -> one API contract -> one inference implementation

Clients consume inference through the service contract; they do not bypass the service contract.

### Question 2
Which responsibilities belong to Streamlit, FastAPI, the inference pipeline, and the frozen model? What is the difference between frontend/preflight validation and authoritative backend/domain validation?

**Best sections to review: 0E — Responsibility Boundaries, 0F — Frontend Validation vs Backend Validation, 0V — Failure Paths Matter Too, and 0W — Do Not Leak Backend Internals**

*Streamlit owns the items on the following list: presentation, user interaction, file selection/upload, basic display formatting, calling HTTP endpoints, showing returned API results, and showing user-friendly connection/errors.*

*FastAPI owns the items on the following list: HTTP contract, request schemas, response schemas, transport-level validation, exception translation, and public endpoint semantics.*

*The inference pipeline owns raw history domain validation, feature engineering, artifact verification, model compatibility, and prediction.*

*The frozen model owns the learned mapping of the inference process, i.e., mapping model features to an RUL estimate.*

*As for frontend/preflight validation, this part of the application improves experience. It offers validation by asking if a file was uploaded, checking if it can be parsed, asking if it appears to have the fields needed to build an API request, and askign if the user provided an engine identifier.*

*As for the backend/domain validation, this part of the application protects the correctness of the serving process. It does things such as asking if history is sufficiently long, checking if cycles are valid and contiguous, checking if values are finite, and asking if the history satisfies the inference contract.*

Streamlit -> presentation/interaction

FastAPI -> HTTP contract/transport concerns

Inference Pipeline -> domain correctness/features/artifacts/prediction

Frozen Model -> learned feature-to-RUL mapping

fronend validation -> convenience 

backend validation -> authority

The frontend is never a security or correctness boundary merely because it happens to perform checks. 

### Question 3
Why is an engine-history CSV a better primary demo input than manually entering sensor values, and why is converting CSV data into the Phase 2.2 API request representation acceptable in the frontend while calculating temporal/model features there would violate the architecture?

**Best sections to review: 0G — What Should the User Input?, 0H — Proposed MVP Input Contract, and 0I — Representation vs Meaning**

*The principle at play here is that we want to avoid making an ugly demo; we don't want to create a situation where a human user needs to manually type in the input values to create an engine history. As for why converting CSV data into the Phase 2.2 API request representation acceptable in the frontend while calculating temporal/model features there would violate the architecture, the frontend can adapt representations without violating the inference contract. The contract states that calculating temporal/model features is owned by the inference pipeline, doing that before uploading an engine history via the UI we're making would violate the inference contract.*

Converting CSV to the JSON request representation is allowed because we're changing representation, not deriving new semantic information. It's not okay to create new, model-specific derived information.

format adaptation -> client responsibility

feature engineering -> client responsibility

Representation versus derived meaning is the phrase worth maintaining.

### Question 4
Describe the intended Phase 2.5 runtime architecture, including the separate Streamlit and FastAPI processes, configurable API location, the role of the existing Docker image, and why we are deliberately not adding Streamlit to the API image or introducing Docker Compose yet.

**Best sections to review: 0O — API URL Is Configuration, 0P — Streamlit and FastAPI Are Separate Processes, 0Q — Keep the Existing API Docker Image Focused, 0R — Don't Add Docker Compose Yet, and 0Y — The MVP Contract We're Freezing**

*An important thing to note here is that Streamlit and FastAPI are separate processes; they each occuput their own ports and addresses. They're separate applications that can communicate over HTTP. When it comes to having a configurable API location, we want local development to take place on a local host. The future hosted deployment can be with some remote API address, and this can be done without rewriting frontend logic. The principle at play here is that environment-specific location should be configuration, not buried application logic.*

*As for the role of the existing Docker image, it is going to maintain its primary responsibility of running the inference API. Adding Streamlit to the same image and expecting it to start multiple application processes will unnecessarily complicate the runtime. For this phase of the project we want the Docker container to house the FastAPI backend and the local Streamlit process to house the frontend/client. Docker Compose would allow us to describe everything on the following list in a single file: frontend container, backend container, network, environment variables, ports. But that isn't something we need for this project at the present time.*

Runtime model: 
-> browser
-> Streamlit process paired with HTTP
-> FastAPI process 
-> Inference

The backend is potentially running inside Docker, so Mac branches into Streamlit process and Docker with FastAPI.

The frontend receives that backend location as configuration.

Docker Compose would be perfectly reasonable is we actually had a multi-container deployment problem to solve. But we don't need to add it merely to demonstrate that we know it exists.

### Ideas to Retain

* The frontend exposes capability; it does not recreate capability.

* Frontend validation improves usability, while backend validation remains authoritative. 

* Changing representation is an interface concern; deriving model features is an inference concern.

* API location should be configuration, not hard-coded deployment knowledge. 

* One serving path means future authentication, logging, validation, monitoring, and policy can be applied consistently to every client. 

* Docker Compose is useful when orchestration becomes a real requirement, not merely because multiple services exist conceptually.