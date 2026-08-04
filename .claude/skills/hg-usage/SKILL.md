---
name: hg-usage
description: Use when you need to (a) de-duplicate repeated contiguous blocks in a sequence or text, or (b) mine frequent — optionally value-weighted — itemsets from transactions. Triggers on "remove repeated blocks/lines", "dedupe a transcript/log/generated text", "find the largest repeated run", "frequent itemsets", "market-basket / co-occurrence analysis", "which items appear together", or weighting co-occurrences by revenue/duration/etc. The package is `hg` (pure stdlib, `pip install hg`).
---

# Using `hg`

`hg` discovers items that recur together. Two independent capabilities.

## 1. Duplication detection (order matters)

Remove the largest repeated **contiguous** blocks, keeping the first occurrence.

```python
from hg import deduplicate_string_lines, deduplicate_sequence

# Text: de-duplicate repeated line-blocks
final_text, removed = deduplicate_string_lines(text, min_block_size=3)

# Any sequence of items
deduped, removed = deduplicate_sequence(items, min_block_size=2)
```

- `min_block_size` (keyword-only): the smallest repeated run to *detect*. Blocks
  are then greedily **extended** to the largest repeated run, so a small
  `min_block_size` can return longer blocks.
- `key` (keyword-only): map each item to a comparable/hashable value to control
  what counts as "equal" (e.g. `key=str.lower`).
- `removed` is a list of `RemovedBlock(removed_start, length, block_items)`
  (a dataclass — use attribute access, not `["..."]`).
- `deduplicate_string_lines` flags: `return_final_text` / `return_removed_blocks`
  (both default `True`). Returns the text, the blocks, both as a tuple, or `None`.

Use for: deduping logs, transcripts, or LLM-generated text with repeated runs.

## 2. Frequent-itemset mining (order does not matter)

Find sets of items co-occurring in at least `minimum_support` transactions.

```python
from hg import find_frequent_itemsets

transactions = [["bread", "milk"], ["bread", "milk", "eggs"], ["milk", "eggs"]]
for items, support, value in find_frequent_itemsets(transactions, minimum_support=2):
    ...  # items: list, support: int, value: float
```

- Yields `FrequentItemset(items, support, value)` namedtuples (tuple-unpackable).
- `minimum_support` (keyword-only, default 2): minimum occurrence count.
- **Value weighting** — pass `transaction_values`, a parallel sequence of numeric
  weights (one per transaction). Then `value` accumulates that weight over the
  matching transactions (e.g. total revenue of baskets containing the itemset).
  With no `transaction_values`, `value == support`.

```python
prices = [4.0, 9.0, 5.0]  # one per transaction
itemsets = find_frequent_itemsets(
    transactions, transaction_values=prices, minimum_support=2
)
```

Use for: market-basket / co-occurrence analysis, tag or feature co-occurrence,
and any "which items show up together, weighted by X" question.

## Choosing

- Order/adjacency matters, collapse repeats → **duplication detection**.
- Co-occurrence (set membership) matters → **frequent-itemset mining**.
