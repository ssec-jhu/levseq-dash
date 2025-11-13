from concurrent.futures import ProcessPoolExecutor, as_completed

from Bio.Align import PairwiseAligner, substitution_matrices

from levseq_dash.app.config import settings
from levseq_dash.app.utils import utils


def setup_aligner_blastp():
    """Sets up a BioPython PairwiseAligner with BLASTP scoring and BLOSUM62 matrix.

    Initializes a PairwiseAligner with BLASTP scoring scheme, which sets default
    scoring parameters used by BLASTP for protein alignments. The substitution
    matrix is then replaced with BLOSUM62 as requested by PI.

    Configuration:
        - Mode: Global alignment
        - Gap open score: -12.0
        - Gap extend score: -1.0
        - Substitution matrix: BLOSUM62 (24x24 matrix) -> substitution_matrices.load("BLASTP")

    Returns:
        PairwiseAligner: Configured aligner ready for protein sequence alignment

    Raises:
        Exception: If aligner configuration doesn't match expected BLASTP settings
                  or if BLOSUM62 matrix shape is incorrect (should be 24x24)

    Reference:
        https://biopython.org/docs/dev/Tutorial/chapter_pairwise.html#using-a-pre-defined-substitution-matrix-and-gap-scores
        https://biopython.org/docs/dev/Tutorial/chapter_pairwise.html#substitution-scores
    """
    # ---------------------
    # set up the aligner
    # ---------------------
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


def sanitize_protein_sequence(sequence: str) -> str:
    """Sanitizes protein sequence by removing whitespace and control characters.

    Removes spaces, tabs, newlines, carriage returns, form feeds, and vertical tabs
    to prepare the sequence for BioPython pairwise alignment.

    Args:
        sequence: Raw protein sequence string

    Returns:
        Sanitized protein sequence with all whitespace removed

    Raises:
        ValueError: If sequence is None, empty, or not a string
    """
    if not sequence or not isinstance(sequence, str):
        raise ValueError("Sequence must be a non-empty string.")

    # Remove whitespace, newlines and other spaces
    # str.maketrans(x, y, z) x and y not used here, z is for removal
    translation_table = str.maketrans("", "", " \t\n\r\f\v")
    sequence_sanitized = sequence.translate(translation_table)

    return sequence_sanitized


def inject_aligner():
    """Initializes aligner in global scope for ProcessPoolExecutor workers.

    This function is used as an initializer for ProcessPoolExecutor to create
    one aligner instance per worker process, avoiding the overhead of pickling
    and creating aligners for each task.

    """
    global aligner
    aligner = setup_aligner_blastp()


# Helper function for alignment
def parallel_function_align_target(target_exp_id, target_exp_sequence, query_sequence, base_score, threshold):
    """Performs pairwise alignment of target sequence against query in parallel worker.

    Worker function for ProcessPoolExecutor that aligns a single target sequence
    against the query sequence, calculates normalized scores, and filters results
    based on threshold.

    Args:
        target_exp_id: Experiment ID of the target sequence
        target_exp_sequence: Target protein sequence to align
        query_sequence: Query protein sequence to align against
        base_score: Base alignment score (query against itself) for normalization
        threshold: Minimum normalized score threshold (0-1) to include in results

    Returns:
        List of result dictionaries for alignments meeting threshold, each containing:
            - experiment_id: Target experiment ID
            - sequence: Target sequence
            - sequence_alignment: Formatted alignment string
            - alignment_score: Raw alignment score
            - norm_score: Normalized score (alignment_score / base_score)
            - identities: Number of identical residues
            - mismatches: Number of mismatched residues
            - gaps: Number of gaps

    """
    # "Move the aligner creation inside the worker function, so it is not pickled or shared"
    # but testing and experiencing shows that it makes it slower AND is pickled anyway
    # keeping notes here that I tried to move aligner creation inside the worker
    # function, but it only made the code slower
    # aligner = setup_aligner_blastp()

    aligner = globals().get("aligner", None)

    alignments = aligner.align(target_exp_sequence, query_sequence)
    results = []
    for alignment in alignments:
        # extract the stats
        # https://biopython.org/docs/dev/Tutorial/chapter_align.html#subsec-slicing-indexing-alignment
        # https://biopython.org/docs/dev/Tutorial/chapter_align.html#counting-identities-mismatches-and-gaps
        counts = alignment.counts()

        # convert the alignment object result into a string
        alignment_str = alignment.__str__()

        # normalize the score by the base score
        norm_score_ratio = round(alignment.score / base_score, 4)

        # only return the alignments that score above a threshold
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
    """Performs parallel pairwise alignment of query sequence against multiple targets.

    Sanitizes input sequences, calculates base score, then uses ProcessPoolExecutor
    to align the query against all target sequences in parallel. Results are filtered
    by normalized score threshold and sorted by score.

    Args:
        query_sequence: Query protein sequence to align against targets
        threshold: Minimum normalized score (0-1) for including results
        targets: Dictionary mapping experiment IDs to target protein sequences

    Returns:
        Tuple of (results, base_score, warning_info):
            - results: List of alignment result dictionaries sorted by norm_score (descending)
            - base_score: Score of query aligned against itself
            - warning_info: Markdown-formatted summary with success/failure counts

    Raises:
        Exception: If query_sequence is empty, targets is empty, or base_score is zero

    Reference:
        https://biopython.org/docs/dev/Tutorial/chapter_pairwise.html#basic-usage
    """

    if query_sequence is None or len(query_sequence) == 0:
        raise Exception("Empty query sequence was provided!")

    if len(targets) == 0:
        raise Exception("Target sequences is empty.")

    # Sanitize the query sequence
    query_sequence_sanitized = sanitize_protein_sequence(query_sequence)

    # Sanitize all target sequences
    sanitized_targets = {}
    for target_id, target_sequence in targets.items():
        sanitized_target = sanitize_protein_sequence(target_sequence)
        sanitized_targets[target_id] = sanitized_target

    # init the aligner with the scoring paradigm of interest
    aligner = setup_aligner_blastp()

    # I create a base score for the query sequence itself to normalize the other scores by this number
    alignments = aligner.align(query_sequence_sanitized, query_sequence_sanitized)
    base_score = alignments[0].score

    if base_score == 0:
        raise Exception("Base score has returned 0. Check your inputs!")

    # ---------------------
    # ProcessPoolExecutor uses multiple processes, each with its own Python interpreter and memory space,
    # bypassing the GIL and allowing real parallel computation on multiple CPU cores.
    # ThreadPoolExecutor threads share the same interpreter and are limited by the GIL,
    # so only one thread runs Python code
    # ---------------------
    # default max_workers is the min(32, os.cpu_count() + 4)
    # if you have N Gunicorn workers and each creates a ProcessPoolExecutor with M workers, you'll have N × M processes
    # This can lead to resource contention

    # ---------------------
    results = []
    warning_info = ""
    failed_targets = []  # Track failed targets for markdown formatting
    # create and configure the process pool
    with ProcessPoolExecutor(initializer=inject_aligner, max_workers=None) as executor:
        # use below for debugging purposes
        utils.log_with_context(
            f"[ProcessPoolExecutor] Starting with  default# Workers: {executor._max_workers}",
            log_flag=settings.is_pairwise_aligner_logging_enabled(),
        )

        # The Future object allows the running asynchronous task to be queried, canceled,
        # and for the results to be retrieved later once the task is done.
        # Alternative implementation using as_completed for better exception handling
        # and optional timeout support
        futures_to_targets = {
            executor.submit(
                parallel_function_align_target,  # function to be executed in parallel
                target_exp_id,
                target_exp_sequence,
                query_sequence_sanitized,
                base_score,
                threshold,
            ): target_exp_id
            for target_exp_id, target_exp_sequence in sanitized_targets.items()
        }

        # Process futures with exception handling
        successful_results = 0
        failed_results = 0

        # timeout_seconds = 300  # 5 minutes per alignment
        for future in as_completed(futures_to_targets):  # Add timeout=timeout_seconds if needed
            target_id = futures_to_targets[future]
            try:
                result = future.result()
                results.extend(result)
                successful_results += 1
            except Exception as e:
                failed_results += 1
                # Log the exception but continue processing other futures
                failed_targets.append(f"{target_id[:10]}: {str(e)}")

        # Log summary of processing results
        total_targets = len(futures_to_targets)

        # Format warning_info as markdown with bullets
        warning_info = f"**Alignment Summary:** **{successful_results}/{total_targets}** alignments succeeded."
        if failed_results > 0:
            warning_info += f" **{failed_results}** sequences skipped due to errors:\n"
            for failed_target in failed_targets:
                warning_info += f"  - {failed_target}\n"

        utils.log_with_context(
            f"[ProcessPoolExecutor] {warning_info}\n[ProcessPoolExecutor] Done with all tasks",
            log_flag=settings.is_pairwise_aligner_logging_enabled(),
        )

    # for sanity’s sake let's make sure its sorted
    results = sorted(results, key=lambda x: x["norm_score"], reverse=True)
    return results, base_score, warning_info
