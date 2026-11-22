/*
 * Admin console (route /admin). Two tabs: Analytics (default) and Workbench.
 * The workbench stays mounted (only hidden) while Analytics is showing, so
 * running investigations are not lost when switching tabs. Opening History
 * switches to the Workbench tab, where reopened results appear.
 */
import { useEffect, useState } from 'react'
import { Ticket, Users } from 'lucide-react'
import { AnalyticsDashboard } from '../components/admin/AnalyticsDashboard'
import { InvitationsModal } from '../components/admin/InvitationsModal'
import { ProfilesModal } from '../components/admin/ProfilesModal'
import { Header } from '../components/Header'
import { Workbench } from '../components/Workbench'
import { getInvitations } from '../lib/api'

type Tab = 'analytics' | 'workbench'

export default function AdminPage() {
  const [tab, setTab] = useState<Tab>('analytics')
  const [historyOpen, setHistoryOpen] = useState(false)
  const [invitationsOpen, setInvitationsOpen] = useState(false)
  const [profilesOpen, setProfilesOpen] = useState(false)
  const [invitationCount, setInvitationCount] = useState<number | null>(null)

  // Count for the header badge. A failure just means no badge is shown.
  useEffect(() => {
    getInvitations().then(
      (list) => setInvitationCount(list.length),
      () => {},
    )
  }, [])

  const tabClass = (active: boolean) =>
    `h-8 rounded-[7px] border px-4 text-[13px] font-medium ${
      active ? 'border-zinc-900 bg-zinc-900 text-white' : 'border-transparent text-zinc-600 hover:text-zinc-900'
    }`

  return (
    <div className="flex min-h-screen flex-col">
      <Header
        badge="Admin"
        left={
          <div role="group" aria-label="Admin view" className="grid grid-cols-2 gap-1 rounded-[10px] border border-zinc-300 bg-zinc-100 p-1">
            <button type="button" aria-pressed={tab === 'analytics'} onClick={() => setTab('analytics')} className={tabClass(tab === 'analytics')}>
              Analytics
            </button>
            <button type="button" aria-pressed={tab === 'workbench'} onClick={() => setTab('workbench')} className={tabClass(tab === 'workbench')}>
              Workbench
            </button>
          </div>
        }
        right={
          <>
            <button type="button" onClick={() => setInvitationsOpen(true)} aria-label="Invitations" className="btn-outline">
              <Ticket className="size-4" aria-hidden="true" />
              <span className="hidden sm:inline">Invitations</span>
              {invitationCount !== null && <span className="tag">{invitationCount}</span>}
            </button>
            <button type="button" onClick={() => setProfilesOpen(true)} aria-label="Profiles" className="btn-outline">
              <Users className="size-4" aria-hidden="true" />
              <span className="hidden sm:inline">Profiles</span>
            </button>
          </>
        }
        onOpenHistory={() => {
          setTab('workbench')
          setHistoryOpen(true)
        }}
      />

      {tab === 'analytics' && <AnalyticsDashboard />}
      <div className={tab === 'workbench' ? 'contents' : 'hidden'}>
        <Workbench historyOpen={historyOpen} onCloseHistory={() => setHistoryOpen(false)} />
      </div>

      <InvitationsModal open={invitationsOpen} onClose={() => setInvitationsOpen(false)} onCountChange={setInvitationCount} />
      <ProfilesModal open={profilesOpen} onClose={() => setProfilesOpen(false)} />
    </div>
  )
}