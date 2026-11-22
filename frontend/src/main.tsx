/*
 * Application entry point: router and auth provider wrap the route table.
 * The outer error boundary is a last resort so a crash never leaves a blank page,
 * and a setup problem (missing .env values) is shown as a message, not a blank page.
 */
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { AuthProvider } from './auth/AuthContext'
import { ErrorBoundary } from './components/ErrorBoundary'
import { configProblems } from './lib/supabase'
import './index.css'

const crashFallback = (
  <div className="flex min-h-dvh flex-col items-center justify-center gap-4 p-6 text-center">
    <p className="text-sm">Something went wrong. Reload the page to continue.</p>
    <button type="button" onClick={() => window.location.reload()} className="btn-primary">
      Reload
    </button>
  </div>
)

const configScreen = (
  <div className="mx-auto flex min-h-dvh max-w-lg flex-col justify-center gap-4 p-6">
    <h1 className="text-xl font-semibold">Configuration problem</h1>
    <ul className="list-disc pl-5 text-sm leading-relaxed">
      {configProblems.map((p) => (
        <li key={p}>{p}</li>
      ))}
    </ul>
    <p className="text-sm text-zinc-600">
      Copy <span className="font-mono text-xs">frontend/.env.example</span> to <span className="font-mono text-xs">frontend/.env</span>, fill in the values, then stop and restart{' '}
      <span className="font-mono text-xs">npm run dev</span>. Changes to <span className="font-mono text-xs">.env</span> are only read at startup.
    </p>
  </div>
)

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {configProblems.length > 0 ? (
      configScreen
    ) : (
      <ErrorBoundary fallback={crashFallback}>
        <BrowserRouter>
          <AuthProvider>
            <App />
          </AuthProvider>
        </BrowserRouter>
      </ErrorBoundary>
    )}
  </StrictMode>,
)