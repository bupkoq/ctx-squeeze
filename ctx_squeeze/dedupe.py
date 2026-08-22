"""Drop near-duplicate segments from a document.

Agent transcripts repeat themselves: the same file gets read three times, the
same traceback comes back after each retry, a tool result gets echoed into the
next prompt verbatim except for a timestamp. Word shingles plus Jaccard
similarity catch those repeats even when a few tokens differ, without needing
to compare whole strings for exact equality.
"""

__all__ = ["shingles", "jaccard", "find_near_duplicates", "dedupe_segments"]


def shingles(text, size=5):
    """Return the set of ``size``-word shingles in ``text``.

    A shingle is a tuple of ``size`` consecutive words. Text shorter than
    ``size`` words becomes a single shingle covering everything it has, so
    two short segments can still be compared instead of always looking
    unrelated.
    """
    words = text.split()
    if not words:
        return frozenset()
    if len(words) < size:
        return frozenset([tuple(words)])
    return frozenset(
        tuple(words[i : i + size]) for i in range(len(words) - size + 1)
    )


def jaccard(a, b):
    """Return the Jaccard similarity of two shingle sets, in ``[0.0, 1.0]``.

    Two empty sets are treated as identical (similarity 1.0); one empty and
    one non-empty set have nothing in common (similarity 0.0).
    """
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union


def find_near_duplicates(segments, shingle_size=5, threshold=0.8):
    """Return the indices of segments that duplicate an earlier segment.

    Each segment is compared against every segment kept so far (not against
    other duplicates), so a run of five near-identical segments reports the
    last four as duplicates of the first rather than of each other.
    """
    shingle_sets = [shingles(segment.text, shingle_size) for segment in segments]
    kept_indices = []
    duplicate_indices = []
    for i, current in enumerate(shingle_sets):
        is_duplicate = False
        for j in kept_indices:
            if jaccard(current, shingle_sets[j]) >= threshold:
                is_duplicate = True
                break
        if is_duplicate:
            duplicate_indices.append(i)
        else:
            kept_indices.append(i)
    return duplicate_indices


def dedupe_segments(segments, shingle_size=5, threshold=0.8):
    """Remove near-duplicate segments, keeping the first occurrence of each.

    Returns ``(kept_segments, dropped_count)``. Segment order is preserved.
    """
    duplicate_indices = set(
        find_near_duplicates(segments, shingle_size=shingle_size, threshold=threshold)
    )
    kept = [
        segment for i, segment in enumerate(segments) if i not in duplicate_indices
    ]
    return kept, len(duplicate_indices)
