import requests
import urllib.parse
from crewai.tools.structured_tool import CrewStructuredTool
from pydantic import BaseModel, Field
from typing import List, Literal
import alpha_fold_fetch

# Define allowed key names as Literals
AllowedKeys = Literal["cc_function", "organism_id"]  # Adjust as needed
Operator = Literal["AND", "OR"]  # Define operators

class QueryItem(BaseModel):
    """
    Represents a single query item with a key-value pair.
    - key: Must be one of the predefined allowed keys.
    - value: A string representing the value associated with the key.
    """
    key: AllowedKeys
    value: str

class APIQuery(BaseModel):
    """
    Represents a UniProt API query format.
    - queries: A list of QueryItem objects containing key-value pairs.
    - operator: Specifies whether the queries should be combined using "AND" or "OR".
    """
    queries: List[QueryItem]
    operator: Operator = "AND"

# Function to construct and execute UniProt queries
def get_uniprot(query_data: APIQuery):
    if not query_data.queries:
        raise ValueError("At least one query item must be provided.")
    
    # Build query string
    query_parts = [f'({item.key}:"{item.value}")' for item in query_data.queries]
    combined_query = f' {query_data.operator} '.join(query_parts)
    encoded_query = urllib.parse.quote(combined_query)
    url = f"https://rest.uniprot.org/uniprotkb/search?format=json&query={encoded_query}&size=1"
    
    print("Requesting URL:", url)
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print("Error querying UniProt:", e)
        return None

    if not data:
        print("No UniProt entries found for query:", combined_query)
        return None
    try:
        alpha_fold_fetch.fetch_from_alphafolddb(data['results'][0]['uniProtKBCrossReferences'][11]["id"])
    except: 
        print("No AlphaFoldDB entry found for the given entry ID.")
    return data

# Wrapper function that calls the get_uniprot function
def uniprot_tool_wrapper(input: APIQuery) -> dict:
    result = get_uniprot(input)
    if result is None:
        return {"error": "No data found or an error occurred while querying UniProt."}
    return result

# Create and return the structured tool for UniProt querying
def create_uniprot_tool():
    return CrewStructuredTool.from_function(
        name="UniProt Fetcher",
        description="Fetches UniProt entries based on multiple query parameters using the UniProt REST API.",
        args_schema=APIQuery,
        func=uniprot_tool_wrapper,
    )