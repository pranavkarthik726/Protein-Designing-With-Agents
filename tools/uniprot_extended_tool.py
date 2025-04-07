import json
import os
import requests
from pathlib import Path
from tools import alpha_fold_fetch #importing tools alpha_fold_fetch


class toolset:
    dir = ""
    def __init__(self,dir):
        self.dir = dir
    def get_protein__site_info(self,protein_id: str) -> str:
        """Fetches the protein site information from cache."""
        loc = r"{parent_path}/uniprot/{protein_id}.json".format(parent_path=self.dir, protein_id=protein_id)
        with open(loc, 'r') as f:
            data = json.load(f)
            print("used")
            return str(data['features'])
        return "No data found"
    def uniprot_fetch_tool(self,query: str) -> str:
        """This tool provides an acces to fetch data from UniProtKB using the UniProt REST API.
        the input has to be strictly a string """
        url = "https://rest.uniprot.org/uniprotkb/search"
        params = {
            "query": query,
            "format": "json",
            "size": 5 #adjust as needed.
        }

        try:
            response = requests.get(url, params=params)
            print(response.url)
            response.raise_for_status() 
            data = response.json()
            for protien in data['results']:
                filename = r"{parent}/uniprot/{file_name}.json".format(parent=self.dir,file_name=protien['primaryAccession'].replace(' ', '_'))
                with open(filename, "w") as f:
                    json.dump(protien, f, indent=4)
                print(f"Data saved to {filename}")
            try:
                for protien in data['results']:
                    for i in protien['uniProtKBCrossReferences']:
                        if i.get('database') == 'AlphaFoldDB':
                            apha_f_id = i.get('id')
                            break
                    print("Starting to search PDB file from AlphaFoldDB...")
                    alpha_fold_fetch.fetch_from_alphafolddb(apha_f_id,self.dir)
            except: 
                print("No AlphaFoldDB entry found for the given entry ID.")
                return "No AlphaFoldDB entry found for the given entry ID.,provide a query with take protein with structure"
            
            return str([protein['primaryAccession'] for protein in data['results']])

        except requests.exceptions.RequestException as e:
            print(f"Error during UniProt API request: {e}")
            return "Error during UniProt API request: {e}".format(e=e)
        except ValueError as e: # Catch JSON decoding errors.
            print(f"Error decoding JSON: {e}")
            return "Error decoding JSON: {e}".format(e=e)
    def get_all_sequence(self)->dict:
        """Fetches the protein sequence information from cache."""
        loc = r"{parent_path}/uniprot".format(parent_path=self.dir)
        seqlist = {}
        for filename in os.listdir(loc):
            if filename.endswith('.json'):
                with open(os.path.join(loc, filename), 'r') as f:
                    data = json.load(f)
                    try:
                        seqlist.update({data['primaryAccession']: data['sequence']['value']})
                    except KeyError:
                        print(f"Sequence not found in {filename}.")
        if seqlist:
            return seqlist
        return ["No sequence found"]
    def get_all_function(self)->dict:
        """Fetches the protein function information from cache."""
        loc = r"{parent_path}/uniprot".format(parent_path=self.dir)
        seqlist = {}
        for filename in os.listdir(loc):
            if filename.endswith('.json'):
                with open(os.path.join(loc, filename), 'r') as f:
                    data = json.load(f)
                    try:
                        seqlist.update({data['primaryAccession']: [func['texts'][0]['value'] for func in data['comments'] if func.get("commentType") == 'FUNCTION']})
                    except KeyError:
                        print(f"Sequence not found in {filename}.")
        if seqlist:
            return seqlist
        return ["No sequence found"]
    def Multiple_sequence_alignment(self) -> str:
        """Performs multiple sequence alignment using Clustal Omega."""
        proteins = self.get_all_sequence()
    def rfdifcom(self,script, pdb_id):
        """
        This function sends a request to the server to run a script with a PDB file.
        The server is expected to be running on localhost at port 5000.
        """
        try:
            SERVER_URL = "http://127.0.0.1:5000/run_script"  # Replace with actual server IP
            pdb_file_path = r"{parent}/pdb/{pdb_id}.pdb".format(parent=self.dir, pdb_id=pdb_id)


            with open(pdb_file_path, 'rb') as pdb_file:
                files = {
                    'script': script,
                    'pdb_file': pdb_file
                }
                response = requests.post(SERVER_URL, files=files)

            if response.status_code == 200:
                with open("output.pdb", "wb") as f:
                    f.write(response.content)
                print("PDB file received and saved as output.pdb")
            else:
                print("Error:", response.json())
        except requests.exceptions.RequestException as e:
            print(f"Error during request: {e}")
            return "Error during request: {e}".format(e=e)
        except FileNotFoundError:
            print(f"PDB file not found: {pdb_file_path}")
            return "PDB file not found: {pdb_file_path}".format(pdb_file_path=pdb_file_path)
        except Exception as e:
            print(f"An error occurred: {e}")
            return "An error occurred: {e}".format(e=e)
            