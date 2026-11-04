import { useEffect, useState } from "react"
import { listTools } from "../api/tools"
import type { ToolList as ToolListData } from "../types/tool"

const PAGE_SIZE = 8

interface Props {
  selectedId: number | null
  refreshKey: number
  onSelect: (id: number) => void
}

// Read list: shows one page of tools and loads it from GET /api/tools.
export default function ToolList({ selectedId, refreshKey, onSelect }: Props) {
  const [data, setData] = useState<ToolListData | null>(null)
  const [skip, setSkip] = useState(0)
  const [includeInactive, setIncludeInactive] = useState(false)
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    listTools(skip, PAGE_SIZE, includeInactive)
      .then((result) => {
        if (cancelled) return
        // We deleted the last item on this page: go back one page.
        if (result.items.length === 0 && skip > 0) {
          setSkip(Math.max(0, skip - PAGE_SIZE))
          return
        }
        setData(result)
        setError("")
        setLoading(false)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setError(err instanceof Error ? err.message : "Could not load tools")
        setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [skip, includeInactive, refreshKey])

  const total = data?.total ?? 0
  const from = total === 0 ? 0 : skip + 1
  const to = Math.min(skip + PAGE_SIZE, total)

  return (
    <section className="card">
      <div className="card-header">
        <h2>Tools</h2>
        <label className="inline">
          <input
            type="checkbox"
            checked={includeInactive}
            onChange={(e) => {
              setIncludeInactive(e.target.checked)
              setSkip(0)
            }}
          />
          Show deleted
        </label>
      </div>

      {error && <p className="error">{error}</p>}
      {loading && !data && <p className="muted">Loading...</p>}
      {data && data.items.length === 0 && !error && (
        <p className="muted">No tools yet. Click "New tool" to add one.</p>
      )}

      {data && data.items.length > 0 && (
        <ul className="tool-list">
          {data.items.map((tool) => (
            <li key={tool.id}>
              <button
                type="button"
                className={`row ${tool.id === selectedId ? "selected" : ""}`}
                onClick={() => onSelect(tool.id)}
              >
                <span className="row-name">{tool.name}</span>
                <span className="muted">{tool.category ?? "No category"}</span>
                {!tool.is_active && <span className="badge">Deleted</span>}
              </button>
            </li>
          ))}
        </ul>
      )}

      <div className="pager">
        <button type="button" disabled={skip === 0} onClick={() => setSkip(skip - PAGE_SIZE)}>
          Previous
        </button>
        <span className="muted">
          {from}-{to} of {total}
        </span>
        <button
          type="button"
          disabled={skip + PAGE_SIZE >= total}
          onClick={() => setSkip(skip + PAGE_SIZE)}
        >
          Next
        </button>
      </div>
    </section>
  )
}
