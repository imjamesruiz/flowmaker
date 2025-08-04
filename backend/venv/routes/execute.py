# routes/execute.py
from fastapi import APIRouter
from tasks import execute_node

router = APIRouter()

@router.post("/run-node")
def run_node(node: dict):
    task = execute_node.delay(node["id"], node["data"])
    return {"task_id": task.id}
