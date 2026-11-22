/*
 * Invitations modal (admin). Create an invitation and share its token, copy
 * any existing token, and delete an invitation. Deleting also removes the
 * person's account and profile on the backend, so it needs confirmation.
 * An admin cannot delete their own invitation.
 */
import { useEffect, useState, type FormEvent } from 'react'
import { AlertCircle, Loader2, Trash2 } from 'lucide-react'
import { useAuth } from '../../auth/AuthContext'
import { ApiError, createInvitation, deleteInvitation, getInvitations } from '../../lib/api'
import { formatDate } from '../../lib/format'
import type { Invitation } from '../../lib/types'
import { Modal } from '../Modal'
import { CopyButton } from '../ReportView'

const messageOf = (err: unknown, fallback: string) => (err instanceof ApiError ? err.message : fallback)

function newestFirst(a: Invitation, b: Invitation): number {
  const ta = Date.parse(a.created_at)
  const tb = Date.parse(b.created_at)
  return Number.isNaN(ta) || Number.isNaN(tb) ? b.created_at.localeCompare(a.created_at) : tb - ta
}

function InlineError({ message }: { message: string }) {
  return (
    <div role="alert" className="flex items-start gap-2 rounded-lg border border-zinc-300 bg-zinc-50 p-3 text-sm leading-normal">
      <AlertCircle className="mt-0.5 size-4 shrink-0 text-zinc-700" aria-hidden="true" />
      <span>{message}</span>
    </div>
  )
}

function InvitationsContent({ onCountChange }: { onCountChange: (count: number) => void }) {
  const { profile } = useAuth()
  const [items, setItems] = useState<Invitation[] | null>(null) // null = loading
  const [loadError, setLoadError] = useState<string | null>(null)

  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [creating, setCreating] = useState(false)
  const [createError, setCreateError] = useState<string | null>(null)
  const [created, setCreated] = useState<{ key: string; email: string } | null>(null)

  const [confirmingKey, setConfirmingKey] = useState<string | null>(null)
  const [deletingKey, setDeletingKey] = useState<string | null>(null)
  const [deleteError, setDeleteError] = useState<string | null>(null)

  // Bumping `attempt` reloads the list (after create/delete, or Retry).
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    let cancelled = false
    getInvitations().then(
      (list) => {
        if (cancelled) return
        setItems([...list].sort(newestFirst))
        setLoadError(null)
        onCountChange(list.length)
      },
      (err: unknown) => {
        if (!cancelled) setLoadError(messageOf(err, 'Could not load invitations. Try again.'))
      },
    )
    return () => {
      cancelled = true
    }
  }, [attempt, onCountChange])

  const refresh = () => setAttempt((n) => n + 1)

  function retry() {
    setLoadError(null)
    setItems(null)
    refresh()
  }

  // Closing the confirmation returns keyboard focus to the Delete button.
  function cancelDelete(key: string) {
    setConfirmingKey(null)
    document.getElementById(`delete-${key}`)?.focus()
  }

  async function handleCreate(e: FormEvent) {
    e.preventDefault()
    if (creating) return
    if (!name.trim() || !email.trim()) return setCreateError('Enter the invitee’s name and work email.')
    if (!email.includes('@')) return setCreateError('Enter a valid email address.')

    setCreateError(null)
    setCreating(true)
    try {
      const key = await createInvitation(name.trim(), email.trim())
      setCreated({ key, email: email.trim() })
      setName('')
      setEmail('')
      refresh()
    } catch (err) {
      setCreateError(messageOf(err, 'Could not create the invitation. Try again.'))
    } finally {
      setCreating(false)
    }
  }

  async function handleDelete(inv: Invitation) {
    setDeletingKey(inv.access_key)
    setDeleteError(null)
    try {
      await deleteInvitation(inv.access_key, inv.email)
      setConfirmingKey(null)
      if (created?.key === inv.access_key) setCreated(null)
      setItems((prev) => prev && prev.filter((i) => i.access_key !== inv.access_key))
      refresh()
    } catch (err) {
      setDeleteError(messageOf(err, 'Could not delete the invitation. Try again.'))
    } finally {
      setDeletingKey(null)
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <form noValidate onSubmit={handleCreate} className="flex flex-col gap-3">
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="flex flex-col gap-1.5">
            <label htmlFor="invite-name" className="text-[13px] font-medium">
              Invitee name
            </label>
            <input id="invite-name" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Sarah Chen" autoComplete="off" className="field-input" />
          </div>
          <div className="flex flex-col gap-1.5">
            <label htmlFor="invite-email" className="text-[13px] font-medium">
              Work email
            </label>
            <input id="invite-email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="name@veloramarket.com" autoComplete="off" className="field-input" />
          </div>
        </div>
        {createError && <InlineError message={createError} />}
        <button type="submit" disabled={creating} className="btn-primary self-start">
          {creating && <Loader2 className="size-4 animate-spin" aria-hidden="true" />}
          Create invitation
        </button>
      </form>

      {created && (
        <div className="flex flex-col gap-2 rounded-lg border-2 border-zinc-900 bg-zinc-50 p-4">
          <span className="text-[13px] font-semibold">Invitation created</span>
          <div className="flex items-center gap-2">
            <code className="min-w-0 flex-1 break-all font-mono text-[13px]">{created.key}</code>
            <CopyButton text={created.key} ariaLabel="Copy new invitation token" />
          </div>
          <span className="text-xs text-zinc-600">Share this token with {created.email}</span>
        </div>
      )}

      <div className="flex flex-col">
        {loadError && (
          <div className="flex flex-col items-start gap-3">
            <InlineError message={loadError} />
            <button type="button" onClick={retry} className="btn-outline">
              Retry
            </button>
          </div>
        )}
        {!loadError && items === null && (
          <p role="status" className="flex items-center gap-2 text-[13px] text-zinc-600">
            <Loader2 className="size-4 animate-spin" aria-hidden="true" />
            Loading invitations
          </p>
        )}
        {items?.length === 0 && <p className="text-sm text-zinc-600">No invitations yet.</p>}

        {items && items.length > 0 && (
          <ul className="border-t border-zinc-200">
            {items.map((inv) => {
              const isSelf = inv.email.toLowerCase() === profile?.email.toLowerCase()
              const confirming = confirmingKey === inv.access_key
              const deleting = deletingKey === inv.access_key
              return (
                <li key={inv.access_key} className="flex flex-col gap-3 border-b border-zinc-200 py-4">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div className="min-w-0">
                      <p className="flex flex-wrap items-center gap-2 text-sm font-medium">
                        {inv.name}
                        {inv.status ? <span className="tag border-zinc-900 bg-white font-medium text-zinc-900">Redeemed</span> : <span className="tag">Pending</span>}
                      </p>
                      <p className="break-all text-[13px] text-zinc-600">{inv.email}</p>
                      <p className="text-xs text-zinc-600">Created {formatDate(inv.created_at)}</p>
                    </div>
                    <span title={isSelf ? 'You cannot delete your own invitation.' : undefined}>
                      <button
                        type="button"
                        disabled={isSelf}
                        id={`delete-${inv.access_key}`}
                        onClick={() => {
                          setDeleteError(null)
                          setConfirmingKey(inv.access_key)
                        }}
                        aria-label={`Delete invitation for ${inv.name}`}
                        className="btn-outline"
                      >
                        <Trash2 className="size-4" aria-hidden="true" />
                        Delete
                      </button>
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <code className="min-w-0 flex-1 break-all rounded-lg border border-zinc-300 bg-zinc-50 px-3 py-2 font-mono text-xs">{inv.access_key}</code>
                    <CopyButton text={inv.access_key} ariaLabel={`Copy token for ${inv.name}`} />
                  </div>

                  {confirming && (
                    <div className="flex flex-col gap-3 rounded-lg border border-zinc-300 bg-zinc-50 p-3">
                      <p className="text-sm leading-normal">Deleting this invitation will also permanently delete {inv.name}’s account and profile.</p>
                      {deleteError && <InlineError message={deleteError} />}
                      <div className="flex gap-2">
                        <button type="button" autoFocus disabled={deleting} onClick={() => cancelDelete(inv.access_key)} className="btn-outline">
                          Cancel
                        </button>
                        <button type="button" disabled={deleting} onClick={() => void handleDelete(inv)} className="btn-primary h-9 px-4 text-[13px]">
                          {deleting && <Loader2 className="size-4 animate-spin" aria-hidden="true" />}
                          Confirm Delete
                        </button>
                      </div>
                    </div>
                  )}
                </li>
              )
            })}
          </ul>
        )}
      </div>
    </div>
  )
}

interface InvitationsModalProps {
  open: boolean
  onClose: () => void
  onCountChange: (count: number) => void
}

export function InvitationsModal({ open, onClose, onCountChange }: InvitationsModalProps) {
  return (
    <Modal open={open} title="Invitations" onClose={onClose} size="lg">
      <InvitationsContent onCountChange={onCountChange} />
    </Modal>
  )
}