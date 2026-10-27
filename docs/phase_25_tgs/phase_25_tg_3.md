## Phase 2.5 — Task Group 3 Active Recall

### Question 1
Walk through the complete successful request path from a user uploading an engine-history CSV in Streamlit to the estimated RUL being displayed. For each major layer—Streamlit, demo adapter, demo client, FastAPI, inference pipeline, and frozen model—state what that layer owns and one thing it deliberately does not own.

**Best sections to review: 3A–3E — Architectural and Boundary Audits, 3AB — Explain the Full Request Without Looking at Code, and 3AH — Final Phase 2 Handoff**

### Question 2
Explain the complete failure path for a structurally representable but domain-invalid request such as a seven-cycle engine history. Why is it important that the frontend can construct and send the request, the inference pipeline remains authoritative for the minimum-history rule, FastAPI translates the backend exception into HTTP, and the client creates its own local error rather than receiving the original Python exception?

**Best sections to review: 3D — Audit the Inference Boundary, 3H — Audit the Error Ownership Model, 3S — Run the Final Failure Paths, and 3AC — Explain the Failure Path**

### Question 3
Distinguish the roles of `pyproject.toml`, `requirements/constraints.txt`, the Dockerfile/image/container, and GitHub Actions. What does each contribute to reproducibility or verification, and what would be an overclaim about what each one proves?

**Best sections to review: 3I–3L — Runtime, Reproducibility, Docker, and CI Audits, 3AD — Why Docker Exists, and 3AE — Why CI Exists**

### Question 4
Why can this project legitimately be described as a production-style ML inference system but not a fully production-deployed platform? Give several concrete Phase 2 capabilities that support the production-style claim, then explain the `claim → evidence → test` mindset using at least two examples from the project.

**Best sections to review: 3Y — What Phase 2 Now Contains, 3Z — What “Production-Style” Means Here, 3AA — The Most Important Interview Story, 3AF — Final Claims → Evidence → Test Audit, and 3AG — Phase 2 Completion Standard**

### Help Needed

* What's the difference between continuous and contiguous? 