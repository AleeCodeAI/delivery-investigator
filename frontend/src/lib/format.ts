/*
 * Display formatting for dates, money and addresses. Used at render time only;
 * stored and transmitted values stay as the backend sent them.
 */

const dateTime = new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' })
const dateOnly = new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' })
const usd = new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD' })

function parse(iso: string | null | undefined): Date | null {
  if (!iso) return null
  const d = new Date(iso)
  return Number.isNaN(d.getTime()) ? null : d
}

export function formatDateTime(iso: string | null | undefined): string {
  const d = parse(iso)
  return d ? dateTime.format(d) : '—'
}

export function formatDate(iso: string | null | undefined): string {
  const d = parse(iso)
  return d ? dateOnly.format(d) : '—'
}

// Decimals can arrive as strings, so convert before formatting.
export function formatMoney(value: string | number): string {
  const n = Number(value)
  return Number.isFinite(n) ? usd.format(n) : String(value)
}

export function formatAddress(street: string, city: string, state: string, zip: string): string {
  return `${street}, ${city}, ${state} ${zip}`
}