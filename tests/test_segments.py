from ctx_squeeze.segments import Segment, join_segments, split_segments


def test_empty_input_has_no_segments():
    assert split_segments("") == []


def test_whitespace_only_input_has_no_segments():
    assert split_segments("   \n  \n\t\n") == []


def test_blank_line_splits_paragraphs():
    text = "para one line1\npara one line2\n\npara two\n"
    segments = split_segments(text)
    assert [s.text for s in segments] == [
        "para one line1\npara one line2",
        "para two",
    ]
    assert [s.kind for s in segments] == ["text", "text"]
    assert [s.index for s in segments] == [0, 1]


def test_paragraph_line_numbers_are_one_indexed():
    text = "first\n\nsecond\n"
    segments = split_segments(text)
    assert segments[0].start_line == 1
    assert segments[0].end_line == 1
    assert segments[1].start_line == 3
    assert segments[1].end_line == 3


def test_fenced_code_block_survives_as_one_segment():
    text = "before\n\n```python\nprint(1)\n\nprint(2)\n```\n\nafter\n"
    segments = split_segments(text)
    assert [s.kind for s in segments] == ["text", "code", "text"]
    code = segments[1]
    assert code.text == "```python\nprint(1)\n\nprint(2)\n```"
    assert code.is_code is True
    assert code.start_line == 3
    assert code.end_line == 7


def test_tilde_fence_is_also_recognized():
    text = "~~~\ncode\n~~~\n"
    segments = split_segments(text)
    assert len(segments) == 1
    assert segments[0].kind == "code"


def test_unterminated_fence_runs_to_end_of_input():
    text = "```\ncode line\n"
    segments = split_segments(text)
    assert len(segments) == 1
    assert segments[0].kind == "code"
    assert segments[0].text == "```\ncode line"
    assert segments[0].end_line == 3


def test_segment_carries_a_token_estimate():
    segments = split_segments("hello world")
    assert segments[0].tokens > 0


def test_join_segments_uses_separator():
    segments = split_segments("first\n\nsecond\n")
    assert join_segments(segments) == "first\n\nsecond"
    assert join_segments(segments, separator=" | ") == "first | second"


def test_segment_equality_compares_fields():
    a = Segment("text", 1, 1, kind="text", index=0)
    b = Segment("text", 1, 1, kind="text", index=0)
    c = Segment("text", 1, 1, kind="text", index=1)
    assert a == b
    assert a != c
    assert a != "not a segment"
