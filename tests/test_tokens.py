from ctx_squeeze.tokens import estimate_tokens, fits_budget, truncate_to_tokens


def test_empty_string_is_zero_tokens():
    assert estimate_tokens("") == 0


def test_horizontal_whitespace_only_is_zero_tokens():
    assert estimate_tokens("   \t  \t ") == 0


def test_short_word_costs_one_token():
    # 2 chars / 4 chars-per-token floors to 0.5, but a word never rounds to 0.
    assert estimate_tokens("hi") == 1


def test_word_length_scales_with_chars_per_word_token():
    # 5 chars / 4 -> 1.25 -> ceil 2
    assert estimate_tokens("hello") == 2


def test_digit_run_uses_its_own_ratio():
    # 5 chars / 3 -> 1.667 -> ceil 2
    assert estimate_tokens("12345") == 2


def test_cjk_characters_cost_one_token_each():
    assert estimate_tokens("日本語") == 3


def test_newlines_cost_half_a_token_each():
    # two newlines: 2 * 0.5 = 1.0 -> ceil 1
    assert estimate_tokens("\n\n") == 1


def test_longer_text_costs_more_tokens():
    short = "one short sentence"
    long_text = short * 20
    assert estimate_tokens(long_text) > estimate_tokens(short)


def test_fits_budget_true_when_under():
    assert fits_budget("hello world", 100) is True


def test_fits_budget_false_when_over():
    assert fits_budget("hello world " * 50, 3) is False


def test_truncate_returns_original_when_it_fits():
    text = "short text"
    assert truncate_to_tokens(text, 100) == text


def test_truncate_zero_budget_is_empty():
    assert truncate_to_tokens("anything at all", 0) == ""


def test_truncate_shrinks_to_fit_budget():
    text = "word " * 200
    budget = 10
    result = truncate_to_tokens(text, budget)
    assert estimate_tokens(result) <= budget
    assert result != ""


def test_truncate_counts_suffix_against_budget():
    text = "word " * 200
    budget = 10
    suffix = " [more]"
    result = truncate_to_tokens(text, budget, suffix=suffix)
    assert estimate_tokens(result) <= budget
    assert result.endswith(suffix)


def test_truncate_returns_empty_when_suffix_alone_exceeds_budget():
    result = truncate_to_tokens("word " * 200, 1, suffix="way more than one token long")
    assert result == ""
