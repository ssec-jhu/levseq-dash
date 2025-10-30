import pytest

from levseq_dash.app.sequence_aligner.bio_python_pairwise_aligner import (
    get_alignments,
    inject_aligner,
    parallel_function_align_target,
    sanitize_protein_sequence,
    setup_aligner_blastp,
)


@pytest.mark.parametrize(
    "index, identities, mismatches, gaps",
    [
        (0, 195, 0, 0),
        (1, 193, 2, 0),
        (2, 194, 0, 1),
        (3, 194, 0, 1),
        (4, 190, 0, 5),
        (5, 157, 0, 38),
    ],
)
def test_get_alignments(index, identities, mismatches, gaps, target_sequences):
    query_sequence = target_sequences["seq_base"]
    results, base_score, _ = get_alignments(query_sequence, 0, target_sequences)
    assert results[index]["identities"] == identities
    assert results[index]["mismatches"] == mismatches
    assert results[index]["gaps"] == gaps


def test_get_alignments_short():
    results, base_score, _ = get_alignments("AACTT", 0, {"target": "AATT"})
    assert base_score == 27
    assert results[0]["identities"] == 4
    assert results[0]["mismatches"] == 0
    assert results[0]["gaps"] == 1


def test_get_alignments_empty_query():
    with pytest.raises(Exception):
        get_alignments("", 0, {"target": "AATT"})


def test_get_alignments_empty_query_2():
    with pytest.raises(Exception):
        get_alignments(None, 0, {"target": "AATT"})


def test_get_alignments_zero_base(mock_base_score):
    # mocking base_score to 0 here
    with pytest.raises(Exception):
        get_alignments("AACTT", 0, {"target": "AATT"})


def test_get_alignments_empty_targets():
    with pytest.raises(Exception):
        get_alignments("AACTT", 0, {})


def test_get_alignments_empty_everything():
    with pytest.raises(Exception):
        get_alignments("", 0, {})


def test_incorrect_aligner_setup(mock_pairwise_aligner):
    with pytest.raises(Exception):
        setup_aligner_blastp()


def test_incorrect_mock_substitution_matrix(mock_substitution_matrix):
    with pytest.raises(Exception):
        setup_aligner_blastp()


@pytest.mark.parametrize(
    "seq",
    [
        "AACTT",  # valid input
        "AA CTT\n\t",  # whitespaces
    ],
)
def test_sanitize_protein_sequence(seq):
    """Test sanitize_protein_sequence with valid input."""
    result = sanitize_protein_sequence(seq)
    assert result == "AACTT"


@pytest.mark.parametrize(
    "seq",
    [
        123,  # Sequence must be a non-empty string
        "",
        None,
    ],
)
def test_sanitize_protein_sequence_exception(seq):
    """Test sanitize_protein_sequence with non-string input."""
    with pytest.raises(ValueError):
        sanitize_protein_sequence(seq)


def test_get_alignments_with_threshold():
    """Test get_alignments with a threshold to filter results."""
    results, base_score, warning_info = get_alignments("AACTT", 0.8, {"target1": "AACTT", "target2": "GGGG"})
    # Only the exact match should pass the threshold
    assert len(results) >= 1
    assert results[0]["norm_score"] >= 0.8


def test_inject_aligner():
    """Test inject_aligner function."""
    inject_aligner()
    from levseq_dash.app.sequence_aligner import bio_python_pairwise_aligner

    aligner = bio_python_pairwise_aligner.aligner
    assert aligner is not None
    assert hasattr(aligner, "align")


def test_parallel_function_align_target():
    inject_aligner()

    # Test with valid sequences
    results = parallel_function_align_target("test_id", "AACTT", "AACTT", 27, 0.5)
    assert len(results) >= 1
    assert results[0]["experiment_id"] == "test_id"
    assert results[0]["norm_score"] >= 0.5


def test_get_alignments_with_problematic_sequence():
    targets = {
        "good": "AACTT",
        "with_numbers": "AAC123TT",  # This might cause issues
    }

    results, base_score, warning_info = get_alignments("AACTT", 0, targets)

    assert "errors" in warning_info
