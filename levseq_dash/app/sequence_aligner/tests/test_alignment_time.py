import time

import pytest

from levseq_dash.app.sequence_aligner import bio_python_pairwise_aligner


@pytest.mark.parametrize(
    "seq_id, query_seq,n_lab_seq_match_data, score, alignment_scores, norm_scores,mismatches, gaps",
    [
        (
            # a very lengthy seq alignment,
            "seq_1",
            "MKGYFGPYGGQYVPEILMGALEELEAAYEGIMKDESFWKEFNDLLRDYAGRPTPLYFARRLSEKYGARVYLKREDLLHTGAHKINNAIGQVLLAKLMGKTRIIAE"
            "TGAGQHGVATATAAALFGMECVIYMGEEDTIRQKLNVERMKLLGAKVVPVK"
            "SGSRTLKDAIDEALRDWITNLQTTYYVFGSVVGPHPYPIIVRNFQKVIGEETKKQIPEKEGRLPDYIVACVSGGSNAA"
            "GIFYPFIDSGVKLIGVEAGGEGLETGKHAASLLKGKIGYLHGSKTFVLQDDWGQVQVSHSVSAGLDYSGVGPEHAYWR"
            "ETGKVLYDAVTDEEALDAFIELSRLEGIIPALESSHALAYLKKINIKGKVVVVNLSGRGDKDLESVLNHPYVRERIR",
            3,
            2011.0,
            [2011.0, 2011.0, 1953.0],
            [1.0, 1.0, 0.9712],
            [0, 0, 10],
            [0, 0, 0],
        ),
        (
            "seq_2",
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
            [5451.0, 5429.0, 5405.0],
            [1.0, 0.996, 0.9916],
            [0, 3, 9],
            [0, 0, 0],
        ),
        (
            "seq_3",
            "MTIKEMPQPKTFGELKNLPLLNTDKPVQALMKIADELGEIFKFEAPGRVTRYLSSQRLIKEACDESRFDKNLSQALKFMRDFLGDGLATSWTHEKNWKKAHN"
            "ILLPSFSQQAMKGYHAMMVDIAVQLVQKWERLNADEHIEVSEDMTRLTLDTIGLCGFNYRFNSFYRDQPHPFIISMVRALDEVMNKLQRANPDDPAYDENKRQ"
            "FQEDIKVMNDLVDKIIADRKARGEQSDDLLTQMLNGKDPETGEPLDDGNIRYQIITFLMAGHEPTSGLLSFALYFLVKNPHVLQKVAEEAARVLVDPVPSYKQ"
            "VKQLKYVGMVLNEALRLWPTVPAFSLYAKEDTVLGGEYPLEKGDEVMVLIPQLHRDKTVWGDDVEEFRPERFENPSAIPQHAFKPFGNGQRASIGQQFALHEA"
            "TLVLGMMLKHFDFEDHTNYELDIKETGSLKPKGFVVKAKSKKIPLGGIPSPSTEQ",
            12,
            2437.0,
            [2437.0, 2343.0, 2237.0],
            [1.0, 0.9614, 0.9179],
            [0, 19, 9],
            [0, 0, 22],
        ),
        (
            "seq_4",
            "MTIKEMPQPKTFGELKNLPLLNTDKPVQALMKIADELGEIFKFEAPGRVTRYLSSQRLIKEACDESRFDKNLSQGLKFLRDFLGDGLATSWTHEKNWKKAHN"
            "ILLPSFSQQAMKGYHAMMVDIAVQLVQKWERLNADEHIEVSEDMTRLTLDTIGLCGFNYRFNSFYRDQPHPFIISLVRALDEVMNKLQRANPDDPAYDENKR"
            "QFQEDIKVMNDLVDKIIADRKARGEQSDDLLTQMLNGKDPETGEPLDDGNIRYQIITFLYAGHEGTSGLLSFALYFLVKNPHVLQKVAEEAARVLVDPVPSYK"
            "QVKQLKYVGMVLNEALRLWPIVPAFSLYAKEDTVLGGEYPLEKGDEVMVLIPQLHRDKTVWGDDVEEFRPERFENPSAIPQHAFKPFGNGQRASIGQQFALHE"
            "ATLVLGMMLKHFDFEDHTNYELDIKELQTLKPKGFVVKAKSKKIPLGGIPSPSTEQSAKKVRKKAENAHNTPLLVLYGSNMGTAEGTARDLADIAMSKGFAPQV"
            "ATLDSHAGNLPREGAVLIVTASYNGHPPDNAKQFVDWLDQASADEVKGVRYSVFGCGDKNWATTYQKVPAFIDETLAAKGAENIADRGEADASDDFEGTYEEW"
            "REHMWSDVAAYFNLDIENSEDNKSTLSLQFVDSAADMPLAKMHGAFST",
            18,
            3478.0,  # base score
            [3478.0, 3478.0, 3466.0],  # alignment scores
            [1.0, 1, 0.9965],  # norm scores
            [0, 0, 2],  # mismatches
            [0, 0, 0],  # gaps
        ),
    ],
)
def test_target_sequence_test_data(
    target_sequence_dictionary,
    seq_id,
    query_seq,
    n_lab_seq_match_data,
    score,
    alignment_scores,
    norm_scores,
    mismatches,
    gaps,
):
    # get the alignment and the base score while timing the call
    start_time = time.time()
    lab_seq_match_data, base_score = bio_python_pairwise_aligner.get_alignments(
        query_sequence=query_seq, threshold=float(0.8), targets=target_sequence_dictionary
    )
    end_time = time.time()
    duration = end_time - start_time

    # Append timing info for this test case
    TIME_RESULTS.append((seq_id, duration))

    # Verify the results (your existing assertions)
    assert len(lab_seq_match_data) == n_lab_seq_match_data
    assert base_score == score

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
