from crewai.tools import BaseTool
import requests
import json
import os
import sys
import json
import requests
from prettytable import PrettyTable


class Uniprot(BaseTool):
    name:str = "Uniprot databse" 
    description: str="Search Uniprot database for the required protein informations"
    
    PROTEINS_API = "https://www.ebi.ac.uk/proteins/api"

    def get_url(url,**kwargs):
        
        response = requests.get(url, **kwargs)
        
        if not response.ok:
            print(response.text)
            response.raise_for_status()
            return "Error"
        print('returned')
        return response
    def _run(self,query:str)->str:
        """
        SEACRH UNIPROT FOR REQUIRED INFO
        """
        WEBSITE_API = "https://rest.uniprot.org/uniprotkb/stream?compressed=false"
        url = WEBSITE_API + query
        response = get_url(url)
        if response != "Error":
            data = response.json()
            return json.dumps(data, indent=4)
        else:
            return f"Error: Unable to fetch data for {query}"
