# Rule Authoring Agent: Implementation Plan

## Overview

Build an AI agent that translates natural language rule descriptions into valid RTEC Prolog rules, with automated validation and repair.

---

## Prerequisites

### Skills to Learn

| Skill | Time | Resources |
|-------|------|-----------|
| Event Calculus semantics | 2-3 days | RTEC papers, 6 example rule files in this repo |
| Prolog syntax basics | 1-2 days | Terms, unification, lists, negation-as-failure |
| Pydantic v2 | 1 day | Official docs: model validation, JSON schema export |
| FastAPI basics | 1 day | Path operations, request/response models |
| LLM prompt engineering | 2-3 days | Few-shot prompting, chain-of-thought, structured outputs |

### Tools

| Tool | Purpose |
|------|---------|
| Python 3.11+ | Main language |
| Pydantic | Rule IR schema definition and validation |
| FastAPI | REST API |
| OpenAI/Anthropic SDK | LLM calls |
| Jinja2 | Prolog code templating |
| SWI-Prolog | Compile and validate generated rules |
| pytest | Testing |

---

## RTEC Rule Hierarchy

Rules form a dependency DAG:

```
Level 0: Input Events (happensAt)
    ↓
Level 1: Simple Fluents (initiatedAt/terminatedAt)
    ↓
Level 2+: Statically Determined Fluents (holdsFor)
    ↓
Level N: Composite patterns referencing lower levels
```

Core rule types:
- `initiatedAt(Fluent=Value, T)` — starts a fluent period
- `terminatedAt(Fluent=Value, T)` — ends a fluent period
- `holdsFor(Fluent=Value, Intervals)` — defines fluent via interval operations

Temporal operators:
- `union_all/2` — merge interval lists
- `intersect_all/2` — find common intervals
- `complement_all/2` — invert intervals
- `relative_complement_all/2` — subtract intervals

---

## Week-by-Week Plan

### Week 1: Foundation

| Day | Task |
|-----|------|
| 1-2 | Study all 6 example rule files, categorize rule patterns |
| 3 | Document RTEC rule grammar: valid constructs and combinations |
| 4 | Design Rule IR schema on paper |
| 5 | Validate IR by manually converting 10 diverse rules to IR and back |

### Week 2: Validation Pipeline

| Day | Task |
|-----|------|
| 1 | Set up Python project structure (src/, tests/, configs/) |
| 2 | Implement Pydantic models for Rule IR |
| 3 | Write Python wrapper to invoke RTEC compiler via subprocess |
| 4 | Build error parser: extract structured errors from compiler output |
| 5 | Test validation pipeline with known-good and known-bad rules |

### Week 3: Generation Pipeline

| Day | Task |
|-----|------|
| 1 | Design prompts: system prompt explaining RTEC, few-shot examples |
| 2 | Implement NL → IR generation with LLM |
| 3 | Implement IR → Prolog renderer using Jinja2 templates |
| 4 | Wire generation to validation: generate → compile → report |
| 5 | Test on 10 simple rule descriptions, measure compile success rate |

### Week 4: Repair Loop

| Day | Task |
|-----|------|
| 1 | Design error-to-feedback mapping |
| 2 | Implement repair loop: generate → validate → augment prompt → retry |
| 3 | Add retry budget (max 3-5) and failure handling |
| 4 | Test repair on first-attempt failures |
| 5 | Tune prompts based on failure patterns |

### Week 5: API and Evaluation

| Day | Task |
|-----|------|
| 1 | Implement FastAPI endpoint: POST /rules/draft-from-text |
| 2 | Add request/response logging for audit |
| 3 | Create evaluation benchmark: 30 rule descriptions with expected outputs |
| 4 | Run benchmark, compute metrics |
| 5 | Document findings, identify improvements |

---

## Key Milestones

| Milestone | Success Criteria |
|-----------|------------------|
| IR Schema Complete | Can represent all rules from 6 example applications |
| Validation Pipeline Working | Correctly accepts valid rules, rejects invalid with parsed errors |
| First Successful Generation | NL → IR → Prolog → compiles without error |
| Repair Loop Working | ≥50% of first-attempt failures recovered on retry |
| API Deployed | Endpoint returns valid rule or structured error |

---

## Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    RULE AUTHORING AGENT                     │
├─────────────────────────────────────────────────────────────┤
│  [User NL Input]                                            │
│       ↓                                                     │
│  [LLM + Prompt] ──→ Rule IR (JSON)                         │
│       ↓                                                     │
│  [Template Renderer] ──→ Candidate Prolog                  │
│       ↓                                                     │
│  [RTEC Compiler] ──→ compiled_rules.prolog OR errors       │
│       ↓                                                     │
│  [Error Parser] ──→ Structured feedback                    │
│       ↓                                                     │
│  [Repair Loop] ──→ Back to LLM (max N retries)             │
│       ↓                                                     │
│  [Output: Valid Rule + Metadata]                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Agent Design Principles

1. **Deterministic validation** — LLM generates, tools verify. Never trust LLM output without checking.

2. **Bounded retries** — Max 3-5 repair attempts, then fail gracefully with explanation.

3. **Explicit state** — Track: current attempt, last error, accumulated context.

4. **Rich feedback** — Don't just say "invalid", explain what's wrong and suggest fixes.

5. **Auditable** — Log every prompt, response, and decision.

6. **Incremental** — Start with simple rules, add complexity later.

---

## Context Strategy (No RAG for MVP)

For MVP, use static prompt injection instead of RAG:

1. **Hardcode domain context per application**
   - List all available predicates extracted from grounding/1 facts
   - ~50 lines max, fits easily in context

2. **Include 3-5 few-shot examples in the prompt**
   - Simple initiation
   - Termination with negation
   - holdsFor with union_all

3. **Pass the target application's full predicate list**

Add RAG later only if:
- Compile success rate below 70% after prompt tuning
- LLM consistently invents non-existent predicates
- Prompt exceeds context limits

---

## Risk Checkpoints

| Risk | Check At | Mitigation |
|------|----------|------------|
| IR can't express complex rules | End of Week 1 | Extend schema before building generators |
| Compiler errors too cryptic | End of Week 2 | Build custom static validators |
| LLM hallucinates predicates | End of Week 3 | Constrain to known predicate list |
| Low compile success rate | End of Week 4 | Add more few-shot examples |

---

## Recommended Learning Order

1. `examples/toy/resources/patterns/rules.prolog` — simplest patterns
2. `examples/maritime/resources/patterns/rules.prolog` — real complexity
3. `src/compiler.prolog` (lines 1-100) — what compilation does
4. Pydantic docs on model validation
5. OpenAI cookbook or Anthropic docs on prompting
