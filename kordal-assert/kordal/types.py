from dataclasses import dataclass


@dataclass(frozen=True)
class Failure:
    rule: str
    step_index: int
    field: str
