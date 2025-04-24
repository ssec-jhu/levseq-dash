import pytest

from levseq_dash.app.sequence_aligner.bio_python_pairwise_aligner import setup_aligner_blastp


@pytest.fixture
def mock_pairwise_aligner(mocker):
    """
    This fixture mocks the PairwiseAligner function to get called with default values
    instead of the score setup used
    """
    from Bio.Align import PairwiseAligner

    mock = mocker.patch("levseq_dash.app.sequence_aligner.bio_python_pairwise_aligner.PairwiseAligner")
    mock.return_value = PairwiseAligner()  # default scoring
    return mock


@pytest.fixture
def mock_substitution_matrix(mocker):
    """
    This fixture mocks the PairwiseAligner function to get called with default values
    instead of the score setup used
    """
    from Bio.Align import substitution_matrices

    replace_with = substitution_matrices.load("BLASTP")
    # now mock the function
    mock = mocker.patch("levseq_dash.app.sequence_aligner.bio_python_pairwise_aligner.substitution_matrices.load")
    mock.return_value = replace_with
    return mock


@pytest.fixture
def mock_base_score(mocker):
    """
    Mocking the base score 0 option as I can't find any case that will make the base
    score 0 to see what happens in the code
    """
    # setup a random aligner and setup it's score to be 0
    aligner = setup_aligner_blastp()
    alignments = aligner.align("A", "AB")
    alignments[0].score = 0
    # now mock the function
    # align is a function within PairwiseAligner hence the patch below
    mock = mocker.patch("levseq_dash.app.sequence_aligner.bio_python_pairwise_aligner.PairwiseAligner.align")
    mock.return_value = alignments
    return mock


@pytest.fixture(scope="session")
def target_sequences():
    return {
        "seq_base": "MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAGGWAASNEHLIYYGSNPDTGAPIKEYLERVRARIGAWVL"
        "DTTCRDYNREWLDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAGIYPITATIKPFLAKKGGSPEDIEGMYNAWLKSVVLQVAIWSHPYTKENDR",
        "seq_removed first letter": "TPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAGGWAASNEHLIYYGSNPDTGAPIK"
        "EYLERVRARIGAWVLDTTCRDYNREWLDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAGIYPITATIKPFLAKKGGSPE"
        "DIEGMYNAWLKSVVLQVAIWSHPYTKENDR",
        "seq_removed last letter": "MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAGGWAASNEHLIYYGSNPDTGAPIK"
        "EYLERVRARIGAWVLDTTCRDYNREWLDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAGIYPITATIKPFLAKKGGSPEDIEGMYNAWLKSVVLQVAIWSHPYTKEND",
        "seq_switched_two_letters": "MAASDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAGGWAASNEHLIYYGSNPDTGAPI"
        "KEYLERVRARIGAWVLDTTCRDYNREWLDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAGIYPITATIKPFLAKKGGSP"
        "EDIEGMYNAWLKSVVLQVAIWSHPYTKENDR",
        "seq_removed_all_w": "MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAGGAASNEHLIYYGSNPDTGAPIKEYLERV"
        "RARIGAVLDTTCRDYNRELDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAGIYPITATIKPFLAKKGGSPEDIEGMYNALKSVVLQVAISHPYTKENDR",
        "seq_half_seq": "MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAGGWAASNEHLIYYGSNPDTGAPIKEYLERVR"
        "ARIGA",
        "seq_portion": "MTPSDISGYDYGRVEKSPITDLEKAADVLKDQVDEILDLAGGWAASNEHLIYYGSNPDTGAPIKEYLERVRARIGAWVLDTTCRDYNREWL"
        "DYQYEVGLRHHYLIAGIYPITATIKPFLAKKGGSPEDIEGMYNAWLKSVVLQVAIWSHPYTKENDR",
    }
