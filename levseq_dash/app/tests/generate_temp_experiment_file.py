import os
import shutil
import tempfile

from levseq_dash.app.tests.mutation_simulator import create_experiment_test_file


def generate_large_test_csv(base_csv_path):
    # Read the base CSV file
    cas_input = [
        "C1=CC=CC=C1",
        "C1=CC=CN=C1",
        "[*:1]C(N[C@@H](C(N[C@@H](C([*:2])=O)[*:4])=O)[*:3])=O.O",
        "[*:1]C(N[C@@H](C(O)=O)[*:3])=O.N[C@@H](C([*:2])=O)[*:4]",
        "C1=CC=CC=C1.O=C(O)C(F)(F)F",
    ]
    df = create_experiment_test_file(cas_input, 1000, 5)

    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix="levseq_test_")

    # Generate a unique experiment ID based on the temp directory
    experiment_id = f"MYTEST-{os.path.basename(temp_dir)}"

    # Create the experiment directory structure
    experiment_dir = os.path.join(temp_dir, experiment_id)
    os.makedirs(experiment_dir, exist_ok=True)

    # Save the CSV file with the same base name as experiment_id
    csv_filename = f"{experiment_id}.csv"
    csv_path = os.path.join(experiment_dir, csv_filename)
    df.to_csv(csv_path, index=False)

    # Copy supporting files (JSON and CIF) from the original directory
    # these files don't matter as long as there is something in the directory
    base_dir = os.path.dirname(base_csv_path)
    base_filename = os.path.splitext(os.path.basename(base_csv_path))[0]  # Get base filename without extension

    # Copy the corresponding JSON and CIF files with the experiment_id as base name
    for file_ext in [".json", ".cif"]:
        original_file = os.path.join(base_dir, f"{base_filename}{file_ext}")
        if os.path.exists(original_file):
            new_filename = f"{experiment_id}{file_ext}"
            new_file_path = os.path.join(experiment_dir, new_filename)
            shutil.copy2(original_file, new_file_path)
        else:
            raise Exception(f"Warning: {file_ext} file not found: {original_file}")

    return temp_dir, csv_path, experiment_id
