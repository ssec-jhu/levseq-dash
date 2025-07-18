import dash_bootstrap_components as dbc
from dash import html

from levseq_dash.app.components import vis

primary_bold = "text-primary fw-bold"


def get_layout():
    # you can convert this div into a dbc.Container but note that it will add a
    # lot of margins and padding around this by default. Maybe that is needed
    # if not much text here
    return html.Div(
        [
            html.H4("Overview & Design Philosophy", className="page-title"),
            html.Hr(),
            html.Div(
                [
                    html.P(
                        "The Directed Evolution Database (DEDB) Dashboard is a specialized visualization tool for "
                        "analyzing directed evolution experiments in protein engineering. "
                        "This dashboard enables researchers to "
                        "explore sequence-function relationships, identify beneficial and detrimental "
                        "mutations, and make data-driven decisions for protein design."
                    ),
                    html.P("DEDB Dashboard was designed with three core principles in mind:", className="mb-3"),
                    html.Ol(
                        [
                            html.Li(
                                [
                                    html.Span("Data Integrity: ", className=primary_bold),
                                    "Providing accurate, unbiased representations of experimental data",
                                ],
                                className="mb-2",
                            ),
                            html.Li(
                                [
                                    html.Span("Visual Clarity: ", className=primary_bold),
                                    "Creating intuitive visualizations that highlight meaningful patterns",
                                ],
                                className="mb-2",
                            ),
                            html.Li(
                                [
                                    html.Span("Research Efficiency: ", className=primary_bold),
                                    "Streamlining the analysis workflow to accelerate discovery",
                                ]
                            ),
                        ],
                        className="mb-4",
                    ),
                    html.P(
                        "By combining these principles, we've created a tool that helps researchers gain deeper "
                        "insights into their directed evolution experiments and make more informed decisions about "
                        "protein design strategies."
                    ),
                ],
                className="px-5",
            ),
            html.H4("Core Functionality", className="page-title mt-4"),
            html.Hr(),
            html.Div(
                [
                    html.Div(
                        [
                            html.H5("Sequence Analysis", className=primary_bold),
                            html.P(
                                "The dashboard provides comprehensive tools for analyzing protein sequences "
                                "from directed evolution experiments. Our sequence alignment algorithms help "
                                "identify patterns of conservation, mutation hotspots, and evolutionary "
                                "relationships"
                                "between variants."
                            ),
                        ],
                    ),
                    html.Div(
                        [
                            html.H5("Structure Visualization", className=primary_bold),
                            html.P(
                                "Integrated 3D molecular viewers allow researchers to examine protein "
                                "structures in "
                                "detail. By mapping sequence information onto structural models, users can gain "
                                "insights into"
                                "how mutations"
                                "affect protein folding, active sites, and functional domains."
                            ),
                        ],
                    ),
                    html.Div(
                        [
                            html.H5("Fitness Landscape Exploration", className=primary_bold),
                            html.P(
                                "Interactive heatmaps and ranking plots visualize the fitness landscape of your "
                                "protein library. These visualizations make it easy to identify "
                                "beneficial mutations (hot spots) that improve function and detrimental "
                                "mutations (cold spots) that should be avoided."
                            ),
                        ],
                    ),
                    html.Div(
                        [
                            html.H5("Comparative Analysis", className=primary_bold),
                            html.P(
                                "Compare sequences and structures across multiple experiments to track "
                                "evolutionary trajectories and identify convergent solutions. "
                                "The multi-view integration connects different data representations "
                                "for comprehensive understanding."
                            ),
                        ],
                    ),
                ],
                className="px-5",
            ),
            html.Div(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.H4("Key Features", className="page-title"),
                                    html.Hr(),
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Span("Data Management: ", className=primary_bold),
                                                    html.Span(
                                                        "Upload, organize, and navigate through experimental datasets"
                                                    ),
                                                ],
                                                className="mb-2",
                                            ),
                                            html.Div(
                                                [
                                                    html.Span("Sequence Alignment: ", className=primary_bold),
                                                    html.Span(
                                                        "Configure alignment parameters to identify related sequences"
                                                    ),
                                                ],
                                                className="mb-2",
                                            ),
                                            html.Div(
                                                [
                                                    html.Span("Interactive Filtering: ", className=primary_bold),
                                                    html.Span(
                                                        "Focus on specific regions, mutation types, or fitness ranges"
                                                    ),
                                                ],
                                                className="mb-2",
                                            ),
                                            html.Div(
                                                [
                                                    html.Span("Statistical Analysis: ", className=primary_bold),
                                                    html.Span(
                                                        "View distribution plots and statistical summaries of your data"
                                                    ),
                                                ],
                                                className="mb-2",
                                            ),
                                            html.Div(
                                                [
                                                    html.Span("Customizable Visualizations: ", className=primary_bold),
                                                    html.Span(
                                                        "Adjust display settings to highlight features of interest"
                                                    ),
                                                ],
                                                className="mb-2",
                                            ),
                                            html.Div(
                                                [
                                                    html.Span("Exportable Results: ", className=primary_bold),
                                                    html.Span(
                                                        "Save graphs, tables, and analysis results for "
                                                        "publications or presentations"
                                                    ),
                                                ]
                                            ),
                                        ],
                                        className="px-5",
                                    ),
                                ]
                            ),
                            dbc.Col(
                                [
                                    html.H4("Use Cases", className="page-title"),
                                    html.Hr(),
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Span("Directed Evolution Projects: ", className=primary_bold),
                                                    html.Span(
                                                        "Track the progress of evolutionary campaigns and identify "
                                                        "successful design strategies"
                                                    ),
                                                ],
                                                className="mb-2",
                                            ),
                                            html.Div(
                                                [
                                                    html.Span("Mutation Effect Analysis: ", className=primary_bold),
                                                    html.Span(
                                                        "Systematically assess how specific mutations "
                                                        "affect protein function"
                                                    ),
                                                ],
                                                className="mb-2",
                                            ),
                                            html.Div(
                                                [
                                                    html.Span(
                                                        "Structure-Function Relationships: ", className=primary_bold
                                                    ),
                                                    html.Span(
                                                        "Correlate sequence changes with structural features "
                                                        "and functional outcomes"
                                                    ),
                                                ],
                                                className="mb-2",
                                            ),
                                            html.Div(
                                                [
                                                    html.Span("Protein Engineering: ", className=primary_bold),
                                                    html.Span(
                                                        "Make informed decisions about which mutations to "
                                                        "combine in the next generation of designs"
                                                    ),
                                                ],
                                                className="mb-2",
                                            ),
                                            html.Div(
                                                [
                                                    html.Span(
                                                        "Evolutionary Pathway Exploration: ", className=primary_bold
                                                    ),
                                                    html.Span(
                                                        "Visualize the evolutionary trajectories "
                                                        "of successful protein variants"
                                                    ),
                                                ],
                                                className="mb-2",
                                            ),
                                        ],
                                        className="px-5",
                                    ),
                                ]  # end of col
                            ),
                        ],
                    ),
                ],
            ),
            html.H4("Technical Details", className="page-title mt-4"),
            html.Hr(),
            html.Div(
                [
                    html.P(
                        "The Directed Evolution Database Dashboard is built using a modern technology stack "
                        "optimized for scientific visualization:"
                    ),
                    html.Div(
                        [
                            html.Span("Frontend: ", className=primary_bold),
                            html.Span("Dash/Plotly framework with Bootstrap styling"),
                        ],
                        className="mb-2",
                    ),
                    html.Div(
                        [
                            html.Span("Data Tables: ", className=primary_bold),
                            html.Span("Dash AG Grid for advanced filtering and sorting capabilities"),
                        ],
                        className="mb-2",
                    ),
                    html.Div(
                        [
                            html.Span("Sequence Analysis: ", className=primary_bold),
                            html.Span("BioPython libraries for alignment algorithms"),
                        ],
                        className="mb-2",
                    ),
                    html.Div(
                        [
                            html.Span("Molecular Visualization: ", className=primary_bold),
                            html.Span("Dash Molstar for interactive protein structure rendering"),
                        ],
                        className="mb-2",
                    ),
                    html.Div(
                        [
                            html.Span("Data Processing: ", className=primary_bold),
                            html.Span("NumPy and Pandas for efficient data manipulation"),
                        ],
                        className="mb-2",
                    ),
                ],
                className="px-5",
            ),
            html.H4("Getting Started", className="page-title mt-4"),
            html.Hr(),
            html.Div(
                [
                    html.Ol(
                        [
                            html.Li(
                                [
                                    html.Span("Upload Data: ", className=primary_bold),
                                    html.P(
                                        [
                                            "To upload your sequence and fitness data, please ",
                                            html.I("use the local instance"),
                                            ". This functionality is disabled on the public version to preserve "
                                            "data integrity and protect your privacy. "
                                            "Once your data is added locally, "
                                            "your data will appear alongside other experiments. If you wish to "
                                            "make your data public, first validate the upload "
                                            "on the local instance"
                                            "to ensure everything appears as intended. When satisfied with the "
                                            "visualization, please take screenshots of the "
                                            "dashboard and email them "
                                            "to us at: ylong[at]caltech[dot]edu, "
                                            "along with the upload files and "
                                            "the required metadata. For more information, refer to our ",
                                            html.A(
                                                "GitHub repository",
                                                href="https://github.com/ssec-jhu/levseq-dash",
                                                target="_blank",
                                            ),
                                            ".",
                                        ]
                                    ),
                                ],
                                className="mb-2",
                            ),
                            html.Li(
                                [
                                    html.Span("Explore Experiments: ", className=primary_bold),
                                    html.P("Select an experiment."),
                                ],
                                className="mb-2",
                            ),
                            html.Li(
                                [
                                    html.Span("Configure Settings: ", className=primary_bold),
                                    html.P("Adjust visualization parameters to suit your analysis needs."),
                                ],
                                className="mb-2",
                            ),
                            html.Li(
                                [
                                    html.Span("Explore Results: ", className=primary_bold),
                                    html.P("Interact with plots, tables, and 3D models to explore your data."),
                                ]
                            ),
                            html.Li(
                                [
                                    html.Span("Compare Sequences: ", className=primary_bold),
                                    html.P("Use alignment tools to find related sequences and shared motifs."),
                                ]
                            ),
                            html.Li(
                                [
                                    html.Span("Export Findings: ", className=primary_bold),
                                    html.P("Download visualizations and data for further analysis."),
                                ]
                            ),
                        ],
                        className="mb-4",
                    ),
                ],
                className="px-5",
            ),
            html.H4("Development Team", className="page-title mt-4"),
            html.Hr(),
            html.Div(
                [
                    html.P(
                        "The Directed Evolution Database Dashboard was developed and is maintained as a joint effort "
                        "between the Scientific Software Engineering Center (SSEC) at Johns Hopkins University "
                        "and the California Institute of Technology. The project brings together domain experts "
                        "in protein engineering, computational biology, data visualization, and "
                        "scientific software development to "
                        "create accessible and reproducible tools for the scientific community."
                    )
                ],
                className="px-5",
            ),
            html.H4("Acknowledgments", className="page-title mt-4"),
            html.Hr(),
            html.Div(
                [
                    "We gratefully acknowledge funding and support provided by:",
                    html.Ul(
                        [
                            html.Li(
                                [
                                    "The Scientific Software Engineering Center at Johns Hopkins University ",
                                    html.A("(SSEC-JHU)", href="https://ai.jhu.edu/ssec/", target="_blank"),
                                ]
                            ),
                            html.Li(
                                [
                                    "The generosity of Eric and Wendy Schmidt by recommendation of the ",
                                    html.A(
                                        "Schmidt Sciences Program.",
                                        href="https://www.schmidtsciences.org/",
                                        target="_blank",
                                    ),
                                ]
                            ),
                            html.Li(["NSF Grant(s): TBD"]),
                        ],
                    ),
                    "We also thank collaborators and users whose feedback has helped shape the design "
                    "and functionality of this tool.",
                ],
                className="px-5",
            ),
            html.H4("GitHub & Support", className="page-title mt-4"),
            html.Hr(),
            html.Div(
                [
                    "The source code for the DEDB Dashboard is open-source and available on ",
                    html.A("GitHub", href="https://github.com/ssec-jhu/levseq-dash", target="_blank"),
                    html.P(
                        "If you encounter a bug, would like to request a feature, or wish to contribute, "
                        "please open an issue on the GitHub Issues page."
                    ),
                ],
                className="px-5",
            ),
            html.H4("Citation", className="page-title mt-4"),
            html.Hr(),
            html.Div(
                [
                    "If you use the DEDB Dashboard in your research, please cite both the paper and the software:",
                    html.Ul(
                        [
                            html.Li("Paper Citation: [TBD]"),
                            html.Li(
                                [
                                    "Software Citation: ",
                                    html.A(
                                        "Zenodo DOI", href="https://doi.org/10.5281/zenodo.15880411", target="_blank"
                                    ),
                                ]
                            ),
                        ]
                    ),
                ],
                className="px-5",
            ),
        ],
        className=vis.main_page_class,
    )
