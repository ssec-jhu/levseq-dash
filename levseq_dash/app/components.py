import dash_bootstrap_components as dbc

from levseq_dash.app.example_aggrid_barchart import data_bars_dynamic, data_bars_hsv, dynamdata_bars_dynamic_2


def get_label(string):
    return dbc.Label(string, width=3, className="fs-6")


def get_top_variant_column_defs(df):
    # mean_value = df.loc[df["amino_acid_substitutions"] == "#PARENT#", "fitness_value"].mean()
    # df["ratio"] = df["fitness_value"] / mean_value

    mean_values = df[df["amino_acid_substitutions"] == "#PARENT#"].groupby("cas_number")["fitness_value"].mean()
    return [
        {
            "field": "cas_number",
            "headerName": "CAS #",
            "width": 180,
        },
        {
            "field": "plate",
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
        },
        {
            "field": "well",
            "width": 125,
        },
        {
            "field": "amino_acid_substitutions",
            "headerName": "Substitutions",
        },
        {
            "field": "fitness_value",
            "filter": "agNumberColumnFilter",
            "cellStyle": {"styleConditions": data_bars_dynamic(df, "fitness_value")},
            # TODO: this doens't work yet. it needs to color off fromt he mean
            # "cellStyle": {"styleConditions": dynamdata_bars_dynamic_2(df)}
        },
    ]


def get_all_experiments_column_defs():
    return [
        {"headerCheckboxSelection": True, "checkboxSelection": True, "headerName": "", "width": 50},  # Checkbox column
        {
            "field": "experiment_id",
            "filter": "agNumberColumnFilter",
            # "checkboxSelection": True,
        },
        {
            "field": "experiment_name",
        },
        {
            "field": "upload_time_stamp",
        },
        {
            "field": "experiment_time",
        },
        {
            "field": "sub_cas",
        },
        {
            "field": "prod_cas",
        },
        {
            "field": "assay",
        },
        {
            "field": "mutagenesis_method",
        },
        {
            "field": "plates_count",
            "filter": "agNumberColumnFilter",
        },
    ]
