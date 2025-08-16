// Workflow Types
export type NodeKind = "trigger" | "action" | "condition" | "transformer" | "webhook";

export interface WFNode {
  id: string;
  type: NodeKind;                // React Flow node.type too
  position: { x: number; y: number };
  data: { 
    name: string; 
    config?: any; 
    ports?: { 
      in?: string[]; 
      out?: string[] 
    } 
  };
}

export interface WFEdge {
  id: string;
  source: string; 
  sourceHandle?: string;
  target: string; 
  targetHandle?: string;
  label?: string; // e.g., "true"/"false"
}

export interface Workflow {
  id: string;
  name: string;
  nodes: WFNode[];
  edges: WFEdge[];
  viewport?: { x: number; y: number; zoom: number };
}

// API Response Types
export interface WorkflowResponse {
  id: string;
  name: string;
  description?: string;
  nodes: WFNode[];
  edges: WFEdge[];
  viewport?: { x: number; y: number; zoom: number };
  created_at: string;
  updated_at?: string;
}

export interface ExecutionResult {
  success: boolean;
  error?: string;
  logs: ExecutionLog[];
  outputs?: Record<string, any>;
  context?: Record<string, any>;
}

export interface ExecutionLog {
  node_id: string;
  node_type: string;
  node_name: string;
  status: 'success' | 'error';
  start_time: string;
  execution_time: number;
  input?: any;
  output?: any;
  error?: string;
  context_patch?: Record<string, any>;
}
