# hg — developer context

`hg` ("Homogenous Groups") finds **items that recur together**, two ways:

- **Duplication detection** (`hg/duplicates.py`): largest repeated *contiguous*
  blocks in an ordered sequence. Public: `deduplicate_string_lines`,
  `deduplicate_sequence` (functional facade), `BlockDeduplicator` (reusable
  form), `RemovedBlock` (frozen dataclass result).
- **Frequent-itemset mining** (`hg/frequent_itemsets.py`): sets of items that
  *co-occur* across transactions, optionally value-weighted. Public:
  `find_frequent_itemsets`, `FrequentItemset` (NamedTuple result).

The public surface is exactly what `hg/__init__.py` re-exports. Keep that file
as the single source of truth for the package's API.

## Invariants (do not break casually)

- **Pure standard library.** `install_requires` is empty by design — both
  modules use only `collections`, `collections.abc`, `dataclasses`, `typing`.
  Adding a runtime dependency is a significant decision; prefer not to.
- **Itemset mining is Eclat** (depth-first over per-item *tidlists*). Support =
  size of the tidlist intersection; value = sum of those transactions' values.
  It is verified against a brute-force reference (`test_matches_brute_force...`).
  `frequent_itemsets.py` replaced a vendored FP-growth fork whose conditional
  tree was subtly **wrong** (an itemset could out-support its own subset). The
  lesson: never trust an itemset-mining change without the property test.
- **Block extension:** `min_block_size` is a detection *seed*; blocks are then
  greedily extended to the largest repeated run. `min_block_size=2` legitimately
  yields a length-3 block — that is the extension working, not a bug.

## Conventions (owner style)

- Functional facade over the class (`deduplicate_sequence` is the common path;
  `BlockDeduplicator` is the reusable form behind it).
- `dataclasses` / `NamedTuple` for result records (`RemovedBlock`,
  `FrequentItemset`), not loose dicts/tuples.
- Keyword-only arguments beyond the first positional; module-level `DFLT_*`
  constants instead of magic numbers.
- Every module has a top-level docstring (auto-extracted for docs); every public
  function has a doctest.

## Tests

```bash
python -m pytest hg/ --doctest-modules -q   # unit tests + doctests
python -m doctest README.md                 # README examples
```

The brute-force property test (`hg/tests/test_frequent_itemsets.py`) is the
guardrail for the mining code — extend it rather than weaken it.

Handoff notes live in `.claude/handoffs/` (gitignored).
