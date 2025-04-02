# app strings
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
# Experiment Card Strings
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

view_all = "View all residues"
select_plate = "Select Plate ID"
select_cas = "Select CAS number"
select_property = "Select Property"

# -----------------------------
# Sequence Alignment page Strings
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
seq_align_form_threshold_default = "0.5"
seq_align_form_hot_cold = "# Hot&Cold to extract"
seq_align_form_hot_cold_n = "2"
seq_align_form_button_sequence_matching = "Find Matching Sequences"


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
cc_seq_alignment = "sequence_alignment"
cc_hot_residue_indices_per_cas = "hot_residue_indices_per_cas"
cc_cold_residue_indices_per_cas = "cold_residue_indices_per_cas"
cc_hot_and_cold_indices_per_cas = "hot_and_cold_residue_indices_per_cas"
cc_exp_residue_per_cas = "all_exp_residue_indices_per_cas"
cc_seq_alignment_mismatches = "seq_align_mismatch_indices"


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
