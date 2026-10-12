## Phase 2.3 — Task Group 1 Active Recall

### Question 1
How does fixture scope relate to resource lifetime, and why is a session-scoped FastAPI `TestClient` reasonable while a session-scoped mutable prediction payload is risky?

**Best sections to review: 1D — Fixture Scope Means Lifetime, 1E — Mutable vs Expensive Is the Key Distinction, and 1F — An Improvement to What We Did in Phase 2.2**

*The thing we need to note here is that pytest fixtures have different lifetimes depending on the resources they are testing. From shortest to longest scope we have functions, modules, and sessions. As for why a session-scope mutable prediction would be risky, that would create a situation where another test could accidentally receive the modified version of the mutable prediction payload. Cheap and mutable payloads shoudl generally be function-scoped.*

The `TestClient` causes application startup, which loads and verifies the real inference pipeline. That's comparatively expensive, and during these tests we're treating that shared application resource as effectively read-only.

`TestClient`/loaded inference pipeline: 
* expensive to construct
* intended to be reused without mutation
* session scope makes sense

Prediction payload: 
* cheap
* mutable dict/list structure
* function scope is safer

### Question 2
What is the difference between a pytest fixture, a factory fixture, and an ordinary helper function? Why is `prediction_payload_factory` useful for our API tests?

**Best sections to review: 1I — Introduce a Fixture Factory and 1K — Fixture vs Factory vs Helper**

*A fixture provides setup/dependency/lifecycle, with an example being that we can setup a fixture that gives a test an initialized API client (and the fixture then provides a single payload). A factory creates test objects with controlled variation, with an example being a test that is given a way to construct variations of an API request (each of which will yield their own unique payloads). As for helper functions, these perform reusable deterministic logic for test construction.*

*Does pytest need to manage its lifetime/dependencies? Then use a fixture.*

*Does the test need to create configurable test objects? Then use a factory.*

*Is it simply reusable deterministic code? Then use an ordinary helper.*

*As for why `prediction_payload_factory` is useful for our API tests, this function returns a factory that creates fresh API payloads. Each call receives an independent deep copy of a payload so tests can safely mutate their own copy.*

lifetime/dependency management -> fixture

configurable object creation -> factory 

reusable deterministic transformation -> helper

A fixture isn't specifically about payloads, nor does it necessarily provide only one object. 

The defining characteristic is that pytest manages how that dependency is created, supplied, scoped, and possibly torn down.

### Question 3
How does a `yield` fixture protect test isolation when we temporarily override FastAPI's inference dependency, and why is restoring the complete previous override state stronger than simply deleting our override?

**Best sections to review: 1N — Move Dependency-Override Cleanup Into a Fixture, 1O — Why Restore the Whole Overrides Dictionary?, and 1R — `yield` Fixtures and Resource Lifetimes**

*When using pytest we are implementing a setup -> yield -> cleanup paradigm. Regardless of if the test fails, there is still a guarantee that the teardown will happen. This keeps the test as an isolated event that won't affect other tests. As for why restonring the complete previous override state is stronger than simply deleting our override, if we approximate a presumed default state instead of restoring the exact state that was in place before, then that can interfere with the ability of other tests to run and give valid answers.*

setup -> test -> yield -> teardown



### Question 4
What is test contamination, why should test order ideally not matter, and how do `tmp_path`, `monkeypatch`, fresh function-scoped data, and teardown fixtures all address the same underlying problem?

**Best sections to review: 1S — Built-In Isolation Fixtures: `tmp_path`, 1T — Built-In Isolation Fixtures: `monkeypatch`, 1U — Test Order Must Not Matter, and 1V — Do a Small Order-Independence Check**

*Test contamination is when what should have been a temporary state set up for another test is not torn down properly, and then it affects another test in a way that wasn't intended. Test order should ideally not matter because if we're doing a good job of preventing test contamination, then all tests will be starting with the program/software in the same state and then returning it to that same state once they're done. As for how all these testing tools address the same underlying problem, they all implement the property that every test should be understanbndable as though it could run independently.*

Give a test a controlled temporary state and prevent that state from leaking into other tests. 

### Additional Help Needed

* Why did we call the file `conftest.py`? 

*It's a special filename that gets automatically recognized by pytest. It means pytest configuration and shared test fixtures for this part of the test tree. In an ordinary Python module you usually import what you need explicitly. In conftest.py pytest discovers its fixtures automatically.*

* What is a payload in this context? I don't know if it's something that gets returned by a test function or if it's something we give a test function or if it's something else. 

*A payload is application data carried by an HTTP request or response. In `POST /predict`, our request payload is effectively a Python dictionary before it gets serialized to JSON. So the payload is the data being carried. There's also a request payload and a response payload. Payload = the meaningful application data carried inside a message.*

* What does `yield` do in this context? 

*In a pytest fixture you can think of `yield` as "Give this resource to the test now; when the test is finished, resume this fixture and perform cleanup." When you see `yield resource` pytest effectively says: "I'll run the test using this value, then come back and continue this fixture after the `yield`."*

### Ideas to Retain 

* `conftest.py` is a pytest-recognized module for fixtures/configuration that pytest discovers automatically.

* A payload is the meaningful data carried by a request or response; in `POST /predict`, the engine history JSON is the request payload. 

* A fixture is pytest-managed dependency/lifecycle machinery; a factory creates configurable test objects; a helper performs reusable logic. 

* In a fixture, `yield` gives a resource to the test and lets the fixture resume afterward for teardown. 

* Session scope is useful for expensive shared resources; mutable scenario-specific data shoudl usually be isolated per test. 