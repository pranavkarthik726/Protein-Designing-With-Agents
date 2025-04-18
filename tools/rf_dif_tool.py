import os
import shutil
import tempfile
import subprocess

def run_rf_diffusion(script_str, pdb_file_path):
    """
    Runs RF Diffusion by executing a provided script and processing a PDB file.

    Parameters:
        script_str (str): A string containing the Python script to be executed.
        pdb_file_path (str): The path to the PDB file that is used by RF Diffusion.

    Returns:
        str: The path to the output PDB file produced by the script.

    Raises:
        Exception: If script execution fails or the expected output file is not found.
    """
    # Configuration parameters
    CONDA_ENV_PATH = "/home/bharath-sooryaa-m/anaconda3/envs/SE3nv/bin/python"
    WORKING_DIR = "/home/bharath-sooryaa-m/RFdiffusion/examples"
    INPUT_PDB_DIR = os.path.join(WORKING_DIR, "input_pdbs")

    os.makedirs(INPUT_PDB_DIR, exist_ok=True)


    pdb_filename = os.path.basename(pdb_file_path)
    target_pdb_path = os.path.join(INPUT_PDB_DIR, pdb_filename)


    shutil.copy2(pdb_file_path, target_pdb_path)

    # Save the provided script string to a temporary file in the working directory
    with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".py", dir=WORKING_DIR) as tmp_script:
        tmp_script.write(script_str)
        script_temp_path = tmp_script.name

    # Build the command to execute the script
    command = f"{CONDA_ENV_PATH} {script_str}"
    print(f"Executing command: {command}")

    try:
        # Run the command in the specified working directory
        subprocess.run(command, shell=True, cwd=WORKING_DIR, check=True)
    except subprocess.CalledProcessError as e:
        os.unlink(script_temp_path)
        raise Exception(f"Script execution failed: {e}") from e
    return "SUCECSS"
    # Define the expected output path
'''    output_pdb = os.path.join(WORKING_DIR, "example_outputs/C6_oligo_0000.pdb")

    # Check if the output file was generated
    if not os.path.exists(output_pdb):
        os.unlink(script_temp_path)
        raise Exception("Output file not found")

    # Remove the temporary script file
    os.unlink(script_temp_path)'''

    