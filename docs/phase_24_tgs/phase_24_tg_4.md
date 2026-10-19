## Phase 2.4 — Task Group 4 Active Recall

### Question 1
What is continuous integration, how is it different from continuous delivery/deployment, and why should CI automate our existing Phase 2.3 definition of “passing” rather than invent a separate quality standard?

**Best sections to review: 4A — What Is CI?, 4B — CI vs CD, 4H — The Existing Quality Gate Must Remain Authoritative, and 4AD — Green CI Does Not Mean “Bug-Free”**

### Question 2
What are a workflow, job, step, action, and runner in GitHub Actions? Why does a fresh GitHub-hosted runner provide useful reproducibility evidence beyond merely running the tests again on your Mac?

**Best sections to review: 4C — Why GitHub Actions?, 4D — A GitHub Actions Mental Model, 4E — CI Is Another Hidden-State Test, and 4M–4N — Checkout and Python Setup**

### Question 3
Explain the roles of `actions/checkout`, `actions/setup-python`, `uses:`, `run:`, `runs-on`, and the `push`, `pull_request`, and `workflow_dispatch` triggers in our workflow.

**Best sections to review: 4K — Workflow Triggers, 4L — `uses:` vs `run:`, 4M — Why `actions/checkout` Is Needed, and 4N — Why `actions/setup-python` Is Needed**

### Question 4
Why does CI install with `pyproject.toml` plus `requirements/constraints.txt` and the `[dev]` extra, why don't we automatically upgrade dependencies during the job, and how does pytest's exit code turn the Phase 2.3 quality gate into a CI pass/fail decision?

**Best sections to review: 4H — The Existing Quality Gate Must Remain Authoritative, 4I — How CI Decides Pass or Fail: Exit Codes, 4P — Dependency Caching, 4Q — Don't Automatically Upgrade Dependencies in CI, and 4R — First CI Job: Python Quality Gate**

### Question 5
Why are `quality-gate` and `docker` separate jobs, what does `needs: quality-gate` accomplish, and why must the Docker job check out the repository again even though the quality-gate job already did so?

**Best sections to review: 4U — Add Docker Verification as a Separate Job, 4V — What Does `needs:` Mean?, and 4W — Jobs Do Not Share a Filesystem**

### Question 6
What does a green TG4 workflow legitimately prove, what does it still not prove, and why would a failure that occurs only on GitHub's clean Linux runner be useful engineering evidence rather than merely a CI inconvenience?

**Best sections to review: 4AD — Green CI Does Not Mean “Bug-Free”, 4AE — CI Failure Is Useful Information, 4AF — Why We Aren't Adding an OS Matrix Yet, 4AG — CI vs Docker Reproducibility, 4AL — Task Group 4 Completion Audit, and 4AM — What TG4 Does Not Yet Establish**

### Help Needed 

* What does YAML stand for? Where does that name come from? 