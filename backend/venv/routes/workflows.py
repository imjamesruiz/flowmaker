# routes/workflows.py
from fastapi import APIRouter
from models.workflow import Workflow
from typing import Dict

router = APIRouter()
db: Dict[str, Workflow] = {}

@router.post("/workflows")
def create_workflow(workflow: Workflow):
    db[workflow.id] = workflow
    return {"message": "Workflow saved"}

@router.get("/workflows/{workflow_id}")
def get_workflow(workflow_id: str):
    return db.get(workflow_id)
