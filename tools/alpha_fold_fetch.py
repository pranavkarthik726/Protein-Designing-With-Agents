import requests
import os
from pathlib import Path

# Change working directory to parent directory
current_path = Path.cwd()
parent_path = current_path.parent
os.chdir(parent_path)
def fetch_from_alphafolddb(entry_id):
    api_url = "https://alphafold.ebi.ac.uk/api/prediction/{entry_id}".format(entry_id=entry_id)
    response = requests.get(api_url)
    result = response.json()
    pdbUrl = result[0]['pdbUrl']
    '''try:
        pdbUrl  = result[0]['pdbUrl']
    except:
        pdbUrl = None
        print("No PDB file found for the given entry ID.")
        return'''
    Dir=r"cache/pdb".format(dir=dir)

    response = requests.get(pdbUrl)
    if response.status_code == 200:
            # Save the file locally
            with open(r"{Dir}/{pdb_id}.pdb".format(pdb_id=entry_id,Dir=Dir), "wb") as file:
                file.write(response.content)
            print("PDB file downloaded successfully.")
    else:
        print(f"Failed to download PDB file. Status code: {response.status_code}")