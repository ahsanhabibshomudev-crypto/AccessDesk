// These mirror the JSON that the FastAPI backend sends and expects.

export interface Tool {
  id: number
  name: string
  description: string | null
  category: string | null
  is_active: boolean
  created_at: string
}

export interface ToolList {
  items: Tool[]
  total: number
  skip: number
  limit: number
}

// Body of POST /api/tools
export interface ToolInput {
  name: string
  description: string
  category: string
}

// Body of PATCH /api/tools/{id}: send only the fields you want to change.
export type ToolChanges = Partial<ToolInput & { is_active: boolean }>
