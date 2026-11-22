/*
 * Reusable modal dialog: centred (or a right-side drawer), dimmed backdrop,
 * close button. Closes on Esc or a click on the backdrop. Keeps keyboard focus inside the
 * dialog while open, locks page scroll, and restores focus on close.
 */
import { useEffect, useId, useRef, type ReactNode } from 'react'
import { createPortal } from 'react-dom'
import { X } from 'lucide-react'

interface ModalProps {
  open: boolean
  title: string
  onClose: () => void
  children: ReactNode
  size?: 'sm' | 'lg'
  placement?: 'center' | 'right' // right = full-height drawer (used for History)
  padded?: boolean // false lets the content run edge to edge
}

const FOCUSABLE = 'a[href],button:not([disabled]),input:not([disabled]),textarea:not([disabled]),select:not([disabled]),[tabindex]:not([tabindex="-1"])'

export function Modal({ open, title, onClose, children, size = 'sm', placement = 'center', padded = true }: ModalProps) {
  const dialogRef = useRef<HTMLDivElement>(null)
  const titleId = useId()

  // Kept in a ref so a new onClose each render does not re-run the effect and steal focus.
  const onCloseRef = useRef(onClose)
  useEffect(() => {
    onCloseRef.current = onClose
  })

  useEffect(() => {
    if (!open) return
    const dialog = dialogRef.current
    const previouslyFocused = document.activeElement as HTMLElement | null
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    dialog?.focus()

    function onKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') {
        onCloseRef.current()
        return
      }
      if (e.key !== 'Tab' || !dialog) return
      const items = dialog.querySelectorAll<HTMLElement>(FOCUSABLE)
      if (items.length === 0) return
      const first = items[0]
      const last = items[items.length - 1]
      const active = document.activeElement
      if (!dialog.contains(active)) {
        // Focus was lost (e.g. the focused row was removed): pull it back in.
        e.preventDefault()
        ;(e.shiftKey ? last : first).focus()
      } else if (e.shiftKey && (active === first || active === dialog)) {
        e.preventDefault()
        last.focus()
      } else if (!e.shiftKey && active === last) {
        e.preventDefault()
        first.focus()
      }
    }

    document.addEventListener('keydown', onKeyDown)
    return () => {
      document.removeEventListener('keydown', onKeyDown)
      document.body.style.overflow = previousOverflow
      previouslyFocused?.focus()
    }
  }, [open])

  if (!open) return null

  return createPortal(
    <div
      className={`fixed inset-0 z-50 flex bg-zinc-900/40 ${placement === 'right' ? 'justify-end' : 'items-center justify-center p-4'}`}
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose()
      }}
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        tabIndex={-1}
        className={`flex w-full flex-col bg-white shadow-[0_8px_32px_rgba(0,0,0,.18)] outline-none ${
          placement === 'right'
            ? 'h-full max-w-md border-l border-zinc-300'
            : `max-h-[90vh] rounded-[14px] border border-zinc-300 ${size === 'lg' ? 'max-w-2xl' : 'max-w-md'}`
        }`}
      >
        <div className="flex items-center justify-between gap-4 border-b border-zinc-200 px-6 py-4">
          <h2 id={titleId} className="text-[15px] font-semibold">
            {title}
          </h2>
          <button type="button" onClick={onClose} aria-label="Close" className="btn-outline">
            <X className="size-4" aria-hidden="true" />
          </button>
        </div>
        <div className={`min-h-0 flex-1 overflow-y-auto ${padded ? 'p-6' : ''}`}>{children}</div>
      </div>
    </div>,
    document.body,
  )
}