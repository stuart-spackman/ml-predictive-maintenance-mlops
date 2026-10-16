## Phase 2.4 — Task Group 3 Active Recall

### Question 1
What exactly does `-p 8000:8000` mean in `docker run`, what is the difference between the host port and container port, and why does Uvicorn bind to `0.0.0.0` inside the container while we call `127.0.0.1` from the Mac?

**Best sections to review: 3B — Container Port vs Host Port and 3E — Why `0.0.0.0` Inside the Container Matters**

### Question 2
What different evidence is provided by `docker ps`, `docker ps -a`, `docker port`, `docker logs`, and successful requests to `/health`, `/metadata`, and `/predict`? Why is no single one of those sufficient to prove the entire service works?

**Best sections to review: 3F — Use a Second Terminal, 3G — Verify `/health`, 3H — Verify `/metadata`, 3I — Test the Real `/predict` Endpoint, and 3S — What If the Container Exits Immediately?**

### Question 3
What is the difference between `docker run`, `docker start`, `docker stop`, and `docker rm`, and why is deleting a container and creating a fresh one from the same image stronger reproducibility evidence than merely restarting the existing container?

**Best sections to review: 3L — Test Graceful Shutdown, 3M — `docker run` vs `docker start`, 3N — Detached Mode, 3O — Restart vs Recreate, and 3P — Container State Must Not Be the Source of Truth**

### Question 4
Why is calling the containerized service through real HTTP stronger system-level evidence than using FastAPI `TestClient`, and what does local/container prediction parity tell us that simple prediction determinism does not?

**Best sections to review: 3I — Test the Real `/predict` Endpoint, 3Q — Local vs Container Prediction Parity, and 3R — Prediction Determinism vs Runtime Parity**

### Question 5
Distinguish the Docker image, container, Uvicorn process, and HTTP service. If `docker build` succeeds but `/health` cannot be reached, what different failure boundaries could still be responsible, and what debugging sequence should you use?

**Best sections to review: 3A — Image Success vs Service Success, 3S — What If the Container Exits Immediately?, 3T — Container Lifetime Follows the Main Process, 3U — Image, Container, Process, and Service, and 3Z — What TG3 Establishes**