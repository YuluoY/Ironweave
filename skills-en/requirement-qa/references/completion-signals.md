# Completion Signals

## Signals That Allow Ending

When ANY of the following texts are matched in user input, it can be considered that the user explicitly allows ending QA and outputting a summary:

- `start output`
- `start producing`
- `ready to write docs`
- `ready to write code`
- `go with this`
- `output based on this`
- `compile into PRD`
- `proceed to implementation`
- `start execution`
- `start implementation`
- `generate now`
- `enough, let's go`

## Continuation Intent Protection

If the response contains any of the following semantics, prioritize interpreting it as "continue clarifying" — do not misjudge as completion:

- `keep asking`
- `continue clarifying`
- `don't start yet`
- `not yet`
- `I'll say start output when ready`
- `wait until I say go`
- `one more question`

## Minimum Completion Criteria

Even when a completion signal appears, ensure the following information has been roughly clarified:

1. **Final deliverable**: What needs to be delivered
2. **Target user / acceptor**: Who it's for
3. **Scope boundary**: What to do + what NOT to do
4. **Key constraints**: Time, technology, resource limitations
5. **Success criteria**: What level of completion counts as done

If the user insists on starting immediately but information is still incomplete, **explicitly list assumptions** in the final output, labeled as "Not confirmed by user, based on inference".
