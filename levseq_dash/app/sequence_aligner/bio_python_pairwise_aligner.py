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
    aligner = PairwiseAligner(scoring="blastp")

    # TODO: I am not sure setting the scoring by default assigns the BLOSUM62 matrix.
    #  This may or may not be redundant. PI will investigate.
    # https://biopython.org/docs/dev/Tutorial/chapter_pairwise.html#substitution-scores Alternatively,
    # you can use the substitution_matrix attribute of the PairwiseAligner object to specify a substitution matrix.
    # This allows you to apply different scores for different pairs of matched and mismatched letters. This is
    # typically used for amino acid sequence alignments. For example, by default BLAST [Altschul1990] uses the
    # BLOSUM62 substitution matrix for protein alignments by blastp. This substitution matrix is available from
    # Biopython:
    aligner.substitution_matrix = substitution_matrices.load("BLOSUM62")

    return aligner


def get_alignments(query_sequence, threshold, targets: dict):
    """
    https://biopython.org/docs/dev/Tutorial/chapter_pairwise.html#basic-usage
    """

    results = []

    if query_sequence is None:
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
            norm_score_ratio = np.round(alignment.score / base_score, 2)

            # only return the alignments that score above a threshold
            if norm_score_ratio >= threshold:
                results.append(
                    {
                        "experiment_id": target_exp_id,  # this should be an id
                        "sequence": target_exp_sequence,
                        "alignment": alignment_str,
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
