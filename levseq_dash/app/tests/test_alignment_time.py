import time

import pytest

from levseq_dash.app.sequence_aligner import bio_python_pairwise_aligner


@pytest.mark.parametrize(
    "id, query_seq,n_lab_seq_match_data, score, experiment_ids, alignment_scores, norm_scores,mismatches, gaps",
    [
        (
            35,
            "MKGYFGPYGGQYVPEILMGALEELEAAYEGIMKDESFWKEFNDLLRDYAGRPTPLYFARRLSEKYGARVYLKREDLLHTGAHKINNAIGQVLLAKLMGKTRIIAE"
            "TGAGQHGVATATAAALFGMECVIYMGEEDTIRQKLNVERMKLLGAKVVPVK"
            "SGSRTLKDAIDEALRDWITNLQTTYYVFGSVVGPHPYPIIVRNFQKVIGEETKKQIPEKEGRLPDYIVACVSGGSNAA"
            "GIFYPFIDSGVKLIGVEAGGEGLETGKHAASLLKGKIGYLHGSKTFVLQDDWGQVQVSHSVSAGLDYSGVGPEHAYWR"
            "ETGKVLYDAVTDEEALDAFIELSRLEGIIPALESSHALAYLKKINIKGKVVVVNLSGRGDKDLESVLNHPYVRERIR",
            3,
            2011.0,
            [2, 11, 35],
            [2011.0, 1953.0, 2011.0],
            [1.0, 0.9712, 1.0],
            [0, 10, 0],
            [0, 0, 0],
        ),
        (
            5,
            "MTIKEMPQPKTFGELKNLPLLNTDKPVQALMKIADELGEIFKFEAPGRVTRYLSSQRLIKEACDESRFDKNLSQALKFARDFAGDGLVTSWTHEKNWKKAHNIL"
            "LPSFSQQAMKGYHAMMVDIAVQLVQKWERLNADEHIEVSEDMTRLTLDTIGLCGFNYRFNSFYRDQPHPFIISMVRALDEVMNKLQRANPDDPAYDENKRQFQ"
            "EDIKVMNDLVDKIIADRKARGEQSDDLLTQMLNGKDPETGETLDDGNIRYQIITFLGAGHEATSGLLSFALYFLVKNPHVLQKVAEEAARVLVDPVPSYKQVK"
            "QLKYVGMVLNEALRLWPTAPAFSLYAKEDTVLGGEYPLEKGDEVMVLIPQLHRDKTVWGDDVEEFRPERFENPSAIPQHAFKPFGNGQRASIGQQFALHEATL"
            "VLGMMLKHFDFEDHTNYELDIKETFTLKPKGFVVKAKSKKIPLGGIPSPSTEQSAKKVRKKAENAHNTPLLVLYGSNMGTAEGTARDLADIAMSKGFAPQVAT"
            "LDSHAGNLPREGAVLIVTASYNGHPPDNAKQFVDWLDQASADEVKGVRYSVFGCGDKNWATTYQKVPAFIDETLAAKGAENIADRGEADASDDFEGTYEEWREH"
            "MWSDVAAYFNLDIENSEDNKSTLSLQFVDSAADMPLAKMHGAFSTNVVASKELQQPGSARSTRHLEIELPKEASYQEGDHLGVIPRNYEGIVNRVTARFGLDASQ"
            "QIRLEAEEEKLAHLPLAKTVSVEELLQYVELQDPVTRTQLRAMAAKTVCPPHKVELEALLEKQAYKEQVLAKRLTMLELLEKYPACEMKFSEFIALLPSIRPRYY"
            "SISSSPRVDEKQASITVSVVSGEAWSGYGEYKGIASNYLAELQEGDTITCFISTPQSEFTLPKDPETPLIMVGPGTGVAPFRGFVQARKQLKEQGQSLGEAHLY"
            "FGCRSPHEDYLYQEELENAQSEGIITLHTAFSRMPNQPKTYVQHVMEQDGKKLIELLDQGAHFYICGDGSQMAPAVEATLMKSYADVHQVSEADARLWLQQLEE"
            "KGRYAKDVWAG",
            9,
            5451.0,
            [4, 5, 7],
            [5375.0, 5451.0, 5405.0],
            [0.9861, 1.0, 0.9916],
            [13, 0, 9],
            [0, 0, 0],
        ),
        # experiment 0
        (
            0,
            "MTIKEMPQPKTFGELKNLPLLNTDKPVQALMKIADELGEIFKFEAPGRVTRYLSSQRLIKEACDESRFDKNLSQALKFMRDFLGDGLATSWTHEKNWKKAHN"
            "ILLPSFSQQAMKGYHAMMVDIAVQLVQKWERLNADEHIEVSEDMTRLTLDTIGLCGFNYRFNSFYRDQPHPFIISMVRALDEVMNKLQRANPDDPAYDENKRQ"
            "FQEDIKVMNDLVDKIIADRKARGEQSDDLLTQMLNGKDPETGEPLDDGNIRYQIITFLMAGHEPTSGLLSFALYFLVKNPHVLQKVAEEAARVLVDPVPSYKQ"
            "VKQLKYVGMVLNEALRLWPTVPAFSLYAKEDTVLGGEYPLEKGDEVMVLIPQLHRDKTVWGDDVEEFRPERFENPSAIPQHAFKPFGNGQRASIGQQFALHEA"
            "TLVLGMMLKHFDFEDHTNYELDIKETGSLKPKGFVVKAKSKKIPLGGIPSPSTEQ",
            12,
            2437.0,
            [0, 1, 8],
            [2437.0, 2179.0, 2179.0],
            [1.0, 0.8941, 0.8941],
            [0, 9, 9],
            [0, 199, 199],
        ),
        (
            17,
            "MTIKEMPQPKTFGELKNLPLLNTDKPVQALMKIADELGEIFKFEAPGRVTRYLSSQRLIKEACDESRFDKNLSQGLKFLRDFLGDGLATSWTHEKNWKKAHN"
            "ILLPSFSQQAMKGYHAMMVDIAVQLVQKWERLNADEHIEVSEDMTRLTLDTIGLCGFNYRFNSFYRDQPHPFIISLVRALDEVMNKLQRANPDDPAYDENKR"
            "QFQEDIKVMNDLVDKIIADRKARGEQSDDLLTQMLNGKDPETGEPLDDGNIRYQIITFLYAGHEGTSGLLSFALYFLVKNPHVLQKVAEEAARVLVDPVPSYK"
            "QVKQLKYVGMVLNEALRLWPIVPAFSLYAKEDTVLGGEYPLEKGDEVMVLIPQLHRDKTVWGDDVEEFRPERFENPSAIPQHAFKPFGNGQRASIGQQFALHE"
            "ATLVLGMMLKHFDFEDHTNYELDIKELQTLKPKGFVVKAKSKKIPLGGIPSPSTEQSAKKVRKKAENAHNTPLLVLYGSNMGTAEGTARDLADIAMSKGFAPQV"
            "ATLDSHAGNLPREGAVLIVTASYNGHPPDNAKQFVDWLDQASADEVKGVRYSVFGCGDKNWATTYQKVPAFIDETLAAKGAENIADRGEADASDDFEGTYEEW"
            "REHMWSDVAAYFNLDIENSEDNKSTLSLQFVDSAADMPLAKMHGAFST",
            18,
            3478.0,  # base score
            [1, 4, 5],  # experiment ids
            [3478.0, 3072.0, 3015.0],  # alignment scores
            [1.0, 0.8833, 0.8669],  # norm scores
            [0, 1, 12],  # mismatches
            [0, 384, 384],  # gaps
        ),
    ],
)
def test_target_sequence_test_data(
    dbmanager_read_all_dedb_data,
    id,
    query_seq,
    n_lab_seq_match_data,
    score,
    experiment_ids,
    alignment_scores,
    norm_scores,
    mismatches,
    gaps,
):
    all_lab_sequences = dbmanager_read_all_dedb_data.get_lab_sequences()
    assert len(all_lab_sequences) == 36

    # get the alignment and the base score while timing the call
    start_time = time.time()
    lab_seq_match_data, base_score = bio_python_pairwise_aligner.get_alignments(
        query_sequence=query_seq, threshold=float(0.8), targets=all_lab_sequences
    )
    end_time = time.time()
    duration = end_time - start_time

    # Append timing info for this test case
    TIME_RESULTS.append((id, duration))

    # Verify the results (your existing assertions)
    assert len(lab_seq_match_data) == n_lab_seq_match_data
    assert base_score == score

    # Test the experiment ids
    assert lab_seq_match_data[0].get("experiment_id") == experiment_ids[0]
    assert lab_seq_match_data[1].get("experiment_id") == experiment_ids[1]
    assert lab_seq_match_data[2].get("experiment_id") == experiment_ids[2]

    # Additionally verify alignment scores, norm_scores, mismatches, gaps if needed:
    assert lab_seq_match_data[0].get("alignment_score") == alignment_scores[0]
    assert lab_seq_match_data[1].get("alignment_score") == alignment_scores[1]
    assert lab_seq_match_data[2].get("alignment_score") == alignment_scores[2]

    assert lab_seq_match_data[0].get("norm_score") == norm_scores[0]
    assert lab_seq_match_data[1].get("norm_score") == norm_scores[1]
    assert lab_seq_match_data[2].get("norm_score") == norm_scores[2]

    assert lab_seq_match_data[0].get("mismatches") == mismatches[0]
    assert lab_seq_match_data[1].get("mismatches") == mismatches[1]
    assert lab_seq_match_data[2].get("mismatches") == mismatches[2]

    assert lab_seq_match_data[0].get("gaps") == gaps[0]
    assert lab_seq_match_data[1].get("gaps") == gaps[1]
    assert lab_seq_match_data[2].get("gaps") == gaps[2]

    # Also verify that sequence_alignment exists
    assert lab_seq_match_data[0].get("sequence_alignment") is not None
    assert lab_seq_match_data[1].get("sequence_alignment") is not None
    assert lab_seq_match_data[2].get("sequence_alignment") is not None


# Global list to collect (test id, execution time)
TIME_RESULTS = []


def test_print_timing_summary():
    # This fixture will run for the entire test session,
    # then print a summary of timing results at teardown.
    print("\n====== Alignment Timing Summary ======")
    for test_id, duration in TIME_RESULTS:
        print(f"Test id {test_id}: {duration:.4f} seconds")
    print("========================================\n")
