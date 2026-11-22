/*
 * Shared Supabase client. Handles sign in, sign out, session storage and
 * token refresh. Only the publishable key belongs in the frontend.
 * Setup problems are collected in configProblems (not thrown) so main.tsx can
 * show a readable message instead of a blank page.
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

// A harmless placeholder client is used when setup is incomplete; the app never renders in that case.
export const supabase = problems.length === 0 ? createClient(url as string, key as string) : createClient('http://localhost', 'missing-key')