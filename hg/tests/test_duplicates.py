"""Test duplicates.py"""

from hg.duplicates import BlockDeduplicator, deduplicate_string_lines


def test_blockdeduplicator_on_integers():
    dedup = BlockDeduplicator(
        min_block_size=2
    )  # TODO: Behaves like min_block_size=3. Look into this.
    seq = [1, 2, 3, 1, 2, 3, 4, 5]
    deduped, removed = dedup.deduplicate_sequence(seq)

    # The repeated block of length 2 is [1, 2], repeated again before the 3
    # So the final deduplicated sequence should remove the second occurrence of that block.
    # Original: 1,2,3,1,2,3,4,5
    # Duplicates: [1,2,3] repeated
    # We keep the first [1,2,3], remove the second.
    # So final should be: 1,2,3,4,5
    assert deduped == [1, 2, 3, 4, 5], f"expected [1, 2, 3, 4, 5]. Got {deduped}"

    # Check removed blocks details
    assert len(removed) == 1
    assert removed[0]['length'] == 3
    assert removed[0]['block_items'] == [1, 2, 3]


def test_deduplicate_string_lines():
    text = """LineA
LineB
LineC
LineA
LineB
LineC
LineD
"""
    # Repetition: "LineA\nLineB\nLineC" occurs twice.
    # We expect the second occurrence to be removed, leaving only:
    # LineA\nLineB\nLineC\nLineD
    final_text, removed_blocks = deduplicate_string_lines(text, min_block_size=3)

    assert final_text == "LineA\nLineB\nLineC\nLineD"
    assert len(removed_blocks) == 1
    assert removed_blocks[0]['length'] == 3
    assert removed_blocks[0]['block_items'] == ["LineA", "LineB", "LineC"]
