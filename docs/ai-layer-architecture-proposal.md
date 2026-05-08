# AI Layer on Top of RTEC: Architecture Proposal

## 1. Goal
Build an AI-driven application that:
- Translates natural language requirements into formal RTEC rules.
- Answers user questions by executing RTEC and interpreting recognitions.
- Supports safe creation, validation, versioning, and promotion of new rules.

## 1.1 Immediate Goal (Now)
First priority is to solve rule generation correctness.

Scope for the immediate goal:
- Natural language to Rule IR to RTEC rule generation.
- Validation and repair loops with behavioral oracle checks.
- Offline evaluation on benchmark scenarios.

Explicitly out of scope for now:
- FastAPI and external API endpoints.
- Frontend/UI work.
- Full production orchestration.

## 2. High-Level Architecture
### 2.1 Control Plane (AI + Orchestration)
Responsibilities:
- Understand user intent.
- Generate and revise rule drafts.
- Build execution plans for queries.
- Explain outputs in user-facing language.

Core components:
- Intent classifier.
- Rule authoring agent.
- Query answering agent.
- Validation orchestrator.
- Promotion and governance workflow.

### 2.2 Execution Plane (Deterministic RTEC)
Responsibilities:
- Compile event descriptions.
- Run continuous queries and batch reasoning.
- Produce recognition outputs and logs.

Properties:
- Fully deterministic.
- No direct LLM write path to production runtime artifacts.
- Every execution is traceable and reproducible.

### 2.3 Data Plane
Stores:
- Rule versions and metadata.
- Rule drafts and review decisions.
- Prompt and response traces for audit.
- Experiment runs, parameters, recognitions, and scores.

## 3. Recommended Tech Stack
## 3.1 Backend
- Python
- Pydantic
- Workflow orchestration with LangGraph or a lightweight state machine

Note:
- FastAPI is deferred until the rule generation core is reliable.

## 3.2 Async Jobs
- Celery or Dramatiq for compile and reasoning jobs
- Redis as broker/cache
- Optional future migration to Temporal for advanced workflow durability

## 3.3 Storage
- PostgreSQL for metadata, versioning, and audit records
- File system or object storage for large outputs and logs

## 3.4 Frontend
- React-based UI
- Two main workspaces:
  - Rule Studio (create, test, compare, promote)
  - Query Studio (ask, run, inspect evidence)

## 3.5 Observability
- Structured logging with run IDs
- Metrics: compile success rate, rule acceptance rate, answer latency
- Tracing with OpenTelemetry

## 4. Agent Design
## 4.1 Rule Authoring Agent
Input:
- Natural language rule description

Output:
- Structured Rule IR
- Candidate RTEC code

Loop:
- Generate
- Validate
- Repair using compiler and validation feedback
- Stop on pass or bounded retry limit

## 4.2 Query Answering Agent
Input:
- Natural language analytical question

Output:
- Execution plan
- RTEC run request
- Final answer with evidence and provenance

## 4.3 Governance Agent (Optional)
Checks:
- Policy violations
- Naming and style consistency
- Performance risks
- Missing safety constraints

## 5. Prompting Strategy
## 5.1 Two-Stage Generation
Stage A:
- Natural language to Rule IR (strict JSON schema)

Stage B:
- Rule IR to RTEC code templates

Why:
- Better reliability than direct natural language to Prolog generation.

## 5.2 Constrained Decoding
- Enforce schema in Stage A.
- Enforce template outputs in Stage B.
- Reject non-conforming outputs and retry.

## 5.3 Retrieval-Augmented Prompting
Retrieve and inject:
- Existing rules and declarations
- Known entities and thresholds
- Relevant examples from the target domain

Benefit:
- Reduces invented predicates and invalid rule structures.

## 5.4 Critic and Repair Loop
- Run semantic checks.
- Compile and execute smoke tests.
- Use tool feedback to revise drafts.

## 6. Validation and Safety Gates
## 6.1 Static Validation
- Syntax checks
- Predicate existence checks
- Declaration completeness checks
- Grounding consistency checks

## 6.2 Compile Validation
- Compile the candidate event description.
- Fail fast on compiler errors.

Important:
- Compile-pass is required but not a correctness signal.
- A rule may compile and still be behaviorally wrong (wrong entities, wrong interval boundaries, wrong temporal conditions).

## 6.3 Runtime Validation
- Run against a smoke-test dataset.
- Verify non-empty, expected-type outputs.

## 6.4 Regression Validation
- Compare against baseline metrics and known scenarios.
- Block promotion on unacceptable regressions.

## 6.6 Behavioral Oracle (Required)
The validation stack must include an explicit behavioral oracle that checks semantic correctness, not only syntactic validity.

Why:
- Static checks, compilation success, and smoke-test non-empty output are necessary but insufficient.
- Behavioral errors often pass all earlier gates (for example, grounding mismatches and interval boundary shifts).

Oracle design:
- Gold scenarios: Curated datasets with expected recognitions for target fluents.
- Entity-level checks: Validate that recognitions apply to the correct entities and argument bindings.
- Interval-level checks: Compare start and end boundaries with tolerance policies where appropriate.
- Metric checks: Per-rule precision/recall/F1, plus micro/macro aggregates.
- Failure signatures: Tag common error classes (grounding failure, over/under-recognition, boundary drift, missing termination).

Promotion policy:
- A draft cannot be promoted unless it passes oracle thresholds.
- Compile-pass alone never qualifies a rule for promotion.
- Regression checks must be oracle-aware (not only runtime/latency aware).

## 6.5 Human-in-the-Loop Promotion
- Draft state
- Review state
- Approved state
- Active state

Only approved rules can be promoted to active.

## 7. Proposed API Surface (Deferred)
## 7.1 Rule Authoring
- POST /rules/draft-from-text
- POST /rules/validate
- POST /rules/compile
- POST /rules/promote

## 7.2 Querying
- POST /queries/answer
- POST /runs/execute
- GET /runs/{run_id}
- GET /runs/{run_id}/evidence

## 7.3 Governance
- GET /rules/{rule_id}/history
- POST /rules/{rule_id}/rollback

## 8. Integration with Current RTEC Repository
Use the current execution boundary as engine adapter:
- Python CLI wrapper for parameterized execution.
- Existing compile and run scripts for deterministic processing.
- Existing scoring utilities for evaluation.

Recommendation:
- Keep current runtime scripts unchanged initially.
- Add a thin orchestration service above them.

## 9. MVP Plan (Phased)
## Phase 1: Rule Drafting Core (Current Priority)
- Natural language to Rule IR to candidate RTEC rule.
- Static and compile validation.
- Behavioral oracle validation.

## Phase 2: Rule Testing and Promotion
- Smoke tests and regression checks.
- Human approval workflow.

## Phase 3: Closed-Loop Repair Agent
- Agent can iteratively improve drafts using validation feedback.
- Controlled automatic promotion policies for low-risk rule classes.

## Phase 4: Query Assistant
- Natural language question to RTEC execution to explanation.
- Uses only promoted rules.

## Phase 5: Service/API Layer
- Add FastAPI endpoints once rule-generation quality is stable.

## 10. Risks and Mitigations
Risk: Hallucinated predicates or unsupported constructs.
Mitigation: Strict schema, retrieval context, compiler gate.

Risk: Behaviorally incorrect rules that compile and appear plausible.
Mitigation: Behavioral oracle with entity/interval/metric thresholds and mandatory promotion gates.

Risk: Performance degradation from generated rules.
Mitigation: Runtime benchmarks and regression thresholds.

Risk: Unsafe direct production changes.
Mitigation: Approval workflow and immutable versioning.

Risk: Non-reproducible answers.
Mitigation: Persist run configuration, input snapshot references, and rule version IDs.

## 11. Open Design Decisions
- Single-agent versus multi-agent workflow orchestration.
- Strict template generation versus hybrid free-form generation with strong repair.
- Policy on automatic promotion for low-risk rule categories.
- Preferred evidence format for user-facing explanations.

## 12. Success Criteria
- High oracle-pass rate for generated drafts on benchmark scenarios.
- Reduced manual effort in rule authoring.
- High answer trustworthiness with explicit evidence.
- Stable runtime performance under realistic workloads.

Secondary (not primary) criteria:
- Compile-pass rate and static validation pass rate.

## 13. Immediate Next Steps
1. Define Rule IR schema and allowed RTEC templates.
2. Build NL-to-IR prompt and IR-to-rule prompt.
3. Implement static and compile validators.
4. Define behavioral oracle datasets, metrics, and pass thresholds.
5. Implement repair loop driven by validator/oracle feedback.
6. Run benchmark evaluation and establish a quality baseline.
7. Add human review and promotion policy for accepted rules.

Deferred items (after step 7):
1. Query-answer pipeline.
2. FastAPI/API surface.
3. UI and broader production orchestration.
