import json
import os
import requests
from pathlib import Path
from tools import alpha_fold_fetch #importing tools alpha_fold_fetch
#change to parent directory
current_path = Path.cwd()
parent_path = current_path.parent
os.chdir(parent_path)

class toolset:
    def get_protein__site_info(protein_id: str) -> str:
        """Fetches the protein site information from cache."""
        loc = r"{parent_path}/cache/uniprot/{protein_id}.json".format(parent_path=parent_path, protein_id=protein_id)
        with open(loc, 'r') as f:
            data = json.load(f)
            print("used")
            return str(data['results'][0]['features'])
        return "No data found"
    def uniprot_fetch_tool(query: str) -> str:
        """This tool provides an acces to fetch data from UniProtKB using the UniProt REST API.
        the input has to be strictly a string """
        url = "https://rest.uniprot.org/uniprotkb/search"
        params = {
            "query": query,
            "format": "json",
            "size": 1 #adjust as needed.
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status() 
            data = response.json()
            filename = f"cache/uniprot/{data['results'][0]['primaryAccession'].replace(' ', '_')}.json"
            with open(filename, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Data saved to {filename}")
            try:
                apha_f_id =0
                for i in data['results'][0]['uniProtKBCrossReferences']:
                    if i.get('database') == 'AlphaFoldDB':
                        apha_f_id = i.get('id')
                        break
                print(apha_f_id)
                alpha_fold_fetch.fetch_from_alphafolddb(apha_f_id)
            except: 
                print("No AlphaFoldDB entry found for the given entry ID.")
                return "No AlphaFoldDB entry found for the given entry ID.,provide a query with take protein with structure"
            return data['results'][0]['primaryAccession']

        except requests.exceptions.RequestException as e:
            print(f"Error during UniProt API request: {e}")
            return "Error during UniProt API request: {e}".format(e=e)
        except ValueError as e: # Catch JSON decoding errors.
            print(f"Error decoding JSON: {e}")
            return "Error decoding JSON: {e}".format(e=e)