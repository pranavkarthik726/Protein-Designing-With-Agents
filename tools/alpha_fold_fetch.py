import requests
dir = r"/home/bharath-sooryaa-m/Documents/BIO/proj/Protein-Designing-With-Agents"
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
    Dir=r"{dir}/cache/pdb".format(dir=dir)

    response = requests.get(pdbUrl)
    if response.status_code == 200:
            # Save the file locally
            with open(r"{Dir}/{pdb_id}.pdb".format(pdb_id=entry_id,Dir=Dir), "wb") as file:
                file.write(response.content)
            print("PDB file downloaded successfully.")
    else:
        print(f"Failed to download PDB file. Status code: {response.status_code}")