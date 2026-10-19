## Phase 2.4 — Task Group 3 Active Recall

### Question 1
What exactly does `-p 8000:8000` mean in `docker run`, what is the difference between the host port and container port, and why does Uvicorn bind to `0.0.0.0` inside the container while we call `127.0.0.1` from the Mac?

**Best sections to review: 3B — Container Port vs Host Port and 3E — Why `0.0.0.0` Inside the Container Matters**

*To begin with, our Dockerfile contains `EXPOSE 8000` and Uvicorn starts with `--host 0.0.0.0` and `--port 8000`. That establishes what happens inside the container. But. The computer we're using to run the code in our project still needs to route to that port. That's what the `-p 8000:8000` command handles for us, it means `-p HOST_PORT:CONTAINER_PORT`.*

*As for the difference between the host port and the container port, the host port is the port on the local computer. The container port is the port inside the Docker container that we've instantiated. The host port can be thought of as plugging in to the container port.*

*`12.0.0.1` signifies the ambient machine/process environment's loopback interface. By binding Uvicorn to `0.0.0.0` we tell it to listen on the container's network interfaces so traffic forwarded by Docker can reach it. If we accept traffic entering the container, then we send it to Uvicorn with its port of `0.0.0.0:8000`. If we want to send traffic to a published host port, then we send it to the Mac client with its port of `127.0.0.1:8000`.*

-p 8000:8000 -> HOST_PORT : CONTAINER_PORT, we plug the host port into the container port

0.0.0.0 is a binding address, not normally the destination a client uses

Inside container: Uvicorn binds to 0.0.0.0:8000
-> accept traffic arriving on any container interface

On local machine: client requests 127.0.0.1:8000
-> Docker forwards that to container port 8000

0.0.0.0 describes where the server listens while 127.0.0.1 describes where our host-side client connects.

### Question 2
What different evidence is provided by `docker ps`, `docker ps -a`, `docker port`, `docker logs`, and successful requests to `/health`, `/metadata`, and `/predict`? Why is no single one of those sufficient to prove the entire service works?

**Best sections to review: 3F — Use a Second Terminal, 3G — Verify `/health`, 3H — Verify `/metadata`, 3I — Test the Real `/predict` Endpoint, and 3S — What If the Container Exits Immediately?**

*`docker ps` allows us to inspect containers that are actively running. If we can see the container that we just instantiated on the list, then we have explicit evidence that Docker published the port associate with the instance.*

*As for `docker ps -a`, I'm not seeing a difference in `docker ps` and `docker ps -a` when I run each of those commands. The both seem to have the same output and I don't know what the `-a` means or does. Oh! I think I found it now. `docker ps -a` has the added benefit of checking if a container is in an exited state.*

*`docker port` I also don't see an explantion on. My guess is that it's for checking if a container is active. Oh! Found this one now too. `docker port` is a good tool for listing the host-container port relationship.*

*`docker logs` is a tool for seeing the server startup and requests.*

*A successful request to `/health` provides evidence that a whole chain of events is working properly. In order, it establishes that the container is running, Uvicorn is accepting traffic, Docker port mapping is working, FastAPI routing is working, and the `/health` endpoint is responding.*

*A successful request to `/metadata` provides a more application-specific block of evidence that `/health`. While `/health` provides an answer to "Can this service respond?", `/metadata` provides an answer to "Is this the expected inference service/model contract?" The desirable reponse is model/contract information that's aligned with the system we created in Phase 2.1.* 

*A successful request to `/predict` provides evidence at a system level that everything is working properly. This provides evidence for the most important string of events to get the behavior that we want. In order, we have raw engine history gets correctly fed in via HTTP, containerized FastAPI, the adapter is working, the Phase 2.1 inference pipeline is working, feature construction is working, the frozen model is working, and the RUL response is working.*

*As for why no single one of those is sufficient to prove the entire service works, there are many different components to our system and no single endpoint or command from the command line can activate all of the components.*

The evidence heirarchy is approximately: 

docker ps -> which containers are running now

docker ps -a -> all containers, including stopped/exited ones

docker port pm-api -> configured host/container port publication

docker logs pm-api -> what the container's main process emitted

GET /health -> basic service reachability

GET /metadata -> expected application/model identity

POST /predict -> actual serving behavior

docker ps primarily proves the container is running. 

docker port pm-api is the more focused evidence for the actual port mapping.

Each command observes a different boundary, so no single one established every claim.

### Question 3
What is the difference between `docker run`, `docker start`, `docker stop`, and `docker rm`, and why is deleting a container and creating a fresh one from the same image stronger reproducibility evidence than merely restarting the existing container?

**Best sections to review: 3L — Test Graceful Shutdown, 3M — `docker run` vs `docker start`, 3N — Detached Mode, 3O — Restart vs Recreate, and 3P — Container State Must Not Be the Source of Truth**

*`docker run` asks Docker Engine to create a new container from an image and start it.*

*`docker start` is reserved for containers that already exist and are in a stopped state. This command means start this existing stopped container again.*

*`docker stop` stops a container that is currently running and puts it in a state of no longer running.*

*`docker rm` removes a container that has been stopped.*

*As for why deleting a container and creating a fresh one from the same image makes for stronger reproducibility evidence than merely restarting the existing container, we want the system to be truly reproducible from the image. Merely restarting the existing container doesn't guarantee that something happened during its previous run that will affect system functionality (e.g., creating a new file that the system depended on for behaving properly the last time it was running). Creating a fresh container from the same image removes this risk.*

docker run -> create a new container from an image and start it 

docker start -> start an already-existing stopped container

docker stop -> stop running a container

docker rm -> remove an existing container

the image is the source of truth, not the accidental runtime state.

### Question 4
Why is calling the containerized service through real HTTP stronger system-level evidence than using FastAPI `TestClient`, and what does local/container prediction parity tell us that simple prediction determinism does not?

**Best sections to review: 3I — Test the Real `/predict` Endpoint, 3Q — Local vs Container Prediction Parity, and 3R — Prediction Determinism vs Runtime Parity**

*We want to test the most important behavior of the system, which is taking in raw engine history via HTTP and putting it through all the steps necessary to return an RUL response. We can create a situation where an inspection script it running on the local computer but the API/model is running inside a container we created. If it succeeds, then we will have carried out a system-level test rather than a FastAPI `TestClient` test. This provides better evidence that our system will work in the operations it was intended for. In a FastAPI `TestClient` test, there is no Uvicorn, no real TCP, and no Docker.*

*As for what a local/container prediction parity tells us that simple prediction determinism does not, determinism asks whether repeated inference behaves consistently, i.e. same inputs result in same outputs. Runtime parity, on the other hand, asks whether changing the runtime environment changed behavior, e.g., if switching from the local environment to a container environment changed the input-output results.*

TestClient
* application-level integration
* no Uvicorn
* no real socket/TCP
* no Docker port publication

real HTTP to container 
* host client 
* TCP
* Docker port mapping
* container networking
* Uvicorn
* FastAPI
* inference pipeline

determinism
-> same runtime, same request, repeated behavior

runtime parity 
-> different runtime environments, same request, equivalent behavior

### Question 5
Distinguish the Docker image, container, Uvicorn process, and HTTP service. If `docker build` succeeds but `/health` cannot be reached, what different failure boundaries could still be responsible, and what debugging sequence should you use?

**Best sections to review: 3A — Image Success vs Service Success, 3S — What If the Container Exits Immediately?, 3T — Container Lifetime Follows the Main Process, 3U — Image, Container, Process, and Service, and 3Z — What TG3 Establishes**

*A docker image is the set of frozen parameters that get used to build a container, i.e., a blueprint from which we instantiate containers. A container is the object that gets created from the build process of using an image. Uvicorn process is the setup in which we listen for HTTP requests that are addressed to our system. HTTP service is the process of taking in an input via HTTP, sending it into a process that will use it to make calculations, and then return the results of those calculations.*

*To provide more concise phrasing: An image is the packaged filesystem/configuration, represented by `predictive-maintenance-api:0.1.0`. A container is an instantiated image with a runtime state, represented by `pm-api`. A process is the system running inside the container, represented by `python -m uvicorn ...`. A service is useful behavior exposed to the client, represented by `HTTP API reachable at localhost:8000`.*

*A container can exist while not running. A process can start and crash. A process can run while network configuration makes it unreachable. An HTTP port can be reachable while `/predict` is broken.*

*As for `docker build` succeeding but `/health` failing, that means the container got instantiated without error, but an HTTP endpoint failed to behave properly. The failure likely occured at the boundary of startup, so it would be best to inspect application startup failure at the docker logs.*

image -> packaged filesystem/configuration

container -> instantiated image with runtime state 

process -> python -m uvicorn ...

service -> HTTP capability exposed to clients

The image isn't frozen parameters. A Docker image is best described as an immutable packaged filesystem plus image configuration used to create containers. It contains things like: 
* Linux userspace
* Python
* installed packaged
* our application
* our model artifacts
* default startup command

docker build does not instantiate a container. docker build -> creates image

docker run -> creates and start a container

Debugging sequence: 
-> `/health` unreachable
-> Is container running? 
-> docker ps
-> No -> docker ps -a -> docker logs
-> Yes -> docker port -> docker logs -> HTTP request

Potential failure boundaries: 
* container never started
* container started then crashed
* FastAPI lifespan startup failed
* model/artifact loading failed
* Uvicorn failed
* wrong Uvicorn bind address
* port wasn't published
* wrong host port
* routing/network problem
* endpoint itself failed

### Help Needed 

* What do the two dashes mean when we use the command line? Do they have any significance or story behind them?

*One dash is to signify the short option. Two dashes is to signify the long option.*

* What does `ps` mean when it comes to running Docker commands from the command line? 

*`ps` means process status.*

* What does the `curl` command do from the command line? 

*`curl` is a command-line network client for transferring data using URLs, i.e., a way to manually act like an HTTP client from the terminal.*

### Ideas to Retain

* `-x` usually denotes a short command-line option; `--long-name` denotes a longer, more descriptive option.

* `ps` comes from "process status"; Docker uses `docker ps` as its familiar container-listing command.

* `curl` lets the terminal act as a real network/HTTP client, making it valuable for testing service boundaries. 

* `docker build` creates an image; `docker run` creates and starts a container.

* If a service is ureachable: check container state -> exited state -> logs -> port mapping -> HTTP behavior.