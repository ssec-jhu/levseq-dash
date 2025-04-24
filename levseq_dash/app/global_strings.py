# -----------------------------
# General App Strings
# -----------------------------
web_title = "Levseq Dashboard"
nav_lab = "Lab Dashboard"
nav_upload = "Upload New Experiment"
nav_seq = "Explore Similar Sequences"

# -----------------------------
# Upload page strings
# -----------------------------
experiment_name = "Experiment Name"
experiment_date = "Experiment Date"
substrate_cas = "Substrate CAS Number"
product_cas = "Product CAS Number"
assay = "Assay"
tech = "Mutagenesis Method"

eppcr = "Error-prone PCR (epPCR)"
ssm = "Site saturation mutagenesis (SSM)"

experiment_name_placeholder = "Enter a name for your experiment."

button_upload_csv = "Upload Experiment Data"
button_upload_pdb = "Upload PDB/CIF"

# -----------------------------
# Lab Experiment page strings
# -----------------------------
lab_exp = "All experiments in the lab"
go_to = "Go to Experiment Dashboard"
lab_total = "Total Experiments"
lab_cas = "Used CAS"

# -----------------------------
# Experiment Page Strings
# -----------------------------
sequence = "Amino Acid Sequence"
experiment = "Experiment Name"
date = "Experiment Date"
upload_date = "Uploaded On"
technique = "Mutagenesis Method"
plates_count = "Plates Count"
cas_file = "Unique CAS"
cas_sub = "Substrate CAS"
cas_prod = "Product CAS"
viewer_header = "Protein Structure"
well_heatmap = "Plate Map"
top_variants = "Top Variants"
retention_function = "Retention Function"

tab_1 = "Experiment Dashboard"
tab_2 = "Related Variants"
view_all = "View all residues"
select_plate = "Select Plate ID"
select_cas = "Select CAS number"
select_property = "Select Property"


# -----------------------------
# Sequence Alignment - Related Variants specific
# -----------------------------

exp_seq_align_blurb = "Some instructions here..."
exp_seq_align_form_input = "Experiment Parent Sequence"
exp_seq_align_residue = "Residue for Lookup"
exp_seq_align_residue_help = (
    "Specify one or more residue indices from the experiment for lookup in the matching sequences."
)
exp_seq_align_query_info_1 = "Selected ExperimentID"
exp_seq_align_query_info_2 = "Query ExperimentID"

# -----------------------------
# Sequence Alignment Strings
# -----------------------------
seq_align_blurb = (
    "Lots of good stuff to write here about the algorithms being used: BLOSOM matrix and blastp algorithm ... !"
)
seq_align_form_input_sequence_default = (
    "MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAGGWAASNEHLIYYGSNPDTGAPIKEYLERVRARI"
    "GAWVLDTTCRDYNREWLDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAGIYPITATIKPFLAKKGGSPEDIEGMYNAWLKSVVLQVAIW"
    "SHPYTKENDR"
)
seq_align_form_placeholder = "Enter your query sequence here."
seq_align_form_input = "Query Sequence"
seq_align_form_threshold = "Threshold"
seq_align_form_threshold_default = "0.8"
seq_align_form_hot_cold = "# Hot/Cold to extract"
seq_align_form_hot_cold_n = "2"
seq_align_form_button_sequence_matching = "Find Matching Sequences"

# if you change below, make sure you also change
# the string lookup in js function seqAlignmentVis -> search for it in assets
hot = "H"
cold = "C"
hot_cold = "B"  # both hot and cold indicator
# this will be treated as markdown
markdown_note_matched_seq = """
- Number of matched sequences is calculated per experiment match not per cas.
- Each row represents experiment-cas information.
- An experiment _may_ have one or more alignments. Each will be represented per cas value
"""
# download ing residue information related
filename_download_residue_info = "matched_seq_aligned_experiment_hot_cold_residues"
download_results = " Download Results"
download_filtered = " Filtered"
download_original = " Unfiltered"
help_download = 'Download results in CSV format. Default is set to "Unfiltered" mode.'
help_download_mode_unfiltered = "Results will be downloaded without table filters applied."
help_download_mode_filtered = "Results will be downloaded WITH table filters applied."


header_experiment_id = "Experiment ID"
header_experiment_name = "Experiment Name"
header_cas_number = "CAS"
header_sub_cas = "Sub CAS"
header_prod_cas = "Prod CAS"
header_substitutions = "Substitutions"
header_fitness = "Fitness"
header_mutagenesis = "Mutagenesis Method"

# -----------------------------
#   DO NOT CHANGE PAST HERE
# -----------------------------
dbc_template_name = "flatly"

# These strings follow the column headers in the csv file.
c_cas = "cas_number"
c_plate = "plate"
c_well = "well"
c_alignment_count = "alignment_count"
# c_fitness = "fitness_value"
c_substitutions = "amino_acid_substitutions"
c_alignment_probability = "alignment_probability"
c_aa_sequence = "aa_sequence"
c_fitness_value = "fitness_value"

# These strings are used in various tables and dictionaries across the app > CC_*
cc_experiment_id = "experiment_id"
cc_substrate_cas = "substrate_cas_number"
cc_prod_cas = "product_cas_number"
cc_mutagenesis = "mutagenesis_method"

cc_ratio = "ratio"
cc_seq_alignment = "sequence_alignment"
cc_hot_indices_per_cas = "hot_residue_indices_per_cas"
cc_cold_indices_per_cas = "cold_residue_indices_per_cas"
cc_hot_and_cold_indices_per_cas = "hot_and_cold_residue_indices_per_cas"
cc_exp_residue_per_cas = "all_exp_residue_indices_per_cas"
cc_seq_alignment_mismatches = "seq_align_mismatch_indices"
cc_hot_cold_type = "variant_type"
cc_hot = "Hot"
cc_cold = "Cold"

# this list is the core data that is read from the CSV files, the rest is not needed
experiment_core_data_list = [
    c_cas,
    c_plate,
    c_well,
    c_alignment_count,
    c_substitutions,
    c_alignment_probability,
    c_aa_sequence,
    c_fitness_value,
]

# this is the data used for the experiment heatmap
# dropdown gets populated with this data
experiment_heatmap_properties_list = [
    c_fitness_value,  # must remain first
    c_alignment_count,
    c_alignment_probability,
    # "average_mutation_frequency", # removed
    # "p_value", # removed
    # "p_adj_value", # removed
]
