r"""
Duplicate detection and handling — find and remove the largest repeated
contiguous blocks in an ordered sequence.

Simple entry points (progressive disclosure — the common cases are one call):

- :func:`deduplicate_string_lines` — de-duplicate repeated line-blocks in text.
- :func:`deduplicate_sequence` — the same for any indexable sequence of items.
- :class:`BlockDeduplicator` — the reusable, configurable form behind both.

A "block" is a maximal run of consecutive items that occurs more than once; the
first occurrence is kept and later ones are removed.

>>> text = "A\nB\nA\nB\nC"
>>> final_text, removed = deduplicate_string_lines(text, min_block_size=2)
>>> print(final_text)
A
B
C
>>> removed
[RemovedBlock(removed_start=2, length=2, block_items=['A', 'B'])]
"""

from collections import defaultdict
from collections.abc import Callable, Sequence
from dataclasses import dataclass

DFLT_MIN_BLOCK_SIZE = 5


@dataclass(frozen=True)
class RemovedBlock:
    """A contiguous block that was removed as a duplicate.

    - ``removed_start``: index (in the original sequence) where the removed
      occurrence began.
    - ``length``: number of items in the block.
    - ``block_items``: the actual items of the block (taken from the first,
      retained, occurrence).
    """

    removed_start: int
    length: int
    block_items: list


class BlockDeduplicator:
    """
    A generic tool that finds repeated blocks in a sequence of items,
    then removes duplicate occurrences (retaining the first occurrence).
    It uses an initial block size for detection and extends the blocks
    to find the largest repeated sequences.

    Example of usage:

    >>> dedup = BlockDeduplicator(min_block_size=2)
    >>> seq = [10, 20, 10, 20, 30]
    >>> deduped, removed = dedup.deduplicate_sequence(seq)
    >>> deduped
    [10, 20, 30]
    >>> removed
    [RemovedBlock(removed_start=2, length=2, block_items=[10, 20])]

    """

    def __init__(
        self, *, min_block_size: int = DFLT_MIN_BLOCK_SIZE, key: Callable | None = None
    ):
        """
        :param min_block_size:  The size (of the sequence) for initial block match.
        :param key:             A function that maps each item to a
                                comparable/hashable value. Defaults to identity.
        """
        self.min_block_size = min_block_size
        self.key = key if key is not None else (lambda x: x)

    def _compute_keys(self, sequence):
        """
        Compute the key values for each item in the sequence.
        This allows us to compare or hash items efficiently.
        """
        return [self.key(item) for item in sequence]

    def _find_exact_size_blocks(self, item_keys):
        """
        Find all repeated blocks of EXACTLY self.min_block_size in the key sequence.

        Returns a list of (block_signature, [start_indices]) pairs:
          - block_signature: tuple of length min_block_size (the keyed items)
          - [start_indices]: list of positions where that signature appears
        """
        n = len(item_keys)
        signature_map = defaultdict(list)

        for i in range(n - self.min_block_size + 1):
            block_tuple = tuple(item_keys[i : i + self.min_block_size])
            signature_map[block_tuple].append(i)

        # Keep only those signatures that appear at least twice
        repeated = []
        for sig, starts in signature_map.items():
            if len(starts) > 1:
                repeated.append((sig, starts))

        return repeated

    def _extend_block(self, item_keys, group_indices, current_size):
        """
        Attempt to extend the repeated block by 1 item if all positions
        in group_indices match the next item.

        :param item_keys:      The keyed sequence of items.
        :param group_indices:  All start positions for the repeated block.
        :param current_size:   Current size of the repeated block.
        :return: new_size      (Either current_size or current_size + 1)
        """
        n = len(item_keys)
        # Check if we can add at least one more item for every start index
        for start in group_indices:
            if start + current_size >= n:
                # Out of range for at least one occurrence
                return current_size

        # If in range, check if the next keyed item is the same for all starts
        first_key = item_keys[group_indices[0] + current_size]
        for start in group_indices[1:]:
            if item_keys[start + current_size] != first_key:
                # mismatch found, can't extend
                return current_size

        # If no mismatches, we can extend by 1
        return current_size + 1

    def _detect_largest_duplicates(self, sequence):
        """
        1) Convert items -> keyed items.
        2) Detect repeated blocks of EXACT self.min_block_size.
        3) Extend each block to find the largest repeated block.
        4) Return a list of dictionaries with:
            {
              'start_indices': [...],
              'length': <final block length>,
              'block_items': <the actual items in the block from the first occurrence>,
            }
           sorted by descending 'length'.
        """
        item_keys = self._compute_keys(sequence)
        repeated_candidates = self._find_exact_size_blocks(item_keys)

        results = []
        for block_signature, group_indices in repeated_candidates:
            current_size = self.min_block_size

            # Attempt to extend the block as far as possible
            while True:
                new_size = self._extend_block(item_keys, group_indices, current_size)
                if new_size == current_size:
                    break
                current_size = new_size

            # Final block info
            first_start = group_indices[0]
            block_items = sequence[first_start : first_start + current_size]
            results.append(
                {
                    "start_indices": group_indices,
                    "length": current_size,
                    "block_items": block_items,
                }
            )

        # Sort by largest length first
        results.sort(key=lambda r: r["length"], reverse=True)
        return results

    def deduplicate_sequence(self, sequence: Sequence):
        r"""
        Detect largest duplicate blocks, then remove the second
        and subsequent occurrences of each block from 'sequence'.

        :param sequence: A list (or other indexable container) of items.
        :returns: ``(deduped_sequence, removed_blocks)``
            - deduped_sequence: final list of items after removing duplicates
            - removed_blocks: list of :class:`RemovedBlock` with the details of
              each removed occurrence

        >>> dedup = BlockDeduplicator(min_block_size=2)
        >>> deduped, removed = dedup.deduplicate_sequence(
        ...     ["A", "B", "A", "B", "C"]
        ... )
        >>> deduped
        ['A', 'B', 'C']
        >>> removed
        [RemovedBlock(removed_start=2, length=2, block_items=['A', 'B'])]

        """
        duplicates_info = self._detect_largest_duplicates(sequence)

        removed_indices = set()
        removed_blocks = []

        # Remove duplicates in descending block size order
        for info in duplicates_info:
            length = info["length"]
            starts = sorted(info["start_indices"])  # ascending for consistency

            # Keep the first occurrence, remove subsequent ones
            first_start = starts[0]
            for other_start in starts[1:]:
                # Check if these items were already removed or not
                overlap = any(
                    (idx in removed_indices)
                    for idx in range(other_start, other_start + length)
                )
                if not overlap:
                    # Remove them
                    for idx in range(other_start, other_start + length):
                        removed_indices.add(idx)
                    removed_blocks.append(
                        RemovedBlock(
                            removed_start=other_start,
                            length=length,
                            block_items=info["block_items"],
                        )
                    )

        # Build the final sequence
        deduped_sequence = [
            item for idx, item in enumerate(sequence) if idx not in removed_indices
        ]
        return deduped_sequence, removed_blocks


def deduplicate_sequence(
    sequence: Sequence,
    *,
    min_block_size: int = DFLT_MIN_BLOCK_SIZE,
    key: Callable | None = None,
):
    r"""
    Functional facade over :class:`BlockDeduplicator`: remove the largest
    repeated contiguous blocks from ``sequence``, keeping the first occurrence.

    Returns ``(deduped_sequence, removed_blocks)`` where ``removed_blocks`` is a
    list of :class:`RemovedBlock`.

    >>> deduped, removed = deduplicate_sequence([1, 2, 1, 2, 3], min_block_size=2)
    >>> deduped
    [1, 2, 3]
    >>> removed
    [RemovedBlock(removed_start=2, length=2, block_items=[1, 2])]
    """
    deduplicator = BlockDeduplicator(min_block_size=min_block_size, key=key)
    return deduplicator.deduplicate_sequence(sequence)


def deduplicate_string_lines(
    text: str,
    *,
    min_block_size: int = DFLT_MIN_BLOCK_SIZE,
    key: Callable | None = hash,
    return_final_text: bool = True,
    return_removed_blocks: bool = True,
):
    r"""
    De-duplicate repeated *line-blocks* in a string by splitting it into lines,
    running :func:`deduplicate_sequence`, and re-joining.

    :param text:             The input string.
    :param min_block_size:   The size (in number of lines) for initial block match.
    :param key:              Optional key function mapping each line to a
                             comparable/hashable value. Defaults to :func:`hash`
                             (lines are matched by hash, which is fine for text).
    :param return_final_text:    Include the deduplicated text in the result.
    :param return_removed_blocks: Include the list of :class:`RemovedBlock`.
    :returns:
        - both flags true (default): ``(final_text, removed_blocks)``
        - only ``return_final_text``: ``final_text``
        - only ``return_removed_blocks``: ``removed_blocks``
        - neither: ``None``

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
    """
    lines = text.splitlines()
    deduped_lines, removed_blocks = deduplicate_sequence(
        lines, min_block_size=min_block_size, key=key
    )
    final_text = "\n".join(deduped_lines)
    if return_final_text and return_removed_blocks:
        return final_text, removed_blocks
    if return_final_text:
        return final_text
    if return_removed_blocks:
        return removed_blocks
    return None
