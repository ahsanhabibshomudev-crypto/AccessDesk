import { type FormEvent, useState } from "react"
import { createTool, updateTool } from "../api/tools"
import type { Tool } from "../types/tool"

interface Props {
  tool?: Tool // given = edit mode, missing = create mode
  onSaved: (tool: Tool) => void
  onCancel: () => void
}

// Create (POST /api/tools) and Update (PATCH /api/tools/{id}) share this form.
export default function ToolForm({ tool, onSaved, onCancel }: Props) {
  const [name, setName] = useState(tool?.name ?? "")
  const [category, setCategory] = useState(tool?.category ?? "")
  const [description, setDescription] = useState(tool?.description ?? "")
  const [isActive, setIsActive] = useState(tool?.is_active ?? true)
  const [error, setError] = useState("")
  const [saving, setSaving] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError("")
    setSaving(true)
    try {
      const saved = tool
        ? await updateTool(tool.id, { name, category, description, is_active: isActive })
        : await createTool({ name, category, description })
      onSaved(saved)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save tool")
      setSaving(false)
    }
  }

  return (
    <section className="card">
      <h2>{tool ? `Edit ${tool.name}` : "New tool"}</h2>
      <form className="form" onSubmit={handleSubmit}>
        <label>
          Name
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            maxLength={100}
            placeholder="GitHub"
            required
          />
        </label>
        <label>
          Category
          <input
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            maxLength={50}
            placeholder="Development"
          />
        </label>
        <label>
          Description
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            maxLength={500}
            rows={4}
            placeholder="What is this tool used for?"
          />
        </label>
        {tool && (
          <label className="inline">
            <input
              type="checkbox"
              checked={isActive}
              onChange={(e) => setIsActive(e.target.checked)}
            />
            Active (shown in the catalog)
          </label>
        )}

        {error && <p className="error">{error}</p>}

        <div className="actions">
          <button type="submit" className="primary" disabled={saving}>
            {saving ? "Saving..." : tool ? "Save changes" : "Create tool"}
          </button>
          <button type="button" onClick={onCancel} disabled={saving}>
            Cancel
          </button>
        </div>
      </form>
    </section>
  )
}
