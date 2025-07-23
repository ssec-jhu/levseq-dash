from concurrent.futures import ProcessPoolExecutor

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
    #  REQUEST BY PI to use BLOSUM62 matrix
    aligner.substitution_matrix = substitution_matrices.load("BLOSUM62")

    # verify the matrix has been replaced with BLOSUM62
    if not aligner.substitution_matrix.shape[0] == 24 or not aligner.substitution_matrix.shape[1] == 24:
        raise Exception("Pairwise aligner matrix not set to BLOSUM62.")

    return aligner


# Helper function for alignment
def parallel_function_align_target(target_exp_id, target_exp_sequence, query_sequence, base_score, threshold, aligner):
    # "Move the aligner creation inside the worker function, so it is not pickled or shared"
    # but testing and experiencing shows that it makes it slower AND is pickled anyway
    # keeping notes here that I tried to move aligner creation inside the worker
    # function, but it only made the code slower
    # aligner = setup_aligner_blastp()

    alignments = aligner.align(target_exp_sequence, query_sequence)
    results = []
    for alignment in alignments:
        counts = alignment.counts()
        alignment_str = alignment.__str__()
        norm_score_ratio = round(alignment.score / base_score, 4)
        if norm_score_ratio >= threshold:
            results.append(
                {
                    "experiment_id": target_exp_id,
                    "sequence": target_exp_sequence,
                    "sequence_alignment": alignment_str,
                    "alignment_score": alignment.score,
                    "norm_score": norm_score_ratio,
                    "identities": counts.identities,
                    "mismatches": counts.mismatches,
                    "gaps": counts.gaps,
                }
            )
    return results


def get_alignments(query_sequence, threshold, targets: dict):
    """
    https://biopython.org/docs/dev/Tutorial/chapter_pairwise.html#basic-usage
    """

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

    # ---------------------
    # example workflow for ProcessPoolExecutor:
    # def square(x):
    #     return x * x
    # with ProcessPoolExecutor(max_workers=4) as executor:
    # futures = [executor.submit(square, x) for x in range(4)]
    # for future in futures:
    #     print(future.result())
    # ---------------------
    # ProcessPoolExecutor uses multiple processes, each with its own Python interpreter and memory space,
    # bypassing the GIL and allowing real parallel computation on multiple CPU cores.
    # ThreadPoolExecutor threads share the same interpreter and are limited by the GIL,
    # so only one thread runs Python code
    # at a time, making it no faster than a single-threaded loop for CPU-bound work.
    # with ThreadPoolExecutor(max_workers=max(2, os.cpu_count() * 2)) as executor:  # does not speed up
    # ---------------------
    # default max_workers is the min(32, os.cpu_count() + 4)
    # if you have N Gunicorn workers and each creates a ProcessPoolExecutor with M workers, you'll have N × M processes
    # This can lead to resource contention
    # a suggestion is max_workers=max(2, os.cpu_count() - 1)
    # ---------------------
    results = []
    with ProcessPoolExecutor() as executor:
        # use below for debugging purposes
        # print(
        #     f"[PID:{os.getpid()}][TID:{threading.get_ident()}][{threading.current_thread().name}] "
        #     f"number of workers: {executor._max_workers}"
        # )
        futures = [
            executor.submit(
                parallel_function_align_target,  # function to be executed in parallel
                target_exp_id,
                target_exp_sequence,
                query_sequence,
                base_score,
                threshold,
                aligner,  # parameters
            )
            for target_exp_id, target_exp_sequence in targets.items()
        ]
        for future in futures:
            results.extend(future.result())

    return results, base_score
