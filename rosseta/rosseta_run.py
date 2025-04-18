import pyrosetta
from pyrosetta.rosetta.protocols.relax import FastRelax

class PyRosettaWrapper:
    dir = ""
    def __init__(self, dir):
        """
        Initialize the PyRosettaWrapper with the directory for PDB files.
        """
        self.dir = dir
        print(f"PyRosettaWrapper initialized with directory: {self.dir}")
        
    
    def initialize_pyrosetta(self,extra_flags=""):
        """
        Initialize PyRosetta with optional extra flags.
        """
        pyrosetta.init(extra_flags)
        print("PyRosetta initialized.")

    def load_protein(self,pdb_id):
        """
        Load a protein structure from a PDB file into a PyRosetta pose.
        """
        try:
            pose = pyrosetta.pose_from_pdb(pdb_id)
            print(f"Loaded structure from {pdb_id} with {pose.total_residue()} residues.")
            return pose
        except Exception as e:
            print(f"Error loading PDB file {pdb_id}: {e}")
            return None

    def score_protein(self,pose, scorefxn=None):
        """
        Score the given pose using a full-atom score function.
        If no scorefxn is provided, the default full-atom score function is used.
        Returns the total score (REU).
        """
        if scorefxn is None:
            scorefxn = pyrosetta.get_fa_scorefxn()
        total_score = scorefxn(pose)
        print(f"Total Score: {total_score:.3f} REU")
        return total_score, scorefxn

    def relax_structure(self, pose, scorefxn, nstruct=1, output_pdb="relaxed_structure.pdb"):
        """
        Apply the FastRelax protocol to the structure and save the relaxed pose to a PDB file.
        Returns the relaxed pose.
        """
        # Create a copy of the pose to relax
        relaxed_pose = pyrosetta.Pose()
        relaxed_pose.assign(pose)
        
        fast_relax = FastRelax()
        fast_relax.set_scorefxn(scorefxn)
        
        # Apply relaxation nstruct times (for multiple models, if desired)
        for i in range(nstruct):
            fast_relax.apply(relaxed_pose)
        
        # Save the relaxed pose to a PDB file
        relaxed_pose.dump_pdb(output_pdb)
        print(f"Relaxed structure saved to {output_pdb}.")
        
        print("Relaxation complete.")
        return relaxed_pose

    def print_per_residue_energies(self,pose):
        """
        Print the per-residue energies for the given pose.
        """
        print("Per-residue energies:")
        # Access the energies from the pose object
        energies = pose.energies()
        for i in range(1, pose.total_residue() + 1):
            energy = energies.residue_total_energy(i)
            print(f"Residue {i}: {energy:.3f} REU")
    
    def run(self,pdb_file):
            # Initialize PyRosetta
 
        self.initialize_pyrosetta("-ex1 -ex2aro")
        # Load protein structure (update path as needed)
        pose = self.load_protein(pdb_file)
        if pose is None:
            raise SystemExit("Failed to load PDB file.")
        
        # Score the original structure
        initial_score, scorefxn = self.score_protein(pose)
        
        # Relax the structure
        pose_relaxed = self.relax_structure(pose, scorefxn)
        
        # Re-score the relaxed structure
        relaxed_score, _ = self.score_protein(pose_relaxed)
        
        # Print per-residue energies
        return initial_score,pose_relaxed, relaxed_score
            
