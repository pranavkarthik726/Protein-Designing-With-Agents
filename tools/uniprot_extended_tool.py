
from crewai.tools import tool
from tools import alpha_fold_fetch
import json
import requests
def uniprot_extended_tool():
    dir = r"/home/bharath-sooryaa-m/Documents/BIO/proj/Protein-Designing-With-Agents"
    @tool(name="uniprot_fetch_tool", platform="protein_designing_with_agents", description="This tool provides an acces to fetch data from.")
    def uniprot_fetch_tool(self,query:json, format="json"):
        url = "https://rest.uniprot.org/uniprotkb/search"
        params = {
            "query": query,
            "format": "json",
            "size": 500 #adjust as needed.
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            filename = f"cache/uniprot/{data['results'][0]['primaryAccession'].replace(' ', '_')}.json"
            with open(filename, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Data saved to {filename}")
            try:
                alpha_fold_fetch.fetch_from_alphafolddb(data['results'][0]['uniProtKBCrossReferences'][11]["id"])
            except: 
                print("No AlphaFoldDB entry found for the given entry ID.")
            return data

        except requests.exceptions.RequestException as e:
            print(f"Error during UniProt API request: {e}")
            return None
        except ValueError as e: # Catch JSON decoding errors.
            print(f"Error decoding JSON: {e}")
            return None


    @tool("get_protein__site_info")
    def get_protein__site_info(self,protein_id: str) -> str:
        """Fetches the protein site information from cache."""
        loc = r"{dir}/cache/uniprot/{protein_id}.json".format(protein_id=protein_id,dir=self.dir)
        with open(loc, 'r') as f:
            data = json.load(f)
            print("used")
            return str(data['results'][0]['features'])
        print("No data found")
        return None