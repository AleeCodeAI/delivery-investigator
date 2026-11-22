/*
 * Operator console (route /operator): header plus the investigation workbench.
 */
import { useState } from 'react'
import { Header } from '../components/Header'
import { Workbench } from '../components/Workbench'

export default function OperatorPage() {
  const [historyOpen, setHistoryOpen] = useState(false)

  return (
    <div className="flex min-h-screen flex-col">
      <Header onOpenHistory={() => setHistoryOpen(true)} />
      <Workbench historyOpen={historyOpen} onCloseHistory={() => setHistoryOpen(false)} />
    </div>
  )
}