import pytest

from levseq_dash.app.sequence_aligner.bio_python_pairwise_aligner import get_alignments


@pytest.mark.parametrize(
    "index, identities, mismatches, gaps",
    [
        (0, 195, 0, 0),
        (1, 194, 0, 1),
        (2, 194, 0, 1),
        (3, 193, 2, 0),
        (4, 190, 0, 5),
        (5, 95, 0, 100),
    ],
)
def test_get_alignments(index, identities, mismatches, gaps, target_sequences):
    query_sequence = target_sequences["seq_base"]
    results, base_score = get_alignments(query_sequence, 0, target_sequences)
    assert results[index]["identities"] == identities
    assert results[index]["mismatches"] == mismatches
    assert results[index]["gaps"] == gaps


def test_get_alignments_short():
    results, base_score = get_alignments("AACTT", 0, {"target": "AATT"})
    assert base_score == 27
    assert results[0]["identities"] == 4
    assert results[0]["mismatches"] == 0
    assert results[0]["gaps"] == 1


def test_get_alignments_empty_query():
    with pytest.raises(Exception):
        get_alignments("", 0, {"target": "AATT"})


def test_get_alignments_empty_targets():
    with pytest.raises(Exception):
        get_alignments("AACTT", 0, {})


def test_get_alignments_empty_everything():
    with pytest.raises(Exception):
        get_alignments("", 0, {})
