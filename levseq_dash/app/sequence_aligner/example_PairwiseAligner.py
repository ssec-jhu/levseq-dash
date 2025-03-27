# from Bio.Align import PairwiseAligner, substitution_matrices
#
# target_sequences = {
#     "seq1": "MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAGGWAASNEHLIYYGSNPDTGAPIKEYLERVRARIGAWVLDTTCRDYNREWLDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAGIYPITATIKPFLAKKGGSPEDIEGMYNAWLKSVVLQVAIWSHPYTKENDR",
#     # removed first letter
#     "seq1-2": "TPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAGGWAASNEHLIYYGSNPDTGAPIKEYLERVRARIGAWVLDTTCRDYNREWLDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAGIYPITATIKPFLAKKGGSPEDIEGMYNAWLKSVVLQVAIWSHPYTKENDR",
#     # removed last letter
#     "seq1-3": "MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAGGWAASNEHLIYYGSNPDTGAPIKEYLERVRARIGAWVLDTTCRDYNREWLDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAGIYPITATIKPFLAKKGGSPEDIEGMYNAWLKSVVLQVAIWSHPYTKEND",
#     # switched two letters
#     "seq1-4": "MXXSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAGGWAASNEHLIYYGSNPDTGAPIKEYLERVRARIGAWVLDTTCRDYNREWLDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAGIYPITATIKPFLAKKGGSPEDIEGMYNAWLKSVVLQVAIWSHPYTKENDR",
#     # missing all W random letters
#     "seq1-5": "MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAGGAASNEHLIYYGSNPDTGAPIKEYLERVRARIGAVLDTTCRDYNRELDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAGIYPITATIKPFLAKKGGSPEDIEGMYNALKSVVLQVAISHPYTKENDR",
#     # only half of the sequence
#     "seq1-6": "MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAGGWAASNEHLIYYGSNPDTGAPIKEYLERVRARIGA",
#     # another portion of the sequence
#     "seq1-7": "MTPSDISGYDYGRVEKSPITDLEKAADVLKDQVDEILDLAGGWAASNEHLIYYGSNPDTGAPIKEYLERVRARIGAWVLDTTCRDYNREWLDYQYEVGLRHHYLIAGIYPITATIKPFLAKKGGSPEDIEGMYNAWLKSVVLQVAIWSHPYTKENDR",
#     # "seq2": "MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAGGWAASNEHLIYYFSNPDTGAPIKEYLERVRARCVAWVLDTTCRDYNREWLDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAGIYPLTATIKPFLAKKGGSPEDIEGMYNAWLKSVVLQVAIWSHPYTKENDRLE",
#     # "seq3": "MAVPGYDFGKVPDAPISDADFESLKKTVMWGEEDEKYRKMACEALKGQVEDILDLWYGLQGSNQHLIYYFGDKSGRPIPQYLEAVRKRFGLWIIDTLCKPLDRQWLNYMYEIGLRHHRTKKGKTDGVDTVEHIPLRYMIAFIAPIGLTIKPILEKSGHPPEAVERMWAAWVKLVVLQVAIWSYPYAKTGEWLE",
#     # "seq4": "MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLMGGWAASNEHLIYYFSNPDTGAPIKEYLERVRARCVAWVLDTTCRDYNREWLDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAEIYPLTATIKPFLAKKGGSPEDIEGMYNAWLKSVVLQVAIWSHPYTKENDRLE",
#     # "seq5": "MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLMGGWAASNEHLIYYFSNPDTGAPIKEYLERVRARCVAWVLDTTCRDYNREWLDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAGIYPLTATIKPFLAKKGGSPEDIEGMYNAWLKSVVLQVAIWSHPYTKENDRLE",
#     # "seq6": "MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLMGGWAASNEHLIYYFSNPDTGAPIKEYLERVRARCVAWVLDTTCRDYNREWLDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAGIYPLTATIKPFLAKKGGSPEDIEGMYNAWLKSVVLQVAIWSHPYTKENDRLE",
#     # 'temp_seq': "GAACT"
# }
# query_name = "seq1"
# query = target_sequences[query_name]
#
# # Initialize the Alignerå
# # aligner = PairwiseAligner(scoring="blastp")
# aligner = PairwiseAligner()
# aligner.mode = "global"
# aligner.match_score = 3
# aligner.mismatch_score = -1
# aligner.open_gap_score = -3
# aligner.extend_gap_score = -0.5
#
#
# # Alternatively, you can use the substitution_matrix attribute of the PairwiseAligner object to specify a
# # substitution matrix. This allows you to apply different scores for different pairs of matched and mismatched letters.
# # This is typically used for amino acid sequence alignments. For example, by default BLAST [Altschul1990] uses
# # the BLOSUM62 substitution matrix for protein alignments by blastp. This substitution matrix is available
# # from Biopython:
# matrix = substitution_matrices.load("BLOSUM62")
# aligner.substitution_matrix = matrix
#
# # run the alignment with itself to get a base score
# alignments = aligner.align(query, query)
# base_score = alignments[0].score
#
# # 🔹 Perform Sequence Matching
# print("-" * 60)
# print(f"🔍 Aligner algorithm: {aligner.algorithm}...\n")
#
# for target_name, target in target_sequences.items():
#     alignments = aligner.align(target, query)
#     print("-" * 60)
#     print(f"✅ Query:{query_name} Target:{target_name}")
#     print(f"   # alignments:{len(alignments)}")
#     print("-" * 60)
#
#     for i, alignment in enumerate(alignments):
#         matches = sum(1 for a, b in zip(alignment[0], alignment[1]) if a == b and a != "-" and b != "-")
#         # total_aligned = sum(1 for a, b in zip(alignment[0], alignment[1]) if a != "-" and b != "-")
#         percentage = (matches / alignment.length) * 100 if alignment.length > 0 else 0
#         # a dot is not a gap, but I want to count how many not matched locations are there
#         gaps_in_alignment = (
#             alignment[0].count("-") + alignment[1].count("-") + alignment[0].count(".") + alignment[1].count(".")
#         )
#
#         print(f"🔢 Alignment {i}")
#         print(f"   - score: {alignment.score}")
#         print(f"   - ratio over base: {alignment.score / base_score}")
#         print(f"   - percentage: {percentage}%")
#         # https://biopython.org/docs/dev/Tutorial/chapter_pairwise.html#chapter-pairwise
#         # The alignment length is defined as the number of columns in the alignment as printed.
#         # This is equal to the sum of the number of matches, number of mismatches, and the total length of gaps in the target and query
#         print(f"   - alignment length:{alignment.length} len(target)={len(target)}  len(query)={len(query)}")
#         print(f"   - matches : {matches}")
#         print(f"   - gaps in alignment: {gaps_in_alignment}")
#         # print(
#         #     f"   - Query maps to target from index **{alignment.aligned[0][0][0]}** to **{alignment.aligned[0][-1][1]}**\n"
#         # )
#         print(alignment)
#         my_str = alignment.__str__()
#         # print("alignment[0]" * 60)
#         # print(alignment[0])
#         # print("alignment[1]-" * 60)
#         # print(alignment[1])
#         # mapped_alignment = alignment[0].map(alignment[1])
#         # print(mapped_alignment)
#         # print("-" * 60)
#         # 🔹 Print Coordinate Mapping
#         # print("🔹Coordinate Mapping (Query → Target):")
#         print(alignment.coordinates)
#         print("-" * 60)
#
#     # alignments = aligner.align(query, target)
#     # print("-" * 60)
#     # print(f"✅ Reverse Query:{target_name} Target:{query_name}")
#     # print(f"   # alignments:{len(alignments)}")
#     # print("-" * 60)
#     #
#     # for i, alignment in enumerate(alignments):
#     #     matches = sum(1 for a, b in zip(alignment[0], alignment[1]) if a == b and a != "-" and b != "-")
#     #     # total_aligned = sum(1 for a, b in zip(alignment[0], alignment[1]) if a != "-" and b != "-")
#     #     percentage = (matches / alignment.length) * 100 if alignment.length > 0 else 0
#     #     gaps_in_alignment = alignment[0].count("-") + alignment[1].count("-")
#     #
#     #     print(f"🔢 Alignment {i}")
#     #     print(f"   - score: {alignment.score}")
#     #     print(f"   - ratio over base: {alignment.score / base_score}")
#     #     print(f"   - percentage: {percentage}%")
#     #     print(f"   - alignment length:{alignment.length} len(target)={len(target)}  len(query)={len(query)}")
#     #     print(f"   - matches : {matches}")
#     #     print(f"   - gaps in alignment: {gaps_in_alignment}")
#     #     print(
#     #         f"   - Query maps to target from index **{alignment.aligned[0][0][0]}** to **{alignment.aligned[0][-1][1]}**\n"
#     #     )
#     #     # print(alignment)
#     #     print("-" * 60)
#     #     # 🔹 Print Coordinate Mapping
#     #     # print("🔹Coordinate Mapping (Query → Target):")
#     #     # print(alignment.coordinates)
#     #     # print("-" * 60)
