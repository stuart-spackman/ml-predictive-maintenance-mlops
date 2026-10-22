## Phase 2.4 — Task Group 5 Active Recall

### Question 1
Starting from a fresh clone of the repository, describe the full reproducibility chain that takes the project from source code to a verified running prediction service. What distinct roles do `pyproject.toml`, `requirements/constraints.txt`, the virtual environment, the Docker image, and GitHub Actions play?

**Best sections to review: 5A — The Core Phase 2.4 Claim, 5D — Audit the Dependency Sources of Truth, 5O — Understand the Full Reproducibility Chain, and 5Z — Final Phase 2.4 Completion Audit**

### Question 2
What is the difference between reproducibility, determinism, portability, and deployment? What evidence from Phase 2.4 supports each concept, and which stronger claims would still be unjustified?

**Best sections to review: 5P — Reproducibility Is Not Determinism, 5Q — Reproducibility Is Also Not Portability, 5R — Reproducibility Is Also Not Deployment, and 5S — Training Reproducibility vs Serving Reproducibility**

### Question 3
Why is it useful to separate the development/testing environment from the serving runtime, what belongs in our Docker image, and why are notebooks, training data, pytest, and other development tools not required merely to serve predictions?

**Best sections to review: 5D — Audit the Dependency Sources of Truth, 5S — Training Reproducibility vs Serving Reproducibility, and 5T — What Belongs in the Runtime Image?**

### Question 4
Explain the architectural dependency chain among the inference core, FastAPI layer, Docker/CI runtime layer, and upcoming Streamlit frontend. Why should Streamlit call FastAPI rather than load the model directly, and what problems would two independent serving paths create?

**Best sections to review: 5W — The Important Architectural Separation, 5X — Phase 2.5 Handoff Contract, and 5Y — What Phase 2.5 Should Not Become**