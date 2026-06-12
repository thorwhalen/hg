# hg

Homogenous Groups — find items that recur together.

To install: `pip install hg`

`hg` bundles two complementary ways of discovering repeated structure in data,
with no third-party dependencies (pure standard library):

- **Duplication detection** — find and remove the largest repeated *contiguous*
  blocks in an ordered sequence (e.g. repeated line-blocks in text).
- **Frequent-itemset mining** — find sets of items that *co-occur* across
  transactions, optionally weighted by a per-transaction value.

## Duplication detection

The simplest case — de-duplicate repeated line-blocks in text, keeping the first
occurrence:

```python
>>> from hg import deduplicate_string_lines
>>> text = "A\nB\nC\nA\nB\nC\nD"
>>> final_text, removed = deduplicate_string_lines(text, min_block_size=3)
>>> print(final_text)
A
B
C
D
>>> removed
[RemovedBlock(removed_start=3, length=3, block_items=['A', 'B', 'C'])]

```

The same works on any sequence of items via `deduplicate_sequence` (or the
reusable `BlockDeduplicator`), with an optional `key` to control how items are
compared:

```python
>>> from hg import deduplicate_sequence
>>> deduped, removed = deduplicate_sequence([1, 2, 1, 2, 3], min_block_size=2)
>>> deduped
[1, 2, 3]

```

`min_block_size` is the smallest repeated run to detect; detected blocks are
then greedily extended to the largest repeated run.

## Frequent-itemset mining

Find sets of items that appear together in at least `minimum_support`
transactions:

```python
>>> from hg import find_frequent_itemsets
>>> transactions = [
...     ['bread', 'milk'],
...     ['bread', 'milk', 'eggs'],
...     ['milk', 'eggs'],
...     ['bread', 'butter'],
... ]
>>> for itemset in sorted(
...     find_frequent_itemsets(transactions, minimum_support=2),
...     key=lambda it: (-it.support, sorted(it.items)),
... ):
...     print(sorted(itemset.items), itemset.support)
['bread'] 3
['milk'] 3
['bread', 'milk'] 2
['eggs'] 2
['eggs', 'milk'] 2

```

### Value-weighted itemsets

The distinguishing feature: pass `transaction_values` to accumulate an arbitrary
per-transaction quantity (revenue, duration, ...) alongside the count. Each
result is a `FrequentItemset(items, support, value)`:

```python
>>> prices = [4.0, 9.0, 5.0, 7.0]   # one value per transaction
>>> by_value = {
...     tuple(sorted(it.items)): it.value
...     for it in find_frequent_itemsets(
...         transactions, transaction_values=prices, minimum_support=2
...     )
... }
>>> by_value[('bread', 'milk')]     # baskets 0 (4.0) and 1 (9.0)
13.0

```

With no `transaction_values`, `value` simply equals `support`.

## When to use which

- Reach for **duplication detection** when *order matters* and you want to
  collapse repeated runs (deduping logs, transcripts, generated text).
- Reach for **frequent-itemset mining** when *co-occurrence* matters and order
  does not (market-basket analysis, tag/feature co-occurrence), especially when
  you want to weight occurrences by a value.
