import { useState } from "react"
import { getTool } from "./api/tools"
import ToolDetail from "./components/ToolDetail"
import ToolForm from "./components/ToolForm"
import ToolList from "./components/ToolList"
import type { Tool } from "./types/tool"

// What the right-hand panel is showing.
type Panel =
  | { mode: "empty" }
  | { mode: "create" }
  | { mode: "detail"; id: number }
  | { mode: "edit"; tool: Tool }

export default function App() {
  const [panel, setPanel] = useState<Panel>({ mode: "empty" })
  // Bump this number to make the list and detail reload from the API.
  const [refreshKey, setRefreshKey] = useState(0)

  const reload = () => setRefreshKey((k) => k + 1)
  const selectedId = panel.mode === "detail" ? panel.id : panel.mode === "edit" ? panel.tool.id : null

  async function startEdit(id: number) {
    // Load the latest copy so the form never edits stale data.
    try {
      setPanel({ mode: "edit", tool: await getTool(id) })
    } catch (err) {
      window.alert(err instanceof Error ? err.message : "Could not load tool")
    }
  }

  return (
    <main>
      <header className="top">
        <div>
          <h1>AccessDesk</h1>
          <p className="muted">Tool catalog</p>
        </div>
        <button type="button" className="primary" onClick={() => setPanel({ mode: "create" })}>
          New tool
        </button>
      </header>

      <div className="layout">
        <ToolList
          selectedId={selectedId}
          refreshKey={refreshKey}
          onSelect={(id) => setPanel({ mode: "detail", id })}
        />

        {panel.mode === "empty" && (
          <section className="card">
            <p className="muted">Select a tool to see its details, or create a new one.</p>
          </section>
        )}

        {panel.mode === "create" && (
          <ToolForm
            onCancel={() => setPanel({ mode: "empty" })}
            onSaved={(tool) => {
              reload()
              setPanel({ mode: "detail", id: tool.id })
            }}
          />
        )}

        {panel.mode === "detail" && (
          <ToolDetail
            id={panel.id}
            refreshKey={refreshKey}
            onEdit={() => startEdit(panel.id)}
            onChanged={reload}
            onDeleted={() => {
              reload()
              setPanel({ mode: "empty" })
            }}
          />
        )}

        {panel.mode === "edit" && (
          <ToolForm
            tool={panel.tool}
            onCancel={() => setPanel({ mode: "detail", id: panel.tool.id })}
            onSaved={(tool) => {
              reload()
              setPanel({ mode: "detail", id: tool.id })
            }}
          />
        )}
      </div>
    </main>
  )
}
