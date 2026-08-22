"""Score segments by keyword density and pick which ones survive a budget.

The scorer is a plain TF-IDF: a word that shows up often within one segment
but rarely across the rest of the document counts for more than a word every
segment shares (heading filler like "the" or "and" ends up worth almost
nothing on its own). There is no external corpus and no stopword list -
importance is judged relative to the other segments in the same document,
which is all a compactor has to work with anyway.
"""

import math
import re
from collections import Counter

__all__ = ["score_segments", "select_by_score"]

_WORD = re.compile(r"[A-Za-z]+")


def _words(text):
    return [word.lower() for word in _WORD.findall(text)]


def score_segments(segments):
    """Return one importance score per segment, aligned by position.

    Higher means more distinctive. A segment with no alphabetic words (a
    fence of pure punctuation or digits, say) scores ``0.0``.
    """
    word_lists = [_words(segment.text) for segment in segments]
    segment_count = len(segments)
    document_frequency = Counter()
    for words in word_lists:
        document_frequency.update(set(words))

    scores = []
    for words in word_lists:
        if not words:
            scores.append(0.0)
            continue
        term_frequency = Counter(words)
        total = 0.0
        for word, count in term_frequency.items():
            tf = count / len(words)
            idf = math.log((segment_count + 1) / (document_frequency[word] + 1)) + 1.0
            total += tf * idf
        scores.append(total)
    return scores


def select_by_score(segments, budget):
    """Greedily keep the highest-density segments that fit inside ``budget``.

    Segments are atomic: one that does not fit on its own is skipped rather
    than truncated, so everything this returns is used unmodified. Candidates
    are ranked by score per token so a short, distinctive segment can win out
    over a long, generic one; the result is re-sorted back into document
    order.
    """
    if budget <= 0 or not segments:
        return []

    scores = score_segments(segments)
    by_density = sorted(
        range(len(segments)),
        key=lambda i: scores[i] / max(segments[i].tokens, 1),
        reverse=True,
    )

    selected_indices = []
    remaining = budget
    for i in by_density:
        tokens = segments[i].tokens
        if tokens <= remaining:
            selected_indices.append(i)
            remaining -= tokens

    selected_indices.sort()
    return [segments[i] for i in selected_indices]
