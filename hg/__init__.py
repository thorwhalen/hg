"""
Homogenous Groups — discovering items that recur together.

Two complementary capabilities:

- **Duplication detection** — find and remove the largest repeated contiguous
  blocks in an ordered sequence (e.g. de-duplicate repeated line-blocks in text)
  via :func:`deduplicate_string_lines`, :func:`deduplicate_sequence`, and
  :class:`BlockDeduplicator`.
- **Frequent-itemset mining** — find sets of items that co-occur across
  transactions, optionally weighted by a per-transaction value, via
  :func:`find_frequent_itemsets`.
"""

from hg.duplicates import (
    BlockDeduplicator,
    RemovedBlock,
    deduplicate_sequence,
    deduplicate_string_lines,
)
from hg.frequent_itemsets import FrequentItemset, find_frequent_itemsets
