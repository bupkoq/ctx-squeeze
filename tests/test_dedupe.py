from ctx_squeeze.dedupe import dedupe_segments, find_near_duplicates, jaccard, shingles
from ctx_squeeze.segments import split_segments


def test_shingles_of_empty_text_is_empty_set():
    assert shingles("", size=5) == frozenset()


def test_short_text_becomes_one_shingle():
    result = shingles("one two three", size=5)
    assert result == frozenset([("one", "two", "three")])


def test_shingles_slide_over_words():
    result = shingles("a b c d e f", size=5)
    assert result == frozenset(
        [("a", "b", "c", "d", "e"), ("b", "c", "d", "e", "f")]
    )


def test_jaccard_of_identical_sets_is_one():
    a = shingles("the quick brown fox jumps", size=5)
    assert jaccard(a, a) == 1.0


def test_jaccard_of_disjoint_sets_is_zero():
    a = shingles("apples and oranges today", size=3)
    b = shingles("completely different words here", size=3)
    assert jaccard(a, b) == 0.0


def test_jaccard_of_two_empty_sets_is_one():
    assert jaccard(frozenset(), frozenset()) == 1.0


def test_jaccard_of_one_empty_set_is_zero():
    a = shingles("some words here", size=3)
    assert jaccard(a, frozenset()) == 0.0


def _segments(*texts):
    return split_segments("\n\n".join(texts))


def test_find_near_duplicates_flags_repeated_paragraph():
    segments = _segments(
        "The build failed after the runner image was bumped last night.",
        "Something unrelated about the release notes for this quarter.",
        "The build failed after the runner image was bumped last night.",
    )
    assert find_near_duplicates(segments, shingle_size=3, threshold=0.8) == [2]


def test_find_near_duplicates_ignores_distinct_segments():
    segments = _segments(
        "First unique paragraph about the database migration.",
        "Second unique paragraph about the frontend redesign.",
        "Third unique paragraph about the release schedule.",
    )
    assert find_near_duplicates(segments, shingle_size=3, threshold=0.8) == []


def test_find_near_duplicates_compares_against_first_of_a_run():
    text = "Reading the same file three times in a row for no good reason."
    segments = _segments(text, text, text)
    assert find_near_duplicates(segments, shingle_size=3, threshold=0.8) == [1, 2]


def test_dedupe_segments_drops_duplicates_and_reports_count():
    text = "Traceback repeated after each retry with no new information."
    segments = _segments(
        "Unrelated paragraph kept as context for the reader.",
        text,
        text,
    )
    kept, dropped = dedupe_segments(segments, shingle_size=3, threshold=0.8)
    assert dropped == 1
    assert [s.text for s in kept] == [
        "Unrelated paragraph kept as context for the reader.",
        text,
    ]


def test_dedupe_segments_keeps_everything_when_nothing_repeats():
    segments = _segments(
        "One paragraph about testing.",
        "A different paragraph about deployment.",
    )
    kept, dropped = dedupe_segments(segments, shingle_size=3, threshold=0.8)
    assert dropped == 0
    assert len(kept) == len(segments)


def test_dedupe_segments_preserves_order():
    segments = _segments(
        "Alpha paragraph with distinct content here.",
        "Bravo paragraph with other distinct content.",
        "Charlie paragraph wrapping things up nicely.",
    )
    kept, _ = dedupe_segments(segments, shingle_size=3, threshold=0.99)
    assert [s.index for s in kept] == [0, 1, 2]
