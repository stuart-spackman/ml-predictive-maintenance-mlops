## Phase 2.4 — Task Group 2 Active Recall

### Question 1
What is the difference between a Dockerfile, a Docker image, a Docker container, and the Docker Engine, and how do they relate during `docker build` and `docker run`?

**Best sections to review: 2B — Image vs Container and 2E — Docker Engine, Dockerfile, Image, Container**

*A Docker image is the packaged template, and a container is a running instance created from that image. The image itself does not run, but a container runs from an image.*

Docker image -> blueprint

Docker container -> instantiated/running copy of blueprint

*Meanwhile, a Dockerfile is best thought of as a recipe. The Docker engine is the system that builds/runs containers. A Docker image is a built artifact that was produced from a recipe. A container is a running instance of an image. The Docker flow is:*

*start with a Dockerfile -> use `docker build` to fire up the engine -> use `docker run` to load an image and instantiate a container from it.*

`docker build` sends a build request to the Docker engine after it is already running.

Dockerfile
-> docker build asks Docker Engine to execute the recipe
-> Docker image
-> docker run asks Docker Engine to create/start a container
-> running container

### Question 2
What is the Docker build context, what does the final `.` mean in `docker build -t predictive-maintenance-api:0.1.0 .`, and why do we use `.dockerignore` rather than simply sending the entire repository state into every build?

**Best sections to review: 2F — The Build Context and 2G — `.dockerignore`: Control What Enters the Build Context**

*The place where the `.` goes is for the build context. The final `.`, which is extremely important, means to use the current directory as the Docker build context. As for why we use `.dockerignore`, we want to avoid sending our entire repository state into Docker. Without the `.dockerignore` file, we would risk copying secrets or the potentially huge local environment.*

The build context isn't necessarily everythin that enters the image. It's the filesystem material Docker is allowed to consider/access during the build.

repository root -> build context
`.dockerignore` -> filtered build context
`COPY src/ src/` -> specific content actually copied into image

`.dockerignore` helps with security, performance, smaller build contexts, cleaner caching, and preventing irrelevant developer-machine state from even being available to `COPY`.

### Question 3
What is the difference between `RUN`, `CMD`, `COPY`, `WORKDIR`, and `EXPOSE` in our Dockerfile? In particular, why does `EXPOSE 8000` not by itself make the FastAPI service reachable from the host?

**Best sections to review: 2H — Dockerfile Instructions, 2R — `EXPOSE 8000` Does Not Publish a Port, and 2S — Why Use the JSON/Exec Form of `CMD`?**

* `RUN` tells the program to begin the image from an existing base image containing a lightweight Linux environment and the enviroment stated on the code line. This is the foundation. `docker build` is the command that executes `RUN`.

* `CMD` defines the default command executed when a container starts from the image. `docker run` executes `CMD`. 

* `COPY`copies files from the build context into the image filesystem (it does not copy from the arbitrary host filesystem).

* `WORKDIR` tells the program to use this directory as the working directory for subsequent instructions and the runtime process.

* `EXPOSE` tells the program to make the image expect the service to listen on the following port. But, this does not make the port reachable. Actually making the port reachable from the host is done with the `docker run` command to establish host/container port mapping. 

`FROM` -> choose the base image

`WORKDIR` -> set the working directory

`COPY` -> copy files from the build context into the image

`RUN` -> executes the command while building the image

`EXPOSE` -> document the port the application expects to use

`CMD` -> define the default command when a container starts

`FROM python:3.13-slim` -> start from a Linux/Python base image

`RUN python -m pip install ...` -> during image construction, execute pip and install our application/dependencies

`docker build` -> `RUN` executes

`EXPOSE 8000` != publish port 8000

Later we'll do something that establishes host-to-host container mapping.

### Question 4
Why does our Docker runtime install the project with `pyproject.toml` plus `requirements/constraints.txt`, but not install the `[dev]` extra? What is the role of the constraints file when it contains packages such as pytest that the runtime installation never requests?

**Best sections to review: 2K — Why Installing the Project Inside Docker Matters, 2L — Our Baseline Dockerfile, 2N — Why the Constraints File Still Matters in Docker, and 2O — What Does `--no-cache-dir` Mean?**

*As part of combining `pyproject.toml` and `constraints.txt`, we are accounting for what runtime dependencies are needed and their exact known-good resolutions. When it comes to not installing the `[dev]` extra, that appendage is best used for development workspaces, which is something the container is not. The role of the constraints file is to constrain packages if they are being installed. The constraints file itself does not request every listed package.*

The constraints file itself does not request every single listed package. 

The constraints file is a list of IF -> THEN statements. 
IF `this particular software package gets installed` -> THEN `use this tested version of it`

It doesn't request that any of the software packages on the list get installed, just what tested version of it to use if it gets installed. 

### Question 5
Why are model-artifact paths especially important for containerizing this ML application, and what distinct evidence is provided by (a) checking that artifact files exist inside the image and (b) actually calling `create_default_inference_pipeline()` inside the container?

**Best sections to review: 2J — Audit Artifact Paths Before We Build, 2M — Why Copy Only the Three Model Artifacts?, 2Z — Verify the Frozen Artifacts Exist Inside the Image, and 2AA — Stronger Image Smoke Test: Load the Real Pipeline**

*Normally, a web application would only need the source and the dependencies. Our project differs from most web applications in that it also requires the frozen model assets. It's also important that we make these dependencies explicit. When it comes to the evidence needed, first a verification that the source package is present and the model artifacts are present is needed. Next, loading the real pipeline is done as a smoke test.*

This isn't merely a web application that we're creating, it's an ML serving application whose runtime depends on frozen model artifacts. 

`assert artifact.is_file()` proves the expected files exist at the expected locations. But that's weak evidence by itself. 

A `.joblib` file could exist while being corrupt, wrong model, wrong hash, incompatible, unreadable, inconsistent with locked metadata. Then `create_default_inference_pipeline()` provides much stronger evidence: 
-> path resolution works
-> files can be opened
-> integrity verification works 
-> metadata can be parsed
-> joblib model can be deserialized
-> model/spec contract is acceptable
-> real inference pipeline initializes

Presence is not usability. The two checks are not redundant. 

artifact existence test -> packaging/location evidence

real pipeline initialization -> application-level comsumption evidence

### Question 6
Why is a successful `docker build` not sufficient evidence that the service works, what does TG2 legitimately establish, and what runtime/service behaviors remain for TG3 to prove?

**Best sections to review: 2AB — Build Success Is Not Runtime Success, 2AE — Mac vs Linux Is Part of the Experiment, 2AG — What TG2 Does Not Yet Prove, and 2AH — Task Group 2 Completion Audit**

*If `docker build` is successful, then we have proven that Docker successfully executed the Dockerfile and produced an image. It does not prove that the API starts, the model loads, the port is reachable, `/health` works, or `/predict` works. We can think of the image build as providing packaging evidence. Runtime evidence is not provided until container execution is done. Task Group 3 will deal with proving the HTTP service is reachable from the host, the port mapping is correct, the health endpoint responds, the prediction endpoint responds, container shutdown behavior is correct, local/container prediction parity, and runtime restart behavior is correct.*

There are three evidence levels: 
* docker build -> packaging evidence
* container execution -> runtime evidence
* HTTP interaction -> service behavior evidence

We can now legitimately say that the project can be packaged into a Linux-based Docker image containing the application, constrained runtime dependencies, and frozen model artifacts, and the real Phase 2.1 inference pipeline successfully initializes from that image.

### Ideas to Retain 

* `FROM` = choose foundation + `RUN` = execute during build + `CMD` = default execution at container startup

* Dockerfile = recipe; image = built artifact; container = running instance; Engine = system that builds and runs them.

* Build context controls what Docker can access; `.dockerignore` deliberately narrows it.

* `FROM` chooses base image, `RUN` executes at build time, and `CMD` defines default container-start behavior. 

* Constraints restrict versions of packages that are requested; they do not request every listed packaged.

* Artifact existence proves packaging/location; real pipeline initialization proves those artifacts can actually participate in the application's inference contract.

* A successful image build is packaging evidence, not service-level evidence.