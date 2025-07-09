from dash import html

from levseq_dash.app import global_strings as gs

# ---------------------------------------------------------------------
#   Strings that require simple styling embedded in them, such as bold
#   The styling uses dash html components, or it could be markdown
#   Separating these strings here, so we know they have embedded
#   styling and are aware of them when replacing the strings if need be
# ----------------------------------------------------------------------

seq_align_algorithm_blurb = [
    "The match is performed using Biopython's ",
    html.A(
        "PairwiseAligner",
        href="https://biopython.org/docs/dev/Tutorial/chapter_pairwise.html",
        target="_blank",
    ),
    " module, using the ",
    html.A(
        "blastp",
        href="https://biopython.org/docs/dev/Tutorial/chapter_pairwise.html#using-a-pre-defined-substitution-matrix-and-gap-scores",
        target="_blank",
    ),
    " scoring scheme with the substitution matrix attribute of the PairwiseAligner object set to use ",
    html.A(
        "BLOSUM62",
        href="https://biopython.org/docs/dev/Tutorial/chapter_pairwise.html#loading-predefined-substitution-matrices",
        target="_blank",
    ),
    ". Similarity scores are normalized such that a value of 1.0 indicates a perfect match.",
]
seq_align_blurb = [
    "Given a query sequence, automatically discover the closest matches among all other sequences "
    "deposited on the platform and pinpoint the exact residue changes those matches carry. "
    "The resulting mutation map helps visualization of which positions have previously "
    "accommodated ",
    html.B("gain-of-function (GoF)"),
    " or ",
    html.B("loss-of-function (LoF) substitutions"),
    ". ",
    html.Span(seq_align_algorithm_blurb),
    html.Br(),
    html.Br(),
    html.Div(
        "Query Sequence is prepopulated as an example for convenience. Please replace with your sequence of interest."
    ),
]

# this will be treated as markdown
markdown_note_matched_seq = """
- Number of matched sequences is calculated per experiment match not per smiles string.
- Each row represents experiment-compound information.
- An experiment _may_ have one or more alignments. Each will be represented per compound(SMILES)
"""

exp_seq_align_blurb = [
    "The parent sequence is preloaded for convenience. ",
    gs.help_threshold,
    " Enter residue positions separated by commas (e.g., 59, 102), then click on ",
    html.B(gs.seq_align_form_button_sequence_matching),
    " to identify variants containing those mutations along with any co-occurring changes. ",
    html.Span(seq_align_algorithm_blurb),
]
