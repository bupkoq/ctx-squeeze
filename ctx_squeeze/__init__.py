"""Context compaction for LLM prompts, using only the standard library.

This is still a partial build: the token estimator, segmenter, and dedupe
stage are in place, but the scoring, message-pruning, and compactor stages
the README describes are not written yet, so they are not imported here.
Add each to this list as it lands instead of importing modules that don't
exist.
"""

from .dedupe import dedupe_segments, find_near_duplicates, jaccard, shingles
from .segments import Segment, join_segments, split_segments
from .tokens import estimate_tokens, fits_budget, truncate_to_tokens

__version__ = "0.1.0"

__all__ = [
    "Segment",
    "__version__",
    "dedupe_segments",
    "estimate_tokens",
    "find_near_duplicates",
    "fits_budget",
    "jaccard",
    "join_segments",
    "shingles",
    "split_segments",
    "truncate_to_tokens",
]
