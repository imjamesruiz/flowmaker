export type DType = 'event' | 'json' | 'text' | 'any'

export interface Port {
  id: string
  dtype: DType
  required?: boolean
  multi?: boolean
}

export interface NodeModel {
  id: string
  type: string
  label: string
  ports: {
    in: Port[]
    out: Port[]
  }
  params?: Record<string, any>
}

export interface EdgeModel {
  id: string
  from: {
    node: string
    port: string
  }
  to: {
    node: string
    port: string
  }
}

export interface Workflow {
  id: string
  nodes: NodeModel[]
  edges: EdgeModel[]
}
