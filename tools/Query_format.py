from pydantic import BaseModel, Field
from typing import List, Literal

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