"""Test duplicates.py"""

from hg.duplicates import (
    BlockDeduplicator,
    RemovedBlock,
    deduplicate_sequence,
    deduplicate_string_lines,
)


def test_blockdeduplicator_on_integers():
    dedup = BlockDeduplicator(min_block_size=2)
    seq = [1, 2, 3, 1, 2, 3, 4, 5]
    deduped, removed = dedup.deduplicate_sequence(seq)

    # The size-2 block [1, 2] repeats, and extends to the size-3 block [1, 2, 3]
    # (the largest repeated run). The second occurrence is removed.
    # Original: 1,2,3,1,2,3,4,5  ->  1,2,3,4,5
    assert deduped == [1, 2, 3, 4, 5], f"expected [1, 2, 3, 4, 5]. Got {deduped}"

    assert len(removed) == 1
    block = removed[0]
    assert isinstance(block, RemovedBlock)
    assert block.length == 3
    assert block.block_items == [1, 2, 3]
    assert block.removed_start == 3


def test_min_block_size_extends_to_largest_run():
    # min_block_size=2 finds the size-2 seed [1,2] but greedily extends to the
    # full repeated run [1,2,3]; it does NOT behave like min_block_size=3 by
    # accident -- it is the extension step that grows the seed.
    dedup = BlockDeduplicator(min_block_size=2)
    deduped, removed = dedup.deduplicate_sequence([1, 2, 3, 1, 2, 3, 4, 5])
    assert removed[0].length == 3


def test_deduplicate_sequence_facade():
    deduped, removed = deduplicate_sequence([10, 20, 10, 20, 30], min_block_size=2)
    assert deduped == [10, 20, 30]
    assert removed == [RemovedBlock(removed_start=2, length=2, block_items=[10, 20])]


def test_deduplicate_sequence_custom_key():
    # Items differ but their keys collide -> treated as duplicates.
    seq = ["Ab", "cD", "aB", "Cd", "x"]
    deduped, removed = deduplicate_sequence(seq, min_block_size=2, key=str.lower)
    assert deduped == ["Ab", "cD", "x"]
    assert removed[0].length == 2
    # block_items come from the first (retained) occurrence
    assert removed[0].block_items == ["Ab", "cD"]


def test_deduplicate_string_lines():
    text = "LineA\nLineB\nLineC\nLineA\nLineB\nLineC\nLineD\n"
    # "LineA\nLineB\nLineC" occurs twice; the second occurrence is removed.
    final_text, removed_blocks = deduplicate_string_lines(text, min_block_size=3)

    assert final_text == "LineA\nLineB\nLineC\nLineD"
    assert len(removed_blocks) == 1
    assert removed_blocks[0].length == 3
    assert removed_blocks[0].block_items == ["LineA", "LineB", "LineC"]


def test_deduplicate_string_lines_return_flags():
    text = "A\nB\nC\nA\nB\nC\nD"

    # default: both
    final_text, removed = deduplicate_string_lines(text, min_block_size=3)
    assert final_text == "A\nB\nC\nD"
    assert removed[0].block_items == ["A", "B", "C"]

    # only the text
    assert (
        deduplicate_string_lines(text, min_block_size=3, return_removed_blocks=False)
        == "A\nB\nC\nD"
    )

    # only the removed blocks
    only_removed = deduplicate_string_lines(
        text, min_block_size=3, return_final_text=False
    )
    assert only_removed == [
        RemovedBlock(removed_start=3, length=3, block_items=["A", "B", "C"])
    ]

    # neither -> None
    assert (
        deduplicate_string_lines(
            text,
            min_block_size=3,
            return_final_text=False,
            return_removed_blocks=False,
        )
        is None
    )


def test_no_duplicates_is_a_noop():
    deduped, removed = deduplicate_sequence([1, 2, 3, 4, 5], min_block_size=2)
    assert deduped == [1, 2, 3, 4, 5]
    assert removed == []
