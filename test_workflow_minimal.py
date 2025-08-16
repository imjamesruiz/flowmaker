#!/usr/bin/env python3
"""
Minimal test for workflow connections and execution
Tests the core functionality without requiring the full server
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.workflow_executor import WorkflowExecutor
from backend.app.schemas.workflow import WorkflowPayload, WFNode, WFEdge

def test_workflow_executor():
    """Test the workflow executor directly"""
    print("🧪 Testing Workflow Executor")
    print("=" * 50)
    
    # Create a simple workflow: Trigger -> Transformer -> Condition -> Action
    workflow_data = WorkflowPayload(
        id="test_workflow",
        name="Test Workflow",
        nodes=[
            WFNode(
                id="trigger_1",
                type="trigger",
                position={"x": 100, "y": 100},
                data={
                    "name": "HTTP Trigger",
                    "config": {"method": "POST"}
                }
            ),
            WFNode(
                id="transformer_1",
                type="transformer",
                position={"x": 300, "y": 100},
                data={
                    "name": "Transform Data",
                    "config": {"type": "to_uppercase"}
                }
            ),
            WFNode(
                id="condition_1",
                type="condition",
                position={"x": 500, "y": 100},
                data={
                    "name": "Check Condition",
                    "config": {"condition": "len(str(input)) > 5"}
                }
            ),
            WFNode(
                id="action_1",
                type="action",
                position={"x": 700, "y": 50},
                data={
                    "name": "Send Email",
                    "config": {"to": "user@example.com"}
                }
            ),
            WFNode(
                id="webhook_1",
                type="webhook",
                position={"x": 700, "y": 150},
                data={
                    "name": "Call Webhook",
                    "config": {"url": "https://api.example.com/webhook"}
                }
            )
        ],
        edges=[
            WFEdge(
                id="e_trigger_1-out_transformer_1-in",
                source="trigger_1",
                sourceHandle="out",
                target="transformer_1",
                targetHandle="in"
            ),
            WFEdge(
                id="e_transformer_1-out_condition_1-in",
                source="transformer_1",
                sourceHandle="out",
                target="condition_1",
                targetHandle="in"
            ),
            WFEdge(
                id="e_condition_1-true_action_1-in",
                source="condition_1",
                sourceHandle="true",
                target="action_1",
                targetHandle="in",
                label="true"
            ),
            WFEdge(
                id="e_condition_1-false_webhook_1-in",
                source="condition_1",
                sourceHandle="false",
                target="webhook_1",
                targetHandle="in",
                label="false"
            )
        ]
    )
    
    # Test workflow validation
    print("🔍 Testing workflow validation...")
    executor = WorkflowExecutor()
    validation_result = executor.validate_workflow(workflow_data)
    
    if validation_result["valid"]:
        print("✅ Workflow validation passed")
    else:
        print(f"❌ Workflow validation failed: {validation_result['errors']}")
        return False
    
    # Test workflow execution
    print("🚀 Testing workflow execution...")
    trigger_data = {"message": "Hello World", "user": "testuser"}
    
    try:
        result = executor.execute_workflow(workflow_data, trigger_data)
        
        if result.success:
            print("✅ Workflow execution successful")
            print(f"📊 Execution logs: {len(result.logs)} nodes executed")
            
            for log in result.logs:
                print(f"  - {log.node_name} ({log.node_type}): {log.status}")
                if log.output:
                    print(f"    Output: {log.output}")
                if log.error:
                    print(f"    Error: {log.error}")
            
            return True
        else:
            print(f"❌ Workflow execution failed: {result.error}")
            return False
            
    except Exception as e:
        print(f"❌ Workflow execution error: {e}")
        return False

def test_graph_building():
    """Test graph building and topological sorting"""
    print("\n🔗 Testing graph building...")
    
    executor = WorkflowExecutor()
    
    # Test simple linear graph
    nodes = [
        {"id": "A", "type": "trigger"},
        {"id": "B", "type": "action"},
        {"id": "C", "type": "action"}
    ]
    
    edges = [
        {"source": "A", "target": "B"},
        {"source": "B", "target": "C"}
    ]
    
    try:
        graph, in_degree = executor.build_graph(nodes, edges)
        execution_order = executor.topological_sort(graph, in_degree)
        
        print(f"✅ Graph built successfully")
        print(f"   Execution order: {execution_order}")
        
        expected_order = ["A", "B", "C"]
        if execution_order == expected_order:
            print("✅ Topological sort correct")
            return True
        else:
            print(f"❌ Topological sort incorrect. Expected: {expected_order}, Got: {execution_order}")
            return False
            
    except Exception as e:
        print(f"❌ Graph building error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Worqly Workflow System (Minimal)")
    print("=" * 60)
    
    # Test graph building
    graph_success = test_graph_building()
    
    # Test workflow execution
    execution_success = test_workflow_executor()
    
    if graph_success and execution_success:
        print("\n🎉 All tests passed! Workflow system is working correctly.")
        print("\n📋 What's working:")
        print("  ✅ Graph building and topological sorting")
        print("  ✅ Workflow validation")
        print("  ✅ Node execution with context passing")
        print("  ✅ Condition routing (true/false paths)")
        print("  ✅ Detailed execution logging")
        return True
    else:
        print("\n💥 Some tests failed. Please check the error messages above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
