# models/workflow.py
from pydantic import BaseModel
from typing import List, Dict, Any

class Node(BaseModel):
    id: str
    type: str
    data: Dict[str, Any]

class Link(BaseModel):
    source: str
    target: str

class Workflow(BaseModel):
    id: str
    name: str
    nodes: List[Node]
    links: List[Link]
