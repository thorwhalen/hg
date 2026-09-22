# hg.duplicates

Duplicate detection and handling — find and remove the largest repeated
contiguous blocks in an ordered sequence.

Simple entry points (progressive disclosure — the common cases are one call):

- [`deduplicate_string_lines()`](#hg.duplicates.deduplicate_string_lines) — de-duplicate repeated line-blocks in text.
- [`deduplicate_sequence()`](#hg.duplicates.deduplicate_sequence) — the same for any indexable sequence of items.
- [`BlockDeduplicator`](#hg.duplicates.BlockDeduplicator) — the reusable, configurable form behind both.

A “block” is a maximal run of consecutive items that occurs more than once; the
first occurrence is kept and later ones are removed.

```pycon
>>> text = "A\nB\nA\nB\nC"
>>> final_text, removed = deduplicate_string_lines(text, min_block_size=2)
>>> print(final_text)
A
B
C
>>> removed
[RemovedBlock(removed_start=2, length=2, block_items=['A', 'B'])]
```

### Functions

| [`deduplicate_sequence`](#hg.duplicates.deduplicate_sequence)(sequence, \*[, ...])   | Functional facade over [`BlockDeduplicator`](#hg.duplicates.BlockDeduplicator): remove the largest repeated contiguous blocks from `sequence`, keeping the first occurrence.   |
|----------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [`deduplicate_string_lines`](#hg.duplicates.deduplicate_string_lines)(text, \*[, ...])   | De-duplicate repeated *line-blocks* in a string by splitting it into lines, running [`deduplicate_sequence()`](#hg.duplicates.deduplicate_sequence), and re-joining.              |

### Classes

| [`BlockDeduplicator`](#hg.duplicates.BlockDeduplicator)(\*[, min_block_size, key])     | A generic tool that finds repeated blocks in a sequence of items, then removes duplicate occurrences (retaining the first occurrence).   |
|---------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| [`RemovedBlock`](#hg.duplicates.RemovedBlock)(removed_start, length, block_items) | A contiguous block that was removed as a duplicate.                                                                                      |

### *class* hg.duplicates.BlockDeduplicator(, min_block_size=5, key=None)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

A generic tool that finds repeated blocks in a sequence of items,
then removes duplicate occurrences (retaining the first occurrence).
It uses an initial block size for detection and extends the blocks
to find the largest repeated sequences.

Example of usage:

```pycon
>>> dedup = BlockDeduplicator(min_block_size=2)
>>> seq = [10, 20, 10, 20, 30]
>>> deduped, removed = dedup.deduplicate_sequence(seq)
>>> deduped
[10, 20, 30]
>>> removed
[RemovedBlock(removed_start=2, length=2, block_items=[10, 20])]
```

#### deduplicate_sequence(sequence)

Detect largest duplicate blocks, then remove the second
and subsequent occurrences of each block from ‘sequence’.

* **Parameters:**
  **sequence** ([`Sequence`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence)) – A list (or other indexable container) of items.
* **Returns:**
  `(deduped_sequence, removed_blocks)`
  - deduped_sequence: final list of items after removing duplicates
  - removed_blocks: list of [`RemovedBlock`](#hg.duplicates.RemovedBlock) with the details of
    each removed occurrence

```pycon
>>> dedup = BlockDeduplicator(min_block_size=2)
>>> deduped, removed = dedup.deduplicate_sequence(
...     ["A", "B", "A", "B", "C"]
... )
>>> deduped
['A', 'B', 'C']
>>> removed
[RemovedBlock(removed_start=2, length=2, block_items=['A', 'B'])]
```

### *class* hg.duplicates.RemovedBlock(removed_start, length, block_items)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

A contiguous block that was removed as a duplicate.

- `removed_start`: index (in the original sequence) where the removed
  occurrence began.
- `length`: number of items in the block.
- `block_items`: the actual items of the block (taken from the first,
  retained, occurrence).

### hg.duplicates.deduplicate_sequence(sequence, , min_block_size=5, key=None)

Functional facade over [`BlockDeduplicator`](#hg.duplicates.BlockDeduplicator): remove the largest
repeated contiguous blocks from `sequence`, keeping the first occurrence.

Returns `(deduped_sequence, removed_blocks)` where `removed_blocks` is a
list of [`RemovedBlock`](#hg.duplicates.RemovedBlock).

```pycon
>>> deduped, removed = deduplicate_sequence([1, 2, 1, 2, 3], min_block_size=2)
>>> deduped
[1, 2, 3]
>>> removed
[RemovedBlock(removed_start=2, length=2, block_items=[1, 2])]
```

### hg.duplicates.deduplicate_string_lines(text, \*, min_block_size=5, key=<built-in function hash>, return_final_text=True, return_removed_blocks=True)

De-duplicate repeated *line-blocks* in a string by splitting it into lines,
running [`deduplicate_sequence()`](#hg.duplicates.deduplicate_sequence), and re-joining.

* **Parameters:**
  * **text** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – The input string.
  * **min_block_size** ([`int`](https://docs.python.org/3/builtins/functions.html#int)) – The size (in number of lines) for initial block match.
  * **key** ([`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable) | [`None`](https://docs.python.org/3/builtins/constants.html#None)) – Optional key function mapping each line to a
    comparable/hashable value. Defaults to [`hash()`](https://docs.python.org/3/builtins/functions.html#hash)
    (lines are matched by hash, which is fine for text).
  * **return_final_text** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – Include the deduplicated text in the result.
  * **return_removed_blocks** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – Include the list of [`RemovedBlock`](#hg.duplicates.RemovedBlock).
* **Returns:**
  - both flags true (default): `(final_text, removed_blocks)`
  - only `return_final_text`: `final_text`
  - only `return_removed_blocks`: `removed_blocks`
  - neither: `None`

```pycon
>>> text = "A\nB\nC\nA\nB\nC\nD"
>>> final_text, removed = deduplicate_string_lines(text, min_block_size=3)
>>> print(final_text)
A
B
C
D
>>> removed
[RemovedBlock(removed_start=3, length=3, block_items=['A', 'B', 'C'])]
>>> deduplicate_string_lines(text, min_block_size=3, return_removed_blocks=False)
'A\nB\nC\nD'
```
