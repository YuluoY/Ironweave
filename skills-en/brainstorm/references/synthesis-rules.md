# Synthesis and Debate Rules

After collecting analyses from all perspectives, the moderator synthesizes according to these rules.

## Consensus Determination

**Strong consensus**: 3/4 or more roles recommend the same approach -> adopt directly, brief rationale sufficient.

**Weak consensus**: 2/4 roles recommend the same approach, others have no strong objections -> adopt the recommended approach, but note minority concerns as risks.

**No consensus**: Each party recommends a different approach -> must enter debate round.

## Debate Round Rules

### Cross-examination

Send A's core arguments to B, requiring B to respond:
- Which of A's points do you agree with?
- Which of A's points do you disagree with? Why?
- If you had to compromise between your approach and A's approach, where would the compromise point be?

### Termination Conditions

- **Maximum 2 debate rounds** — if no consensus after 2 rounds, the moderator makes a ruling based on project constraints
- New information discovered (previously unconsidered constraints) -> re-dispatch analysis round
- All parties acknowledge the other side has merit but priorities differ -> moderator weighs by project stage

### Ruling Priority

When a choice must be made between opposing viewpoints, weigh by the following priorities:

1. **Security & Compliance** — Security issues found by the Challenger have highest priority
2. **User Value** — Domain Expert's business judgment comes second
3. **Feasibility** — Pragmatist's implementation assessment comes third
4. **Long-term Health** — Architect's maintainability considerations come fourth

But this is not an absolute ranking — if the project is in MVP stage, feasibility weight increases; if in refactoring stage, long-term health weight increases. The moderator should flexibly adjust based on project stage.

## Dissent Records

All rejected approaches and their rationale must be recorded in the "Rejected Approaches" section of the design summary. Rejection does not equal wrong — recording rejection rationale helps with re-evaluation when future requirements change.

## Quality Check

Before outputting the synthesis report, the moderator self-checks:

- [ ] Were each role's core viewpoints mentioned?
- [ ] Are disagreement points clearly marked?
- [ ] Does the recommended approach's rationale reference specific roles' analyses?
- [ ] Do known risks have mitigation measures?
- [ ] Are outstanding issues recorded?
