import { useEffect, useState } from "react"
import { deleteTool, getTool, updateTool } from "../api/tools"
import type { Tool } from "../types/tool"

interface Props {
  id: number
  refreshKey: number
  onEdit: () => void
  onChanged: () => void
  onDeleted: () => void
}

// Read single: loads one tool from GET /api/tools/{id}. Also has Delete.
export default function ToolDetail({ id, refreshKey, onEdit, onChanged, onDeleted }: Props) {
  const [tool, setTool] = useState<Tool | null>(null)
  const [error, setError] = useState("")

  useEffect(() => {
    let cancelled = false
    setTool(null)
    setError("")
    getTool(id)
      .then((result) => {
        if (!cancelled) setTool(result)
      })
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Could not load tool")
      })
    return () => {
      cancelled = true
    }
  }, [id, refreshKey])

  async function handleDelete() {
    if (!tool) return
    const ok = window.confirm(`Delete "${tool.name}"? It will be removed from the catalog.`)
    if (!ok) return
    try {
      await deleteTool(tool.id)
      onDeleted()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not delete tool")
    }
  }

  async function handleRestore() {
    if (!tool) return
    try {
      await updateTool(tool.id, { is_active: true })
      onChanged()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not restore tool")
    }
  }

  if (error && !tool) return <section className="card"><p className="error">{error}</p></section>
  if (!tool) return <section className="card"><p className="muted">Loading...</p></section>

  return (
    <section className="card">
      <div className="card-header">
        <h2>{tool.name}</h2>
        {!tool.is_active && <span className="badge">Deleted</span>}
      </div>

      <dl className="details">
        <dt>ID</dt>
        <dd>{tool.id}</dd>
        <dt>Category</dt>
        <dd>{tool.category ?? "-"}</dd>
        <dt>Description</dt>
        <dd>{tool.description ?? "-"}</dd>
        <dt>Created</dt>
        <dd>{new Date(tool.created_at).toLocaleString()}</dd>
      </dl>

      {error && <p className="error">{error}</p>}

      <div className="actions">
        <button type="button" onClick={onEdit}>Edit</button>
        {tool.is_active ? (
          <button type="button" className="danger" onClick={handleDelete}>Delete</button>
        ) : (
          <button type="button" onClick={handleRestore}>Restore</button>
        )}
      </div>
    </section>
  )
}
