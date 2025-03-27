# import subprocess
#
# from Bio.Blast.Applications import NcbiblastpCommandline
#
# # Sequences for the target BLAST database
# target_sequences = {
#     "seq1": "MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAGGWAASNEHLIYYGSNPDTGAPIKEYLERVRARIGAWVLDTTCRDYNREWLDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAGIYPITATIKPFLAKKGGSPEDIEGMYNAWLKSVVLQVAIWSHPYTKENDR",
#     "seq2": "MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAGGWAASNEHLIYYFSNPDTGAPIKEYLERVRARCVAWVLDTTCRDYNREWLDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAGIYPLTATIKPFLAKKGGSPEDIEGMYNAWLKSVVLQVAIWSHPYTKENDRLE",
#     "seq3": "MAVPGYDFGKVPDAPISDADFESLKKTVMWGEEDEKYRKMACEALKGQVEDILDLWYGLQGSNQHLIYYFGDKSGRPIPQYLEAVRKRFGLWIIDTLCKPLDRQWLNYMYEIGLRHHRTKKGKTDGVDTVEHIPLRYMIAFIAPIGLTIKPILEKSGHPPEAVERMWAAWVKLVVLQVAIWSYPYAKTGEWLE",
#     "seq4": "MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLMGGWAASNEHLIYYFSNPDTGAPIKEYLERVRARCVAWVLDTTCRDYNREWLDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAEIYPLTATIKPFLAKKGGSPEDIEGMYNAWLKSVVLQVAIWSHPYTKENDRLE",
#     "seq5": "MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLMGGWAASNEHLIYYFSNPDTGAPIKEYLERVRARCVAWVLDTTCRDYNREWLDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAGIYPLTATIKPFLAKKGGSPEDIEGMYNAWLKSVVLQVAIWSHPYTKENDRLE",
# }
#
#
# # Function to create a BLAST database
# def create_blast_db(sequences):
#     """Create a BLAST database from given sequences."""
#     fasta_path = "blast_db.fasta"
#     with open(fasta_path, "w") as f:
#         for name, seq in sequences.items():
#             f.write(f">{name}\n{seq}\n")
#     print(f"FASTA file created at {fasta_path}")
#
#     # Create the BLAST database using makeblastdb
#     subprocess.run(["makeblastdb", "-in", fasta_path, "-dbtype", "prot", "-out", "blast_db"], check=True)
#     print("BLAST database created successfully.")
#
#
# # Function to run BLAST search using a query sequence
# def run_blast(query_sequence):
#     """Run BLAST using a query sequence against the created database."""
#     query_path = "query.fasta"
#     with open(query_path, "w") as f:
#         f.write(f">query\n{query_sequence}\n")
#
#     print(f"Query sequence written to {query_path}")
#
#     # Run BLAST using the query against the database
#     blastp_cline = NcbiblastpCommandline(query=query_path, db="blast_db", outfmt=6, out="blast_results.txt")
#     subprocess.run(str(blastp_cline), shell=True, check=True)
#
#     # Parse and print results
#     results = []
#     with open("blast_results.txt") as f:
#         for line in f:
#             parts = line.strip().split("\t")
#             results.append(f"✅ {parts[0]}: Score={parts[11]}, Identity={parts[2]}%")
#
#     if not results:
#         print("No significant alignments found.")
#     else:
#         print("\n".join(results))
#
#
# # Main function to create the database and run the query
# def main():
#     # Create the BLAST database
#     create_blast_db(target_sequences)
#
#     # Use seq2 as the query
#     query_sequence = target_sequences["seq2"]
#
#     # Run BLAST with the query sequence
#     run_blast(query_sequence)
#
#
# if __name__ == "__main__":
#     main()
