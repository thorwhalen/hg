---
name: hg-dev
description: Use when developing or modifying the `hg` package itself — changing the public API, touching duplication detection (`hg/duplicates.py`) or frequent-itemset mining (`hg/frequent_itemsets.py`), adding algorithms, or working on its tests. Triggers on editing files under the hg repo, "add X to hg", "fix the dedup/itemset code", or changing what `hg/__init__.py` exports.
---

# Developing `hg`

`hg` = "Homogenous Groups": discovering items that recur together. Two modules,
one public surface (`hg/__init__.py`).

## Architecture

- `hg/duplicates.py` — largest repeated *contiguous* blocks in a sequence.
  `BlockDeduplicator` does detection (exact-size seed via a signature map, then
  greedy extension to the largest run); `deduplicate_sequence` is the functional
  facade; `deduplicate_string_lines` is the text convenience; `RemovedBlock` is
  the frozen-dataclass result.
- `hg/frequent_itemsets.py` — **Eclat** mining. Build `tidlists[item] = {tx
  indices}`; an itemset's support is the size of its items' tidlist
  intersection, and its value is the sum of those transactions' values. Depth-
  first `grow()` extends each itemset with later siblings whose intersection is
  still frequent. Result type: `FrequentItemset(items, support, value)`.

## Hard rules

1. **Stay pure-stdlib.** `install_requires` is empty by design. Do not add a
   runtime dependency without a strong reason and an explicit decision.
2. **Never change itemset mining without the property test.** The previous
   implementation was a vendored FP-growth fork whose conditional-tree pruning
   double-counted — it reported itemsets with *higher* support than their own
   subsets and missed others, on ~60% of random inputs, and it had **no test**,
   so the bug shipped silently (also hidden behind a `NameError` that meant it
   never ran). `test_matches_brute_force_on_random_inputs` and
   `test_subset_support_never_exceeded` are the guardrails. If you optimize or
   replace the algorithm, these must still pass — extend them, never weaken them.
3. **Keep `__init__.py` the SSOT for the public API.** New public functions get
   exported there, a docstring, and a doctest.

## Style

Functional facade over class; `dataclass`/`NamedTuple` results (not loose
dicts/tuples); keyword-only args beyond the first positional; module-level
`DFLT_*` constants; a top-level docstring on every module.

## Verifying

```bash
python -m pytest hg/ --doctest-modules -q
python -m doctest README.md
```

CI is the wads uv-based workflow (`pytest --doctest-modules`, ruff `D100`
module-docstring rule). Add a test *before* changing mining behavior, run the
brute-force property test, then make the change.
