## Phase 3.2 — Task Group 4 Active Recall

### Question 1
What is the difference between model promotion and model deployment in our project, and why does moving `models:/fd001-rul@champion` from the Random Forest version to the Extra Trees version not automatically mean the FastAPI service is now serving Extra Trees?

**Best sections to review: 4A — Promotion as Governance, 4M — Registry Promotion vs. Deployment, and 4P — Phase 3.2 Exit State**

*Model promotion is the process of figuring out which model is approved to be the new champion and changing the associated label in MLflow.*

*Model deployment is the process of changing the model bytes that the ML application actually loads.*

*As for why moving `model:/fd001-rul@champion` from the Random Forest version to the Extra Trees version does not automatically mean the FastAPI service is now serving Extra Trees, changing the MLflow pointer is just one of several things that needs to happen in order for the FastAPI service to now serve Extra Trees. There are also several changes that need to happen in the codebase of our application.*

### Question 2
What does the final provenance gate establish, and how do the candidate's MLflow model version, source `run_id`, source artifact, Phase 3.1/3.2 evidence files, evidence hashes, and Git state work together to make the promotion decision traceable?

**Best sections to review: 4B–4D — Provenance, Source Runs, and Git State, and 4L — Decision Record**

*The final provenance gate establishes that we can answer a list of questions about the model that was evaluated, such as:*
* Which MLflow run produced it? 
* Did that run finish successfully? 
* Which TG2/TG3 evidence files support approval?
* What Git state existed when promotion occurred?
*We've already proven that the candidate works, now that we're at the final provenance gate we need to be able to tell the story of how it got there and make sure any information in that story isn't missing from our historical records.*

*As for how the candidate's MLflow model version, source `run_id`, source artifact, Phase 3.1/3.2 evidence files, evidence hashes, and Git state work together to make the promotion decision traceable, they give a comprehensive list of which evidence bytes were part of the decision record of promoting the model. The principle at play here is that we want to show integrity in addition to correctness.*

### Question 3
Why does TG4 recheck the current champion and rerun the software quality gate immediately before promotion, and what purpose does rollback serve if part of the registry transition fails after mutation has begun?

**Best sections to review: 4F–4H — Rechecking Evidence, Final Tests, and Rollback Protection**

*TG4 rechecks the current champion and reruns the software quality gate immediately before promotion because decision evidence can become stale. We don't want to assume that nothing important in our codebase changed in between TG2 and TG4, for example. There are situations where people manually change aliases without telling other stake holders. The principle at play here is that we need to verify the world still matches the assumptions under which we're making the decision.*

*As for what purpose the rollback serves if part of the registry transition failes after mutation has begun, we don't want to leave open the possibility that verification crashes and we're left with an ambiguous registry state. The principle at play here is that we want to implement fail-safe release engineering.*