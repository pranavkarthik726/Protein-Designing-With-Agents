from vina import Vina
import tempfile
import os

try:
    import meeko
except ImportError:
    raise ImportError("The 'meeko' package is required for PDB to PDBQT conversion. Install with 'pip install meeko'.")

class VinaDocking:
    """
    A wrapper class for performing AutoDock Vina docking runs in Python,
    with automatic conversion of receptor PDB files to PDBQT.

    Attributes:
        v (Vina): The Vina instance.
        receptor_input (str): Path to the receptor file (PDB or PDBQT).
        ligand_path (str): Path to the ligand PDBQT file.
        center (list of float): [x, y, z] coordinates for the search box center.
        box_size (list of float): [size_x, size_y, size_z] dimensions of the search box in Å.
        receptor_pdbqt (str): Path to the converted receptor PDBQT file.
    """
    def __init__(self, receptor_input, ligand_path, center, box_size, sf_name='vina'):
        """
        Initialize the docking engine.

        Args:
            receptor_input (str): Path to receptor file (PDB or PDBQT).
            ligand_path (str): Path to ligand PDBQT.
            center (list of float): Center of search box [x, y, z].
            box_size (list of float): Box dimensions [size_x, size_y, size_z].
            sf_name (str): Scoring function name (default 'vina').
        """
        self.v = Vina(sf_name=sf_name)
        self.receptor_input = receptor_input
        self.ligand_path = ligand_path
        self.center = center
        self.box_size = box_size
        self.receptor_pdbqt = None

    def _convert_receptor(self):
        """
        Convert receptor from PDB to PDBQT using Meeko, if needed.
        """
        if self.receptor_input.lower().endswith('.pdbqt'):
            self.receptor_pdbqt = self.receptor_input
            return

        # Use Meeko to prepare and convert
        prep = meeko.MoleculePreparation()
        prep.prepare(self.receptor_input)
        pdbqt_str = prep.write_pdbqt_string()

        # Write to a temporary file
        fd, tmp_path = tempfile.mkstemp(suffix='.pdbqt')
        os.close(fd)
        with open(tmp_path, 'w') as f:
            f.write(pdbqt_str)
        self.receptor_pdbqt = tmp_path

    def load_structures(self):
        """
        Load receptor (converting if needed) and ligand into the Vina instance.
        """
        # Ensure receptor is in PDBQT
        self._convert_receptor()

        self.v.set_receptor(self.receptor_pdbqt)
        self.v.set_ligand_from_file(self.ligand_path)

    def define_search_space(self):
        """
        Define the docking search space by computing Vina maps.
        """
        self.v.compute_vina_maps(center=self.center, box_size=self.box_size)

    def score_initial(self):
        """
        Score the initial ligand pose (before docking).

        Returns:
            float: Initial binding affinity (kcal/mol).
        """
        return self.v.score()[0]

    def minimize_initial(self):
        """
        Perform local optimization of the initial pose.

        Returns:
            float: Score after local minimization (kcal/mol).
        """
        return self.v.optimize()[0]

    def dock(self, exhaustiveness=8, n_poses=5):
        """
        Run the docking search.

        Args:
            exhaustiveness (int): Search thoroughness (higher is slower).
            n_poses (int): Number of top poses to generate.
        """
        self.v.dock(exhaustiveness=exhaustiveness, n_poses=n_poses)

    def write_poses(self, out_path, n_poses=5, overwrite=True):
        """
        Write docked poses to a PDBQT file.

        Args:
            out_path (str): Output file path.
            n_poses (int): Number of poses to write.
            overwrite (bool): Overwrite existing file if True.
        """
        self.v.write_poses(out_path, n_poses=n_poses, overwrite=overwrite)

    def get_results(self, n_poses=5):
        """
        Retrieve docking results.

        Args:
            n_poses (int): Number of poses to retrieve.

        Returns:
            list of tuples: [(pose_coords, score, rmsd), ...]
        """
        return self.v.poses(n_poses=n_poses, return_rmsd=True)