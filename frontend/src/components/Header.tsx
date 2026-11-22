/*
 * Top bar shared by both consoles: logo and name, optional role badge, a
 * "left" slot (session tabs or the Analytics/Workbench switch), a "right"
 * slot (admin buttons), then History and the profile menu.
 */
import type { ReactNode } from 'react'
import { History } from 'lucide-react'
import { Logo } from './Logo'
import { ProfileMenu } from './ProfileMenu'

interface HeaderProps {
  badge?: string
  left?: ReactNode
  right?: ReactNode
  onOpenHistory: () => void
}

export function Header({ badge, left, right, onOpenHistory }: HeaderProps) {
  return (
    <header className="flex flex-wrap items-center justify-between gap-x-4 gap-y-3 border-b border-zinc-200 px-4 py-3.5 sm:px-8">
      <div className="flex min-w-0 items-center gap-3.5">
        <div className="flex shrink-0 items-center gap-2.5">
          <Logo showName />
          {badge && <span className="tag border-zinc-900 bg-zinc-900 font-medium text-white">{badge}</span>}
        </div>
        {left && (
          <>
            <span className="h-5 w-px shrink-0 bg-zinc-300" aria-hidden="true" />
            <div className="-m-1 min-w-0 overflow-x-auto p-1">{left}</div>
          </>
        )}
      </div>

      <div className="flex items-center gap-2">
        {right}
        {right && <span className="mx-1 h-5 w-px bg-zinc-300" aria-hidden="true" />}
        <button type="button" onClick={onOpenHistory} aria-label="History" className="btn-outline">
          <History className="size-[17px]" aria-hidden="true" />
        </button>
        <ProfileMenu />
      </div>
    </header>
  )
}