/*
 * Result of one investigation: the report card and the suggested-next-step
 * card. Advice only: the UI never offers refund, reship or contact actions.
 * An inconclusive result is a valid outcome and is shown calmly in grey.
 */
import { useEffect, useRef, useState } from 'react'
import { Check, Copy } from 'lucide-react'
import type { RunResult } from '../lib/types'

// UI-only thresholds, kept in one place.
function confidenceText(value: number): string {
  const v = Number.isFinite(value) ? Math.min(1, Math.max(0, value)) : 0
  const label = v >= 0.8 ? 'High' : v >= 0.5 ? 'Moderate' : 'Low'
  return `${label} · ${Math.round(v * 100)}%`
}

function ConfidenceBadge({ value }: { value: number }) {
  return <span className="tag border-zinc-900 bg-white font-medium text-zinc-900">{confidenceText(value)}</span>
}

function EvidenceList({ items }: { items: string[] }) {
  return (
    <div className="flex flex-col gap-2">
      <h3 className="text-xs font-semibold uppercase tracking-wide text-zinc-600">Supporting evidence</h3>
      {items.length === 0 ? (
        <p className="text-[13px] text-zinc-600">No supporting evidence was recorded.</p>
      ) : (
        <ul className="flex flex-col gap-2">
          {items.map((text, i) => (
            <li key={i} className="rounded-lg border border-zinc-300 bg-zinc-50 px-3.5 py-2.5 text-[13px] leading-normal">
              {text}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export function CopyButton({ text, ariaLabel }: { text: string; ariaLabel?: string }) {
  const [state, setState] = useState<'idle' | 'copied' | 'failed'>('idle')
  const timer = useRef<number | undefined>(undefined)

  useEffect(() => () => window.clearTimeout(timer.current), [])

  async function copy() {
    try {
      await navigator.clipboard.writeText(text)
      setState('copied')
    } catch {
      setState('failed')
    }
    window.clearTimeout(timer.current)
    timer.current = window.setTimeout(() => setState('idle'), 2000)
  }

  return (
    <button type="button" onClick={() => void copy()} aria-label={ariaLabel} className="btn-outline">
      {state === 'copied' ? <Check className="size-4" aria-hidden="true" /> : <Copy className="size-4" aria-hidden="true" />}
      {state === 'copied' ? 'Copied' : state === 'failed' ? 'Could not copy' : 'Copy'}
    </button>
  )
}

export function ReportView({ run, orderId }: { run: RunResult; orderId: string }) {
  const { agent_result: agent, recommender_result: rec } = run

  const copyText = [
    `Order: ${orderId}`,
    `Investigation report:\n${agent.investigation_report}`,
    rec ? `Suggested next step:\n${rec.recommendation}` : '',
  ]
    .filter(Boolean)
    .join('\n\n')

  return (
    <div className="flex flex-col gap-4">
      <section className="card flex flex-col gap-5 p-6">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-base font-semibold">Investigation report</h2>
          {agent.investigation_success ? <ConfidenceBadge value={agent.confidence} /> : <span className="tag font-medium">Inconclusive</span>}
        </div>
        <p className="whitespace-pre-line text-[14.5px] leading-relaxed">{agent.investigation_report}</p>
        <EvidenceList items={agent.evidences} />
      </section>

      <section className="card flex flex-col gap-5 p-6">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-base font-semibold">Suggested next step</h2>
          <div className="flex items-center gap-2">
            {rec && <ConfidenceBadge value={rec.confidence} />}
            {rec && <CopyButton text={copyText} />}
          </div>
        </div>
        {rec ? (
          <>
            <p className="whitespace-pre-line text-[14.5px] leading-relaxed">{rec.recommendation}</p>
            <EvidenceList items={rec.evidences} />
          </>
        ) : (
          <p className="text-sm text-zinc-600">No recommendation was produced for this investigation.</p>
        )}
      </section>
    </div>
  )
}