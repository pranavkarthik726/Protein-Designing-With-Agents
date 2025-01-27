from crewai.tools import BaseTool
import requests
import json
import os

class Uniprot(BaseTool):
    name:str = "Uniprot databse" 
    description: str="Search Uniprot database for the required protein informations"
    
    def _run(self,query:str)->str:
        """
        SEACRH UNIPROT FOR REQUIRED INFO
        """
        url = f"https://www.uniprot.org/uniprot/{query}.json"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            return json.dumps(data, indent=4)
        else:
            return f"Error: Unable to fetch data for {query}. Status code: {response.status_code}"