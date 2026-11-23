/*
 * Sign in / sign up screen (route /auth). Sign-up is invitation only and
 * needs the access token an administrator generated. Signing up does not log
 * the user in: they are told to confirm their email, then sign in manually.
 * After a successful sign-in the route guard redirects to their console.
 */
import { useEffect, useState, type FormEvent, type ReactNode } from 'react'
import { AlertCircle, ArrowRight, CheckCircle2, Eye, EyeOff, KeyRound, Loader2, MailCheck } from 'lucide-react'
import { EmailNotConfirmedError, useAuth } from '../auth/AuthContext'
import { Logo } from '../components/Logo'
import { emailLinkOutcome } from '../lib/supabase'

type Mode = 'signin' | 'signup'

const inputClass = 'field-input'
const RESEND_COOLDOWN_SECONDS = 30

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

function Notice({ icon: Icon, role, children }: { icon: typeof AlertCircle; role: 'alert' | 'status'; children: ReactNode }) {
  return (
    <div role={role} className="flex items-start gap-2 rounded-lg border border-zinc-300 bg-zinc-50 p-3 text-sm leading-normal">
      <Icon className="mt-0.5 size-4 shrink-0 text-zinc-700" aria-hidden="true" />
      <span>{children}</span>
    </div>
  )
}

// Sends the confirmation email again. A short cooldown stops accidental hammering.
function ResendConfirmation({ email, initialCooldown = 0 }: { email: string; initialCooldown?: number }) {
  const { resendConfirmation } = useAuth()
  const [cooldown, setCooldown] = useState(initialCooldown)
  const [sending, setSending] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (cooldown <= 0) return
    const timer = setTimeout(() => setCooldown((c) => c - 1), 1000)
    return () => clearTimeout(timer)
  }, [cooldown])

  async function resend() {
    if (sending || cooldown > 0) return
    setSending(true)
    setError(null)
    setMessage(null)
    try {
      await resendConfirmation(email)
      setMessage('Confirmation email sent. Check your inbox and spam folder.')
      setCooldown(RESEND_COOLDOWN_SECONDS)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not send the email. Try again.')
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="flex flex-col gap-2">
      <button type="button" onClick={() => void resend()} disabled={sending || cooldown > 0} className="btn-outline h-10 self-start px-4">
        {sending && <Loader2 className="size-4 animate-spin" aria-hidden="true" />}
        {cooldown > 0 ? `Resend in ${cooldown}s` : 'Resend confirmation email'}
      </button>
      {message && (
        <p role="status" className="text-[13px] text-zinc-600">
          {message}
        </p>
      )}
      {error && (
        <p role="alert" className="text-[13px]">
          {error}
        </p>
      )}
    </div>
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
  const [unconfirmed, setUnconfirmed] = useState(false) // sign-in failed only because the email is unconfirmed
  const [submitting, setSubmitting] = useState(false)
  const [sent, setSent] = useState<{ email: string; emailFailed: boolean } | null>(null)
  const [linkNotice, setLinkNotice] = useState(emailLinkOutcome) // result of the confirmation link, if the user just came from it

  const isSignIn = mode === 'signin'
  const shownError = error ?? notice

  function switchMode(next: Mode) {
    setMode(next)
    setError(null)
    setUnconfirmed(false)
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
    setLinkNotice(null)
    setUnconfirmed(false)
    const problem = validate()
    if (problem) {
      setError(problem)
      return
    }
    setError(null)
    setSubmitting(true)
    try {
      if (isSignIn) {
        await signIn(email.trim(), password)
      } else {
        const status = await signUp({ full_name: fullName.trim(), email: email.trim(), password, access_key: token.trim() })
        setSent({ email: email.trim(), emailFailed: status === 'created_email_failed' })
        setFullName('')
        setPassword('')
        setConfirm('')
        setToken('')
      }
    } catch (err) {
      setUnconfirmed(err instanceof EmailNotConfirmedError)
      setError(err instanceof Error ? err.message : 'Something went wrong. Try again.')
    } finally {
      setSubmitting(false)
    }
  }

  function goToSignIn() {
    setSent(null)
    switchMode('signin')
  }

  const tabClass = (active: boolean) =>
    `h-9 rounded-[7px] border text-[13px] font-medium ${
      active ? 'border-zinc-900 bg-zinc-900 text-white' : 'border-transparent bg-transparent text-zinc-600 hover:text-zinc-900'
    }`

  return (
    <div className="flex min-h-dvh flex-col bg-white text-zinc-900">
      <header className="px-8 py-5">
        <Logo showName />
      </header>

      <main className="flex flex-1 items-center justify-center p-6">
        <div className="flex w-full max-w-[420px] flex-col gap-6 rounded-[14px] border border-zinc-300 bg-white p-8 shadow-[0_1px_2px_rgba(0,0,0,.05),0_8px_24px_rgba(0,0,0,.06)]">
          {sent ? (
            <>
              <div className="flex flex-col gap-3">
                <MailCheck className="size-7" aria-hidden="true" />
                <h1 className="text-[22px] font-semibold tracking-[-0.02em]">Check your email</h1>
                <p className="text-sm leading-normal text-zinc-600">
                  We sent a confirmation link to <span className="break-all font-medium text-zinc-900">{sent.email}</span>. Open it to confirm your address, then come back here and sign in.
                </p>
              </div>

              {sent.emailFailed && <Notice icon={AlertCircle} role="alert">Your account was created, but the confirmation email could not be sent. Use the button below to send it again.</Notice>}

              <button type="button" onClick={goToSignIn} className="flex h-[46px] items-center justify-center gap-2 rounded-lg bg-zinc-900 text-sm font-medium text-white hover:bg-zinc-800">
                Go to sign in
                <ArrowRight className="size-4" aria-hidden="true" />
              </button>

              <div className="flex flex-col gap-2 border-t border-zinc-200 pt-5">
                <p className="text-[13px] text-zinc-600">Did not receive it? Check your spam folder, or send it again.</p>
                <ResendConfirmation email={sent.email} initialCooldown={sent.emailFailed ? 0 : RESEND_COOLDOWN_SECONDS} />
              </div>
            </>
          ) : (
            <>
              <div className="flex flex-col gap-1.5">
                <h1 className="text-[22px] font-semibold tracking-[-0.02em]">{isSignIn ? 'Welcome back' : 'Create your account'}</h1>
                <p className="text-sm leading-normal text-zinc-600">
                  {isSignIn ? 'Sign in to continue to your console.' : 'Registration is by invitation. Use the token your administrator gave you.'}
                </p>
              </div>

              {linkNotice === 'confirmed' && <Notice icon={CheckCircle2} role="status">Your email is confirmed. Sign in to continue.</Notice>}
              {linkNotice === 'failed' && <Notice icon={AlertCircle} role="status">This confirmation link is invalid or has expired. Sign in to get a new one.</Notice>}

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
                    <input id="full-name" type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="e.g. Sarah Chen" autoComplete="name" className={inputClass} />
                  </Field>
                )}

                <Field id="email" label="Work email">
                  <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="name@veloramarket.com" autoComplete="email" className={inputClass} />
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
                    <PasswordField id="confirm-password" label="Confirm password" value={confirm} onChange={setConfirm} placeholder="Re-enter your password" autoComplete="new-password" />
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

                {shownError && <Notice icon={AlertCircle} role="alert">{shownError}</Notice>}
                {isSignIn && unconfirmed && email.trim() && <ResendConfirmation email={email.trim()} />}

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
                <button type="button" onClick={() => switchMode(isSignIn ? 'signup' : 'signin')} className="font-medium text-zinc-900 underline underline-offset-[3px]">
                  {isSignIn ? 'Create an account' : 'Sign in'}
                </button>
              </p>
            </>
          )}
        </div>
      </main>

      <footer className="p-5 text-center text-xs text-zinc-600">Velora Market · Internal system · Authorized personnel only</footer>
    </div>
  )
}