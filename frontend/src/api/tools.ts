import type { Tool, ToolChanges, ToolInput, ToolList } from "../types/tool"

const BASE = "/api/tools"

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

// FastAPI sends {"detail": "text"} for our own errors and
// {"detail": [{"loc": [...], "msg": "..."}]} for validation errors (422).
async function errorMessage(res: Response): Promise<string> {
  try {
    const body: { detail?: unknown } = await res.json()
    if (typeof body.detail === "string") return body.detail
    if (Array.isArray(body.detail)) {
      return body.detail
        .map((d: { loc?: unknown[]; msg?: string }) => {
          const field = d.loc?.slice(1).join(".")
          return field ? `${field}: ${d.msg}` : (d.msg ?? "Invalid input")
        })
        .join("; ")
    }
  } catch {
    // the body was not JSON, use the generic message below
  }
  return `Request failed: ${res.status}`
}

async function request<T>(url: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(url, {
    ...options,
    headers: { "Content-Type": "application/json" },
  })
  if (!res.ok) throw new ApiError(res.status, await errorMessage(res))
  if (res.status === 204) return undefined as T
  return (await res.json()) as T
}

// Read list: GET /api/tools?skip=0&limit=10
export function listTools(
  skip: number,
  limit: number,
  includeInactive: boolean,
): Promise<ToolList> {
  const params = new URLSearchParams({
    skip: String(skip),
    limit: String(limit),
    include_inactive: String(includeInactive),
  })
  return request<ToolList>(`${BASE}?${params}`)
}

// Read single: GET /api/tools/{id}
export function getTool(id: number): Promise<Tool> {
  return request<Tool>(`${BASE}/${id}`)
}

// Create: POST /api/tools
export function createTool(input: ToolInput): Promise<Tool> {
  return request<Tool>(BASE, { method: "POST", body: JSON.stringify(input) })
}

// Update: PATCH /api/tools/{id}
export function updateTool(id: number, changes: ToolChanges): Promise<Tool> {
  return request<Tool>(`${BASE}/${id}`, {
    method: "PATCH",
    body: JSON.stringify(changes),
  })
}

// Delete: DELETE /api/tools/{id}  (the backend deactivates the tool)
export function deleteTool(id: number): Promise<void> {
  return request<void>(`${BASE}/${id}`, { method: "DELETE" })
}
