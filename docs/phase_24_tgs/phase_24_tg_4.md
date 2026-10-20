## Phase 2.4 — Task Group 4 Active Recall

### Question 1
What is continuous integration, how is it different from continuous delivery/deployment, and why should CI automate our existing Phase 2.3 definition of “passing” rather than invent a separate quality standard?

**Best sections to review: 4A — What Is CI?, 4B — CI vs CD, 4H — The Existing Quality Gate Must Remain Authoritative, and 4AD — Green CI Does Not Mean “Bug-Free”**

*The idea of continuous integration is that changes to a shared codebase are automatically integrated with a verification process, i.e., running quality tests and checks. Continuous delivery/deployment, on the other hand, is the process of automatically preparing or releasing changes. As for why CI should automate our existing Phase 2.3 definition of "passing" instead of inventing a new quality standard, not doing so could create situations where false negatives and false positives could come up when it comes to passing quality checks. Without having alignment with the Phase 2.3 definition of "passing", there could be a local pass while CI fails or a local fail while CI passes. We don't want to create a situation where there are different environments enforcing different rules.*

The goal is to have one definition of passing, not two.

local quality gate = CI quality gate

CI should automate the project's quality contract, not create a competing quality contract.

### Question 2
What are a workflow, job, step, action, and runner in GitHub Actions? Why does a fresh GitHub-hosted runner provide useful reproducibility evidence beyond merely running the tests again on your Mac?

**Best sections to review: 4C — Why GitHub Actions?, 4D — A GitHub Actions Mental Model, 4E — CI Is Another Hidden-State Test, and 4M–4N — Checkout and Python Setup**

*A workflow is the blueprint for running a CI process. A successful workflow means the current revision satisfied the checks we chose.*

*A job is a component within a workflow.*

*A step is a component of running a job.*

*An action is a command that gets triggered and runs from within a job.*

*A runner is a machine on which the job executes.*

*As for why a fresh GitHub-hosted running provides especially useful reprodcibility, GitHub-hosted runners can be thought of as fresh virtual machines. GitHub-hosted runners could be described as clean-room experiments; they don't inherit anything from the following list: the Mac's `.venv`, the shell configuration, the manually installed packages, the local Docker containers, and the untracked files.*

Heirarchy: workflow -> job -> step

An action is best thought of as reusable packaged automation that a workflow step can invoke.

step -> one unit of work inside a job

action -> reusable packaged functionality that a step can invoke

shell command -> command that a `run:` step executes directly

### Question 3
Explain the roles of `actions/checkout`, `actions/setup-python`, `uses:`, `run:`, `runs-on`, and the `push`, `pull_request`, and `workflow_dispatch` triggers in our workflow.

**Best sections to review: 4K — Workflow Triggers, 4L — `uses:` vs `run:`, 4M — Why `actions/checkout` Is Needed, and 4N — Why `actions/setup-python` Is Needed**

*`actions/checkout` is needed because the runner starts off as a fresh machine; it does not contain our repository at the very start of the process. `actions/checkout` is a key component of getting our YAML file to put the repository contents into the job workspace.*

*`actions/setup-python` exists to deliberately choose the interpreter instead of accepting whatever Python happens to be first in the runner's `PATH`. This is important because runner defaults can vary, but `setup-python` gives a guaranteed interpreter selection.*

*`uses:` is a command for running a reusable GitHub action. It invokes packaged workflow functionality.*

*`run:` is a tool for executing a shell command on the runner. This is when we want to execute a command ourselves.*

*`runs-on` is how we select the substrate operating system that our workflow runs on. So far in our project the best option for this has been `ubuntu-latest`.*

*`push` refers to us pushing changes to our codebase. In the case of writing a push into a YAML file, we are putting in a checks that asks, "Does the resulting `main` branch satisfy the gate?"*

*`pull_request` refers to dealing with a request to make changes to our existing codebase, and such changes are gated by our workflow. The `pull_request` part of our YAML file is a check to ask, "Does this proposed change satisfy the gate before merging?"*

*`workflow_dispatch` lets you manually invoke the workflow from GitHub when useful.*

`runs-on` selects the runner

push -> verify the resulting repository state

pull_request -> verify proposed repository state

workflow_dispatch -> manually request workflow execution

### Question 4
Why does CI install with `pyproject.toml` plus `requirements/constraints.txt` and the `[dev]` extra, why don't we automatically upgrade dependencies during the job, and how does pytest's exit code turn the Phase 2.3 quality gate into a CI pass/fail decision?

**Best sections to review: 4H — The Existing Quality Gate Must Remain Authoritative, 4I — How CI Decides Pass or Fail: Exit Codes, 4P — Dependency Caching, 4Q — Don't Automatically Upgrade Dependencies in CI, and 4R — First CI Job: Python Quality Gate**

*The principle at play here is that we do not watn to turn our baseline CI job into an upgrade experiment. The question our CI process needs to answer is, "Can the push pass in the declared/constrained environment?" If we installed with the latest and greatest versions of all our dependencies, then the question would become more like, "Can the push pass our CI process now that we've changed the code AND modernized our tooling?" It's also worth noting that CI is a development/testing evironment, so the `[dev]` extra needs to be included.*

*As for why we don't automatically upgrade dependencies during the job, we don't want to create a confounding test situation. When we push code, we want to see if that code passes our quality checks in the constrained environment that was already verified. Upgrading dependencies during the job could create a situation where our push fails and we won't have a distinct way of knowing if it was because new code got introduced or if it was because an upgraded software package got introduced.*

*Finally, pytest's exit codes turn the Phase 2.3 quality gate into a CI pass/fail decision as a result of the fact that command-line prompts report an exit status. pytest adheres to this convention as well when we run it from the command line. If pytest exits with a code of 0, then our CI process passed. If pytest exits with a code that isn't zero, then we can infer that something failed and use the exit code as a starting point for our investigation.*

Key idea: code changed + dependencies held controlled -> failure is easier to attribute

CI gets `[dev]` because CI is exercising development/verification tooling: pytest, pytest-cov, httpx. But keep in mind the production Docker runtime doesn't need those simply to serve predictions.

GitHub Actions doesn't need to understand pytest's testing semantics. It mainly sees operating-system-level results: process exited 0 or process exited nonzero.

### Question 5
Why are `quality-gate` and `docker` separate jobs, what does `needs: quality-gate` accomplish, and why must the Docker job check out the repository again even though the quality-gate job already did so?

**Best sections to review: 4U — Add Docker Verification as a Separate Job, 4V — What Does `needs:` Mean?, and 4W — Jobs Do Not Share a Filesystem**

*`quality-gate` and `docker` are separate jobs because jobs do not share a filesystem; each job normally gets its own runner environment. So, the `quality-gate` process gets its own runner and the `docker` process gets its own runner. Steps within one job share that jobs workspace and can access the same resources. Separate jobs do not automatically share filesystem state and are blind to the results that were obtained during other jobs.*

*`needs: quality-gate` means that the Docker job isn't allowed to start unless the quality-gate job succeeds. Building an image after a failed a quality gate would be a waste of resources. If a test fails, then the quality gate fails, then the docker job does not run. That's the negated sequence of events we're trying to enforce.*

*As for why the Docker job must check out the repository again even though the quality-gate job already did so, this is because jobs are set up to be independent of each other. Each job gets set up with its own filesystem and can't access the filesystem of other jobs unless some sort of an explicit caching situation is set up.*

Separate jobs do not automatically share filesystem or process state. But! Jobs can communicate deliberately.

`needs:` itself lets a downstream job know whether its prerequisite succeeded.

Separate jobs are isolated by default and don't automatically share files, installed packages, processes, or workspace state. Any information transfer must be explicit.

Skipping Docker after quality-gate failure is partly about saving resources, but even more importantly it expresses our intended dependency: 
-> Don't ask: "Can failing software be packaged?" until we've established: "Does the software satisfy its primary gate?"

### Question 6
What does a green TG4 workflow legitimately prove, what does it still not prove, and why would a failure that occurs only on GitHub's clean Linux runner be useful engineering evidence rather than merely a CI inconvenience?

**Best sections to review: 4AD — Green CI Does Not Mean “Bug-Free”, 4AE — CI Failure Is Useful Information, 4AF — Why We Aren't Adding an OS Matrix Yet, 4AG — CI vs Docker Reproducibility, 4AL — Task Group 4 Completion Audit, and 4AM — What TG4 Does Not Yet Establish**

*A green TG4 workflow legitimately proves that all encoded checks passed in the environment that they were run in. There is still a relatively long list of things that it does not prove: no bugs exist, model is optimal, API scales infinitely, security is perfect, data drift won't happen, production deployment will work everywhere. The principle at play here is that the confidence of the workflow we've created is bounded by the tests and checks that we've encoded, nothing more.*

*As for why a failure that occurs only on GitHub's clean Linux runner would be useful engineering evidence rather than merely a CI inconvenience, it means a project assumption got exposed as needing a fix by the clean runner. If the goal is to have our project get up and running in a clean environment, then now we have evidence of that goal not being met yet.*

The confidence of the workflow we've created is bounded by the tests and checks that we've encoded.

passes on developer Max + fails on fresh Linux runner -> environmental assumption exposed

### Help Needed 

* What does YAML stand for? Where does that name come from? 

*YAML stands for YAML Ain't Markup Language.*

HTML -> markup describing a document/page

YAML -> structured data/configuration

### Ideas to Retain

* Workflow -> job -> step; an action is a reusable packaged automation invoked by a step.

* Separate GitHub Actions jobs are isolated by default, not completely incapable of communication. 

* Exit codes are the generic operating-system contract that lets pytest drive CI success or failure.

* A clean-runner fialure is evidence of an assumption that your developer machine was hiding. 

* YAML originally meant "Yet Another Markup Language," but now officially means the recursive acronym "YAML Ain't Markup Language."