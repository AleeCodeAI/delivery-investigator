/*
 * Auth state for the whole app: Supabase session plus the backend profile
 * (GET /me). Role is always read from the profile, never from the JWT.
 * Exposes signIn, signUp (invitation only, does NOT sign in: the user must
 * confirm their email first), resendConfirmation, signOut and a one-line
 * notice for problems found while restoring a session.
 */
import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from 'react'
import type { Session } from '@supabase/supabase-js'
import { ApiError, getMe, resendConfirmation as apiResend, signUp as apiSignUp, type SignUpInput, type SignUpStatus } from '../lib/api'
import { supabase } from '../lib/supabase'
import type { Profile } from '../lib/types'

interface AuthContextValue {
  profile: Profile | null
  loading: boolean
  notice: string | null
  signIn: (email: string, password: string) => Promise<void>
  signUp: (input: SignUpInput) => Promise<SignUpStatus>
  resendConfirmation: (email: string) => Promise<void>
  signOut: () => Promise<void>
  changePassword: (current: string, next: string) => Promise<void>
  clearNotice: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

// Thrown by signIn when the password was right but the email is not confirmed yet.
// eslint-disable-next-line react-refresh/only-export-components
export class EmailNotConfirmedError extends Error {
  constructor() {
    super('Your email address is not confirmed yet. Open the link in the confirmation email, or send it again below.')
    this.name = 'EmailNotConfirmedError'
  }
}

function profileErrorMessage(err: unknown): string {
  if (err instanceof ApiError && err.status === 403) return 'Your account is not set up. Contact an administrator.'
  return err instanceof ApiError ? err.message : 'Could not load your account. Try again.'
}

function signUpErrorMessage(err: unknown): string {
  if (err instanceof ApiError) {
    if (err.status === 403) return err.message
    if (err.status === 409) return 'An account with this email already exists.'
    if (err.status === 429) return 'Too many attempts. Wait a minute and try again.'
    if (err.status === 0 || err.status === 408) return err.message
  }
  return 'Could not create the account. Try again.'
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [profile, setProfile] = useState<Profile | null>(null)
  const [loading, setLoading] = useState(true)
  const [notice, setNotice] = useState<string | null>(null)

  // One in-flight profile load per user, so the listener and signIn never double-fetch.
  const inflight = useRef<{ userId: string; promise: Promise<void> } | null>(null)
  // True while signIn is running; the listener then leaves the work to signIn.
  const manualSignIn = useRef(false)

  const syncProfile = useCallback((session: Session | null): Promise<void> => {
    if (!session) {
      inflight.current = null
      setProfile(null)
      return Promise.resolve()
    }
    if (inflight.current?.userId === session.user.id) return inflight.current.promise

    const promise = getMe().then(setProfile, async (err: unknown) => {
      inflight.current = null
      await supabase.auth.signOut()
      throw new Error(profileErrorMessage(err))
    })
    inflight.current = { userId: session.user.id, promise }
    return promise
  }, [])

  useEffect(() => {
    const { data } = supabase.auth.onAuthStateChange((event, session) => {
      // Deferred on purpose: calling Supabase inside this callback can deadlock.
      setTimeout(() => {
        if (event === 'SIGNED_OUT') {
          void syncProfile(null)
          setLoading(false)
        } else if (event === 'INITIAL_SESSION' || (event === 'SIGNED_IN' && !manualSignIn.current)) {
          syncProfile(session)
            .catch((err: Error) => setNotice(err.message))
            .finally(() => setLoading(false))
        }
        // TOKEN_REFRESHED and USER_UPDATED (e.g. password change) need no reload.
      }, 0)
    })
    return () => data.subscription.unsubscribe()
  }, [syncProfile])

  const signIn = useCallback(
    async (email: string, password: string) => {
      manualSignIn.current = true
      try {
        const { data, error } = await supabase.auth.signInWithPassword({ email, password })
        if (error?.code === 'email_not_confirmed' || /not confirmed/i.test(error?.message ?? '')) throw new EmailNotConfirmedError()
        if (error || !data.session) throw new Error('Incorrect email or password.')
        await syncProfile(data.session)
      } finally {
        manualSignIn.current = false
      }
    },
    [syncProfile],
  )

  // Creates the account only. No sign-in here: Supabase refuses until the email is confirmed.
  const signUp = useCallback(async (input: SignUpInput): Promise<SignUpStatus> => {
    try {
      return await apiSignUp(input)
    } catch (err) {
      throw new Error(signUpErrorMessage(err))
    }
  }, [])

  const resendConfirmation = useCallback(async (email: string) => {
    try {
      await apiResend(email)
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 429) throw new Error('Too many attempts. Wait a minute and try again.')
        if (err.status === 422) throw new Error('Enter a valid email address.')
        if (err.status === 0 || err.status === 408) throw new Error(err.message)
      }
      throw new Error('Could not send the email. Try again.')
    }
  }, [])

  const signOut = useCallback(async () => {
    await supabase.auth.signOut()
    await syncProfile(null)
  }, [syncProfile])

  // Supabase's updateUser does not check the current password, so verify it first.
  const changePassword = useCallback(
    async (current: string, next: string) => {
      if (!profile) throw new Error('Please sign in again.')
      manualSignIn.current = true
      try {
        const { error: verifyError } = await supabase.auth.signInWithPassword({ email: profile.email, password: current })
        if (verifyError) throw new Error('Current password is incorrect.')
        const { error } = await supabase.auth.updateUser({ password: next })
        if (error) {
          throw new Error(
            error.message.toLowerCase().includes('different')
              ? 'New password must be different from the current one.'
              : 'Could not update the password. Try again.',
          )
        }
      } finally {
        manualSignIn.current = false
      }
    },
    [profile],
  )

  const clearNotice = useCallback(() => setNotice(null), [])

  return (
    <AuthContext.Provider value={{ profile, loading, notice, signIn, signUp, resendConfirmation, signOut, changePassword, clearNotice }}>
      {children}
    </AuthContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>.')
  return ctx
}