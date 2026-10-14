## Phase 2.4 — Task Group 0 Active Recall

### Question 1
What does reproducibility mean specifically for this project, and what is the difference between a reproducible environment and merely having a working `.venv` on the original development machine?

**Best sections to review: 0A — What “Reproducible” Means Here, 0B — Reproducibility Is Mostly About Eliminating Hidden State, 0Y — Define Phase 2.4's Source-of-Truth Hierarchy, and 0Z — Why We Don't Commit `.venv`**

*Reproducible here means that given the repository, declared dependencies, and several other parts of the software suite, a clean supported environment can install the project, run the automated quality gate, start the FastAPI service, and reproduce the intended serving behavior without depending on undocumented state from the original development machine. A reproducible enviroment is one where machine requirements are explicit and reconstructable, with no hidden state being required to run the application outside of the last machine it correctly functioned on. As for `.venv`, it's not something we want to copy around. It's an installed environment and we want enough information to reconstruct it instead of copying it.*

Working `.venv` -> one already-installed environment. 

Reproducible environment -> enough explicit information to reconstruct a working environment elsewhere.

The source of truth should increasingly become: 
* repository
* dependency declarations
* runtime artifacts
* configuration
* quality gate

### Question 2
What is the difference between a direct dependency and a transitive dependency, and between a runtime dependency and a development/test dependency? Why will those distinctions matter when we reconstruct the environment and later build the Docker image?

**Best sections to review: 0J — Direct vs Transitive Dependencies and 0K — Runtime vs Development Dependencies**

*A direct dependency comes in the form of a software package that we directly import in lines of code in our application. A transitive depedency is a dependency of the software packages that we directly import. If it's direct, then the project explicitly depends on it. If it's transitive, then the dependency depends on it.*

*A runtime dependency is something that's needed for the application to actually run. Examples in this project include FastAPI and Pydantic. A development/test dependency is something that's needed to develop and/or test the application, but not necessarily to serve predictions. An example could be pytest; it's needed to develop and do CI for the application, but it's not used while serving predictions to HTTP clients.* 

*These distinctions matter because a Docker runtime image does not automatically need every development tool.*

A direct dependency is something our project intentially declares that it requires.

runtime -> needed to operate the service

development/test -> needed to build, test, inspect, or verify it

For Docker to run a production runtime image it usually does not need pytest and similar tooling.

### Question 3
Why are machine-specific absolute paths and undocumented environment variables threats to portability/reproducibility, and what should we document instead of dumping the developer's entire environment?

**Best sections to review: 0N — Audit Model Artifact Dependencies, 0O — Relative Paths vs Absolute Paths, 0P — Audit Runtime Configuration Without Dumping Secrets, and 0Q — Environment Variables**

*A principle at play here is that we want to avoid having a path that a clean Linux CI runner or container obviously won't have. As for why machine-specific absolute paths and undocumented environment variables are threats to portability/reproducibiliy, absolute paths will vary going from one machine to another. We don't want those hard-coded into our application because the application won't work after being transferred to a machine with a potentially different absolute path. When it comes to why we should document instead of dumping the developer's entire environment, environment variables can contain things like credentials and private paths. We don't want secret values getting exposed as a result of dumping the entire development system.*

The core portability problem is: hard-coded machine path -> assumes one filesystem layout -> breaks elsewhere.

Yes document: required variable names, expected meaning, whether required/optimal, safe example values

No document: real API keys, real secrets, private paths, tokens. 

### Question 4
Why do we run the Phase 2.3 quality gate in the existing environment before changing dependency management or rebuilding the environment, and how will that gate function as evidence during the rest of Phase 2.4?

**Best sections to review: 0R — Audit the Verification Contract From Phase 2.3, 0AB — Run the Existing Quality Gate Once, and 0AD — Phase 2.4's Core Experiment**

*Phase 2.3 handed us a crucial thing in the form of a machine-readable definition of passing. Phase 2.4 must eventually reproduce this in a clean environment. Environment reproducibility is not enough because it only tells us the correct packages are installed. What we really need is proof that the reconstructed environment actually behaves the way we want it to.*

Phase 2.3 gave us a machine-readable definition of passing and that reconstructing packages alone in insufficient.

Establish the known-good baseline before changing the indepdent variable.

### Help Needed 

* What does the `-c` mean in `python -c ...`? 

*`-c` means execute the following string as Python code.*

* What is a runtime image when referring to Docker? 

*A Docker image is a packaged filesystem plus metadata/instructions needed to create a container.*

*A runtime image specifically refers to an image containing what is needed to run the application, rather than everything needed to develop or test it.*

*The container's job is: start API -> receive requests -> serve predictions*

*workshop -> tools needed to build/test the product*

*finished appliance -> components needed to operate the product*

* What is training-serving skew? 

*Training-serving skew means the data transformation or feature logic used during model serving differs from what was used during model training.*

*Reuse one implementation so training and serving perform the same transformation.*

*Training-serving skew is a mismatch between how model inputs are produced during model development/training and how they are produced when the trained model is actually served.*

* What does deterministic means in this context? 

### Ideas to Retain 

* `python -c` executes a short Python program supplied by the command line.

* A Docker runtime image contains what is needed to operate the application, not necessarily all development/testing tools.

* Training-serving skew means the model sees differently constructed inputs in serving than it learned from training. 

* Determinism means same relevant input/state -> same output. 

* Reproducibility means the required environment and behavior can be reconstructed elsewhere. 

* Running the old quality gate first gives us a known-good baseline before we change the environment.