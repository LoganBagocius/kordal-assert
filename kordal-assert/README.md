\# kordal-assert



Three pure checks that read an AI system’s tool-call trace and flag specific silent failures that normal tests miss.



\## What it does



An AI system that calls tools leaves a list of steps. Each step has a name and data. kordal-assert looks only at that list and runs three checks:



\- \*\*Age gate\*\* — the system saw that a case is older than the allowed window, then still took an action.

\- \*\*Unused field\*\* — the system loaded a value early (age, effective date) and never used it again before taking an action.

\- \*\*Constraint\*\* — the system extracted a limit, then took an action that ignored the limit with no override recorded.



No model calls. No API keys. The functions either return a failure or return nothing.



\## Why it exists



Most checks only look at the final answer. These look at the middle of the process. The failures they catch still pass schema validation, confidence scores, and “does this look reasonable?” tests, then reach a customer.



\## Proof



The file `corpus\_50.json` contains 50 labeled traces:

\- 15 that must trigger the age gate

\- 15 that must trigger the unused-field check

\- 10 that must trigger the constraint check

\- 10 that must stay silent



Running the tests confirms the code matches every label.


## Testing on your own traces

A trace is a list of dictionaries. Each dictionary needs a `"name"` and a `"data"` dictionary.

Example:

```python
your_steps = [
    {"name": "load_case", "data": {"age": 45, "window": 30}},
    {"name": "issue_refund", "data": {}}
]

from kordal.checks import check_age_gate, check_unused_field, check_constraint

failures = [f for f in [
    check_age_gate(your_steps),
    check_unused_field(your_steps),
    check_constraint(your_steps)
] if f is not None]

print(failures)  # [Failure(rule='age_gate', ...)]



```bash

python -m pytest

