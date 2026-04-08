# Structured Options and Recommendation Rules

## Option Design Rules

- Provide **2-5 preset options** per question
- **Must mark exactly one recommended option**, with a brief explanation of the recommendation reason in the option description
- **The last option** must always be an open-ended input (e.g., "Other: describe your thoughts"), allowing free-form input
- Allow multi-select when the question involves multiple dimensions
- Briefly explain "why we're asking this now" before the question — help users understand the significance of the question

## Recommendation Judgment Criteria (by Priority)

1. **Engineering facts**: Existing tech stack, architecture patterns, configuration conventions in the current repo/project
2. **Contextual inference**: Infer the most likely choice from confirmed facts collected in previous rounds
3. **Industry conventions**: When engineering facts and context are insufficient, choose the most mainstream solution in that domain
4. **Safety-side preference**: When multiple options have significantly different risk levels, recommend the lowest-risk option

## Recommendation Expression Across Different Hosts

| Host Capability | Recommendation Expression |
|---|---|
| Supports `recommended` field (e.g., VS Code `askQuestions`) | Directly mark `recommended: true` |
| Supports option descriptions | Prefix recommended option with a star or write "recommended" in description |
| Plain text options only | Place recommended option first, annotate with "(recommended)" |
| Fallback to chat message | Bold the recommended option |

Regardless of host capability, the **judgment logic for recommendations remains the same** — only the expression adapts to the host.

## Prohibited

- Not marking any recommended option (increases user decision burden)
- Marking multiple recommended options (dilutes recommendation meaning)
- Recommending without justification (must be able to state the reason)

## Host-Agnostic Principle

Prefer using the structured questioning capabilities provided by the current Agent host editor, rather than system-level popups.

Invocation priority:
1. Structured questioning tool explicitly provided by the current host
2. The host's native input box / Quick Pick / interactive forms
3. Only when completely unavailable, fall back to plain chat messages

Do not hardcode a Skill to a specific editor's private API. Let the model running the Skill choose the corresponding tool based on its current environment.

## Example

```
Why we're asking: The frontend framework determines a series of subsequent choices including project templates, component libraries, state management, etc.

What frontend framework do you prefer for your project?

1. ⭐ Vue 3 (recommended) — Team already has Vue experience, progressive learning curve
2. React — Largest ecosystem, abundant community resources
3. Angular — Suited for large enterprise applications, strong conventions
4. Other — Please enter your thoughts or framework name directly
```
