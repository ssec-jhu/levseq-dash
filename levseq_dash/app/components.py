import dash_bootstrap_components as dbc


def get_label(string):
    return dbc.Label(string, width=3, className="fs-6")


def get_top_variant_column_defs():
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
            "cellStyle": {
                "function": """
                function(params) {
                    let value = params.value;
                    let min = 0;
                    let max = 1000000;

                    if (value === null || value === undefined) return {}; // Handle missing values

                    let percent = (value - min) / (max - min);
                    percent = Math.max(0, Math.min(1, percent));  // Clamp between 0 and 1

                    let red = Math.round(255 * (1 - percent));
                    let green = Math.round(255 * percent);
                    let blue = 100; // Keeps a soft tint

                    return { backgroundColor: `rgb(${red}, ${green}, ${blue})`, color: 'black' };
                }
                """
            },
        },
    ]


def get_all_experiments_column_defs():
    return [
        {"headerCheckboxSelection": True, "checkboxSelection": True, "headerName": "", "width": 50},  # Checkbox column
        {
            "field": "experiment_id",
            "filter": "agNumberColumnFilter",
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
