/*
 * Sign in / sign up screen (route /auth). Sign-up is invitation only and
 * needs the access token an administrator generated. After success the
 * route guard redirects to the user's console, so no navigation happens here.
 */
import { useState, type FormEvent, type ReactNode } from 'react'
import { AlertCircle, ArrowRight, Eye, EyeOff, KeyRound, Loader2 } from 'lucide-react'
import { useAuth } from '../auth/AuthContext'
import { Logo } from '../components/Logo'

type Mode = 'signin' | 'signup'

const inputClass = 'field-input'

function Field({ id, label, hint, children }: { id: string; label: string; hint?: string; children: ReactNode }) {
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={id} className="text-[13px] font-medium">
        {label}
      </label>
      {children}
      {hint && <span className="text-xs leading-normal text-zinc-600">{hint}</span>}
    </div>
  )
}

interface PasswordFieldProps {
  id: string
  label: string
  value: string
  onChange: (value: string) => void
  placeholder: string
  autoComplete: string
  hint?: string
}

function PasswordField({ id, label, value, onChange, placeholder, autoComplete, hint }: PasswordFieldProps) {
  const [visible, setVisible] = useState(false)
  const Icon = visible ? EyeOff : Eye
  return (
    <Field id={id} label={label} hint={hint}>
      <div className="relative">
        <input
          id={id}
          type={visible ? 'text' : 'password'}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          autoComplete={autoComplete}
          className={`${inputClass} pr-12`}
        />
        <button
          type="button"
          onClick={() => setVisible((v) => !v)}
          aria-label={visible ? 'Hide password' : 'Show password'}
          aria-pressed={visible}
          className="absolute right-1.5 top-[3px] flex size-[38px] items-center justify-center rounded-md hover:bg-zinc-100"
        >
          <Icon className="size-[18px] text-zinc-600" aria-hidden="true" />
        </button>
      </div>
    </Field>
  )
}

export default function AuthPage() {
  const { signIn, signUp, notice, clearNotice } = useAuth()
  const [mode, setMode] = useState<Mode>('signin')
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [token, setToken] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const isSignIn = mode === 'signin'
  const shownError = error ?? notice

  function switchMode(next: Mode) {
    setMode(next)
    setError(null)
    clearNotice()
  }

  function validate(): string | null {
    if (isSignIn) return email.trim() && password ? null : 'Enter your email and password.'
    if (!fullName.trim() || !email.trim() || !password || !confirm || !token.trim()) return 'Fill in all fields.'
    if (password.length < 8) return 'Password must be at least 8 characters.'
    if (password !== confirm) return 'Passwords do not match.'
    return null
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (submitting) return
    clearNotice()
    const problem = validate()
    if (problem) {
      setError(problem)
      return
    }
    setError(null)
    setSubmitting(true)
    try {
      if (isSignIn) await signIn(email.trim(), password)
      else await signUp({ full_name: fullName.trim(), email: email.trim(), password, access_key: token.trim() })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong. Try again.')
    } finally {
      setSubmitting(false)
    }
  }

  const tabClass = (active: boolean) =>
    `h-9 rounded-[7px] border text-[13px] font-medium ${
      active ? 'border-zinc-900 bg-zinc-900 text-white' : 'border-transparent bg-transparent text-zinc-600 hover:text-zinc-900'
    }`

  return (
    <div className="flex min-h-screen flex-col bg-white text-zinc-900">
      <header className="px-8 py-5">
        <Logo showName />
      </header>

      <main className="flex flex-1 items-center justify-center p-6">
        <div className="flex w-full max-w-[420px] flex-col gap-6 rounded-[14px] border border-zinc-300 bg-white p-8 shadow-[0_1px_2px_rgba(0,0,0,.05),0_8px_24px_rgba(0,0,0,.06)]">
          <div className="flex flex-col gap-1.5">
            <h1 className="text-[22px] font-semibold tracking-[-0.02em]">{isSignIn ? 'Welcome back' : 'Create your account'}</h1>
            <p className="text-sm leading-normal text-zinc-600">
              {isSignIn
                ? 'Sign in to continue to your console.'
                : 'Registration is by invitation. Use the token your administrator gave you.'}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-1 rounded-[10px] border border-zinc-300 bg-zinc-100 p-1">
            <button type="button" aria-pressed={isSignIn} onClick={() => switchMode('signin')} className={tabClass(isSignIn)}>
              Sign in
            </button>
            <button type="button" aria-pressed={!isSignIn} onClick={() => switchMode('signup')} className={tabClass(!isSignIn)}>
              Sign up
            </button>
          </div>

          <form noValidate onSubmit={handleSubmit} className="flex flex-col gap-4">
            {!isSignIn && (
              <Field id="full-name" label="Full name">
                <input
                  id="full-name"
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Sarah Chen"
                  autoComplete="name"
                  className={inputClass}
                />
              </Field>
            )}

            <Field id="email" label="Work email">
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@veloramarket.com"
                autoComplete="email"
                className={inputClass}
              />
            </Field>

            <PasswordField
              id="password"
              label="Password"
              value={password}
              onChange={setPassword}
              placeholder={isSignIn ? 'Enter your password' : 'Create a password'}
              autoComplete={isSignIn ? 'current-password' : 'new-password'}
              hint={isSignIn ? undefined : 'At least 8 characters.'}
            />

            {!isSignIn && (
              <>
                <PasswordField
                  id="confirm-password"
                  label="Confirm password"
                  value={confirm}
                  onChange={setConfirm}
                  placeholder="Re-enter your password"
                  autoComplete="new-password"
                />
                <Field id="access-token" label="Access token" hint="Single-use and tied to your email address.">
                  <div className="relative">
                    <KeyRound className="pointer-events-none absolute left-[13px] top-3.5 size-4 text-zinc-600" aria-hidden="true" />
                    <input
                      id="access-token"
                      type="text"
                      value={token}
                      onChange={(e) => setToken(e.target.value)}
                      placeholder="Paste your access token"
                      autoComplete="off"
                      spellCheck={false}
                      className={`${inputClass} pl-[38px] font-mono text-[13px]`}
                    />
                  </div>
                </Field>
              </>
            )}

            {shownError && (
              <div role="alert" className="flex items-start gap-2 rounded-lg border border-zinc-300 bg-zinc-50 p-3 text-sm leading-normal">
                <AlertCircle className="mt-0.5 size-4 shrink-0 text-zinc-700" aria-hidden="true" />
                <span>{shownError}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={submitting}
              className="mt-1 flex h-[46px] items-center justify-center gap-2 rounded-lg bg-zinc-900 text-sm font-medium text-white hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {submitting ? (isSignIn ? 'Signing in' : 'Creating account') : isSignIn ? 'Sign in' : 'Create account'}
              {submitting ? <Loader2 className="size-4 animate-spin" aria-hidden="true" /> : <ArrowRight className="size-4" aria-hidden="true" />}
            </button>
          </form>

          <p className="text-center text-[13px] text-zinc-600">
            {isSignIn ? 'Have an invitation token? ' : 'Already have an account? '}
            <button
              type="button"
              onClick={() => switchMode(isSignIn ? 'signup' : 'signin')}
              className="font-medium text-zinc-900 underline underline-offset-[3px]"
            >
              {isSignIn ? 'Create an account' : 'Sign in'}
            </button>
          </p>
        </div>
      </main>

      <footer className="p-5 text-center text-xs text-zinc-600">Velora Market · Internal system · Authorized personnel only</footer>
    </div>
  )
}