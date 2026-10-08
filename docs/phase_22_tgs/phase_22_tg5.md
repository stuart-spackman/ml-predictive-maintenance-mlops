## Phase 2.2 — Task Group 5 Active Recall

### Question 1
What is the difference between an API-schema failure, an inference-domain input failure, and an internal inference failure, and which layer owns each type of failure?

*An API-schema failure is when the HTTP request was sent with malformed or invalid data; this is caught by Pydantic. An inference-domain input failure is when the input data had the correct structure, but something was found in the data that made it incompatible with the inference pipeline such as an infinite value; this is caught by Phase 2.1. An internal inference failure is when the output of the inference process is found to be malformed or invalid; this is caught by the inference system and it's worth noting that this error is not the client's fault, unlike the two other types of errors.*

**Best sections to review: 5B — The Three Main Failure Layers and 5C — Client Errors vs Server Errors**

An internal inference failure is a failure inside the serving/inference machinery that the client cannot correct merely by changing the request.

### Question 2
Why do we translate `InferenceInputError` into HTTP 422 while translating other known `InferenceError` failures into HTTP 500, and what question can you ask to distinguish a 4xx problem from a 5xx problem?

**Best sections to review: 5C — Client Errors vs Server Errors and 5D — Why Use HTTP 422 for `InferenceInputError`?**

*This has to do with how HTTP status codes are grouped into families. `InferenceInputError` means something went wrong on the client side, i.e., they submitted invalid data, hence we use HTTP 422. If it starts with a 4, then that means something went wrong on the client side. If if starts with a 5, then that means something went wrong internally and it's not the client's fault. The defining questions behind these classifications is, "Who needs to fix something before this process can run correctly?"*

Who needs to fix something before this process can run correctly? 

### Question 3
Why do server-side inference errors return a generic public message while detailed exception information is preserved in server logs, and why can caller-input errors safely contain more actionable detail?

**Best sections to review: 5H — Translate Internal Inference Failures Differently and 5I — Why Don't We Return `str(exc)` for Internal Errors?**

*The princple at play here is that it's best to log diagnostic details internally while exposing the only the details that the client needs. Caller input errors can contain more detail because callers have more agency over errors that are happening on their side as opposed to inside our system. More details are better for client errors so they can figure out how to correct their errors. We don't have expectations that clients will fix internally errors, so we don't need to give them as much information in that case.*

### Question 4
Why do we register global exception handlers instead of wrapping the `/predict` endpoint in a broad `try/except Exception`, and what dangerous misclassification could happen if every exception were converted into HTTP 422?

**Best sections to review: 5L — Do NOT Put a Giant `try/except` Inside `/predict` and 5M — Why `except Exception → 422` Would Be Dangerous**

*The princple at play here is that we don't want our endpoint to become an encyclopedia of every different error type. We already have a dedicated translation layer where the route orchestrates successful operations and exception handlers translate known failures. As for why `except Exception -> 422` would be dangerous, that creates a situation where we could have an internal error and return a 4XX error, incorrectly telling the client that the error is something they are responsible for.*

### Question 5
What is the difference between error ownership and error translation in our architecture? Using the 10-cycle minimum as an example, explain which phase owns the rule and which phase decides how its violation appears to an HTTP client.

**Best sections to review: 5V — Update the Service Contract and 5W — One More Important Concept: Error Translation vs Error Ownership**

*The princple at play here is that the system and rule that caused the error and the system that translates the error can exist in different architectural locations. When it comes to error ownership, the code we wrote in Phase 2.1 asks, "What went wrong semantically?" When it comes to error translation, the code we wrote in Phase 2.2 asks, "What should that error explanation look like when it gets sent back to the client over HTTP?"*

Phase 2.1 was built to ask what went wrong semantically. 

Phase 2.2 was built to ask how that thing that went wrong should appear over HTTP. 

Phase 2.1 owns the meaning. Phase 2.2 owns the transport representation of that meaning. 

### Ideas to Retain 

* Schema failure = HTTP data shape problem. 

* Inference-input failure = structurally valid request that violates Phase 2.1's domain contract. 

* Internal inference failure = serving machinery failed in a way that the caller cannot fix by changing the request. 

* Ask "Who needs to change something?" to distinguish many 4xx and 5xx cases. 

* Detailed server diagnostics belong in logs; public responses should expose only useful, safe information. 

* Routes orchestrate successful behavior; exception handlers translate known failures. 

* Error ownership and error translation are different responsibility. 

* Phase 2.1 owns the 10-cycle run; Phase 2.2 decides that violating it appears as HTTP 422. 