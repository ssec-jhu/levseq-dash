from levseq_dash.app.experiment import Experiment, MutagenesisMethod
from levseq_dash.app.graphs import creat_rank_plot
from levseq_dash.app.tests.conftest import path_exp_ep_cif, path_exp_ep_data, test_assay_list

sample_experiment = Experiment(
    experiment_data_file_path=path_exp_ep_data,
    experiment_name="ep_file",
    experiment_date="TBD",
    mutagenesis_method=MutagenesisMethod.epPCR,
    geometry_file_path=path_exp_ep_cif,
    assay=test_assay_list[2],
)

# if the graph requires the "ratio" information in the frame, run this:
# ratio_df = utils.calculate_group_mean_ratios_per_cas_and_plate(sample_experiment.data_df)

fig = creat_rank_plot(
    df=sample_experiment.data_df,
    plate_number=sample_experiment.plates[1],
    cas_number=sample_experiment.unique_cas_in_data[0],
)

fig.show()
