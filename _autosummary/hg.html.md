# hg

Homogenous Groups — discovering items that recur together.

Two complementary capabilities:

- **Duplication detection** — find and remove the largest repeated contiguous
  blocks in an ordered sequence (e.g. de-duplicate repeated line-blocks in text)
  via `deduplicate_string_lines()`, `deduplicate_sequence()`, and
  `BlockDeduplicator`.
- **Frequent-itemset mining** — find sets of items that co-occur across
  transactions, optionally weighted by a per-transaction value, via
  `find_frequent_itemsets()`.

### Modules

| [`duplicates`](hg.duplicates.html.md#module-hg.duplicates)               | Duplicate detection and handling — find and remove the largest repeated contiguous blocks in an ordered sequence.                            |
|------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| [`frequent_itemsets`](hg.frequent_itemsets.html.md#module-hg.frequent_itemsets) | Frequent-itemset mining, augmented so each transaction can carry a numeric *value* that is accumulated alongside the item *count* (support). |
