---
name: requirement-qa
description: >-
  Guides users from vague ideas to complete requirements through a "Set Direction → Incremental Output → User Review → Confirm/Correct" loop. Unlike pure Q&A mode, this skill produces reviewable document fragments to docs/01-requirement/ each round — users only need to judge "is this right?" rather than articulate requirements from scratch.
  Use this skill when: user's requirements are vague or incomplete (e.g., "I want to build a XX system"), user is unsure about technical choices, user requests requirement analysis/review/interview/brainstorming/architecture discussion, or says "help me think about what's missing", "help me sort out the requirements", "let's talk about this project". When input is insufficient for a complete document, enter this skill's QA flow rather than delivering guesswork.
---

# Requirement QA

This skill guides users from vague ideas to clear, complete, actionable requirements through **incremental output + user review** loops.

**Core principle**: Users don't need to "articulate requirements clearly" — they just need to judge "is what the Agent produced correct?" This shifts the information quality burden from user to Agent, changing the user's role from "answerer" to "reviewer."

## Output Target

Each QA loop directly creates or updates modular files under `docs/01-requirement/`:

```
docs/01-requirement/
├── project-profile.md      ← Project profile (positioning, users, goals)
├── feature-scope.md        ← Feature scope (feature list + MoSCoW priorities)
├── business-rules.md       ← Business rules (core rules + edge cases)
├── non-functional.md       ← Non-functional requirements (performance, security, compliance)
└── tech-constraints.md     ← Technical constraints (tech stack, deployment, integrations)
```

These files serve as input for subsequent skills like `spec-writing`. requirement-qa addresses **What** (what to build), spec-writing addresses **How** (how to achieve it).

## Core Loop: Output → Review → Correct

Every module follows the same three-step loop:

### Step 1: User Sets Direction

User provides high-level direction or existing information — can be very brief:
- "I want to build an online education platform"
- "An internal project management tool for the team"
- Or even just "help me think about what this system is missing"

The Agent infers as many details as possible based on available information (user input + repository engineering facts).

### Step 2: Agent Outputs + Recommends Options

The Agent does two things:

1. **Directly produces document fragments**: Writes inferrable content as structured documents, creates or updates the corresponding file in `docs/01-requirement/`
2. **Provides recommended options for uncertain points**: Following option rules (2-5 options, one marked as recommended, last one is free input)

Key: **Output first, then ask**. Don't come empty-handed asking "what do you want to build?" — first write a draft based on known information, then ask about uncertain points in the draft.

### Step 3: User Review + Confirmation

What the user sees is a **reviewable document**, not a pile of questions. Users can:
- Confirm: "Yes, that's right" → Agent moves to next module
- Mark corrections: "The role description is wrong, it should be XX" → Agent updates the file
- Add information: "There's a scenario you missed" → Agent adds to the file

After confirming user review results, the Agent **updates the file in place** (no delete-and-recreate), then moves to the next module or deeper follow-ups.

## Interaction: Prefer Structured Options

Prefer the structured questioning capability provided by the current Agent host editor, not system-level popups. Only fall back to plain chat messages if the host completely lacks structured questioning support. There is only one clarification logic — different hosts only differ in UI presentation, no logic forking allowed.

Core rules:
- Each question has **2-5 options**, **must mark exactly one as recommended** (with rationale), **last option is always free input**
- Recommendation basis: Engineering facts > Context inference > Industry conventions > Safety-side preference

For detailed option design rules, recommendation marking rules, and host adaptation, see [references/option-rules.md](references/option-rules.md).

## Question Pacing

### Output First, Then Ask

The core output of each round is a **document fragment** — questions only clarify uncertain points in the document. Instead of "ask 5 questions and wait for answers", the better approach is:
- Write a draft (80% inferred + 20% to be confirmed)
- Mark uncertain points in the draft with `<!-- to be confirmed -->` or **bold annotations**
- Ask about the 1-3 most critical uncertain points

### Generate Questions as Needed

How many questions per round depends on actual unknowns that need clarification:

- Only one key unknown → ask only one question
- Multiple **independent** unknowns can be asked together in one round to reduce round-trips
- Multiple **dependent** unknowns must be split across rounds — later questions depend on earlier answers

**Anti-pattern**: Forcing dependent questions into one round — "Are you building for web or desktop? Which browsers to support?" (browsers depend on "web" as a prerequisite)

**Correct approach**: First ask "what's the final product form", then ask specific constraints based on the answer.

### High-Value Questions First

Prioritize questions that change the execution path:

- **Ask first**: What to build, for whom, to what extent, scope boundaries
- **Ask later**: Which technology, what style, what UI preferences

### Start from Engineering Facts

If the current repository is already a Vue 3 project, don't ask "Do you want React or Vue?" — read facts first, write them directly into tech-constraints.md, then ask about genuinely unknown things.

## Module Progression

### Module 1: Project Profile (project-profile.md)

**Output content**: Project positioning, target user roles and core needs, core pain points, success criteria, time constraints.

**Agent's approach**:
1. Read user input + scan repository (README, package.json, existing docs, etc.)
2. Based on known information, **directly write** a `project-profile.md` draft
3. Ask about uncertain points (e.g., target user roles, success criteria)
4. User reviews → update file → confirm and move to next module

**Output template**:

```markdown
# Project Profile: {Project Name}

## Positioning
{One or two sentences describing what problem this product solves}

## Target Users
| Role | Core Need | Usage Frequency |
|------|-----------|-----------------|
| ... | ... | ... |

## Core Pain Points
- How users currently solve this problem
- Main dissatisfaction with existing solutions

## Success Criteria
- {Quantifiable business objectives}

## Time Constraints
- MVP deadline:
- Key milestones:
```

### Module 2: Feature Scope (feature-scope.md)

**Output content**: Feature list (categorized by MoSCoW), each with brief acceptance criteria.

**Agent's approach**:
1. Based on project profile, **proactively infer** likely feature list
2. Write `feature-scope.md` draft, categorized by MoSCoW
3. Ask: "Is this feature list complete? Are priorities correct?"
4. User reviews → add/remove/modify → update file

**Output template**:

```markdown
# Feature Scope: {Project Name}

## Must (MVP Essential)
- [ ] {Feature} — Acceptance criteria: {brief description}
- [ ] ...

## Should (Important but Deferrable)
- [ ] ...

## Could (Nice to Have)
- [ ] ...

## Won't (Explicitly Excluded)
- [ ] ...

## Feature Dependencies
- {Feature A} depends on {Feature B}
```

### Module 3: Business Rules (business-rules.md)

**Output content**: Core business rules, edge cases, exception handling strategies.

**Agent's approach**:
1. Extract implicit business rules from feature scope
2. **Proactively infer** common edge cases and exception scenarios
3. Write `business-rules.md`, annotating which items are inferred
4. User reviews → correct/supplement → update file

### Module 4: Non-Functional Requirements (non-functional.md)

**Output content**: Performance, security, availability, compliance requirements.

**Agent's approach**:
1. Based on project type and user scale, **proactively infer** reasonable non-functional metrics
2. Write `non-functional.md` with recommended values
3. Ask: Focus on confirming performance metrics and security/compliance requirements
4. User reviews → update file

### Module 5: Technical Constraints (tech-constraints.md) (if applicable)

**Output content**: Tech stack, deployment environment, integration points, team constraints.

**Agent's approach**:
1. Scan repository for existing tech stack information
2. **Directly write** confirmed facts (don't ask about things already visible in code)
3. For decision points, provide comparison tables + recommendations
4. User reviews → update file

## Conversation Techniques

### Adapting to Different User Types

- **Talkative users**: Promptly update documents so users see information being structured; avoid information scattering in chat
- **Quiet users**: More output, fewer questions; write more complete drafts so users only need to confirm "right/wrong"
- **Indecisive users**: Provide recommended solution + rationale: "Based on your scenario, I suggest doing X first because..."
- **Divergent users**: Record ideas to the Could/Won't section of documents, gently guide back to core flow

### Review Confirmation Template

After completing a module's document update:

```
Updated docs/01-requirement/project-profile.md

Points to confirm:
1. Are the target users limited to "students" and "teachers"?
2. Is "1000 DAU" a reasonable success criterion?

Please review the file content and let me know what needs correction. After confirmation, I'll move to the next module (feature scope).
```

## Execution

1. **Entry condition**: When user input is insufficient for a complete document, enter QA flow
2. **Start with project profile**: Regardless of information volume, first produce a project-profile.md draft
3. **Progress by module**: Each module goes through "output → review → correct" loop; skip modules if information is sufficient
4. **Update in place**: Each correction updates the same file, no new files created
5. **Exit when ready**: When all Must modules are reviewed and user is satisfied, output completion summary
6. **Handoff**: Prompt user that `docs/01-requirement/` output can feed into spec-writing for detailed requirement documents

## Completion Signals

QA can only end in these situations by default:
- User explicitly says "start output", "ready to write docs", "go with this", etc.
- project-profile.md and feature-scope.md have at least completed review

If user says "keep asking" or "don't start yet", treat as continue clarification. Even if user insists on ending immediately but information is incomplete, **explicitly list assumptions** in documents, annotated as "Not confirmed by user, based on inference."

For the complete signal list and minimum exit criteria, see [references/completion-signals.md](references/completion-signals.md).
