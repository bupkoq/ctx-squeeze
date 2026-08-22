from ctx_squeeze.scoring import score_segments, select_by_score
from ctx_squeeze.segments import split_segments


def _segments(*texts):
    return split_segments("\n\n".join(texts))


def test_score_segments_of_empty_list_is_empty():
    assert score_segments([]) == []


def test_score_segments_returns_one_score_per_segment():
    segments = _segments("first paragraph", "second paragraph", "third paragraph")
    assert len(score_segments(segments)) == len(segments)


def test_score_segments_gives_zero_to_a_segment_with_no_words():
    segments = _segments("12345 !!! ---")
    assert score_segments(segments) == [0.0]


def test_score_segments_rewards_a_distinctive_word_over_a_shared_one():
    segments = _segments(
        "shared shared unique unique unique unique",
        "shared shared shared shared",
    )
    scores = score_segments(segments)
    assert scores[0] > scores[1]


def test_select_by_score_returns_empty_for_zero_budget():
    segments = _segments("some text here")
    assert select_by_score(segments, 0) == []


def test_select_by_score_returns_empty_for_negative_budget():
    segments = _segments("some text here")
    assert select_by_score(segments, -10) == []


def test_select_by_score_returns_empty_for_no_segments():
    assert select_by_score([], 1000) == []


def test_select_by_score_keeps_everything_when_budget_covers_total():
    segments = _segments("first paragraph", "second paragraph", "third paragraph")
    total = sum(segment.tokens for segment in segments)
    result = select_by_score(segments, total)
    assert [s.index for s in result] == [0, 1, 2]


def test_select_by_score_never_exceeds_the_budget():
    segments = _segments(
        "first paragraph about the release",
        "second paragraph about the migration",
        "third paragraph about the rollout",
    )
    total = sum(segment.tokens for segment in segments)
    budget = total - 1
    result = select_by_score(segments, budget)
    assert sum(s.tokens for s in result) <= budget


def test_select_by_score_output_is_in_original_document_order():
    segments = _segments(
        "alpha alpha alpha alpha alpha",
        "beta beta beta beta beta",
        "gamma gamma gamma gamma gamma",
    )
    total = sum(segment.tokens for segment in segments)
    result = select_by_score(segments, total)
    assert [s.index for s in result] == sorted(s.index for s in result)


def test_select_by_score_drops_the_least_valuable_segment_when_tight_on_budget():
    segments = _segments(
        "juniper juniper juniper juniper juniper",
        "common common common common common",
        "common common common common feather",
    )
    scores = score_segments(segments)
    weakest = min(range(len(segments)), key=lambda i: scores[i] / segments[i].tokens)
    budget = sum(s.tokens for s in segments) - segments[weakest].tokens
    result = select_by_score(segments, budget)
    assert weakest not in [s.index for s in result]


def test_select_by_score_skips_an_oversized_segment_but_keeps_a_smaller_one():
    padding = " ".join(["padding"] * 500)
    segments = _segments("short useful note about the fix", padding)
    budget = segments[0].tokens + 5
    result = select_by_score(segments, budget)
    assert [s.index for s in result] == [0]
