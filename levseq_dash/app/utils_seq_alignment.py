import re

from levseq_dash.app import global_strings as gs


def parse_alignment_pipes(alignment_str, hot_indices, cold_indices):
    # TODO: need to add condition where hot and cold indices are not provided, maybe break this up into two functions
    """
    Utility function to parse the alignment string and reformat it for visualization in the dash table
    This function is tailored toward the results of the sequence aligner.
    Args:
        alignment_str: the alignment string output from biopython pairwise aligner
        hot_indices: list of indices with high function in the experiment
        cold_indices: list of indices with low function in the experiment

    Returns:
        a re-formatted string that also identifies the high and low functioning residue locations
        based on the input indices
    """
    # there are multiple groups of 4-pair lines
    # break up the string on the newline
    # the 4th line of each group is empty space
    lines = alignment_str.strip().split("\n")

    # parse each of the alignment strings in groups of 4 and merge into one big string
    target = ""
    pipes = ""
    query = ""
    seq_alignment_mismatches = []
    for i in range(0, len(lines), 4):
        target_striped = re.sub(r"^(query|target)?\s*\d*\s*", "", lines[i]).strip()
        pipes_stripped = re.sub(r"^(query|target)?\s*\d*\s*", "", lines[i + 1]).strip()
        query_stripped = re.sub(r"^(query|target)?\s*\d*\s*", "", lines[i + 2]).strip()

        # merge with the correct string
        target = target + target_striped
        pipes = pipes + pipes_stripped
        query = query + query_stripped

    # parse the pipes to find the mismatch indices which are identified by "."
    # NOTE: the indices on the protein start from 1 so add 1
    # TODO: this parsing needs to be checked, maybe I need to skip the gaps
    for i in range(len(pipes)):
        if pipes[i] == ".":
            seq_alignment_mismatches.append(str(i + 1))

    # parse over pipes and mark the hot spots and cold spots
    length = len(pipes)  # this also includes the text at the end which makes more than enough space
    hot_cold_spots = [" "] * length

    # put down the H first
    for index in hot_indices:
        index_int = int(index)
        # index_int can't be 0 because it comes from the experiment
        if index_int > 0:
            # NOTE: the indices on the protein start from 1 but the strings array start from 0 so subtract 1
            hot_cold_spots[index_int - 1] = gs.hot
        else:
            raise IndexError(f"Index {index_int} is out of the valid range (1 to {length})")

    # now mark C
    for index in cold_indices:
        index_int = int(index)
        if index_int > 0:
            # if this is already a hot spot, put a B for both
            if hot_cold_spots[index_int - 1] == gs.hot:
                hot_cold_spots[index_int - 1] = gs.hot_cold
            else:
                hot_cold_spots[index_int - 1] = gs.cold
        else:
            raise IndexError(f"Index {index_int - 1} is out of the valid range (1 to {length})")

    # merge the three strings into one long string for the table
    parsed_alignment = target + "\n" + pipes + "\n" + "".join(hot_cold_spots) + "\n" + query + "\n"

    return parsed_alignment, seq_alignment_mismatches


def gather_seq_alignment_data_per_cas(df_hot_cold_residue_per_cas, seq_match_data, exp_meta_data, seq_match_row_data):
    """
    This utility function is used to gather row data per cas for sequence alignment data on the matched sequences
    This function solely designed for the purpose of reusing code for gathering row data

    Args:
        df_hot_cold_residue_per_cas:  df where the list of hot and cold residue indices are listed peer cas
        seq_match_data: the sequence alignment data retrieved from the aligner
        exp_meta_data: the metadata associated with the experiment
        seq_match_row_data: the aggrid row data that is gathering the results over all the matched sequences

    Returns:
        seq_match_row_data:
        the aggrid row data that is gathering the results over all the matched sequences
    """
    # convert he df do a list of records
    dict_list = df_hot_cold_residue_per_cas.to_dict(orient="records")

    # for each cas in the list, create a row with the hot and cold residue list
    # associated with that CAS
    for cas_index in range(len(dict_list)):
        hot_residues = dict_list[cas_index][gs.cc_hot_indices_per_cas]
        cold_residues = dict_list[cas_index][gs.cc_cold_indices_per_cas]
        sub_residues = dict_list[cas_index][gs.cc_exp_residue_per_cas]  # TODO: do we need this

        parsed_alignment_string, mutation_indices = parse_alignment_pipes(
            alignment_str=seq_match_data[gs.cc_seq_alignment], hot_indices=hot_residues, cold_indices=cold_residues
        )
        per_cas_records = {}
        per_cas_records.update(seq_match_data)
        per_cas_records.update(dict_list[cas_index])
        per_cas_records.update(exp_meta_data)
        per_cas_records.update({gs.c_substitutions: sub_residues})
        # mutation_indices_str = ", ".join(map(str, mutation_indices))
        per_cas_records.update({gs.cc_seq_alignment_mismatches: mutation_indices})
        per_cas_records.update({gs.cc_seq_alignment: parsed_alignment_string})
        seq_match_row_data.append(per_cas_records)

    return seq_match_row_data


def gather_seq_alignment_data_for_experiment(df, seq_match_data, exp_meta_data, seq_match_row_data):
    """
    This utility function is used to gather row data for experiment related variants.
    This function solely designed for the purpose of reusing code for gathering row data
    """

    # convert the df do a list of records
    dict_list = df.to_dict(orient="records")

    # gather sequence alignment parsed string
    parsed_alignment_string, mutation_indices = parse_alignment_pipes(
        alignment_str=seq_match_data[gs.cc_seq_alignment], hot_indices=[], cold_indices=[]
    )

    for record in dict_list:
        # add the sequence alignment stats
        record.update(seq_match_data)
        # add the experiment meta data
        record.update(exp_meta_data)
        # add the mismatch indices and the
        record.update({gs.cc_seq_alignment_mismatches: mutation_indices})
        record.update({gs.cc_seq_alignment: parsed_alignment_string})
        seq_match_row_data.append(record)

    return seq_match_row_data
