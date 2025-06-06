from dash import html

# ---------------------------------------------------------------------
#   Strings that require simple styling embedded in them, such as bold
#   The styling uses dash html components, or it could be markdown
#   Separating these strings here, so we know they have embedded
#   styling and are aware of them when replacing the strings if need be
# ----------------------------------------------------------------------

seq_align_blurb = [
    "Given a query sequence, automatically discover the closest matches among all other sequences "
    "deposited on the platform and pinpoint the exact residue changes those matches carry. "
    "The resulting mutation map helps visualization of which positions have previously "
    "accommodated ",
    html.B("gain-of-function (GoF)"),
    " or ",
    html.B("loss-of-function (LoF) substitutions"),
    ". The match is performed with BLASTP. Each sequence is broken into overlapping three-amino-acid “words”; "
    "exact word hits seed an extension whose running BLOSUM62 score must stay above a threshold. "
    "Only these promising segments are refined into full gaped alignments scored with affine gap penalties. "
    "The alignment with the highest bit-score (lowest E-value) is treated as the closest neighbour, "
    "and every identical or non-identical position is logged for the mutation map.",
]

# this will be treated as markdown
markdown_note_matched_seq = """
- Number of matched sequences is calculated per experiment match not per smiles string.
- Each row represents experiment-compound information.
- An experiment _may_ have one or more alignments. Each will be represented per compound(SMILES)
"""
