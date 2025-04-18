import os
import uuid
import datetime
from pathlib import Path

class StorageManager:
    def __init__(self, base_cache_dir="cache"):
        """
        Initializes the StorageManager with a base cache directory.
        Creates session-specific directories for storing PDB and UniProt data.
        """
        self.base_cache_dir = Path(base_cache_dir)
        self.session_id = self._generate_session_id()
        self.session_path = self.base_cache_dir / self.session_id
        self.pdb_path = self.session_path / "pdb"
        self.uniprot_path = self.session_path / "uniprot"

        self._initialize_storage()

    def _generate_session_id(self):
        """
        Generates a unique session ID using a timestamp and a UUID.
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        return f"session_{timestamp}_{unique_id}"

    def _initialize_storage(self):
        """
        Creates the necessary directories for the session.
        """
        try:
            # Create base cache directory if it doesn't exist
            self.base_cache_dir.mkdir(parents=True, exist_ok=True)

            # Create session-specific directories
            self.session_path.mkdir(parents=True, exist_ok=True)
            self.pdb_path.mkdir(parents=True, exist_ok=True)
            self.uniprot_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise RuntimeError(f"Failed to initialize storage directories: {e}")

    def get_session_id(self):
        """
        Returns the unique session ID.
        """
        return self.session_id

    def get_pdb_path(self):
        """
        Returns the path to the PDB directory for the session.
        """
        return self.pdb_path

    def get_uniprot_path(self):
        """
        Returns the path to the UniProt directory for the session.
        """
        return self.uniprot_path

    def get_session_path(self):
        """
        Returns the path to the session directory.
        """
        return self.session_path

    def __str__(self):
        """
        Returns a string representation of the StorageManager.
        """
        return f"StorageManager(session_id={self.session_id})"

# Example integration with the main project
if __name__ == "__main__":
    # Initialize the storage manager
    storage = StorageManager()

    # Print session details
    print(f"Session initialized: {storage.get_session_id()}")
    print(f"PDB path: {storage.get_pdb_path()}")
    print(f"UniProt path: {storage.get_uniprot_path()}")