## Phase 2.3 — Task Group 0 Active Recall

### Question 1
What is the difference between classifying a test by its **scope** and classifying it by its **purpose**? Give an example from our project of a test that can legitimately belong to more than one category.

**Best sections to review: 0C — Tests Need to Be Classified by Scope, 0E — Another Axis: What Is the Test Trying to Protect?, and 0F — Two Axes, Not One Giant Taxonomy**

*One thing worth noting here is that testing scope often exists along a spectrum; there are narrow tests at one end of the spectrum and broad tests at the other end of the spectrum. Classifying a test by its scope is the process of determining how narrow or broad it is. As for classifying a test by its purpose, this involves categorizing by what it is trying to protect. These categories include:*

* Contract test -> protects an agreed behavior/interface 

* Regression test -> protects against a defect running 

* Invariant test -> protects something that should always remain true

* Failure-path test -> verifies how the system behaves when something goes wrong

*An example of a hybrid test is `seven cycle POST /predict`. This falls into the categories of API regression test, contract test, and regression test.*

Scope -> how much of the system does the test exercise? 

Purpose -> what guarantee is the test trying to protect? 

Classifications are not mutually exclusive. In the case of `POST /predict`: 

* Scope -> API/service integration test 

* Purpose -> contract test, regression test, failure path test

### Question 2
What is a test oracle, and why is a test weak if it does not have an independent, defensible reason for expecting a particular result? Use the Phase 2.2 API-vs-Phase-2.1 prediction test as an example.

**Best sections to review: 0G — The Most Important Concept: A Test Needs an Oracle and 0H — Bad Oracle Example**

*A test oracle is a source that tells a test what the correct outcome should be. As for why a test is weak if it doesn't have a reason for expecting a particular result that is both independent and defensible, otherwise we wind up comparing the code's result against itself. This creates a situation where the test will pass regardless of correctness, and there is nothing giving reason to expect a particular type of behavior. As for the example comparing Phase 2.2 and Phase 2.1, there we used an authoritative Phase 2.1 result as the oracle for the Phase 2.2 translation.*

We do not want to compare the code's result against itself. A meaningful test needs some defensible expectation. 

An oracle doesn't always have to be another implementation. It can also be: a written contract, a mathematical property, an invariant.

### Question 3
Why is “What important claim currently lacks automated evidence?” a better question than “How can we increase the number of tests?”, and what factors make a missing test especially high-value?

**Best sections to review: 0L — Tests Are Evidence About Claims, 0M — Identify Gaps Without Writing Tests Yet, and 0N — How Do We Decide Whether a Missing Test Is Worth Adding?**

*The most important aspect of testing is verifying important behavioral capabilities. The number of tests present in a program carries no implications about behaviors. As for what factors make a missing test especially high-value, there are four factors. We can gauge if a failure would be: likely enough, important enough, difficult to notice manually, and cheap enough to verify automatically.*

The number of tests in a program carries no implications about behaviors. 

How likely is failure? How important would failure be? How hard would failure be to notice manually? How cheaply can we automate the check? 

### Question 4
Why should Phase 2.3 avoid unnecessary tests of implementation details, and why does that NOT mean that internal properties such as locked feature ordering or artifact integrity should never be tested?

**Best sections to review: 0O — Avoid Testing Implementation Details and 0P — But Some Internal Properties ARE Contracts**

*Because tests of implementation details aren't good at accounting for changes to the structure of a program, i.e., making improvements by refactoring. This creates a situation where the program still has 100% correct behavior after a change but the test will switch to flagging it as failing even though the contract still works. As for why that doesn't mean that internal properties such as locked feature ordering or artifact integrity should never be tested, artifacts have identities that should exist as real system guarantess and there should be tests to validate that.*

### Ideas to Retain

* Test scope answers "How much of the system?"; test purpose answers "What guarantee?"

* One test can be an integration test, contract test, regression test, and failure-path test simultaneously.

* A test oracle is the defensible basis for knowing what should happen. 

* Test count is not evidence of test quality. 

* High-value tests protect likely, important, subtle, automatable failures. 

* Avoid coupling tests to incidental implementation structure. 

* Internal details become legitimate test targets when violating them would break a meaningful system guarantee—such as artifact identity or exact model feature ordering.