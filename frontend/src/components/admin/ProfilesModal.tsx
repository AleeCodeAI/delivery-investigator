/*
 * Profiles modal (admin). Lists every account and lets an admin promote an
 * operator to admin after confirmation. There is no demote and no delete
 * here; removing an account is done by deleting its invitation.
 */
import { useEffect, useState } from 'react'
import { AlertCircle, Loader2 } from 'lucide-react'
import { ApiError, getProfiles, promoteToAdmin } from '../../lib/api'
import type { Profile } from '../../lib/types'
import { Modal } from '../Modal'

const messageOf = (err: unknown, fallback: string) => (err instanceof ApiError ? err.message : fallback)

function InlineError({ message }: { message: string }) {
  return (
    <div role="alert" className="flex items-start gap-2 rounded-lg border border-zinc-300 bg-zinc-50 p-3 text-sm leading-normal">
      <AlertCircle className="mt-0.5 size-4 shrink-0 text-zinc-700" aria-hidden="true" />
      <span>{message}</span>
    </div>
  )
}

function ProfilesContent() {
  const [items, setItems] = useState<Profile[] | null>(null) // null = loading
  const [loadError, setLoadError] = useState<string | null>(null)
  const [confirmingId, setConfirmingId] = useState<string | null>(null)
  const [promotingId, setPromotingId] = useState<string | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)

  // Bumping `attempt` reloads the list (after a promotion, or Retry).
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    let cancelled = false
    getProfiles().then(
      (list) => {
        if (cancelled) return
        setItems(list)
        setLoadError(null)
      },
      (err: unknown) => {
        if (!cancelled) setLoadError(messageOf(err, 'Could not load profiles. Try again.'))
      },
    )
    return () => {
      cancelled = true
    }
  }, [attempt])

  function retry() {
    setLoadError(null)
    setItems(null)
    setAttempt((n) => n + 1)
  }

  // Closing the confirmation returns keyboard focus to the Make Admin button.
  function cancelPromote(id: string) {
    setConfirmingId(null)
    document.getElementById(`promote-${id}`)?.focus()
  }

  async function handlePromote(p: Profile) {
    setPromotingId(p.user_id)
    setActionError(null)
    try {
      await promoteToAdmin(p.user_id, p.email)
      setConfirmingId(null)
      setItems((prev) => prev && prev.map((x) => (x.user_id === p.user_id ? { ...x, role: 'admin' } : x)))
      setAttempt((n) => n + 1)
    } catch (err) {
      setActionError(messageOf(err, 'Could not update the role. Try again.'))
    } finally {
      setPromotingId(null)
    }
  }

  if (loadError) {
    return (
      <div className="flex flex-col items-start gap-3">
        <InlineError message={loadError} />
        <button type="button" onClick={retry} className="btn-outline">
          Retry
        </button>
      </div>
    )
  }
  if (items === null) {
    return (
      <p role="status" className="flex items-center gap-2 text-[13px] text-zinc-600">
        <Loader2 className="size-4 animate-spin" aria-hidden="true" />
        Loading profiles
      </p>
    )
  }
  if (items.length === 0) return <p className="text-sm text-zinc-600">No profiles yet.</p>

  return (
    <ul className="border-t border-zinc-200">
      {items.map((p) => {
        const display = p.name ?? p.email
        const confirming = confirmingId === p.user_id
        const promoting = promotingId === p.user_id
        return (
          <li key={p.user_id} className="flex flex-col gap-3 border-b border-zinc-200 py-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="min-w-0">
                <p className="flex flex-wrap items-center gap-2 text-sm font-medium">
                  {display}
                  <span className={p.role === 'admin' ? 'tag border-zinc-900 bg-zinc-900 font-medium text-white' : 'tag capitalize'}>{p.role === 'admin' ? 'Admin' : 'Operator'}</span>
                </p>
                <p className="break-all text-[13px] text-zinc-600">{p.email}</p>
              </div>
              {p.role === 'operator' && (
                <button
                  type="button"
                  id={`promote-${p.user_id}`}
                  onClick={() => {
                    setActionError(null)
                    setConfirmingId(p.user_id)
                  }}
                  aria-label={`Make ${display} an admin`}
                  className="btn-outline"
                >
                  Make Admin
                </button>
              )}
            </div>

            {confirming && (
              <div className="flex flex-col gap-3 rounded-lg border border-zinc-300 bg-zinc-50 p-3">
                <p className="text-sm leading-normal">Making {display} an admin gives them all the administrative privileges you hold.</p>
                {actionError && <InlineError message={actionError} />}
                <div className="flex gap-2">
                  <button type="button" autoFocus disabled={promoting} onClick={() => cancelPromote(p.user_id)} className="btn-outline">
                    Cancel
                  </button>
                  <button type="button" disabled={promoting} onClick={() => void handlePromote(p)} className="btn-primary h-9 px-4 text-[13px]">
                    {promoting && <Loader2 className="size-4 animate-spin" aria-hidden="true" />}
                    Confirm
                  </button>
                </div>
              </div>
            )}
          </li>
        )
      })}
    </ul>
  )
}

export function ProfilesModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  return (
    <Modal open={open} title="Profiles" onClose={onClose} size="lg">
      <ProfilesContent />
    </Modal>
  )
}