import pytest

from levseq_dash.app import utils_seq_alignment, global_strings as gs


def test_basic_functionality(alignment_string):
    hot_indices = ["3", "5", "7"]
    cold_indices = ["10", "20", "30"]

    _, mismatches = utils_seq_alignment.parse_alignment_pipes(alignment_string, hot_indices, cold_indices)
    assert mismatches == ["59", "73", "93", "94", "145", "149"]


def test_hot_and_cold_both(alignment_string):
    hot_indices = [10, 15, 30]
    cold_indices = [30, 50]

    parsed_alignment, _ = utils_seq_alignment.parse_alignment_pipes(alignment_string, hot_indices, cold_indices)

    assert gs.hot_cold in parsed_alignment
    assert parsed_alignment.count(gs.hot_cold) == 1


@pytest.mark.parametrize(
    "hot_indices, cold_indices",
    [
        ([0, 2], [4]),
        ([0, 2], [0, 4]),
        ([1, 2, 3], [0, 4]),
    ],
)
def test_out_of_range_index(alignment_string, hot_indices, cold_indices):
    with pytest.raises(IndexError):
        utils_seq_alignment.parse_alignment_pipes(alignment_string, hot_indices, cold_indices)


def test_edge_cases(alignment_string, list_of_residues_edge):
    hot_indices = list_of_residues_edge[0]
    cold_indices = list_of_residues_edge[1]
    parsed_alignment, _ = utils_seq_alignment.parse_alignment_pipes(alignment_string, hot_indices, cold_indices)

    # 201+201 is the length of the first two lines plus \n
    # the index listed in the hot indices must be marked with H
    assert gs.hot == parsed_alignment[201 + 201 + 1 + hot_indices[0]]


def test_edge_cases_2(alignment_string, list_of_residues_edge):
    hot_indices = list_of_residues_edge[0]
    cold_indices = list_of_residues_edge[1]
    parsed_alignment, _ = utils_seq_alignment.parse_alignment_pipes(alignment_string, hot_indices, cold_indices)
    # 201+201 is the length of the first two lines plus \n
    # the index listed in the hot indices must be marked with H
    assert gs.hot == parsed_alignment[201 + 201 + 1 + hot_indices[1]]


def test_edge_cases_3(alignment_string, list_of_residues_edge):
    hot_indices = list_of_residues_edge[0]
    cold_indices = list_of_residues_edge[1]
    parsed_alignment, _ = utils_seq_alignment.parse_alignment_pipes(alignment_string, hot_indices, cold_indices)
    # 201+201 is the length of the first two lines plus \n
    # the index listed in the hot indices must be marked with H
    s = parsed_alignment[201 + 201 + 1 + cold_indices[0]]
    assert gs.cold == parsed_alignment[201 + 201 + 1 + cold_indices[0]]
