from Bio.Align import PairwiseAligner, substitution_matrices


def printa_alignment_info(i, base_score, alignment):
    print(f"🔢 Alignment {i}")
    print(f"   - score: {alignment.score}")
    print(f"   - ratio over base: {alignment.score / base_score}")
    # https://biopython.org/docs/dev/Tutorial/chapter_pairwise.html#chapter-pairwise
    # The alignment length is defined as the number of columns in the alignment as printed.
    # This is equal to the sum of the number of matches, number of mismatches, and the total length
    # of gaps in the target and query
    print(f"   - alignment length:{alignment.length} len(target)={len(target)}  len(query)={len(query)}")
    print(f"   - identities : {alignment.counts().identities}")
    print(f"   - mismatches : {alignment.counts().mismatches}")
    print(f"   - gaps: {alignment.counts().gaps}")
    # print( f"   - Query maps to target from index **{alignment.aligned[0][0][0]}** to **{alignment.aligned[0][
    # -1][1]}**\n" )
    print(alignment)
    print("-" * 60)
    print("🔹Coordinate Mapping (Query → Target):")
    print(alignment.coordinates)
    print("-" * 60)


target_sequences = {
    "seq_base": "MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAGGWAASNEHLIYYGSNPDTGAPIKEYLERVRARIGAWVL"
    "DTTCRDYNREWLDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAGIYPITATIKPFLAKKGGSPEDIEGMYNAWLKSVVLQVAIWSHPYTKENDR",
    "seq_removed first letter": "TPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAGGWAASNEHLIYYGSNPDTGAPIK"
    "EYLERVRARIGAWVLDTTCRDYNREWLDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAGIYPITATIKPFLAKKGGSPE"
    "DIEGMYNAWLKSVVLQVAIWSHPYTKENDR",
    "seq_removed last letter": "MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAGGWAASNEHLIYYGSNPDTGAPIK"
    "EYLERVRARIGAWVLDTTCRDYNREWLDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAGIYPITATIKPFLAKKGGSPEDI"
    "EGMYNAWLKSVVLQVAIWSHPYTKEND",
    "seq_switched_two_letters": "MAASDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAGGWAASNEHLIYYGSNPDTGAPI"
    "KEYLERVRARIGAWVLDTTCRDYNREWLDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAGIYPITATIKPFLAKKGGSP"
    "EDIEGMYNAWLKSVVLQVAIWSHPYTKENDR",
    "seq_removed_all_w": "MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAGGAASNEHLIYYGSNPDTGAPIKEYLERV"
    "RARIGAVLDTTCRDYNRELDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAGIYPITATIKPFLAKKGGSPEDIEGMYNALKSVVLQ"
    "VAISHPYTKENDR",
    "seq_half_seq": "MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAGGWAASNEHLIYYGSNPDTGAPIKEYLERVRARIGA",
    "seq_portion": "MTPSDISGYDYGRVEKSPITDLEKAADVLKDQVDEILDLAGGWAASNEHLIYYGSNPDTGAPIKEYLERVRARIGAWVLDTTCRDYNREWL"
    "DYQYEVGLRHHYLIAGIYPITATIKPFLAKKGGSPEDIEGMYNAWLKSVVLQVAIWSHPYTKENDR",
}

query_name = "seq_base"
query = target_sequences[query_name]

# # Initialize the aligner
# aligner = PairwiseAligner()
# aligner.mode = "global"
# aligner.match_score = 3
# aligner.mismatch_score = -1
# aligner.open_gap_score = -3
# aligner.extend_gap_score = -0.5

aligner = PairwiseAligner(scoring="blastp")

# Alternatively, you can use the substitution_matrix attribute of the PairwiseAligner object to specify a
# substitution matrix. This allows you to apply different scores for different pairs of matched and mismatched letters.
# This is typically used for amino acid sequence alignments. For example, by default BLAST [Altschul1990] uses
# the BLOSUM62 substitution matrix for protein alignments by blastp. This substitution matrix is available
# from Biopython:
aligner.substitution_matrix = substitution_matrices.load("BLOSUM62")

# run the alignment with itself to get a base score
alignments = aligner.align(query, query)
base_score = alignments[0].score

# 🔹 Perform Sequence Matching
print("-" * 60)
print(f"🔍 Aligner algorithm: {aligner.algorithm}...\n")

for target_name, target in target_sequences.items():
    alignments = aligner.align(target, query)
    print("-" * 60)
    print(f"✅ Query:{query_name} Target:{target_name}")
    print(f"   # alignments:{len(alignments)}")
    print("-" * 60)

    for i, alignment in enumerate(alignments):
        printa_alignment_info(i, base_score, alignment)

    # # REVERSE RESULTS
    # alignments = aligner.align(query, target)
    # print("-" * 60)
    # print(f"✅ Reverse Query:{target_name} Target:{query_name}")
    # print(f"   # alignments:{len(alignments)}")
    # print("-" * 60)
    #
    # for i, alignment in enumerate(alignments):
    #     printa_alignment_info(i, base_score, alignment)
