/*
 * Right-side drawer listing the signed-in user's past investigations, newest
 * first. The list is reloaded every time the drawer opens (the content mounts
 * only while open). Selecting a row hands the stored execution to the workbench.
 */
import { useEffect, useState } from 'react'
import { AlertCircle, Loader2 } from 'lucide-react'
import { ApiError, getHistory } from '../lib/api'
import { formatDateTime } from '../lib/format'
import type { Execution } from '../lib/types'
import { Modal } from './Modal'

function newestFirst(a: Execution, b: Execution): number {
  const ta = Date.parse(a.execution_date)
  const tb = Date.parse(b.execution_date)
  return Number.isNaN(ta) || Number.isNaN(tb) ? b.execution_date.localeCompare(a.execution_date) : tb - ta
}

function tagFor(e: Execution): string | null {
  if (!e.agent_result) return 'Error'
  return e.agent_result.investigation_success ? null : 'Inconclusive'
}

function HistoryList({ onSelect }: { onSelect: (execution: Execution) => void }) {
  const [items, setItems] = useState<Execution[] | null>(null) // null = loading
  const [error, setError] = useState<string | null>(null)
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    let cancelled = false
    getHistory().then(
      (result) => {
        if (!cancelled) setItems([...result].sort(newestFirst))
      },
      (err: unknown) => {
        if (!cancelled) setError(err instanceof ApiError ? err.message : 'Could not load history. Try again.')
      },
    )
    return () => {
      cancelled = true
    }
  }, [attempt])

  function retry() {
    setError(null)
    setItems(null)
    setAttempt((n) => n + 1)
  }

  if (error) {
    return (
      <div role="alert" className="flex flex-col items-start gap-3 p-6">
        <p className="flex items-start gap-2 text-sm leading-normal">
          <AlertCircle className="mt-0.5 size-4 shrink-0 text-zinc-700" aria-hidden="true" />
          {error}
        </p>
        <button type="button" onClick={retry} className="btn-outline">
          Retry
        </button>
      </div>
    )
  }

  if (items === null) {
    return (
      <p role="status" className="flex items-center gap-2 p-6 text-[13px] text-zinc-600">
        <Loader2 className="size-4 animate-spin" aria-hidden="true" />
        Loading history
      </p>
    )
  }

  if (items.length === 0) return <p className="p-6 text-sm text-zinc-600">No past investigations yet.</p>

  return (
    <ul>
      {items.map((e) => {
        const tag = tagFor(e)
        return (
          <li key={e.execution_id} className="border-b border-zinc-200">
            <button type="button" onClick={() => onSelect(e)} className="flex w-full flex-col gap-1.5 px-6 py-4 text-left hover:bg-zinc-50">
              <span className="flex items-center justify-between gap-3">
                <span className="flex min-w-0 items-center gap-2">
                  <span className="truncate font-mono text-[13px] font-medium">{e.order_id}</span>
                  {tag && <span className="tag">{tag}</span>}
                </span>
                <span className="shrink-0 text-xs text-zinc-600">{formatDateTime(e.execution_date)}</span>
              </span>
              <span className="line-clamp-2 text-[13px] leading-normal text-zinc-600">{e.investigation_prompt}</span>
            </button>
          </li>
        )
      })}
    </ul>
  )
}

interface HistoryDrawerProps {
  open: boolean
  onClose: () => void
  onSelect: (execution: Execution) => void
}

export function HistoryDrawer({ open, onClose, onSelect }: HistoryDrawerProps) {
  return (
    <Modal open={open} title="History" onClose={onClose} placement="right" padded={false}>
      <HistoryList onSelect={onSelect} />
    </Modal>
  )
}