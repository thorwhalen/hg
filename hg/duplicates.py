r"""
Duplicate detection and handling.


>>> example_text = '''Lorem ipsum
... dolor sit amet
... dolor sit amet
... dolor sit amet
... Consectetur adipiscing
... Lorem ipsum
... dolor sit amet
... dolor sit amet
... Consectetur adipiscing
... Something else
... '''
>>> final_text, removed = deduplicate_string_lines(example_text, min_block_size=3)
>>> print("=== Deduplicated Lines ===")
=== Deduplicated Lines ===
>>> print(final_text)
Lorem ipsum
dolor sit amet
dolor sit amet
dolor sit amet
Consectetur adipiscing
Consectetur adipiscing
Something else
>>> print("\n=== Removed Blocks ===")
<BLANKLINE>
=== Removed Blocks ===
>>> for block in removed:
...     print(f"Removed block starting at line {block['removed_start']} with length {block['length']}:")
...     for item in block['block_items']:
...         print(f"  {item}")
...     print()
Removed block starting at line 5 with length 3:
  Lorem ipsum
  dolor sit amet
  dolor sit amet
<BLANKLINE>

"""

from typing import Callable, Optional, Tuple, List, Dict
from collections import defaultdict


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
    [{'removed_start': 2, 'length': 2, 'block_items': [10, 20]}]

    """

    def __init__(self, min_block_size=5, key=None):
        """
        :param min_block_size:  The size for initial block match.
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

    def deduplicate_sequence(self, sequence):
        r"""
        Detect largest duplicate blocks, then remove the second
        and subsequent occurrences of each block from 'sequence'.

        :param sequence: A list (or other indexable container) of items.
        :returns: (deduped_sequence, removed_blocks)
            - deduped_sequence: final list of items after removing duplicates
            - removed_blocks: list of removed blocks with details

        >>> text = "Line A\nLine B\nLine A\nLine B\nLine C"
        >>> final_text, removed = deduplicate_string_lines(text, min_block_size=2)
        >>> print(final_text)
        Line A
        Line B
        Line C
        >>> removed
        [{'removed_start': 2, 'length': 2, 'block_items': ['Line A', 'Line B']}]

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
                        {
                            "removed_start": other_start,
                            "length": length,
                            "block_items": info["block_items"],
                        }
                    )

        # Build the final sequence
        deduped_sequence = [
            item for idx, item in enumerate(sequence) if idx not in removed_indices
        ]
        return deduped_sequence, removed_blocks


def deduplicate_string_lines(
    text: str,
    min_block_size: int = 5,
    key: Optional[Callable] = hash,
    *,
    return_final_text: bool = True,
    return_removed_blocks: bool = True
) -> Tuple[str, List[Dict]]:
    """
    Example function demonstrating how to use the generic BlockDeduplicator
    on a string by splitting it into lines. Returns:
       - final_text: deduplicated text (lines joined by newline)
       - removed_blocks: metadata about removed blocks

    :param text:             The input string.
    :param min_block_size:   The size for initial block match.
    :param key:              Optional key function mapping each line to a comparable/hashable value.
                             If None, lines are hashed as-is.
    """
    lines = text.splitlines()
    deduplicator = BlockDeduplicator(min_block_size=min_block_size, key=key)
    deduped_lines, removed_blocks = deduplicator.deduplicate_sequence(lines)
    if return_final_text:
        final_text = "\n".join(deduped_lines)
        if return_removed_blocks:
            return final_text, removed_blocks
        else:
            return final_text
    elif return_removed_blocks:
        return final_text, removed_blocks
