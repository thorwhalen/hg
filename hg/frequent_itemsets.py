"""
Frequent-itemset mining, augmented so each transaction can carry a numeric
*value* that is accumulated alongside the item *count* (support).

This lets you mine itemsets weighted by an arbitrary per-transaction quantity
(revenue, duration, ...) in addition to plain co-occurrence support. Pass no
``transaction_values`` to get ordinary (count-only) frequent-itemset mining.

The implementation is `Eclat`_ (depth-first search over item *tidlists* — the
sets of transaction indices an item appears in), which is both correct and
simple: an itemset's support is the size of the intersection of its items'
tidlists, and its accumulated value is the sum of those transactions' values.

(Earlier versions of this module vendored an FP-growth fork whose conditional
tree was subtly wrong; this Eclat implementation replaces it and is verified
against a brute-force reference.)

.. _Eclat: https://en.wikipedia.org/wiki/Association_rule_learning#Eclat_algorithm
"""

from collections import defaultdict
from collections.abc import Iterable, Sequence
from typing import NamedTuple

DFLT_MINIMUM_SUPPORT = 2


class FrequentItemset(NamedTuple):
    """A frequent itemset result.

    Tuple-unpackable as ``(items, support, value)``:

    - ``items``: the items making up the itemset (a list).
    - ``support``: number of transactions containing the itemset (the count).
    - ``value``: the accumulated per-transaction value over those transactions
      (equals ``support`` when no ``transaction_values`` were supplied).
    """

    items: list
    support: int
    value: float


def find_frequent_itemsets(
    transactions: Iterable[Iterable],
    *,
    transaction_values: Sequence | None = None,
    minimum_support: int = DFLT_MINIMUM_SUPPORT,
):
    """
    Find frequent itemsets in ``transactions``, yielded as
    :class:`FrequentItemset` (``(items, support, value)``).

    ``transactions`` is any iterable of iterables of hashable items.
    ``transaction_values`` is an optional parallel sequence of numeric weights
    (one per transaction); when omitted, every transaction has weight 1 so
    ``value`` equals ``support`` (ordinary frequent-itemset mining).
    ``minimum_support`` is the minimum number of occurrences for an itemset to
    be reported.

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

    Pass ``transaction_values`` to weight each transaction (here by basket
    price); the third field accumulates that weight over the matching
    transactions:

    >>> prices = [4.0, 9.0, 5.0, 7.0]
    >>> by_value = {
    ...     tuple(sorted(it.items)): it.value
    ...     for it in find_frequent_itemsets(
    ...         transactions, transaction_values=prices, minimum_support=2
    ...     )
    ... }
    >>> by_value[('bread', 'milk')]  # baskets 0 (4.0) and 1 (9.0)
    13.0
    """
    transactions = [set(t) for t in transactions]
    if transaction_values is None:
        transaction_values = [1] * len(transactions)
    transaction_values = list(transaction_values)

    # tidlists[item] = set of transaction indices in which `item` appears.
    tidlists = defaultdict(set)
    for index, transaction in enumerate(transactions):
        for item in transaction:
            tidlists[item].add(index)

    def value_of(tids):
        return sum(transaction_values[i] for i in tids)

    # Process items most-frequent-first (a heuristic that keeps the search
    # shallow); ``repr`` breaks ties deterministically.
    frequent_items = sorted(
        (item for item, tids in tidlists.items() if len(tids) >= minimum_support),
        key=lambda item: (-len(tidlists[item]), repr(item)),
    )

    def grow(prefix, branch):
        # `branch` is a list of (item, tidlist) all frequent given `prefix`.
        for idx, (item, tids) in enumerate(branch):
            itemset = prefix + [item]
            yield FrequentItemset(itemset, len(tids), value_of(tids))
            # Extend with later siblings whose intersection is still frequent.
            extensions = [
                (other_item, tids & other_tids)
                for other_item, other_tids in branch[idx + 1 :]
                if len(tids & other_tids) >= minimum_support
            ]
            if extensions:
                yield from grow(itemset, extensions)

    yield from grow([], [(item, tidlists[item]) for item in frequent_items])
