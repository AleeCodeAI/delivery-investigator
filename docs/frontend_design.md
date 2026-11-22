# Delivery Investigator: Frontend Build Plan

This document is the full brief for building the frontend. Read it end to end before writing code. Where it says "decided", do not re-debate it; where it says "assumed", build it that way and flag it if the backend disagrees.

---

## 1. What this product is

**Delivery Investigator** is an internal tool for **Velora Market** (a fictional California e-commerce company). Human operators use it to investigate delivery complaints. An LLM agent reads the order's records and returns a bounded, evidence-backed finding plus a suggested next step. The system is **read-only**: it never refunds, reships, edits records or contacts anyone. The human decides what to do.

Key product rules that shape the UI:

- **Inconclusive is a valid result,** not an error. `investigation_success: false` is shown calmly as "Inconclusive".
- **The UI never implies actions.** No "refund", "reship" or "contact customer" buttons. The recommendation is advice text only.
- **Do not hint at a cause in the form.** The prompt placeholder is neutral ("What do you want to establish about this delivery?"). Never prefill suspected causes.
- **It is an internal tool.** Accounts are created only through admin invitations and removed only by an admin. There is **no self-service sign-up and no "delete my account" button.**

---

## 2. Users and screens

Two roles, returned by the backend (`GET /me`): `operator` and `admin`.

| Screen | Route | Who |
|---|---|---|
| Sign in / Sign up | `/auth` | Everyone (logged out) |
| Operator console | `/operator` | Operators (admins may also open it) |
| Admin console | `/admin` | Admins only |

Admin console has two tabs: **Analytics** (default) and **Workbench** (the same investigation component the operator uses).

Redirect rules:
- Logged out → `/auth` for every route except `/auth`.
- Logged in on `/auth` → their console (`admin` → `/admin`, `operator` → `/operator`).
- Operator opening `/admin` → `/operator`.
- `/` → redirects by the same rules.

---

## 3. Stack (decided)

- React + TypeScript + Vite (already scaffolded in `frontend/`)
- Tailwind CSS v4 via `@tailwindcss/vite`
- `react-router-dom` for routes
- `@supabase/supabase-js` for sign in, sign out, session and JWT
- `lucide-react` for icons
- No state library, no data-fetching library, no test setup. Plain `useState`, `useEffect` and `useContext`. Keep it simple; the owner is not a frontend developer, so favour readable code with short comments.

Environment variables (`.env`, all must start with `VITE_`):

```
VITE_SUPABASE_URL=
VITE_SUPABASE_PUBLISHABLE_KEY=
VITE_API_URL=
```

**Never** use or mention the Supabase secret/service-role key in the frontend.

---

## 4. Project structure

```
frontend/
├── .env  .env.example  .gitignore  index.html  package.json  vite.config.ts  tsconfig*.json
└── src/
    ├── main.tsx            entry
    ├── App.tsx             routes
    ├── index.css           Tailwind import + fonts
    ├── lib/
    │   ├── supabase.ts     createClient (URL + publishable key)
    │   ├── api.ts          every backend call; attaches JWT; handles 401
    │   └── types.ts        TypeScript types for API data
    ├── auth/
    │   ├── AuthContext.tsx session + profile (from /me) + signIn/signUp/signOut
    │   └── RouteGuards.tsx <RequireAuth>, <RequireAdmin>, <RedirectIfAuthed>
    ├── pages/
    │   ├── AuthPage.tsx
    │   ├── OperatorPage.tsx
    │   └── AdminPage.tsx
    └── components/
        ├── Logo.tsx  Header.tsx  ProfileMenu.tsx  HistoryDrawer.tsx  Modal.tsx
        ├── Workbench.tsx       session tabs + form + results (shared)
        ├── ReportView.tsx      report card + suggested-step card
        ├── UpfrontRecords.tsx  collapsible customer / order / shipment / events
        └── admin/
            ├── AnalyticsDashboard.tsx
            ├── InvitationsModal.tsx
            └── ProfilesModal.tsx
```

Keep this structure. Do not add folders (hooks, utils, store) unless a file becomes genuinely unmanageable.

---

## 5. Authentication workflow

**Division of labour:** the frontend signs users in and sends the JWT with every backend request. The backend verifies the JWT and decides what the caller may do. Hiding the admin console in the UI is a convenience, not security.

### Sign in
1. `supabase.auth.signInWithPassword({ email, password })`.
2. On success, `AuthContext` calls `GET /me` to load the profile (name, email, role) and redirects by role.
3. On failure show one generic message: **"Incorrect email or password."** Do not say which was wrong.

### Sign up (invitation only)
Fields: full name, work email, password (**min 8 characters**), confirm password, access token (a UUID the admin generated, tied to the email).

1. Validate locally: all fields filled, password ≥ 8, passwords match.
2. `POST /auth/sign-up/` with JSON `{ full_name, email, password, access_key }`. This endpoint validates the invitation and creates the Supabase user server-side. It is **not** a Supabase `signUp` call.
3. `201` → immediately call `signInWithPassword` with the same email and password → load `/me` → redirect.
4. `403` → show the backend message ("Invalid invitation."). `409` → "An account with this email already exists." `429` → "Too many attempts. Wait a minute and try again." Anything else → "Could not create the account. Try again."
5. On failure keep what the user typed (except nothing needs clearing) and show the error inline above the button.

### Session and JWT
- Supabase stores the session and refreshes the token. Get the current token with `supabase.auth.getSession()` inside `api.ts` on every call.
- `api.ts` adds `Authorization: Bearer <access_token>` to every backend request.
- On any `401` from the backend: call `supabase.auth.signOut()`, clear the profile, go to `/auth`.
- `AuthContext` listens to `supabase.auth.onAuthStateChange` to keep state in sync.
- Show a full-page neutral loading state while the initial session and profile load, so guarded routes do not flash.
- If the session exists but `/me` returns `403` (no profile), sign out and show "Your account is not set up. Contact an administrator."

### Profile menu (both consoles)
Shows name, email, role. Actions:
- **Change password:** fields current, new (≥ 8), confirm. Supabase's `updateUser` does not verify the current password, so first call `signInWithPassword({ email, password: current })`; if that fails show "Current password is incorrect"; otherwise `supabase.auth.updateUser({ password: next })`.
- **Log out:** `signOut()` then `/auth`.
- **No delete account.**

---

## 6. Backend API contract

Base URL: `VITE_API_URL`. All endpoints below need the Bearer JWT except `/auth/sign-up/`.

**Error shape:** most errors are `{ "status": "error", "message": "..." }`. Some are different: rate limit (429) returns `{ "error": "..." }`, validation (422) returns `{ message, detail: [...] }`, and a delete 404 returns `{ status: "failure", email }`. `api.ts` must extract a readable message from `message`, then `error`, then fall back to a generic string, and throw an `ApiError` with `status` and `message`.

| # | Method + path | Access | Body | Success response |
|---|---|---|---|---|
| 1 | `POST /auth/sign-up/` | public, 5/min | `{ full_name, email, password, access_key }` | 201 `{ status: "success" }` |
| 2 | `GET /me` | any user | none | `{ status, result: Profile }` |
| 3 | `POST /master-pipeline/delivery-investigator-run` | any user | `{ customer_id, order_id, investigation_prompt }` | `{ status, investigation_success: "True"\|"False", result: { agent_result, recommender_result } }` |
| 4 | `POST /upfront_data/get-upfront-data` | any user | `{ customer_id, order_id, investigation_prompt }` | `{ status, result: UpfrontData }` |
| 5 | `GET /history/get_user_history` | any user | none | `{ status, number_of_histories, result: Execution[] }` |
| 6 | `GET /admin/get_execution_analytics` | admin | none | `{ status, result: Analytics }` |
| 7 | `GET /admin/get_all_invitation` | admin | none | `{ status, number_of_invitations, result: Invitation[] }` |
| 8 | `POST /admin/insert-invitation` | admin | `{ name, email }` | `{ status, result: { access_key } }` |
| 9 | `DELETE /admin/delete-invitation/` | admin | JSON body `{ access_key, email }` | `{ status, deleted_invitation_email }`; 404 if not found |
| 10 | `GET /admin/get_all_profiles` | admin | none | `{ status, number_of_profiles, result: Profile[] }` |
| 11 | `POST /admin/update-role/` | admin | `{ user_id, email }` | `{ status, updated_role_email }`; 404 if not found |

Notes:
- Endpoint 3 and 4 take the **same body**. Endpoint 4 has no `investigation_prompt` use, but the schema requires the field; send it.
- Endpoint 9 is a **DELETE with a JSON body**. Set `Content-Type: application/json` and pass `body`.
- Deleting an invitation also deletes the person's account and profile on the backend.
- Endpoint 11 only promotes operator → admin. There is no demote.
- Dates arrive as ISO strings. Format with `Intl.DateTimeFormat` in the user's locale.

### Types (put in `lib/types.ts`)

```ts
export type Role = 'admin' | 'operator'

export interface Profile {
  user_id: string
  name: string | null
  email: string
  role: Role
  created_at: string
}

export interface AgentResult {
  investigation_report: string
  evidences: string[]          // plain strings
  investigation_success: boolean
  confidence: number           // 0..1
}

export interface RecommenderResult {
  recommendation: string
  evidences: string[]
  confidence: number           // 0..1
}

export interface RunResult {
  agent_result: AgentResult
  recommender_result: RecommenderResult | null   // can be null
}

export interface Customer {
  customer_id: string; name: string
  current_street: string; current_city: string; current_state: string; current_zip: string
  account_created_at: string
}
export interface Order {
  order_id: string; customer_id: string; order_date: string
  sku: string; product_name: string; quantity: number
  unit_price: string | number; order_value: string | number   // Decimal: may arrive as string
  delivery_street: string; delivery_city: string; delivery_state: string; delivery_zip: string
  order_status: string; fulfilled_from_warehouse_id: string
}
export interface Shipment {
  shipment_id: string; order_id: string; carrier: string; tracking_number: string
  ship_date: string; shipment_status: string; delivered_at: string | null
  delivery_confirmation: string
}
export interface ShipmentEvent {
  event_id: string; shipment_id: string; event_type: string
  event_timestamp: string; location: string; description: string
}
export interface UpfrontData {
  customer: Customer
  order: Order
  shipment: Shipment | null              // can be null (no shipment yet)
  shipment_events: ShipmentEvent[] | null
}

export interface Execution {            // one history item
  execution_id: string
  user_id: string | null
  customer_id: string
  order_id: string
  investigation_prompt: string
  upfront_data: UpfrontData | null
  agent_result: AgentResult | null
  recommender_result: RecommenderResult | null
  execution_success: boolean | null
  execution_date: string
  error_message: string | null
}

export interface Invitation {
  access_key: string
  name: string
  email: string
  status: boolean                        // true = redeemed (account made), false = pending
  created_at: string
}

// ASSUMED shape (matches the original design); verify with a real response
export interface Analytics {
  overview: {
    total_executions: number; successful_executions: number; failed_executions: number
    success_rate: number               // percent, e.g. 75.0
    unique_orders_investigated: number; unique_customers_investigated: number
    active_operators: number
  }
  failure_analytics: { total_failures: number; common_errors: Record<string, number> }
  execution_trends: {
    daily: Record<string, { total: number; successful: number }>
    weekly: Record<string, { total: number; successful: number }>
    monthly: Record<string, { total: number; successful: number }>
  }
  invitations: { total_invitations: number }
}
```

---

## 7. Investigation workflow (the core feature)

Used by both consoles through one `Workbench` component.

### Session model (in component state)

```ts
interface Session {
  id: string                 // local id, e.g. crypto.randomUUID()
  orderId: string
  customerId: string
  prompt: string
  status: 'running' | 'done' | 'error'
  startedAt: number          // for the elapsed timer
  upfront?: UpfrontData | null
  run?: RunResult
  errorMessage?: string
  fromHistory?: boolean
}
```

### Starting an investigation
1. Operator fills Order ID, Customer ID, Investigation prompt (all required, trimmed; IDs are used as typed, uppercase not forced).
2. On submit: create a session with `status: 'running'`, add it as a new tab, select it, clear the form.
3. Fire **two requests in parallel**: run endpoint (3) and upfront endpoint (4).
   - The upfront response fills the collapsible records panel as soon as it arrives, even while the agent is still running. If it fails, leave the panel empty with "Records unavailable"; do not fail the session for that.
   - The run response sets `status: 'done'` with `run`, or `'error'` with `errorMessage`.
4. Each session is independent. The operator can start another while one is running. Closing a tab only removes it from the screen (the run still completes and is saved server-side).
5. Runs can take a while. Do not set a short timeout; use an `AbortController` with about 3 minutes, then show "This is taking longer than expected. Check History in a minute."
6. The running state shows a spinner, "Investigating <ORDER ID>…" and an elapsed timer. No tool-call progress is available from the backend.

### Showing a result (`ReportView`)
Two cards, stacked.

**Investigation report card**
- Header: "Investigation report" and a confidence badge.
- If `investigation_success` is true: badge text like "High · 85%". If false: show an **"Inconclusive"** badge (neutral grey, not red) and, above the report text, nothing alarming; the report text itself explains what is unknown.
- Body: `investigation_report` as paragraphs (preserve line breaks).
- "Supporting evidence": each string in `evidences` as one evidence row (grey bordered box). Evidence is plain text; do not invent IDs or source tags.

**Suggested next step card**
- Title is **"Suggested next step"**, never "action".
- Shows `recommendation`, its confidence badge, its `evidences` list, and a **Copy** button that copies: order ID, the report text, and the recommendation.
- If `recommender_result` is `null`: show "No recommendation was produced for this investigation."

**Confidence label** (UI-only thresholds, keep in one helper): `>= 0.8` High, `>= 0.5` Moderate, otherwise Low; always show the percentage too.

**Error state** (`status: 'error'`): a calm card with the message and a note that the investigation could not be completed. Backend 500 message is "The investigation could not be completed. Please try again later." Show it as is.

### Upfront records panel (`UpfrontRecords`)
Collapsed by default, under the results. Three columns (customer, order, shipment) then a table of shipment events sorted by `event_timestamp` ascending (never by `event_id`).
- Customer: id, name, one-line current address (`street, city, state zip`). There is no email field.
- Order: id, warehouse, product (name, SKU, quantity), order date, value, delivery address (one line), order status.
- Shipment: id, carrier, tracking number, status, delivered at (or "Not delivered"), delivery confirmation. If `shipment` is null show "No shipment recorded".
- Events table columns: timestamp, type, location, description.

### History drawer
- Opens from the clock icon in the header. Loads `GET /history/get_user_history` each time it opens. Newest first by `execution_date`.
- Each row: order ID (mono), date, prompt (2 lines max), and a small "Inconclusive" or "Error" tag where relevant.
- Clicking a row opens (or switches to) a session built from the stored execution: `status: 'done'` if `agent_result` exists, else `'error'` using `error_message`. No re-run, no extra requests; `upfront_data` is already stored.
- Empty state: "No past investigations yet."

---

## 8. Admin console

Header has a segmented switch **Analytics | Workbench**, an **Invitations** button (with count badge), a **Profiles** button, History and Profile icons.

### Analytics tab
Loaded on open from endpoint 6.
- Four KPI cards: Total executions (with "N successful · N failed"), Success rate (`success_rate` is already a percent; one decimal), Orders investigated (with unique customers), Active operators (`overview.active_operators`; with total invitations underneath).
- **Execution trends** card with Daily / Weekly / Monthly toggle. For each period key (sorted ascending) show two thin horizontal bars: total (light grey) and successful (black), scaled to the largest `total` in the selected view, with "N total · N successful" text. Legend underneath.
- **Failures** card: total failures big number; if `common_errors` is empty show "No errors recorded"; otherwise a list of error name and count.
- Loading skeleton or spinner while fetching; error card with a Retry button if it fails.

### Invitations modal
- List from endpoint 7, newest first: name, email, status badge (**Redeemed** if `status` true, **Pending** if false), created date, token, Delete button.
- Create form: invitee name + work email → endpoint 8 → show the new `access_key` in a highlighted box with a Copy button and a line "Share this token with <email>". Then refresh the list.
- The list already returns `access_key`, so admins can copy any token later. Show it in monospace with a Copy button.
- Delete: inline confirmation first: "Deleting this invitation will also permanently delete <name>'s account and profile." Buttons Cancel / Confirm Delete. Calls endpoint 9 with `{ access_key, email }`, then refreshes the list. Also refresh Profiles and the invitation count in the header.
- Do not allow deleting your own invitation (match by the signed-in profile's email): disable the button with a tooltip.

### Profiles modal
- List from endpoint 10: name (fall back to email if null), email, role badge. Operators get a **Make Admin** button.
- Inline confirmation: "Making <name> an admin gives them all the administrative privileges you hold." Confirm → endpoint 11 with `{ user_id, email }` → refresh list.
- No demote or delete here.

### Admin Workbench tab
Renders the same `Workbench` component. No extra logic.

---

## 9. Visual design

Mockups exist for all four screens (sign in, sign up, operator console, admin console) at https://claude.ai/artifact/X18Vb7QDV9C3qV2eSsJqcQ . Match them. If they are unavailable, follow this spec.

**Theme: white, grey, black.** Use Tailwind's built-in `zinc` scale; no custom colours.

| Use | Tailwind |
|---|---|
| Page and card background | `bg-white` |
| Subtle surfaces (switcher track, evidence boxes, table headers) | `bg-zinc-100` / `bg-zinc-50` |
| Card border | `border border-zinc-300` plus `shadow-sm` |
| Input border | `border-zinc-400`, focus: `border-zinc-900 ring-4 ring-zinc-900/10` |
| Dividers | `border-zinc-200` |
| Primary text | `text-zinc-900` |
| Muted text | `text-zinc-600` (never lighter than zinc-500 for readable text) |
| Primary button / active tab | `bg-zinc-900 text-white hover:bg-zinc-800` |
| Secondary button / icon button | `bg-white border border-zinc-300 hover:border-zinc-900` |

- Font: Inter for UI, JetBrains Mono for IDs, tokens, timestamps and numbers.
- Radius: cards `rounded-2xl` (about 14px), inputs and buttons `rounded-lg`.
- Inputs 44px tall (`h-11`), labels above in `text-sm font-medium`, hints below in `text-xs text-zinc-600`.
- **Header is light:** logo + name on white with a thin `border-b border-zinc-200`. No heavy coloured bar.
- Borders must be clearly visible; that was an explicit complaint about the first design.
- Focus states visible everywhere. Use real `<button>`, `<label htmlFor>` and `<input>`.
- No emoji. Icons from `lucide-react`. The logo is the custom SVG (dossier with magnifying lens) in `Logo.tsx`, drawn in `#111` with grey `#8A8A8F` record lines.
- Responsive: single column on phones; the form's two ID fields stack under 640px; tables scroll horizontally inside their own box.

### Auth page
```
 [logo] Delivery Investigator                         (plain white header)

            ┌──────────────────────────────┐
            │ Welcome back                  │
            │ Sign in to continue.          │
            │ [ Sign in | Sign up ]  switch │
            │ Work email      [__________]  │
            │ Password        [________ 👁] │
            │ [      Sign in  →          ]  │
            │ Have an invitation? Create an │
            │ account                       │
            └──────────────────────────────┘
        Velora Market · Internal system · Authorized personnel only
```
Sign up adds, in order: Full name (first), then email, password (hint "At least 8 characters."), confirm password, access token (monospace, key icon, hint "Single-use and tied to your email address."). Button: "Create account". Sign in / sign up is a segmented switch with a grey track and black active tab.

### Operator console
```
 [logo] Delivery Investigator | [+ New] [ORD-3106 ✓] [ORD-4092 ⟳ Running]     [🕘] [👤]
 ─────────────────────────────────────────────────────────────────────────────────────
                       Delivery investigation  (centered intro, max-w-3xl column)
   ┌ card ─────────────────────────────────────────────────────┐
   │ Order ID [________]   Customer ID [________]               │
   │ Investigation prompt [textarea, 3 rows]                     │
   │ Runs in its own tab…                         [Investigate] │
   └────────────────────────────────────────────────────────────┘
   Results for ORD-3106 · CUST-8821                [High · 85%]
   ┌ Investigation report ───────────────────────┐
   │ report text …                               │
   │ Supporting evidence: [row][row][row]        │
   └─────────────────────────────────────────────┘
   ┌ Suggested next step ──────────────── [Copy] ┐
   │ recommendation …   evidence rows            │
   └─────────────────────────────────────────────┘
   ▸ Upfront records: customer, order, shipment and tracking events   (collapsed)
```
"New" tab shows the empty state: "Ready for a new investigation."

### Admin console
```
 [logo] Delivery Investigator [Admin] | [Analytics|Workbench]   [🎫 Invitations 2] [👥 Profiles] | [🕘] [👤]
                     Investigation analytics
   [KPI] [KPI] [KPI] [KPI]
   ┌ Execution trends  [Daily|Weekly|Monthly] ┐ ┌ Failures ┐
   │ per-period dual bars + legend            │ │ total / empty state │
   └──────────────────────────────────────────┘ └─────────┘
```
Admin column max width about `max-w-5xl`; operator column `max-w-3xl`.

### Shared UI behaviours
- Modals: centred, dim backdrop, close button, Esc closes, click on backdrop closes.
- Profile menu: popover from the user icon, closes on outside click.
- History: right-side drawer.
- Buttons show a disabled state while their request runs; avoid double submits.
- Every list and panel has a loading state, an empty state and an error state.

---

## 10. Build order (milestones)

Do them in order. After each, the app must run with `npm run dev` without errors.

1. **Foundation.** `index.css` (Tailwind import, fonts), `Logo.tsx`, `lib/supabase.ts`, `lib/types.ts`, `lib/api.ts` (fetch wrapper with JWT, error extraction, 401 handling, one typed function per endpoint). *Done when:* the project compiles and a test call to `/health` works from the browser (CORS permitting).
2. **Auth.** `AuthContext.tsx`, `RouteGuards.tsx`, `AuthPage.tsx`, `App.tsx` routes with placeholder Operator and Admin pages that show the user's name and a Log out button. *Done when:* sign in, sign up with a real invitation, redirect by role, refresh keeps the session, and logging out all work.
3. **Shell.** `Header.tsx`, `ProfileMenu.tsx` (including change password), `Modal.tsx`.
4. **Workbench.** Session tabs, form, parallel run + upfront calls, running state with timer, `ReportView.tsx`, `UpfrontRecords.tsx`. *Done when:* two investigations can run at once in separate tabs.
5. **History.** `HistoryDrawer.tsx` and reopening past executions.
6. **Admin.** `AnalyticsDashboard.tsx`, `InvitationsModal.tsx`, `ProfilesModal.tsx`, the Analytics / Workbench switch in `AdminPage.tsx`.
7. **Polish.** Empty / loading / error states audit, responsive pass, keyboard and focus pass, copy review against section 1's product rules.

---

## 11. Coding rules

- TypeScript strict. No `any`; use the types in section 6.
- One component per file, named exports matching the file name (default export for pages).
- All HTTP goes through `lib/api.ts`. Components never call `fetch` directly.
- All user-visible errors come from `ApiError.message` or a fixed friendly string; never show raw stack traces or JSON.
- Short comments explaining *why*, plain language, for a reader new to React.
- No `localStorage` of your own; Supabase handles session storage.
- Dates and numbers formatted for display only at render time.
- Do not add dependencies beyond section 3 without asking.

---

## 12. Backend facts and open items

Things the frontend relies on, so they should stay true:
- `GET /me` returns the profile including `role`. Role is read from there, not from the JWT.
- The profile row is created (likely by a database trigger on `auth.users`) with `name` read from `user_metadata.full_name`, which is the key the sign-up endpoint sets.
- CORS currently allows all origins. Restrict to the frontend origin before production.

Open items for the owner (the frontend works around them for now):
- `check_invitation` should also require `status == False` so a redeemed token cannot be reused, and something must set `status = True` after sign-up.
- The upfront endpoint returns a generic 500 for an unknown order; a 404 with a clear message ("Order not found for this customer") would let the UI say so.
- No protection yet against an admin deleting their own invitation or the last admin; the UI blocks the self case only.
- The analytics response shape in section 6 is assumed; confirm against a real response.
- Real sample responses for the run endpoint (successful and inconclusive) are still needed to tune the report card and the evidence list.