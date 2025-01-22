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
        },
    ]
