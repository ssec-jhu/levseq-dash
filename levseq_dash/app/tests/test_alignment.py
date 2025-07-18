import time

import pytest

from levseq_dash.app import global_strings as gs
from levseq_dash.app.sequence_aligner import bio_python_pairwise_aligner
from levseq_dash.app.utils import u_seq_alignment


def test_basic_functionality(alignment_string):
    hot_indices = ["3", "5", "7"]
    cold_indices = ["10", "20", "30"]

    _, mismatches = u_seq_alignment.parse_alignment_pipes(alignment_string, hot_indices, cold_indices)
    assert mismatches == ["59", "73", "93", "94", "145", "149"]


def test_hot_and_cold_both(alignment_string):
    hot_indices = [10, 15, 30]
    cold_indices = [30, 50]

    parsed_alignment, _ = u_seq_alignment.parse_alignment_pipes(alignment_string, hot_indices, cold_indices)

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
        u_seq_alignment.parse_alignment_pipes(alignment_string, hot_indices, cold_indices)


def test_edge_cases(alignment_string, list_of_residues_edge):
    hot_indices = list_of_residues_edge[0]
    cold_indices = list_of_residues_edge[1]
    parsed_alignment, _ = u_seq_alignment.parse_alignment_pipes(alignment_string, hot_indices, cold_indices)

    # 201+201 is the length of the first two lines plus \n
    # the index listed in the hot indices must be marked with H
    assert gs.hot == parsed_alignment[201 + 201 + 1 + hot_indices[0]]


def test_edge_cases_2(alignment_string, list_of_residues_edge):
    hot_indices = list_of_residues_edge[0]
    cold_indices = list_of_residues_edge[1]
    parsed_alignment, _ = u_seq_alignment.parse_alignment_pipes(alignment_string, hot_indices, cold_indices)
    # 201+201 is the length of the first two lines plus \n
    # the index listed in the hot indices must be marked with H
    assert gs.hot == parsed_alignment[201 + 201 + 1 + hot_indices[1]]


def test_edge_cases_3(alignment_string, list_of_residues_edge):
    hot_indices = list_of_residues_edge[0]
    cold_indices = list_of_residues_edge[1]
    parsed_alignment, _ = u_seq_alignment.parse_alignment_pipes(alignment_string, hot_indices, cold_indices)
    # 201+201 is the length of the first two lines plus \n
    # the index listed in the hot indices must be marked with H
    s = parsed_alignment[201 + 201 + 1 + cold_indices[0]]
    assert gs.cold == parsed_alignment[201 + 201 + 1 + cold_indices[0]]


@pytest.mark.parametrize(
    "index,property, value",
    [
        (0, "norm_score", 1.0),
        (0, "mismatches", 0),
        (0, "gaps", 0.0),
        (0, "plates_count", 4),
    ],
)
def test_gather_seq_alignment_data_per_smiles(seq_align_per_smiles_data, index, property, value):
    result = []
    result = u_seq_alignment.gather_seq_alignment_data_per_smiles(
        df_hot_cold_residue_per_smiles=seq_align_per_smiles_data[0],
        seq_match_data=seq_align_per_smiles_data[1],
        exp_meta_data=seq_align_per_smiles_data[2],
        seq_match_row_data=result,
    )
    # verify some of the properties and make sure they were added properly
    assert len(result) == 1
    assert result[index][property] == value


@pytest.mark.parametrize(
    "index,property, value",
    [
        (0, "alignment_score", 1040.0),
        (0, "norm_score", 1.0),
        (0, "mismatches", 0),
        (0, "gaps", 0.0),
        (0, "plates_count", 4),
        (1, "alignment_score", 1040.0),
        (1, "norm_score", 1.0),
        (1, "mismatches", 0),
        (1, "gaps", 0.0),
        (1, "plates_count", 4),
    ],
)
def test_gather_seq_alignment_data_per_smiles_2(seq_align_per_smiles_data, index, property, value):
    # run the data twice and make sure there is two sets for testing purposes
    result = []
    result = u_seq_alignment.gather_seq_alignment_data_per_smiles(
        df_hot_cold_residue_per_smiles=seq_align_per_smiles_data[0],
        seq_match_data=seq_align_per_smiles_data[1],
        exp_meta_data=seq_align_per_smiles_data[2],
        seq_match_row_data=result,
    )
    result = u_seq_alignment.gather_seq_alignment_data_per_smiles(
        df_hot_cold_residue_per_smiles=seq_align_per_smiles_data[0],
        seq_match_data=seq_align_per_smiles_data[1],
        exp_meta_data=seq_align_per_smiles_data[2],
        seq_match_row_data=result,
    )

    # verify some of the properties and make sure they were added properly
    assert len(result) == 2
    assert result[index][property] == value


@pytest.mark.parametrize(
    "residue_list,count",
    [
        (["59"], 10),
        (["59", "70"], 20),
        ([], 0),
        (["33"], 4),
        (["123"], 14),
        (["33", "123"], 18),
        (["170"], 4),
        (["42", "90", "173", "123"], 58),
    ],
)
def test_search_for_variants_in_experiment_data(residue_list, count, experiment_ep_pcr):
    df = experiment_ep_pcr.data_df
    result_df = u_seq_alignment.lookup_residues_in_experiment_data(df, residue_list)
    assert result_df.shape[0] == count


@pytest.mark.parametrize(
    "residue_list,count",
    [
        (["59"], 10),
        (["59", "70"], 20),
        ([], 0),
        (["33"], 4),
        (["123"], 14),
        (["33", "123"], 18),
        (["170"], 4),
        (["42", "90", "173", "123"], 58),
    ],
)
def test_search_and_gather_variant_info_for_matching_experiment(residue_list, count, experiment_ep_pcr, seq_align_data):
    exp_results_row_data = list(dict())
    exp_results_row_data = u_seq_alignment.search_and_gather_variant_info_for_matching_experiment(
        experiment_ep_pcr,
        1,  # this can be anything for this test
        residue_list,
        seq_align_data,
        exp_results_row_data,
    )
    assert len(exp_results_row_data) == count
    if count != 0:
        assert len(exp_results_row_data[0]) == 28


def test_target_sequence_test_data(dbmanager_read_all_dedb_data):
    # experiment 35's sequence
    query = (
        "MKGYFGPYGGQYVPEILMGALEELEAAYEGIMKDESFWKEFNDLLRDYAGRPTPLYFARRLSEKYGARVYLKREDLLH"
        "TGAHKINNAIGQVLLAKLMGKTRIIAETGAGQHGVATATAAALFGMECVIYMGEEDTIRQKLNVERMKLLGAKVVPVK"
        "SGSRTLKDAIDEALRDWITNLQTTYYVFGSVVGPHPYPIIVRNFQKVIGEETKKQIPEKEGRLPDYIVACVSGGSNAA"
        "GIFYPFIDSGVKLIGVEAGGEGLETGKHAASLLKGKIGYLHGSKTFVLQDDWGQVQVSHSVSAGLDYSGVGPEHAYWR"
        "ETGKVLYDAVTDEEALDAFIELSRLEGIIPALESSHALAYLKKINIKGKVVVVNLSGRGDKDLESVLNHPYVRERIR"
    )

    all_lab_sequences = dbmanager_read_all_dedb_data.get_lab_sequences()
    assert len(all_lab_sequences) == 36
    # get the alignment and the base score
    start_time = time.time()
    lab_seq_match_data, base_score = bio_python_pairwise_aligner.get_alignments(
        query_sequence=query, threshold=float(0.8), targets=all_lab_sequences
    )
    end_time = time.time()
    # verify the results
    assert len(lab_seq_match_data) == 3
    assert base_score == 2011.0
    # test the experiment ids
    assert lab_seq_match_data[0].get("experiment_id") == 2
    assert lab_seq_match_data[1].get("experiment_id") == 11
    assert lab_seq_match_data[2].get("experiment_id") == 35

    assert lab_seq_match_data[0].get("alignment_score") == 2011.0
    assert lab_seq_match_data[1].get("alignment_score") == 1953.0
    assert lab_seq_match_data[2].get("alignment_score") == 2011.0

    assert lab_seq_match_data[0].get("norm_score") == 1.0
    assert lab_seq_match_data[1].get("norm_score") == 0.9712
    assert lab_seq_match_data[2].get("norm_score") == 1.0

    assert lab_seq_match_data[0].get("mismatches") == 0
    assert lab_seq_match_data[1].get("mismatches") == 10
    assert lab_seq_match_data[2].get("mismatches") == 0

    assert lab_seq_match_data[0].get("gaps") == 0.0
    assert lab_seq_match_data[1].get("gaps") == 0.0
    assert lab_seq_match_data[2].get("gaps") == 0.0

    # verify the sequence alignment
    assert lab_seq_match_data[0].get("sequence_alignment") is not None
    assert lab_seq_match_data[1].get("sequence_alignment") is not None
    assert lab_seq_match_data[2].get("sequence_alignment") is not None

    print(f"***** Execution time for get_alignments: {end_time - start_time} seconds")
