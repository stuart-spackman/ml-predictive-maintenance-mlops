## Phase 2.1 — Task Group 6 Active Recall

### Question 1
What is a software regression, and how does converting our manual inspection checks into automated pytest tests help protect against regressions?

**Best sections to review: 6A — What Changes When a Check Becomes a Test? and 6K — Notice How Powerful This Becomes**

*Software regression is a term used to describe when something in a software system used to work correctly but has now stopped working correctly after a code change. Converting our manual inspection checks into automated pytest tests help protect against regressions by converting previously established correct behavior into a rule that future code changes must continue to satisfy. The goal is to turn a necessary guarantee into an automated test that the repository can continually reinforce.*

### Question 2
What are pytest fixtures, and why is it useful for tests to declare reusable dependencies such as `engine_1_df`, `verified_artifacts`, and `inference_pipeline` instead of rebuilding them independently inside every test?

**Best sections to review: 6F — Create Shared Test Fixtures and 6G — What Is a Fixture?**

*pytest fixtures are reusable test setups made in pytest. Perhaps the DRY principle is in play here. We have two options, with one being to writing a bunch of repeated code inside a significant number of tests. The other option is to simply write a test with a parameter in it that pytest can easily recognize. Upon seeing that parameter, pytest will then find a fixture with that name, run it, and pass its return value to the test. (I still don't feel confident in my understanding of this though.)*

Not only are pytest fixtures reusable test setups, but they also let tests declare their dependencies explicitly. 

There can actually be a dependency chain between fixtures. 

Fixtures help with reuse, consistency, test readability, setup/cleanup, object lifetime, and dependency management.

### Question 3
What is the difference between a unit test and an integration test, and give one example of each from our Phase 2.1 inference test suite?

**Best section to review: 6R — Unit Tests vs Integration Tests in Our Suite**

*A unit-style test only focuses on one component, and that component is validation. An example could be testing for confirmation that our software rejects an input whenever a cycle is missing. These kinds of tests isolate one contract rule and then test if the rule is being followed. An integration test is a test that needs to account for multiple components. An example in our software is ensuring that providing a valid engine history produces a finite answer. Executing a test like this cross several components, with those being raw data, validation, temporal features, locked schema, real frozen model, and prediction.* 

A unit test doesn't have to involve validation specifically. It simply focuses on a small isolated unit of behavior. 

### Question 4
Why do we use temporary files and `monkeypatch` when testing destructive artifact-failure scenarios such as SHA-256 mismatches instead of modifying the real frozen Phase 1 model artifact?

**Best sections to review: 6M — Test Corruption Without Touching the Real Model and 6O — What Does `monkeypatch` Actually Do?**

*The principle at play here is that we have a production loader pointing to important `.json` and `.joblib` files associated with our model. It is not desirable to have destructive tests pointing to these files due to their importance. They need to remain unedited throughout the process of using our inference software. `monkeypatch` can temporarily replace module values for one test. Our desire is to test dangerous situations without editing important real estate in our software ecosystem. By using `monkeypatch`, we can create a temporary fake model/artifact that the test uses and then restore the real artifact once the test is over.*

The real artifact was never changed. When the test ends `monkeypatch` restores the reference/configuration value, not the artifact contents.

Destructive tests should operate on isolated temporary resources, not authoritative project artifacts.

### Question 5
Why should automated tests generally assert externally meaningful behavior and contracts rather than incidental implementation details, and why does a completely passing test suite still not prove that the software contains no bugs?

**Best sections to review: 6V — Don't Test Implementation Details Unless They Matter and 6W — Tests Are Not Proof of Correctness**

*Because if we tested incidental implementation details, then changing a function that doesn't meaningfully change the desired behavior of our application could break the test. We want to account for the fact that there are multiple ways of implementing the exact behavior that we need. As for why a completely passing test suite still doesn't prove that the software contains no bugs, test suites only establish that every behavior we actually tested functioned as expected. There will still almost always be conditions that weren't contained in the test suite.*

### Extra Questions 

* What is a dependency injection? 

*A dependency injection refers to giving an object or function the things it depends on from the outside, rather than making it construct those depedencies itself. Dependency injection gives us control over dependencies.*

*Is this function being given something it needs instead of creating it internally?*

*This pipeline depends on model artifacts. Whoever constructs me must inject them.*

### Ideas to Retain

* A behavior that matters enough to depend on should, whenever practical, become an executable test rather than a rule humans must remember to recheck manually.

* Software regression = previously working behavior breaks after a change.

* Fixtures are reusable test setups, but they also make dependencies explicit and manage their lifecycle. 

* Pytest can inject fixtures into other fixtures and into tests. 

* Unit tests isolate small behaviors; integration tests verify cooperation between components. 

* `monkeypatch` temporarily redirects Python state/references; it does not need to mutate your authoritative artifact.

* Dependency injection = supply dependencies from outside rather than constructing them inside the component that uses them. 

* Injection makes code easier to test because production dependencies can be replaced with controlled fake/test dependencies. 

* Tests should protect behavior, not necessarily freeze implementation details. 

* Passing tests increase confidence; they do not prove the absence of bugs. 