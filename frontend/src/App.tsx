/*
 * Route table. Guards live in auth/RouteGuards.tsx.
 *   /auth      logged-out users only
 *   /operator  any signed-in user (admins may open it too)
 *   /admin     admins only
 *   /          redirects by role
 */
import { Navigate, Route, Routes } from 'react-router-dom'
import { HomeRedirect, RedirectIfAuthed, RequireAdmin, RequireAuth } from './auth/RouteGuards'
import AdminPage from './pages/AdminPage'
import AuthPage from './pages/AuthPage'
import OperatorPage from './pages/OperatorPage'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomeRedirect />} />
      <Route element={<RedirectIfAuthed />}>
        <Route path="/auth" element={<AuthPage />} />
      </Route>
      <Route element={<RequireAuth />}>
        <Route path="/operator" element={<OperatorPage />} />
        <Route element={<RequireAdmin />}>
          <Route path="/admin" element={<AdminPage />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}