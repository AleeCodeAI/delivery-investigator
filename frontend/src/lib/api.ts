/*
 * API client: the only place that talks to the backend.
 * Attaches the Supabase JWT, converts failures into ApiError with a readable
 * message, and signs the user out on a 401. Components must not call fetch.
 */
import { supabase } from './supabase'
import type { Analytics, Execution, Invitation, Profile, RunResult, UpfrontData } from './types'

const API_URL = ((import.meta.env.VITE_API_URL as string | undefined) ?? '').replace(/\/+$/, '')

const GENERIC_ERROR = 'Something went wrong. Please try again.'
const NETWORK_ERROR = 'Could not reach the server. Check your connection and try again.'
const TIMEOUT_ERROR = 'This is taking longer than expected. Check History in a minute.'
const INVESTIGATION_TIMEOUT_MS = 3 * 60 * 1000

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

function extractMessage(body: unknown): string | null {
  if (typeof body !== 'object' || body === null) return null
  const data = body as Record<string, unknown>
  if (typeof data.message === 'string' && data.message) return data.message
  if (typeof data.error === 'string' && data.error) return data.error
  return null
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'DELETE'
  body?: unknown
  auth?: boolean
  timeoutMs?: number
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, auth = true, timeoutMs } = options

  const headers: Record<string, string> = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'

  if (auth) {
    const { data } = await supabase.auth.getSession()
    const token = data.session?.access_token
    if (!token) throw new ApiError(401, 'Please sign in to continue.')
    headers.Authorization = `Bearer ${token}`
  }

  const controller = new AbortController()
  const timer = timeoutMs ? setTimeout(() => controller.abort(), timeoutMs) : undefined

  let status = 0
  let ok = false
  let data: unknown = null
  try {
    const res = await fetch(`${API_URL}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    })
    status = res.status
    ok = res.ok
    data = await res.json().catch(() => null) // an error page may not be JSON
  } catch (err) {
    if (err instanceof DOMException && err.name === 'AbortError') throw new ApiError(408, TIMEOUT_ERROR)
    throw new ApiError(0, NETWORK_ERROR)
  } finally {
    clearTimeout(timer)
  }

  if (!ok) {
    // Sign-out triggers AuthContext's listener, which clears the profile and
    // lets the route guards redirect. Skipped for public endpoints.
    if (status === 401 && auth) await supabase.auth.signOut()
    throw new ApiError(status, extractMessage(data) ?? GENERIC_ERROR)
  }

  return data as T
}

interface Envelope<T> {
  status: string
  result: T
}

export interface SignUpInput {
  full_name: string
  email: string
  password: string
  access_key: string
}

export async function signUp(input: SignUpInput): Promise<void> {
  await request<unknown>('/auth/sign-up/', { method: 'POST', body: input, auth: false })
}

export async function getMe(): Promise<Profile> {
  return (await request<Envelope<Profile>>('/me')).result
}

export interface InvestigationInput {
  customer_id: string
  order_id: string
  investigation_prompt: string
}

export async function runInvestigation(input: InvestigationInput): Promise<RunResult> {
  const res = await request<Envelope<RunResult>>('/master-pipeline/delivery-investigator-run', {
    method: 'POST',
    body: input,
    timeoutMs: INVESTIGATION_TIMEOUT_MS,
  })
  return res.result
}

export async function getUpfrontData(input: InvestigationInput): Promise<UpfrontData> {
  return (await request<Envelope<UpfrontData>>('/upfront_data/get-upfront-data', { method: 'POST', body: input })).result
}

export async function getHistory(): Promise<Execution[]> {
  return (await request<Envelope<Execution[]>>('/history/get_user_history')).result
}

export async function getAnalytics(): Promise<Analytics> {
  return (await request<Envelope<Analytics>>('/admin/get_execution_analytics')).result
}

export async function getInvitations(): Promise<Invitation[]> {
  return (await request<Envelope<Invitation[]>>('/admin/get_all_invitation')).result
}

export async function createInvitation(name: string, email: string): Promise<string> {
  const res = await request<Envelope<{ access_key: string }>>('/admin/insert-invitation', {
    method: 'POST',
    body: { name, email },
  })
  return res.result.access_key
}

// Deleting an invitation also deletes the person's account and profile.
export async function deleteInvitation(access_key: string, email: string): Promise<void> {
  try {
    await request<unknown>('/admin/delete-invitation/', { method: 'DELETE', body: { access_key, email } })
  } catch (err) {
    // The 404 body has no message field, so supply one.
    if (err instanceof ApiError && err.status === 404) throw new ApiError(404, 'Invitation not found. It may already have been deleted.')
    throw err
  }
}

export async function getProfiles(): Promise<Profile[]> {
  return (await request<Envelope<Profile[]>>('/admin/get_all_profiles')).result
}

// Operator to admin only; there is no demote.
export async function promoteToAdmin(user_id: string, email: string): Promise<void> {
  try {
    await request<unknown>('/admin/update-role/', { method: 'POST', body: { user_id, email } })
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) throw new ApiError(404, 'Profile not found.')
    throw err
  }
}

export async function checkHealth(): Promise<unknown> {
  return request<unknown>('/health', { auth: false })
}