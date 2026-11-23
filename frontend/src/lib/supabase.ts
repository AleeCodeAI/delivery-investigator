/*
 * Shared Supabase client. Handles sign in, sign out, session storage and
 * token refresh. Only the publishable key belongs in the frontend.
 * Setup problems are collected in configProblems (not thrown) so main.tsx can
 * show a readable message instead of a blank page.
 *
 * Email confirmation: the link in the confirmation email returns to the site
 * with tokens in the URL. We deliberately do NOT sign the user in from it
 * (detectSessionInUrl: false); they sign in manually. emailLinkOutcome records
 * what the link said so the sign-in page can show a notice, and the URL is
 * cleaned so tokens do not stay in the address bar or browser history.
 */
import { createClient } from '@supabase/supabase-js'

const url = import.meta.env.VITE_SUPABASE_URL as string | undefined
const key = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY as string | undefined
const apiUrl = import.meta.env.VITE_API_URL as string | undefined

const problems: string[] = []
if (!url) problems.push('VITE_SUPABASE_URL is missing.')
else if (!/^https?:\/\//.test(url)) problems.push('VITE_SUPABASE_URL must start with https:// (remove any quotes).')
if (!key) problems.push('VITE_SUPABASE_PUBLISHABLE_KEY is missing.')
if (!apiUrl) problems.push('VITE_API_URL is missing.')

export const configProblems = problems

export type EmailLinkOutcome = 'confirmed' | 'failed' | null

function readEmailLinkOutcome(): EmailLinkOutcome {
  const params = new URLSearchParams(window.location.hash.slice(1))
  let outcome: EmailLinkOutcome = null
  if (params.has('access_token') && params.get('type') === 'signup') outcome = 'confirmed'
  else if (params.has('error') || params.has('error_code')) outcome = 'failed'
  if (outcome) window.history.replaceState(null, '', window.location.pathname + window.location.search)
  return outcome
}

export const emailLinkOutcome = readEmailLinkOutcome()

// A harmless placeholder client is used when setup is incomplete; the app never renders in that case.
export const supabase = problems.length === 0
    ? createClient(url as string, key as string, { auth: { detectSessionInUrl: false } })
    : createClient('http://localhost', 'missing-key')