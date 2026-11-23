## Phase 4.1 — Task Group 0 Active Recall

### Question 1
What does progressive disclosure mean in the context of this project's documentation, and what should a recruiter understand in roughly the first 15–60 seconds versus what an ML/software engineer should be able to discover through a deeper read?

**Best sections to review: 0B–0C — Audiences and Progressive Disclosure**

*Progressive disclosure means layering the information you reveal about the project so the most important information comes first, and technical details are still made available to readers who choose to read past the initial part of a README document.*

*As for what a recruiter should understand in roughly the first 15-60 seconds versus what an ML/software engineer should be able to discover through a deeper read:*

*A recruiter should be able to understand the fundamental surface-level facts about what your project is, i.e., the problem that it solved, the technologies that were used, if it was more than just a notebook, what makes it an MLOps project, and what the outcome was. These details should be possible to discern very quickly.*

*An ML/software engineer shuold be able to discover some of the deeper details of the project, i.e., how you demonstrated knowledge of concepts such as data leakage prevention, evaluation methodology, model selection, serving architecture, testing, containerization, CI, model versioning, monitoring, and retraining policy.*

Put the most important information first, while preserving deeper technical detail for readers who choose to keep going. 

15 seconds -> Why should I care? 

60 seconds -> What did you build? 

5+ minutes -> Was it engineered correctly? 

### Question 2
Why should the project's technical story be organized around problem → engineering decisions → architecture → evidence rather than around a list of technologies, and what does it mean for a portfolio claim to have an evidence path?

**Best sections to review: 0D — Core Technical Story, 0H–0I — Evidence-Backed Claims and Technology Inventory**

*The project's technical story should be organized around problem -> engineering decision -> architecture -> evidence rather than around a list of technologies because people reading the story of the project need to have a sense that a coherent sequence of event took place to create the application. Otherwise they will have to do the heavy lifting of looking at a list of technologies and figuring out how they were used without any helpful descriptions.*

*As for what it means for a portfolio claim to have an evidence path, it means every time we make a claim about what our application can do there is an evidence path paired with it. Taking this approach is much stronger than simply listing technologies.*

problem -> engineering decision -> architecture -> evidence

An evidence path connects a documentation claim to the concrete code, tests, metrics, or artifacts that demonstrate the claim is true. 

### Question 3
Why would it currently be risky to document Extra Trees as "the production model," and how should the README distinguish experimental superiority, registry/promotion state, deployment state, and the artifact actually served by FastAPI?

**Best sections to review: 0J–0K — Extra Trees Story and Evidence-Backed Metrics**

*It would currently be risky to document Extra Trees as "the production model" because within the project we established that Extra Trees was a better experimental challenger. But! That is not synonymous with being the actually deployed model. On top of that, registry state is not the same as deployment state. Controlled experimentation identified Extra Trees as a stronger challenger, while model promotion and deployment were deliberately treated as separate lifecycle decisions.*

*As for how the README should distinguish experimental superiority, registry/promotion state, deployment state, and the artifact actually served by FastAPI, each of them should trace their associated metrics back to retained artifacts. We need to implement a documentation rule that verified artifacts are paired with metrics and documentation. We should not rely on memory and then go about typing up the documentation.*

Extra Trees performed better experimentally != Extra Trees is necessarily the production model 

registry state != deployment state

The README should conceptually distinguish that four states like this: 

* EXPERIMENTAL RESULT -> Extra Trees achieved stronger validation performance than the Random Forest benchmark. 

* REGISTRY / PROMOTION STATE -> A model may be registered, validated, or assigned a lifecycle alias such as the champion. 

* DEPLOYMENT STATE -> A separate decision determines whether serving should actually cut over to that approved model. 

* ACTUAL SERVING STATE -> The real production identity is whatever artifact the FastAPI inference loader actually loaded. 

Extra Trees demonstrated stronger experimental performance and advanced as a challenger. Model registry promotion and actual serving deployment were treated as separate lifecycle stages; the runtime serving identity is determined by the artifact loaded by the FastAPI inference pipeline.

### Ideas to Retain 

* Documentation is an interface to the project, not merely a record of what files exist.

* Progressive disclosure lets a recruiter understand the project in seconds while still giving an engineer enough depth to inspect it.

* Good technical storytelling emphasizes problem -> decisions -> architecture -> evidence rather than simply listing tools. 

* Every strong portfolio claim should have an evidence path to code, tests, or retained artifacts. 

* Implemented capability and real production experiences are different claims and should never be blurred. 

* A stronger experimental model is not automatically the deployed model.

### More Ideas to Retain 

* Progressive disclosure answers increasingly technical questions as the reader goes deeper. 

* A technical portfolio should tell an engineering story, not display a dependency inventory. 

* An evidence path connects a claim to the implementation, test, report, or artifact that proves it. 

* Experimental superiority, registry status, deployment status, and actual runtime serving identity are four different facts. 

* The serving model is determined by what the runtime actually loads—not by what a registry alias says should be serving. 

* Exact metrics should come from retained evidence, not memory. 

better experiment
!= promoted model 
!= deployed model
!= necessarily actually served model