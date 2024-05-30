from util.ascii import AsciiHelper  # Noqa

def test_get_progress_bar():
    # Test case for a normalized score of 0.6
    normalized_score = 0.6
    expected_output = f"[████████████░░░░░░░░] 60%"

    assert AsciiHelper.get_progress_bar(normalized_score) == expected_output
