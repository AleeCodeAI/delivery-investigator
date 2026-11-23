/*
 * Investigation workbench shared by the operator and admin consoles.
 * Each investigation is its own session (tab) and runs independently: the
 * agent run and the upfront-records request start in parallel, and closing a
 * tab only hides it (the run still finishes and is saved by the backend).
 */
import { useEffect, useRef, useState, type FormEvent } from 'react'
import { AlertCircle, CheckCircle2, FileSearch, HelpCircle, Loader2, Plus, Search, X } from 'lucide-react'
import { ApiError, getUpfrontData, runInvestigation, type InvestigationInput } from '../lib/api'
import { formatDateTime } from '../lib/format'
import type { Execution, RunResult, UpfrontData } from '../lib/types'
import { HistoryDrawer } from './HistoryDrawer'
import { ErrorBoundary } from './ErrorBoundary'
import { ReportView } from './ReportView'
import { UpfrontRecords } from './UpfrontRecords'

interface Session {
  id: string
  orderId: string
  customerId: string
  prompt: string
  status: 'running' | 'done' | 'error'
  startedAt: number
  upfront?: UpfrontData | null // undefined = loading, null = unavailable
  run?: RunResult
  errorMessage?: string
  fromHistory?: boolean
}

const NEW_TAB = 'new'
const DEFAULT_ERROR = 'The investigation could not be completed. Please try again later.'

// randomUUID only exists on secure origins (https or localhost).
function newId(): string {
  return crypto.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(36).slice(2)}`
}

function errorText(err: unknown): string {
  return err instanceof ApiError ? err.message : DEFAULT_ERROR
}

// Builds a finished session from a stored execution. No re-run, no extra requests.
function sessionFromExecution(e: Execution): Session {
  return {
    id: e.execution_id,
    orderId: e.order_id,
    customerId: e.customer_id,
    prompt: e.investigation_prompt,
    status: e.agent_result ? 'done' : 'error',
    startedAt: Date.parse(e.execution_date) || 0,
    upfront: e.upfront_data,
    run: e.agent_result ? { agent_result: e.agent_result, recommender_result: e.recommender_result } : undefined,
    errorMessage: e.agent_result ? undefined : (e.error_message ?? DEFAULT_ERROR),
    fromHistory: true,
  }
}

// Reads the outcome defensively so a malformed response cannot break the tab bar.
function tabOutcome(s: Session): 'running' | 'error' | 'inconclusive' | 'done' {
  if (s.status !== 'done') return s.status
  return s.run?.agent_result?.investigation_success === false ? 'inconclusive' : 'done'
}

const OUTCOME_LABEL = { running: 'Running', error: 'Failed', inconclusive: 'Inconclusive', done: 'Completed' }

function TabBar({
  sessions,
  activeId,
  onSelect,
  onClose,
}: {
  sessions: Session[]
  activeId: string
  onSelect: (id: string) => void
  onClose: (id: string) => void
}) {
  const tab = (active: boolean) =>
    `flex h-9 items-center gap-1.5 rounded-lg border text-[13px] font-medium ${
      active ? 'border-zinc-900 bg-zinc-900 text-white' : 'border-zinc-300 bg-white text-zinc-900 hover:border-zinc-900'
    }`

  return (
    <nav aria-label="Investigations" className="flex gap-2 overflow-x-auto border-b border-zinc-200 px-4 py-2.5 sm:px-8">
      <button type="button" onClick={() => onSelect(NEW_TAB)} aria-current={activeId === NEW_TAB} className={`${tab(activeId === NEW_TAB)} shrink-0 px-3`}>
        <Plus className="size-4" aria-hidden="true" />
        New
      </button>
      {sessions.map((s) => {
        const active = s.id === activeId
        const outcome = tabOutcome(s)
        const Icon = outcome === 'error' ? AlertCircle : outcome === 'inconclusive' ? HelpCircle : CheckCircle2
        return (
          <div key={s.id} className={`${tab(active)} shrink-0 pr-1`}>
            <button
              type="button"
              onClick={() => onSelect(s.id)}
              aria-current={active}
              title={`${s.orderId} · ${s.customerId}`}
              className="flex h-full items-center gap-1.5 rounded-lg pl-3"
            >
              {outcome === 'running' ? <Loader2 className="size-4 animate-spin" aria-hidden="true" /> : <Icon className="size-4" aria-hidden="true" />}
              <span className="max-w-[140px] truncate font-mono text-xs">{s.orderId}</span>
              {outcome === 'running' ? (
                <span className="text-xs font-normal opacity-80">Running</span>
              ) : (
                <span className="sr-only">, {OUTCOME_LABEL[outcome]}</span>
              )}
            </button>
            <button type="button" onClick={() => onClose(s.id)} aria-label={`Close ${s.orderId}`} className="flex size-7 items-center justify-center rounded-md hover:bg-zinc-500/20">
              <X className="size-3.5" aria-hidden="true" />
            </button>
          </div>
        )
      })}
    </nav>
  )
}

function RunningCard({ session }: { session: Session }) {
  // Starts at startedAt so rendering stays pure; the interval keeps it current.
  const [now, setNow] = useState(session.startedAt)
  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(timer)
  }, [])

  const secs = Math.max(0, Math.floor((now - session.startedAt) / 1000))
  const elapsed = `${Math.floor(secs / 60)}:${String(secs % 60).padStart(2, '0')}`

  return (
    <section role="status" className="card flex items-center gap-4 p-6">
      <Loader2 className="size-6 shrink-0 animate-spin text-zinc-900" aria-hidden="true" />
      <div className="flex min-w-0 flex-col gap-1">
        <p className="text-[15px] font-semibold">Investigating {session.orderId}…</p>
        <p className="text-[13px] text-zinc-600">
          Elapsed <span className="font-mono text-xs">{elapsed}</span>. This can take a while; you can start another investigation in a new tab.
        </p>
      </div>
    </section>
  )
}

function ErrorCard({ message }: { message: string }) {
  return (
    <section role="alert" className="card flex items-start gap-3 p-6">
      <AlertCircle className="mt-0.5 size-5 shrink-0 text-zinc-700" aria-hidden="true" />
      <div className="flex flex-col gap-1">
        <h2 className="text-[15px] font-semibold">Investigation not completed</h2>
        <p className="text-sm leading-normal text-zinc-600">{message}</p>
      </div>
    </section>
  )
}

interface WorkbenchProps {
  historyOpen: boolean
  onCloseHistory: () => void
}

export function Workbench({ historyOpen, onCloseHistory }: WorkbenchProps) {
  const [sessions, setSessions] = useState<Session[]>([])
  const [activeId, setActiveId] = useState(NEW_TAB)
  const [orderId, setOrderId] = useState('')
  const [customerId, setCustomerId] = useState('')
  const [prompt, setPrompt] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const lastSubmit = useRef(0)

  const active = sessions.find((s) => s.id === activeId)

  // Updates a session by id. If its tab was closed meanwhile, nothing happens.
  function patchSession(id: string, patch: Partial<Session>) {
    setSessions((prev) => prev.map((s) => (s.id === id ? { ...s, ...patch } : s)))
  }

  function closeSession(id: string) {
    setSessions((prev) => prev.filter((s) => s.id !== id))
    if (id === activeId) setActiveId(NEW_TAB)
  }

  // Opens the stored execution as a tab, or switches to it if already open.
  function openFromHistory(execution: Execution) {
    if (!sessions.some((s) => s.id === execution.execution_id)) {
      setSessions((prev) => [...prev, sessionFromExecution(execution)])
    }
    setActiveId(execution.execution_id)
    onCloseHistory()
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const order = orderId.trim()
    const customer = customerId.trim()
    const text = prompt.trim()
    if (!order || !customer || !text) {
      setFormError('Fill in the order ID, customer ID and investigation prompt.')
      return
    }

    // The form keeps its values, so ignore a second submit within moments (double click or Enter twice).
    const now = Date.now()
    if (now - lastSubmit.current < 1500) return
    lastSubmit.current = now

    const id = newId()
    const input: InvestigationInput = { customer_id: customer, order_id: order, investigation_prompt: text }

    setSessions((prev) => [...prev, { id, orderId: order, customerId: customer, prompt: text, status: 'running', startedAt: Date.now() }])
    setActiveId(id)
    setFormError(null)

    // Two independent requests: records may appear before the agent finishes.
    runInvestigation(input).then(
      (run) => patchSession(id, { status: 'done', run }),
      (err: unknown) => patchSession(id, { status: 'error', errorMessage: errorText(err) }),
    )
    getUpfrontData(input).then(
      (upfront) => patchSession(id, { upfront }),
      () => patchSession(id, { upfront: null }),
    )
  }

  return (
    <>
      <TabBar sessions={sessions} activeId={activeId} onSelect={setActiveId} onClose={closeSession} />

      <main className="mx-auto flex w-full max-w-[760px] flex-1 flex-col gap-6 px-4 py-10 sm:px-6">
        <div className="flex flex-col gap-1.5 text-center">
          <h1 className="text-[26px] font-semibold tracking-[-0.02em]">Delivery investigation</h1>
          <p className="text-sm leading-normal text-zinc-600">Enter an order and describe what you want to establish. The system reads the records and reports what the evidence shows.</p>
        </div>

        <form noValidate onSubmit={handleSubmit} className="card flex flex-col gap-4 p-6">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="flex flex-col gap-1.5">
              <label htmlFor="order-id" className="text-[13px] font-medium">
                Order ID
              </label>
              <input id="order-id" value={orderId} onChange={(e) => setOrderId(e.target.value)} placeholder="e.g. ORD-3106" autoComplete="off" spellCheck={false} className="field-input font-mono text-[13px]" />
            </div>
            <div className="flex flex-col gap-1.5">
              <label htmlFor="customer-id" className="text-[13px] font-medium">
                Customer ID
              </label>
              <input id="customer-id" value={customerId} onChange={(e) => setCustomerId(e.target.value)} placeholder="e.g. CUST-8821" autoComplete="off" spellCheck={false} className="field-input font-mono text-[13px]" />
            </div>
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="prompt" className="text-[13px] font-medium">
              Investigation prompt
            </label>
            <textarea id="prompt" rows={3} value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder="What do you want to establish about this delivery?" className="field-input h-auto resize-y py-3 leading-normal" />
          </div>

          {formError && (
            <div role="alert" className="flex items-start gap-2 rounded-lg border border-zinc-300 bg-zinc-50 p-3 text-sm leading-normal">
              <AlertCircle className="mt-0.5 size-4 shrink-0 text-zinc-700" aria-hidden="true" />
              <span>{formError}</span>
            </div>
          )}

          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="text-xs text-zinc-600">Runs in its own tab. Your inputs stay in place so you can adjust them and run again.</p>
            <button type="submit" className="btn-primary h-11">
              <Search className="size-4" aria-hidden="true" />
              Investigate
            </button>
          </div>
        </form>

        {!active && (
          <div className="flex flex-col items-center gap-2 py-10 text-center text-zinc-600">
            <FileSearch className="size-7" aria-hidden="true" />
            <p className="text-sm">Ready for a new investigation.</p>
          </div>
        )}

        {/* key resets the records panel when switching tabs; the boundary keeps a bad result from blanking the app */}
        {active && (
          <ErrorBoundary key={active.id} fallback={<ErrorCard message="This result could not be displayed. Check History for the saved record." />}>
          <div className="flex flex-col gap-4">
            <p className="text-[13px] text-zinc-600">
              Results for <span className="font-mono text-xs text-zinc-900">{active.orderId}</span> ·{' '}
              <span className="font-mono text-xs text-zinc-900">{active.customerId}</span>
              {active.fromHistory && <> · {formatDateTime(new Date(active.startedAt).toISOString())}</>}
            </p>
            {active.status === 'running' && <RunningCard session={active} />}
            {active.status === 'error' && <ErrorCard message={active.errorMessage ?? DEFAULT_ERROR} />}
            {active.status === 'done' && active.run && <ReportView run={active.run} orderId={active.orderId} />}
            <UpfrontRecords data={active.upfront} />
          </div>
          </ErrorBoundary>
        )}
      </main>

      <HistoryDrawer open={historyOpen} onClose={onCloseHistory} onSelect={openFromHistory} />
    </>
  )
}