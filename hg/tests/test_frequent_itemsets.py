"""Tests for frequent_itemsets.py.

Includes a brute-force property test: had this existed, it would have caught the
correctness bug in the previous (FP-growth) implementation, where an itemset
could be reported with greater support than one of its own subsets.
"""

import random
from itertools import combinations

from hg.frequent_itemsets import FrequentItemset, find_frequent_itemsets


TRANSACTIONS = [
    ["bread", "milk"],
    ["bread", "milk", "eggs"],
    ["milk", "eggs"],
    ["bread", "butter"],
]


def _brute_force(transactions, values, minimum_support):
    """Reference: enumerate every itemset and count it directly."""
    tx = [set(t) for t in transactions]
    items = set().union(*tx) if tx else set()
    out = {}
    for r in range(1, len(items) + 1):
        for combo in combinations(sorted(items), r):
            ids = [i for i, t in enumerate(tx) if set(combo) <= t]
            if len(ids) >= minimum_support:
                out[frozenset(combo)] = (len(ids), sum(values[i] for i in ids))
    return out


def test_basic_support():
    got = {
        frozenset(it.items): it.support
        for it in find_frequent_itemsets(TRANSACTIONS, minimum_support=2)
    }
    assert got == {
        frozenset({"bread"}): 3,
        frozenset({"milk"}): 3,
        frozenset({"eggs"}): 2,
        frozenset({"bread", "milk"}): 2,
        frozenset({"eggs", "milk"}): 2,
    }


def test_value_accumulation():
    prices = [4.0, 9.0, 5.0, 7.0]
    by_value = {
        frozenset(it.items): it.value
        for it in find_frequent_itemsets(
            TRANSACTIONS, transaction_values=prices, minimum_support=2
        )
    }
    # {bread, milk} occurs in baskets 0 (4.0) and 1 (9.0)
    assert by_value[frozenset({"bread", "milk"})] == 13.0
    # {eggs, milk} occurs in baskets 1 (9.0) and 2 (5.0)
    assert by_value[frozenset({"eggs", "milk"})] == 14.0
    # singletons: value sums every basket containing them
    assert by_value[frozenset({"milk"})] == 4.0 + 9.0 + 5.0


def test_default_value_equals_support():
    for it in find_frequent_itemsets(TRANSACTIONS, minimum_support=2):
        assert it.value == it.support


def test_returns_frequent_itemset_namedtuples():
    results = list(find_frequent_itemsets(TRANSACTIONS, minimum_support=2))
    assert all(isinstance(it, FrequentItemset) for it in results)
    # tuple-unpackable
    items, support, value = results[0]
    assert isinstance(items, list)


def test_subset_support_never_exceeded():
    # The invariant the old implementation violated: support is anti-monotone,
    # so no itemset may have higher support than any of its subsets.
    results = list(find_frequent_itemsets(TRANSACTIONS, minimum_support=1))
    support = {frozenset(it.items): it.support for it in results}
    for itemset, sup in support.items():
        for item in itemset:
            subset = itemset - {item}
            if subset:
                assert support[subset] >= sup


def test_matches_brute_force_on_random_inputs():
    rng = random.Random(1234)
    universe = list("abcdef")
    for _ in range(500):
        n = rng.randint(1, 9)
        tx = [
            rng.sample(universe, rng.randint(1, len(universe))) for _ in range(n)
        ]
        vals = [round(rng.uniform(1, 10), 1) for _ in range(n)]
        minsup = rng.randint(1, 3)
        ref = {k: (v[0], round(v[1], 4)) for k, v in _brute_force(tx, vals, minsup).items()}
        got = {
            frozenset(it.items): (it.support, round(it.value, 4))
            for it in find_frequent_itemsets(
                tx, transaction_values=vals, minimum_support=minsup
            )
        }
        assert got == ref, f"mismatch for tx={tx}, minsup={minsup}"


def test_empty_and_below_support():
    assert list(find_frequent_itemsets([], minimum_support=1)) == []
    # nothing reaches support 5 here
    assert list(find_frequent_itemsets(TRANSACTIONS, minimum_support=5)) == []
