---
name: requirement-qa
description: >-
  Guide users to progressively clarify requirements or technical decisions through multi-round QA dialog. Uses a "diverge then converge" pattern: first ask open questions to expand requirement boundaries, then ask focused follow-ups to converge on actionable conclusions. Outputs structured requirement summaries or technical decision summaries.
  Use this skill when: the user's requirement description is vague or incomplete (e.g. "I want to build an XX system"), the user is unsure about technical approach selection, the user requests requirement analysis, requirement research, requirement interviews, requirement review, requirement communication, technical proposal discussion, architecture discussion, or says "help me think about what's missing", "help me sort out requirements", "let's discuss this project". When input is insufficient to produce a complete document, enter this skill's QA flow first rather than delivering half-baked guesswork.
---

# Requirement QA Dialog

This Skill helps users move from fuzzy ideas to clear, complete, actionable requirement descriptions or technical decisions through structured multi-round dialog. The core problem it solves: users have requirements in their heads, but what they express is often just the tip of the iceberg — this skill's goal is to surface what's beneath.

## Core Methodology: Diverge then Converge

Each topic goes through two phases:

1. **Diverge Phase**: Open-ended questions to explore possibility boundaries
   - "What other user roles will use this feature?"
   - "What happens if we don't impose this restriction?"
   - "Are there similar products we can reference?"

2. **Converge Phase**: Directed follow-ups to lock in specific decisions
   - "Among these three options, which do you prefer? Why?"
   - "Is this feature P0 or can it be deferred?"
   - "I understand you mean X — is that correct?"

## Interaction Style: Prefer Structured Options

Prefer using the structured questioning capabilities provided by the current Agent's host editor, rather than system-level dialogs. Fall back to plain chat messages only if the host completely lacks structured questioning support. The clarification logic is the same across hosts — only the UI presentation differs; no logic branching is allowed.

Core rules:
- Each question has **2-5 options**, **must mark exactly one recommended option** (with reasoning), **last option is always free-form input**
- Recommendation basis: Engineering facts > contextual inference > industry conventions > safety-side preference

For detailed option design rules, recommended option marking rules, and host adaptation methods, see [references/option-rules.md](references/option-rules.md).

At the end of each dialog round, do a **brief summary confirmation** to ensure mutual understanding before moving to the next topic.

## Questioning Rhythm Control

### Generate Questions On Demand

How many questions per round depends on the actual unknowns to clarify:

- Only one key unknown? Ask just one question
- Multiple **independent** unknowns can be asked together in one round to reduce back-and-forth
- Multiple **dependent** unknowns must be split across rounds — later questions depend on earlier answers

**Bad example**: Forcing dependent questions into one round — "Are you building Web or desktop? Which browsers to support?" (browser question depends on the "Web" premise)

**Correct approach**: First ask "What is the final product form?", then ask specific constraints based on the answer.

### High-Value Questions First

Prioritize questions that can change the execution path:

- **Ask first**: What to build, for whom, to what extent, scope boundaries
- **Ask later**: What technology, what style, what UI preferences

### Start from Engineering Facts

If the current repo is already a Vue 3 project, don't ask "Do you want React or Vue?" — read facts first, then ask about genuinely unknown things.

## State Tracking

After each Q&A round, maintain two internal states:

- **Current understanding**: What has been stably established based on this round's Q&A
- **Draft output**: What deliverable draft could be produced if we had to output right now

These states ensure subsequent rounds focus on "what's still missing" rather than re-understanding from scratch each round. They can be shown to the user during summaries so they can see requirements taking shape.

## Dialog Flow

### Round 1: Project Profile (Required)

Goal: Establish the full project picture within 5-8 questions.

**Requirement-oriented core questions:**
- Who is this product/feature for? (target user roles)
- What problem does it solve? (core pain points)
- How do users currently solve this problem? (status quo and alternatives)
- What does success look like? (quantifiable business goals)
- Project timeline constraints? (MVP deadline, milestones)

**Technology-oriented core questions:**
- Current team tech stack? (existing projects, team expertise)
- Any predetermined technical constraints? (e.g., must deploy on-premise, must support IE)
- Expected user scale? (impacts architecture and performance design)
- Deployment environment? (cloud / private / hybrid)
- Budget and staffing limitations?

> **Questioning principle**: Ask at most 3 questions per round. Too many causes fatigue, degrading information quality. Adjust rhythm based on answer detail level — detailed answers mean fewer questions needed; brief answers mean more follow-up.

### Round 2: Feature Boundary Exploration (Diverge-heavy)

Goal: Enumerate feature points, user scenarios, boundary conditions.

**Questioning strategies:**
- **Role dimension**: Beyond primary users, are there admins, auditors, third-party systems?
- **Scenario dimension**: Beyond normal flow, how to handle exceptions? Batch operations? Concurrent scenarios?
- **Data dimension**: What data inputs/outputs? Data volume? Data lifecycle?
- **Integration dimension**: Which external systems to connect with? Auth methods? Data formats?
- **Non-functional dimension**: Performance requirements? Security/compliance requirements? Availability requirements?

**Anti-patterns to avoid:**
- Don't start discussing implementation details in this round
- Don't steer users away from features just because they're "hard to implement" — record first, discuss priority later
- Don't dump all questions at once — dynamically select next questions based on previous answers

### Round 3: Priority and Scope Convergence

Goal: From the diverged feature list, determine MVP scope.

**Convergence strategies:**
- Classify by **MoSCoW** (Must / Should / Could / Won't)
- For each Must feature, follow up with acceptance criteria: "What level of completion counts as OK?"
- For Won't features, confirm: "Definitely not this phase? Possibly later?"
- Mark dependencies: "Feature A depends on Feature B, so B must also be Must"

### Round 4: Technical Constraint Convergence (if tech decisions involved)

Goal: Determine key technical decision points.

**Convergence strategies:**
- Aggregate collected constraints into comparison tables
- For each decision point, present 2-3 options + pros/cons analysis
- Let user choose, record the reasoning
- Mark "to-be-validated" technical risks

### Round 5: Completeness Check and Output

Goal: Confirm nothing is missed, output structured summary.

**Checklist:**
- [ ] All user roles identified
- [ ] Core business flows clarified
- [ ] Exception and boundary scenarios discussed
- [ ] Priorities ranked (MoSCoW)
- [ ] Acceptance criteria defined (at least for Must items)
- [ ] Technical constraints documented (if any)
- [ ] "Not doing this phase" boundaries explicit
- [ ] Integration points with external systems identified

## Dialog Techniques

### Handling Different User Types

- **Verbose users**: Interrupt with timely summaries — "Let me confirm I understood correctly..."; help focus on pending questions
- **Terse users**: Provide specific options instead of open-ended questions — "Do you need A or B?"; use yes/no questions for confirmation
- **Indecisive users**: Give recommended approaches + reasoning — "Based on your scenario, I suggest doing X first because..."
- **Over-divergent users**: Gently redirect — "Great idea, I'll note it down. Let's finish confirming the core flow first?"

### Summary Template

After completing discussion of each topic, do a concise structured confirmation:

```
[Summary Confirmation]
Topic: User Login
Confirmed:
- Support phone number+SMS code and email+password methods
- No third-party login for now (WeChat, GitHub)
- Lock account for 30 minutes after 5 failed attempts
Pending:
- SMS code validity period (suggest 5 minutes, TBC)
- Whether "remember me" feature is needed
```

## Output Format

After dialog completion, output a **structured requirement summary** or **technical decision summary**.

### Requirement Summary Template

```markdown
# Requirement Summary: [Project/Feature Name]

## Project Positioning
[One or two sentence description]

## Target Users
| Role | Core Need |
|------|----------|
| ... | ... |

## Feature Scope (MoSCoW)
### Must (MVP Essentials)
- [ ] Feature + brief acceptance criteria
### Should (Important but Deferrable)
- [ ] ...
### Could (Nice-to-have)
- [ ] ...
### Won't (Explicitly Out of Scope)
- [ ] ...

## Key Business Rules
- Rule 1
- Rule 2

## Non-Functional Requirements
- Performance: ...
- Security: ...

## Pending Items
- [ ] ...

## Technical Constraints (if any)
- ...
```

### Technical Decision Summary Template

```markdown
# Technical Decision Summary: [Project Name]

## Project Constraints
- Team size: ...
- Timeline: ...
- Deployment environment: ...

## Confirmed Decisions
| Decision Point | Choice | Reasoning |
|--------|------|------|
| ... | ... | ... |

## Risks to Validate
- [ ] ...

## Version Constraints
- Node.js: ...
- pnpm: ...
```

## Execution Method

1. **Check entry conditions**: Enter QA flow when user input is insufficient to produce a complete document
2. **Progress by rounds**: No need to strictly follow five rounds — adjust flexibly based on actual needs; end early when enough info is gathered
3. **Summarize each round**: Ensure mutual understanding before continuing
4. **Exit when ready**: When most checklist items are checked or user says "that's about it", output structured summary
5. **Output summary**: After summary output, prompt user that they can use it to generate formal documents

## Completion Signals

By default, QA ends and summary is output only when:
- User explicitly says "start producing", "you can write the doc now", "go ahead with this", etc.
- All Must items in the checklist are confirmed

If user says "keep asking" or "don't start yet", treat as continuing clarification. Even if user demands immediate end but info is incomplete, **explicitly list assumptions** in the output summary.

For the complete signal list and minimum exit criteria, see [references/completion-signals.md](references/completion-signals.md).

## Document Persistence

Each Q&A round should be persisted to a Markdown file, not relying on model memory. Use `scripts/qa_session.py` to manage session documents:

```bash
# Start new session
python3 skills/requirement-qa/scripts/qa_session.py start \
  --topic "User Login Feature" \
  --initial-request "I need a login feature"

# Record each round
python3 skills/requirement-qa/scripts/qa_session.py append-turn \
  --doc-path "<doc_path>" \
  --question "Which login methods to support?" \
  --answer "Phone+SMS code, email+password" \
  --confirmed "Support phone+SMS code" \
  --confirmed "Support email+password" \
  --open-item "Whether third-party login is needed" \
  --current-understanding "Core login methods confirmed"

# Finalize session
python3 skills/requirement-qa/scripts/qa_session.py finalize \
  --doc-path "<doc_path>" \
  --final-summary "Login feature requirements converged" \
  --deliverable "Requirement summary document"
```

Documents are stored in the `docs/qa/` directory, one file per session.

## Resources

| Path | Description |
|------|------|
| `references/option-rules.md` | Option design rules, recommended option marking rules, host adaptation |
| `references/completion-signals.md` | Completion signal list, continue-intent protection, minimum exit criteria |
| `scripts/qa_session.py` | QA session document creation, appending, and finalization |
