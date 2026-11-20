import json
import os
from pathlib import Path

import pytest

from kordal.checks import check_age_gate, check_constraint, check_unused_field

CORPUS_PATH = Path(
    os.environ.get("KORDAL_CORPUS", Path(__file__).parent / "corpus_50.json")
)

CHECKS = {
    "age_gate": check_age_gate,
    "unused_field": check_unused_field,
    "constraint": check_constraint,
}

with open(CORPUS_PATH, encoding="utf-8") as fh:
    CORPUS = json.load(fh)


def fired_rules(trace):
    fired = set()
    for name, check in CHECKS.items():
        failure = check(trace)
        if failure is not None:
            assert failure.rule == name, (
                f"{check.__name__} returned a Failure with rule {failure.rule!r}"
            )
            fired.add(failure.rule)
    return fired


@pytest.mark.parametrize("index", range(len(CORPUS)), ids=lambda i: f"entry_{i:02d}")
def test_entry_matches_expect(index):
    entry = CORPUS[index]
    fired = fired_rules(entry["trace"])
    assert fired == set(entry["expect"]), (
        f"entry {index}: fired {sorted(fired)}, expected {sorted(entry['expect'])}"
    )


def test_corpus_has_no_mismatches():
    mismatches = [
        (i, sorted(fired_rules(e["trace"])), sorted(e["expect"]))
        for i, e in enumerate(CORPUS)
        if fired_rules(e["trace"]) != set(e["expect"])
    ]
    assert not mismatches, f"{len(mismatches)} trace(s) mismatched: {mismatches}"
