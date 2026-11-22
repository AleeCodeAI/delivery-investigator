/*
 * Route guards. Hiding screens here is a convenience only; the backend
 * decides what each caller may do.
 *   RequireAuth      logged out -> /auth
 *   RequireAdmin     operator   -> /operator
 *   RedirectIfAuthed logged in  -> their console
 *   HomeRedirect     "/" follows the same rules
 */
import { Loader2 } from 'lucide-react'
import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from './AuthContext'
import type { Role } from '../lib/types'

function homePathFor(role: Role): string {
  return role === 'admin' ? '/admin' : '/operator'
}

// Shown while the session and profile load, so guarded routes never flash.
function FullPageLoading() {
  return (
    <div role="status" aria-live="polite" className="flex min-h-screen items-center justify-center bg-white">
      <Loader2 className="size-6 animate-spin text-zinc-500" aria-hidden="true" />
      <span className="sr-only">Loading</span>
    </div>
  )
}

export function RequireAuth() {
  const { profile, loading } = useAuth()
  if (loading) return <FullPageLoading />
  if (!profile) return <Navigate to="/auth" replace />
  return <Outlet />
}

export function RequireAdmin() {
  const { profile } = useAuth()
  if (profile?.role !== 'admin') return <Navigate to="/operator" replace />
  return <Outlet />
}

export function RedirectIfAuthed() {
  const { profile, loading } = useAuth()
  if (loading) return <FullPageLoading />
  if (profile) return <Navigate to={homePathFor(profile.role)} replace />
  return <Outlet />
}

export function HomeRedirect() {
  const { profile, loading } = useAuth()
  if (loading) return <FullPageLoading />
  return <Navigate to={profile ? homePathFor(profile.role) : '/auth'} replace />
}