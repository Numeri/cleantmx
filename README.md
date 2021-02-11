# cleantmx
*A small Python library to build NLP data cleaning pipelines*

This library is meant to be a lightweight but powerful tool to help create data cleaning pipelines for NLP. It's designed to be flexible, and you can easily extend it with your own code.

It comes with several built in filters of different types: most operate only on an individual segment, but some can modify source/target text using information from both (to remove source/target pairs that are identical, or with mismatched segment lengths, for example).

See `examples/process_tmx.py` for an example of reading in a `.tmx` file of English-Swedish pairs, cleaning it, then saving two segment-aligned text files.
