## Phase 2.4 — Task Group 1 Active Recall

### Question 1
What is the difference between an installed package, a direct project dependency, and a transitive dependency, and why would copying every line from an old `pip freeze` into `pyproject.toml` be poor dependency management?

**Best sections to review: 1A — Installed Packages Are Not the Same as Project Dependencies, 1B — Audit What the Project Directly Uses, 1C — Direct Dependency Does Not Always Mean “Imported in Python,” and 1O — Why We Shouldn't Generate the Constraints File From a Dirty Environment**

*An installed pacakge is simply a software package that got installed on the system we are using, stating that something has been installed doesn't carry an implication that we are depedent on it, or how we are dependent on it. A direct dependency is a software package that we explicitly depend on, usually stated with an import in our code (but not always). A transitive dependency is something our direct dependencies depend on, so our application could be descrived as being indirectly dependent on it.*

*As for why copying every line from an old `pip freeze` into `pyproject.toml` would be poor dependency management, `pip freeze` would capture everything in the `.venv`, and it wouldn't be surprising if there were lots of things in the `.venv` that were no longer relevant to the project (or were even harmful to the effeciency of the project). We don't want to turn accidental environment history into official project infrastructure.*

Installed package -> happens to exist in this environment. 

Direct dependency -> our project deliberately requires it.

Transitive dependency -> required by one of our dependencies. 

We don't want to turn accidental environment history into official project architecture.

The bigger problems in this context are unnecessary complexity, larger environments, more dependecy-conflict opportunities, more maintenance/security surface, and false claims about what the project actually requires.

### Question 2
What roles do `pyproject.toml` and `requirements/constraints.txt` play in our design, and why are they complementary rather than conflicting sources of truth?

**Best sections to review: 1L — Direct Dependency Declaration vs Full Resolution, 1M — Our Two-Layer Strategy, 1N — Requirements vs Constraints, and 1AC — Why We Need Both Flexible Intent and Tested Resolution**

*In `pyproject.toml`, we list the packages our project intentionally depends on. However, it's perhaps more useful to know the exact dependency graph that produced our known-good environment. That's where `requirements/constraints.txt` comes in.*

*`pyproject.toml` -> What does the application directly require?*

*`constraints.txt` -> Which package versions formed the test environment?*

*As for why they are complimentary rather than conflicting sources of truth, they offer different layers of the drill-down process for figuring out which packages are best to install in the environment that the application will run in. `pyproject.toml` tells the user which packages to install. `constraints.txt` tells the user that if those packages get installed, there's a specific version that would work best, so use that one.*

pyproject.toml -> dependency intent. 

constraints.txt -> tested resolution (which exact versions formed a known-good, tested environment).

allowed != tested != objectively best

### Question 3
Explain every part of `python -m pip install -e ".[dev]"`. Why is this installation mode useful for local development, and why do development dependencies form a larger set than the dependencies needed by the eventual runtime container?

**Best sections to review: 1H — Source Layout and Installing Our Own Project, 1I — Understanding `pip install -e ".[dev]"`, 1K — Version Constraints, and 1AF — Runtime Installation vs Development Installation**

*The most important part of this command is that `-e` signifies that it's an editable install.*
* python -m pip -> use the version of pip belonging to this Python interpreter
* install -> install something
* -e -> editable installation
* . -> install the project in the current directory
* [dev] -> also install the optional dependency group named dev
*All of that adds up to saying, "Install this project in editable mode together with its development/testing dependencies."*

*As for why this installation mode is useful for the local development, it's sufficient to obtain application dependencies, pytest/test dependencies, and our package, all from project-controlled metadata.*

*Finally, as for why development dependencies form a larger set than the dependencies needed by the eventual runtime container, one of our goals here is to use a Docker runtime image to install the project and the runtime dependencies. Notice the testing dependencies are not included in what Docker can function with, hence the development dependencies form a larger set.*

python -m pip -> pip associated with this interpreter

install -> install 

-e -> editable 

. -> current project 

[dev] -> also install dev extra

One benefit of `-e`: Because the installation points back at your working source tree, you generally do not have to reinstall your project after every source-code change.

development evironment = runtime dependencies + testing/development tooling

runtime container = runtime dependencies + application + artifacts

### Question 4
Why do we deliberately construct a new virtual environment, run the quality gate, capture its resolved dependencies, recreate the environment again using those constraints, and run the quality gate a second time? What different evidence do those two reconstructions give us?

**Best sections to review: 1S — Build a Clean Reconstruction Environment, 1U — Install Only From Declared Project Information, 1V — Test the Newly Reconstructed Environment, 1X — Generate the Known-Good Constraints Snapshot, and 1Z–1AA — Stronger Reconstruction Test**

*To being with, we want to create a clean environment that does not yet know our application's dependencies. Then, we want to check if `pyproject.toml` is sufficient to reconstruct the Python dependencies required for development and testing. We need critical evidence that the quality gate passes in the old environment and the new clean environment, otherwise our dependency metadata has something in need of fixing, i.e., a reproducibility defect. If it passes in the new environment we can create a list of constraints that describe the complete tested dependency resolution.*

First reconstruction: fresh environment -> install from pyproject.toml -> quality gate passes
This proves our declared dependency intent is sufficient to construct a working development/test environment.

Then we capture the exact resolved graph: requirements/constraints.txt

Second experiment after we've destroyed the previous results: fresh environment -> pyproject.toml -> constraints.txt -> quality gate passes
Now we can say that not only can pip find some compatible working environment, but the specific dependency resolution we recorded can itself be reconstructed and verified.

FIRST RECONSTRUCTION with pyproject.toml -> Can our declared requirements resolve into a working environment? 

SECOND RECONSTRUCTION with pyproject.toml + constraints.txt -> Can we reproduce the specific known-good dependency resolution we recorded? 

### Question 5
Why should dependency upgrades be kept separate from this reproducibility work, and how do the constraints file and Phase 2.3 quality gate turn a future dependency upgrade into a controlled engineering change rather than an uncontrolled environment mutation?

**Best sections to review: 1AD — Don't Upgrade Packages Just Because We're Here and 1AE — Dependency Upgrades Become Controlled Experiments**

*The current phase of the project is about reproducing a known-good environment, not modernizing every dependency simultaneously (that might upgrade us into a state of not having a functioning application). After confirming our environment is reproducible, we need to only do one controlled update at a time and then run the quality gate to see if it still passes.*

The current phase's experimental question is: Can we reproduce what already works? 

The controlled engineering process we're aiming for is: 
known-good constrained environment
-> deliberate dependency change
-> resolve 
-> quality gate
-> accept/reject
-> update constraints if accepted

### Help Needed

* Do the letters in `.toml` stand for something? 

Tom's Obvious, Minimal Language

TOML is a configuration-file format designed to be relatively easy for humans to read and edit. 

* What is Starlette and why didn't I see that mentioned in the majority of the previous sections of this project? 

Starlette is a lightweight ASGI web framework/toolkit for Python. 

our API code -> FastAPI -> Starlette -> ASGI -> Uvicorn

FastAPI uses Starlette underneath for much of the fundamental web machinery. 

### Ideas to Retain

Installed means present; direct means deliberately required; transitive means required through another dependency.

`pyproject.toml` expresses dependency intent; `constraints.txt` preserves a known-good tested resolution.

Editable installs point the project back towards the working tree. 

The first clean reconstruction proves dependency declarations are sufficient; the second proves the recorded resolution itself is reproducible. 

TOML means "Tom's Obvious, Minimal Language."

FastAPI is our direct web-framework dependency; Starlette is a lower-level framework FastAPI depends on, making Starlette transitive from our project's perspective.