import numpy as np
from Bio.Align import PairwiseAligner, substitution_matrices


def setup_aligner_blastp():
    # ---------------------
    # set up the aligner
    # ---------------------
    # Currently, the provided scoring schemes are blastn and megablast, which are suitable for nucleotide alignments,
    # and blastp, which is suitable for protein alignments. Selecting these scoring schemes will initialize the
    # PairwiseAligner object to the default scoring parameters used by BLASTN, MegaBLAST, and BLASTP, respectively.
    # https://biopython.org/docs/dev/Tutorial/chapter_pairwise.html#using-a-pre-defined-substitution-matrix-and-gap-scores
    # this will set:
    #   open_gap_score = -12.0
    #   extend_gap_score = -1.0
    #   substitution_matrix = substitution_matrices.load("BLASTP")
    aligner = PairwiseAligner(scoring="blastp")

    # verify that scores are set to blastp algorithm
    if not aligner.mode == "global" or not aligner.open_gap_score == -12 or not aligner.extend_gap_score == -1:
        raise Exception("Pairwise aligner is not set to blastp aligner. ")

    # https://biopython.org/docs/dev/Tutorial/chapter_pairwise.html#substitution-scores
    # Alternatively, you can use the substitution_matrix attribute of the PairwiseAligner object to specify a
    # substitution matrix.This allows you to apply different scores for different pairs of matched and
    # mismatched letters. This is typically used for amino acid sequence alignments. For example,
    # by default BLAST [Altschul1990] uses the BLOSUM62 substitution matrix for protein alignments by blastp.
    # This substitution matrix is available from Biopython.
    # IMPORTANT: BLASTP default substitution scores.
    #  For the default gap scores, as used for BLASTP on NCBI Web
    #  BLAST, The BLAST documentation shows gap costs a = 11 for opening
    #  a gap, and b = 1 for each letter in the gap, and defines the
    #  total score of a gap of k residues as -(a + b*k). In contrast,
    #  Biopython follows the definition given in "Biological Sequence
    #  Analysis" (Durbin et al., 1998), for which the total score of a
    #  gap of k residues is -d - e * (k - 1), where d is the gap-open
    #  penalty and e is the gap-extend penalty. Biopython uses -d as
    #  the gap open score and -e as the gap extend penalty:
    #  gap open score: -12
    #  gap extend score: -1
    #  The substitution matrix is identical to BLOSUM62, except for some
    #  values of the ambiguous amino acids B, Z, and X; the values for
    #  the ambiguous amino acids U, O, and J are not included in BLOSUM62.
    #  REQUEST BY PI to use BLOSOM62 matrix
    aligner.substitution_matrix = substitution_matrices.load("BLOSUM62")

    # verify the matrix has been replaced with BLOSUM62
    if not aligner.substitution_matrix.shape[0] == 24 or not aligner.substitution_matrix.shape[1] == 24:
        raise Exception("Pairwise aligner matrix not set to BLOSUM62.")

    return aligner


def get_alignments(query_sequence, threshold, targets: dict):
    """
    https://biopython.org/docs/dev/Tutorial/chapter_pairwise.html#basic-usage
    """

    results = []

    if query_sequence is None or len(query_sequence) == 0:
        raise Exception("Empty query sequence was provided!")

    if len(targets) == 0:
        raise Exception("Target sequences is empty.")

    # init the aligner with the scoring paradigm of interest
    aligner = setup_aligner_blastp()

    # I create a base score for the query sequence itself to normalize the other scores by this number
    alignments = aligner.align(query_sequence, query_sequence)
    base_score = alignments[0].score

    if base_score == 0:
        raise Exception("Base score has returned 0. Check your inputs!")

    # now iterate over the target sequences and run the aligner on the sequence
    for target_exp_id, target_exp_sequence in targets.items():
        alignments = aligner.align(target_exp_sequence, query_sequence)
        for i, alignment in enumerate(alignments):
            # extract the stats
            # https://biopython.org/docs/dev/Tutorial/chapter_align.html#subsec-slicing-indexing-alignment
            # https://biopython.org/docs/dev/Tutorial/chapter_align.html#counting-identities-mismatches-and-gaps
            counts = alignment.counts()

            # convert the alignment object result into a string
            alignment_str = alignment.__str__()

            # manually calculated values
            norm_score_ratio = np.round(alignment.score / base_score, 4)

            # only return the alignments that score above a threshold
            if norm_score_ratio >= threshold:
                results.append(
                    {
                        "experiment_id": target_exp_id,  # this should be an id
                        "sequence": target_exp_sequence,
                        "sequence_alignment": alignment_str,
                        "alignment_score": alignment.score,
                        # "coordinates": alignment.coordinates,
                        "norm_score": norm_score_ratio,
                        # "indices": alignment.indices,
                        "identities": counts.identities,  # The number of identical letters in the alignment
                        "mismatches": counts.mismatches,  # The number of mismatched letters in the alignment
                        # The total number of gaps in the alignment, equal to left_gaps + right_gaps + internal_gaps
                        "gaps": counts.gaps,
                    }
                )
    return results, base_score
