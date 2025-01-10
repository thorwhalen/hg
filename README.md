# hg

Homogenous Groups, Duplication detection, Frequent Itemsets etc.

To install:	```pip install hg```

# Examples

```python
>>> from hg import deduplicate_string_lines
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
```
