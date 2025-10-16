from pathlib import Path

from levseq_dash.app.components.graphs import creat_rank_plot, create_ssm_plot
from levseq_dash.app.data_manager.experiment import Experiment

test_data = Path(__file__).parent.parent.resolve() / "levseq_dash" / "app" / "tests" / "test_data"
data_path = Path(__file__).parent.parent.resolve() / "levseq_dash" / "app" / "data"

ssm = "flatten_ssm_processed_xy_cas"
eppcr = "flatten_ep_processed_xy_cas"

ssm_exp = Experiment(
    experiment_data_file_path=test_data / ssm / f"{ssm}.csv",
    geometry_file_path=test_data / ssm / f"{ssm}.cif",
)

eppcr_exp = Experiment(
    experiment_data_file_path=test_data / eppcr / f"{eppcr}.csv",
    geometry_file_path=test_data / eppcr / f"{eppcr}.cif",
)

fig = creat_rank_plot(
    df=eppcr_exp.data_df,
    plate_number=eppcr_exp.plates[1],
    smiles=eppcr_exp.unique_smiles_in_data[0],
)

# if the graph requires the "ratio" information in the frame, run this:
# ratio_df = utils.calculate_group_mean_ratios_per_cas_and_plate(sample_experiment.data_df)

fig = creat_rank_plot(eppcr_exp.data_df, eppcr_exp.plates[1], eppcr_exp.unique_smiles_in_data[0])
# fig.show()

fig = create_ssm_plot(ssm_exp.data_df, ssm_exp.unique_smiles_in_data[0], 59)
fig.show()

fig = create_ssm_plot(ssm_exp.data_df, ssm_exp.unique_smiles_in_data[0], 93)
fig.show()

fig = create_ssm_plot(ssm_exp.data_df, ssm_exp.unique_smiles_in_data[0], 149)
fig.show()

dmsdb_4442_ssm = "DMSDB-4442-30311dbb-3d05-457f-8edf-d214a17d5711"
dmsdb_4442_ssm_exp = Experiment(
    experiment_data_file_path=data_path / dmsdb_4442_ssm / f"{dmsdb_4442_ssm}.csv",
    geometry_file_path=data_path / dmsdb_4442_ssm / f"{dmsdb_4442_ssm}.csv",
)

fig = create_ssm_plot(dmsdb_4442_ssm_exp.data_df, dmsdb_4442_ssm_exp.unique_smiles_in_data[0], 106)
fig.show()
fig = create_ssm_plot(dmsdb_4442_ssm_exp.data_df, dmsdb_4442_ssm_exp.unique_smiles_in_data[0], 107)
fig.show()
fig = create_ssm_plot(dmsdb_4442_ssm_exp.data_df, dmsdb_4442_ssm_exp.unique_smiles_in_data[0], 105)
fig.show()
