/*
 * Admin analytics tab: KPI cards, execution trends and failures. Loaded each
 * time the tab opens. The response shape is assumed (see Analytics in
 * lib/types.ts), so every read is defensive and degrades to an empty state.
 */
import { useEffect, useState } from 'react'
import { AlertCircle } from 'lucide-react'
import { ApiError, getAnalytics } from '../../lib/api'
import type { Analytics } from '../../lib/types'

type Period = 'daily' | 'weekly' | 'monthly'

const PERIODS: { key: Period; label: string }[] = [
  { key: 'daily', label: 'Daily' },
  { key: 'weekly', label: 'Weekly' },
  { key: 'monthly', label: 'Monthly' },
]

function num(value: unknown): number {
  return typeof value === 'number' && Number.isFinite(value) ? value : 0
}

function Kpi({ label, value, sub }: { label: string; value: string; sub: string }) {
  return (
    <div className="card flex flex-col gap-1.5 p-5">
      <span className="text-[13px] font-medium text-zinc-600">{label}</span>
      <span className="font-mono text-[28px] font-medium leading-tight">{value}</span>
      <span className="text-xs text-zinc-600">{sub}</span>
    </div>
  )
}

function Trends({ data }: { data: Analytics }) {
  const [period, setPeriod] = useState<Period>('daily')
  const rows = Object.entries(data.execution_trends?.[period] ?? {}).sort(([a], [b]) => a.localeCompare(b))
  const max = Math.max(0, ...rows.map(([, v]) => num(v?.total)))
  const pct = (n: number) => (max > 0 ? `${(n / max) * 100}%` : '0%')

  return (
    <section className="card flex flex-col gap-5 p-6 lg:col-span-2">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-base font-semibold">Execution trends</h2>
        <div role="group" aria-label="Trend period" className="grid grid-cols-3 gap-1 rounded-[10px] border border-zinc-300 bg-zinc-100 p-1">
          {PERIODS.map((p) => (
            <button
              key={p.key}
              type="button"
              aria-pressed={period === p.key}
              onClick={() => setPeriod(p.key)}
              className={`h-8 rounded-[7px] border px-3 text-[13px] font-medium ${
                period === p.key ? 'border-zinc-900 bg-zinc-900 text-white' : 'border-transparent text-zinc-600 hover:text-zinc-900'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {rows.length === 0 ? (
        <p className="text-sm text-zinc-600">No executions recorded for this period.</p>
      ) : (
        <ul className="flex max-h-[420px] flex-col gap-4 overflow-y-auto pr-1">
          {rows.map(([key, v]) => (
            <li key={key} className="grid items-center gap-x-4 gap-y-1.5 sm:grid-cols-[110px_1fr_170px]">
              <span className="font-mono text-xs">{key}</span>
              <div className="flex flex-col gap-1">
                <div className="h-1.5 rounded-full bg-zinc-300" style={{ width: pct(num(v?.total)) }} />
                <div className="h-1.5 rounded-full bg-zinc-900" style={{ width: pct(num(v?.successful)) }} />
              </div>
              <span className="font-mono text-xs text-zinc-600">
                {num(v?.total)} total · {num(v?.successful)} successful
              </span>
            </li>
          ))}
        </ul>
      )}

      <div className="flex gap-5 border-t border-zinc-200 pt-4 text-xs text-zinc-600">
        <span className="flex items-center gap-2">
          <span className="h-1.5 w-5 rounded-full bg-zinc-300" aria-hidden="true" />
          Total
        </span>
        <span className="flex items-center gap-2">
          <span className="h-1.5 w-5 rounded-full bg-zinc-900" aria-hidden="true" />
          Successful
        </span>
      </div>
    </section>
  )
}

function Failures({ data }: { data: Analytics }) {
  const errors = Object.entries(data.failure_analytics?.common_errors ?? {}).sort(([, a], [, b]) => num(b) - num(a))

  return (
    <section className="card flex flex-col gap-4 p-6">
      <h2 className="text-base font-semibold">Failures</h2>
      <span className="font-mono text-[28px] font-medium leading-tight">{num(data.failure_analytics?.total_failures)}</span>
      {errors.length === 0 ? (
        <p className="text-sm text-zinc-600">No errors recorded</p>
      ) : (
        <ul className="flex flex-col divide-y divide-zinc-200">
          {errors.map(([name, count]) => (
            <li key={name} className="flex items-start justify-between gap-3 py-2 text-[13px]">
              <span className="break-words">{name}</span>
              <span className="font-mono text-xs">{num(count)}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

function Skeleton() {
  return (
    <div role="status" aria-label="Loading analytics" className="flex animate-pulse flex-col gap-4">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="h-[112px] rounded-[14px] bg-zinc-100" />
        ))}
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="h-64 rounded-[14px] bg-zinc-100 lg:col-span-2" />
        <div className="h-64 rounded-[14px] bg-zinc-100" />
      </div>
    </div>
  )
}

export function AnalyticsDashboard() {
  const [data, setData] = useState<Analytics | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    let cancelled = false
    getAnalytics().then(
      (result) => {
        if (!cancelled) setData(result)
      },
      (err: unknown) => {
        if (!cancelled) setError(err instanceof ApiError ? err.message : 'Could not load analytics. Try again.')
      },
    )
    return () => {
      cancelled = true
    }
  }, [attempt])

  function retry() {
    setError(null)
    setData(null)
    setAttempt((n) => n + 1)
  }

  const o = data?.overview

  return (
    <main className="mx-auto flex w-full max-w-[1040px] flex-1 flex-col gap-6 px-4 py-10 sm:px-6">
      <h1 className="text-center text-[26px] font-semibold tracking-[-0.02em]">Investigation analytics</h1>

      {error && (
        <div role="alert" className="card flex flex-col items-start gap-3 p-6">
          <p className="flex items-start gap-2 text-sm leading-normal">
            <AlertCircle className="mt-0.5 size-4 shrink-0 text-zinc-700" aria-hidden="true" />
            {error}
          </p>
          <button type="button" onClick={retry} className="btn-outline">
            Retry
          </button>
        </div>
      )}

      {!error && !data && <Skeleton />}

      {data && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Kpi label="Total executions" value={String(num(o?.total_executions))} sub={`${num(o?.successful_executions)} successful · ${num(o?.failed_executions)} failed`} />
            <Kpi label="Success rate" value={`${num(o?.success_rate).toFixed(1)}%`} sub="Of all executions" />
            <Kpi label="Orders investigated" value={String(num(o?.unique_orders_investigated))} sub={`${num(o?.unique_customers_investigated)} unique customers`} />
            <Kpi label="Active operators" value={String(num(o?.active_operators))} sub={`${num(data.invitations?.total_invitations)} invitations issued`} />
          </div>
          <div className="grid gap-4 lg:grid-cols-3">
            <Trends data={data} />
            <Failures data={data} />
          </div>
        </>
      )}
    </main>
  )
}