# tasks.py
from celery_app import celery_app

@celery_app.task
def execute_node(node_id, data):
    print(f"Executing {node_id} with {data}")
    return {"status": "done", "node": node_id}
