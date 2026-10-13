# Phase 2.3 — Automated Testing Strategy

## Objective

Phase 2.3 consolidates and strengthens the automated verification system
built incrementally during Phases 2.1 and 2.2.

The objective is not to maximize test count.

The objective is to establish meaningful, maintainable evidence that the
critical software and serving contracts of the predictive-maintenance
system continue to hold as the project changes.

## Existing Test Layers

### Phase 2.1 — Inference

Existing coverage includes areas such as:

- raw engine-history validation,
- causal temporal feature construction,
- prefix invariance,
- artifact integrity/loading,
- model-contract compatibility,
- end-to-end inference behavior,
- deterministic repeated inference,
- expected inference failure behavior.

### Phase 2.2 — API

Existing coverage includes areas such as:

- health endpoint behavior,
- runtime metadata,
- OpenAPI route exposure,
- successful HTTP prediction,
- parity between API and Phase 2.1 prediction,
- Pydantic schema rejection,
- inference-domain error translation,
- sanitized internal inference failures.

## Verification Responsibility Matrix

| Area | Primary test scope | Important guarantees | Current status |
|---|---|---|---|
| Raw history validation | Unit/component | Illegal histories rejected; normalization safe | Existing |
| Temporal feature engineering | Unit/component | Causality; expected feature structure | Existing |
| Artifact loading | Component/integration | Integrity and compatibility checks | Existing |
| Inference pipeline | Integration | Raw history reaches frozen model correctly | Existing |
| API schemas | API/component | Public structure enforced | Existing |
| API endpoints | Integration/service | HTTP contract behaves correctly | Existing |
| HTTP error translation | Integration/service | Caller vs server failures classified correctly | Existing |
| Cross-layer regressions | Integration | Important past defects stay fixed | Partial / audit |
| Test isolation | Test infrastructure | Tests do not contaminate one another | Audit needed |
| Coverage quality | Whole suite | Critical behaviors are represented | Audit needed |
| CI execution contract | Whole suite | One reliable automated verification command | Not yet finalized |

## Out of Scope for Phase 2.3

The automated software test suite does not attempt to prove:

- that the model has strong predictive performance,
- that the production population has not drifted,
- that model predictions are physically correct for every engine,
- that Docker/container behavior is correct,
- that CI infrastructure is configured correctly,
- that a cloud deployment is healthy,
- that production-scale concurrency or load requirements are met.

Predictive-performance evidence belongs primarily to Phase 1.

Containerization and CI execution infrastructure belong to Phase 2.4.

Future monitoring/drift capabilities belong outside the current Phase 2.3
software-testing scope.

## Initial Coverage-Gap Audit

| Capability | Assessment | Notes |
|---|---|---|
| Raw-history validation | TBD | |
| Temporal feature correctness | TBD | |
| Prefix invariance | TBD | |
| Artifact integrity | TBD | |
| Model-contract compatibility | TBD | |
| End-to-end inference | TBD | |
| API health/metadata | TBD | |
| API prediction | TBD | |
| Schema-error behavior | TBD | |
| Domain-error behavior | TBD | |
| Internal-error sanitization | TBD | |
| Test isolation | TBD | |
| Cross-layer regression protection | TBD | |

## Testing Principles

1. Tests should protect meaningful behavioral contracts, invariants, and
   regressions rather than maximize test count.

2. Narrow tests and broad integration tests serve different purposes and
   should coexist.

3. Test scope and test purpose are separate classification axes.

4. Every meaningful test should have a defensible oracle.

5. Existing Phase 2.1 and Phase 2.2 tests should be reused rather than
   duplicated.

6. Important real defects should become permanent regression tests when
   practical.

7. Tests should avoid unnecessary dependence on implementation details.

8. Critical internal invariants may still warrant explicit testing when
   violating them would silently corrupt behavior.

9. Passing software tests establish evidence about encoded software
   contracts, not predictive quality, absence of drift, or universal
   correctness.

10. New tests should be justified by an identifiable risk or missing
    guarantee.

## Test Infrastructure and Isolation Strategy

### Fixture scope

Fixtures should use the narrowest practical lifetime.

Broad fixture scope is appropriate when setup is expensive and the shared
resource behaves effectively read-only during tests.

Mutable scenario-specific data should normally be function-scoped or
copied before use.

### API lifecycle

FastAPI `TestClient` is session-scoped so the application lifespan and
verified inference pipeline are initialized once for the API test session.

### Prediction payloads

The canonical FD001 API payload may be constructed from a session-scoped
template, but each test receives an independent deep copy.

Tests may therefore mutate their own request payload without contaminating
other tests.

### Dependency overrides

Tests that substitute the FastAPI inference dependency use a fixture with
guaranteed teardown.

The prior dependency-override state is restored after each such test.

### Temporary external state

Temporary filesystem behavior should use pytest-managed facilities such as
`tmp_path`.

Temporary Python/configuration changes should use `monkeypatch` or another
fixture with deterministic cleanup.

### Isolation principle

Tests must not rely on execution order or leave shared state altered for
later tests.

## Core Inference Hardening

Phase 2.3 reviewed the existing Phase 2.1 inference suite against the
highest-risk behavioral contracts.

Hardening prioritizes:

- contract boundary values,
- caller-owned input immutability,
- normalization invariance,
- temporal causality,
- engine isolation,
- artifact integrity,
- model/feature compatibility,
- deterministic end-to-end inference.

Existing Phase 2.1 tests are retained when they already provide strong
evidence. New tests are added only for meaningful gaps.

### Testing techniques

Boundary-value testing checks behavior immediately around contract
thresholds.

Metamorphic testing verifies known relationships between outputs when
inputs undergo meaning-preserving transformations.

Examples include:

- shuffled but otherwise identical engine histories producing the same
  prediction,
- past-cycle temporal features remaining unchanged when future cycles are
  appended,
- one engine's features remaining unchanged when other engines are
  processed alongside it.

Tests prefer behavioral guarantees over incidental implementation details.

## API, Failure-Injection, and Regression Hardening

The Phase 2.2 API suite was reviewed against public-service boundaries,
failure behavior, and important historical regressions.

Hardening prioritizes:

- controlled public response shapes,
- preservation of inference semantics through the HTTP adapter,
- rejection of undeclared request fields,
- proof that schema-invalid requests do not execute prediction logic,
- domain-input error translation,
- sanitized server-side failure responses,
- preservation of detailed diagnostics in server logs,
- regression protection for previously observed integration failures.

### Failure injection

Known internal failure behavior is tested using controlled test doubles
injected through FastAPI dependency overrides.

Real production model artifacts are not damaged to manufacture failures.

### Regression strategy

Real defects become permanent regression tests when they reveal an
important system or public-contract guarantee.

Tests are not created merely to memorialize every implementation mistake.

### Framework boundary

Tests focus on application-specific FastAPI configuration and integration
rather than attempting to re-test basic FastAPI, Starlette, Pydantic, or
scikit-learn behavior.

## Coverage-Gap Review

| Area | Behavioral status | Coverage observation | Action |
|---|---|---|---|
| Raw validation | Strong | Major success/failure branches exercised | Retain |
| Temporal features | Strong | Core transformations and invariants exercised | Retain |
| Artifact verification | Strong | Real load + corruption paths exercised | Retain |
| Pipeline | Strong | Success + compatibility/input failures exercised | Retain |
| API prediction | Strong | Public success path exercised | Retain |
| HTTP errors | Strong | 422 and sanitized 500 exercised | Retain |
| <actual uncovered area> | Partial | Important branch uncovered | Add targeted test |

## Coverage and Quality Gates

### Coverage role

Coverage is used as a diagnostic map for identifying untested code and
decision branches.

Coverage percentage is not treated as a direct measure of test quality.

Uncovered high-risk behavior is prioritized over maximizing the global
percentage.

### Coverage mode

The project measures:

- line execution,
- branch execution,
- missing source lines.

Coverage focuses on the `predictive_maintenance` application package.

### Quality review

Important tests are reviewed for:

- meaningful behavioral assertions,
- defensible test oracles,
- clear scenario/expected-behavior naming,
- correct architectural error boundaries,
- isolation from unrelated test state,
- avoidance of unnecessary implementation-detail coupling.

### Coverage threshold

Initial coverage is measured after inference and API hardening.

The enforcement threshold is selected from the observed stable baseline
rather than from an arbitrary target percentage.

The threshold acts primarily as a regression guardrail against growth in
untested production code.

### CI-ready verification contract

The authoritative full-suite quality gate is:

`python -m pytest --cov=predictive_maintenance --cov-report=term-missing --cov-fail-under=<THRESHOLD> -q`

Branch coverage is enabled through project coverage configuration.

Phase 2.4 will automate this command in CI.

## Phase 2.3 Coverage Baseline

- Tests collected: <actual>
- Tests passing: <actual>
- Line/statement coverage: <actual>
- Branch-aware coverage: <actual>
- Coverage gate: <actual threshold>
- Slowest-test review completed: yes/no

### Important uncovered areas reviewed

- <area>: <decision>
- <area>: <decision>