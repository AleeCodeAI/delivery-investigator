/*
 * Profile popover opened from the user icon (both consoles).
 * Shows name, email and role, with Change password and Log out.
 * There is intentionally no "delete account": accounts are removed by admins only.
 */
import { useEffect, useRef, useState, type FormEvent } from 'react'
import { AlertCircle, CheckCircle2, KeyRound, Loader2, LogOut, User } from 'lucide-react'
import { useAuth } from '../auth/AuthContext'
import { Modal } from './Modal'

function ChangePasswordForm({ onClose }: { onClose: () => void }) {
  const { changePassword } = useAuth()
  const [current, setCurrent] = useState('')
  const [next, setNext] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [done, setDone] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (submitting) return
    if (!current || !next || !confirm) return setError('Fill in all fields.')
    if (next.length < 8) return setError('New password must be at least 8 characters.')
    if (next !== confirm) return setError('New passwords do not match.')

    setError(null)
    setSubmitting(true)
    try {
      await changePassword(current, next)
      setDone(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not update the password. Try again.')
    } finally {
      setSubmitting(false)
    }
  }

  if (done) {
    return (
      <div className="flex flex-col gap-5">
        <p className="flex items-center gap-2 text-sm">
          <CheckCircle2 className="size-4 text-zinc-700" aria-hidden="true" />
          Your password has been updated.
        </p>
        <button type="button" onClick={onClose} className="btn-primary self-end">
          Done
        </button>
      </div>
    )
  }

  return (
    <form noValidate onSubmit={handleSubmit} className="flex flex-col gap-4">
      <div className="flex flex-col gap-1.5">
        <label htmlFor="current-password" className="text-[13px] font-medium">
          Current password
        </label>
        <input id="current-password" type="password" autoComplete="current-password" value={current} onChange={(e) => setCurrent(e.target.value)} className="field-input" />
      </div>
      <div className="flex flex-col gap-1.5">
        <label htmlFor="new-password" className="text-[13px] font-medium">
          New password
        </label>
        <input id="new-password" type="password" autoComplete="new-password" value={next} onChange={(e) => setNext(e.target.value)} className="field-input" />
        <span className="text-xs text-zinc-600">At least 8 characters.</span>
      </div>
      <div className="flex flex-col gap-1.5">
        <label htmlFor="confirm-new-password" className="text-[13px] font-medium">
          Confirm new password
        </label>
        <input id="confirm-new-password" type="password" autoComplete="new-password" value={confirm} onChange={(e) => setConfirm(e.target.value)} className="field-input" />
      </div>

      {error && (
        <div role="alert" className="flex items-start gap-2 rounded-lg border border-zinc-300 bg-zinc-50 p-3 text-sm leading-normal">
          <AlertCircle className="mt-0.5 size-4 shrink-0 text-zinc-700" aria-hidden="true" />
          <span>{error}</span>
        </div>
      )}

      <div className="flex justify-end gap-2 pt-1">
        <button type="button" onClick={onClose} className="btn-outline h-10 px-4">
          Cancel
        </button>
        <button type="submit" disabled={submitting} className="btn-primary">
          {submitting && <Loader2 className="size-4 animate-spin" aria-hidden="true" />}
          Update password
        </button>
      </div>
    </form>
  )
}

export function ProfileMenu() {
  const { profile, signOut } = useAuth()
  const [open, setOpen] = useState(false)
  const [passwordOpen, setPasswordOpen] = useState(false)
  const rootRef = useRef<HTMLDivElement>(null)
  const triggerRef = useRef<HTMLButtonElement>(null)

  // Close on outside click or Esc while the popover is open.
  useEffect(() => {
    if (!open) return
    function onMouseDown(e: MouseEvent) {
      if (!rootRef.current?.contains(e.target as Node)) setOpen(false)
    }
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') {
        setOpen(false)
        triggerRef.current?.focus()
      }
    }
    document.addEventListener('mousedown', onMouseDown)
    document.addEventListener('keydown', onKeyDown)
    return () => {
      document.removeEventListener('mousedown', onMouseDown)
      document.removeEventListener('keydown', onKeyDown)
    }
  }, [open])

  if (!profile) return null

  // The menu item that opened the dialog no longer exists, so focus the user icon.
  function closePasswordDialog() {
    setPasswordOpen(false)
    triggerRef.current?.focus()
  }

  const itemClass = 'flex w-full items-center gap-2.5 px-4 py-2.5 text-left text-[13px] font-medium hover:bg-zinc-50'

  return (
    <div ref={rootRef} className="relative">
      <button
        ref={triggerRef}
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-label="Profile"
        aria-expanded={open}
        aria-controls="profile-popover"
        className="btn-outline"
      >
        <User className="size-[17px]" aria-hidden="true" />
      </button>

      {open && (
        <div id="profile-popover" className="absolute right-0 top-[calc(100%+8px)] z-40 w-72 overflow-hidden rounded-xl border border-zinc-300 bg-white shadow-[0_8px_24px_rgba(0,0,0,.12)]">
          <div className="flex flex-col gap-1 border-b border-zinc-200 px-4 py-3.5">
            <span className="truncate text-sm font-semibold">{profile.name ?? profile.email}</span>
            <span className="break-all text-[13px] text-zinc-600">{profile.email}</span>
            <span className="tag mt-1 self-start capitalize">{profile.role}</span>
          </div>
          <button
            type="button"
            onClick={() => {
              setOpen(false)
              setPasswordOpen(true)
            }}
            className={itemClass}
          >
            <KeyRound className="size-4 text-zinc-600" aria-hidden="true" />
            Change password
          </button>
          <button type="button" onClick={() => void signOut()} className={`${itemClass} border-t border-zinc-200`}>
            <LogOut className="size-4 text-zinc-600" aria-hidden="true" />
            Log out
          </button>
        </div>
      )}

      <Modal open={passwordOpen} title="Change password" onClose={closePasswordDialog}>
        <ChangePasswordForm onClose={closePasswordDialog} />
      </Modal>
    </div>
  )
}