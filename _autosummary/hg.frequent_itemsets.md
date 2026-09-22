# hg.frequent_itemsets

Frequent-itemset mining, augmented so each transaction can carry a numeric
*value* that is accumulated alongside the item *count* (support).

This lets you mine itemsets weighted by an arbitrary per-transaction quantity
(revenue, duration, …) in addition to plain co-occurrence support. Pass no
`transaction_values` to get ordinary (count-only) frequent-itemset mining.

The implementation is [Eclat](https://en.wikipedia.org/wiki/Association_rule_learning#Eclat_algorithm) (depth-first search over item *tidlists* — the
sets of transaction indices an item appears in), which is both correct and
simple: an itemset’s support is the size of the intersection of its items’
tidlists, and its accumulated value is the sum of those transactions’ values.

(Earlier versions of this module vendored an FP-growth fork whose conditional
tree was subtly wrong; this Eclat implementation replaces it and is verified
against a brute-force reference.)

### Functions

| [`find_frequent_itemsets`](#hg.frequent_itemsets.find_frequent_itemsets)(transactions, \*[, ...])   | Find frequent itemsets in `transactions`, yielded as [`FrequentItemset`](#hg.frequent_itemsets.FrequentItemset) (`(items, support, value)`).   |
|----------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|

### Classes

| [`FrequentItemset`](#hg.frequent_itemsets.FrequentItemset)(items, support, value)   | A frequent itemset result.   |
|-------------------------------------------------------------------------------------------|------------------------------|

### *class* hg.frequent_itemsets.FrequentItemset(items, support, value)

Bases: [`NamedTuple`](https://docs.python.org/3/library/typing.html#typing.NamedTuple)

A frequent itemset result.

Tuple-unpackable as `(items, support, value)`:

- `items`: the items making up the itemset (a list).
- `support`: number of transactions containing the itemset (the count).
- `value`: the accumulated per-transaction value over those transactions
  (equals `support` when no `transaction_values` were supplied).

#### items *: [list](https://docs.python.org/3/builtins/stdtypes.html#list)*

Alias for field number 0

#### support *: [int](https://docs.python.org/3/builtins/functions.html#int)*

Alias for field number 1

#### value *: [float](https://docs.python.org/3/builtins/functions.html#float)*

Alias for field number 2

### hg.frequent_itemsets.find_frequent_itemsets(transactions, , transaction_values=None, minimum_support=2)

Find frequent itemsets in `transactions`, yielded as
[`FrequentItemset`](#hg.frequent_itemsets.FrequentItemset) (`(items, support, value)`).

`transactions` is any iterable of iterables of hashable items.
`transaction_values` is an optional parallel sequence of numeric weights
(one per transaction); when omitted, every transaction has weight 1 so
`value` equals `support` (ordinary frequent-itemset mining).
`minimum_support` is the minimum number of occurrences for an itemset to
be reported.

```pycon
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

Pass `transaction_values` to weight each transaction (here by basket
price); the third field accumulates that weight over the matching
transactions:

```pycon
>>> prices = [4.0, 9.0, 5.0, 7.0]
>>> by_value = {
...     tuple(sorted(it.items)): it.value
...     for it in find_frequent_itemsets(
...         transactions, transaction_values=prices, minimum_support=2
...     )
... }
>>> by_value[('bread', 'milk')]  # baskets 0 (4.0) and 1 (9.0)
13.0
```
