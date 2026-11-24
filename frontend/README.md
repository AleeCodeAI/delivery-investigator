# Delivery Investigator: Frontend

Internal web app for **Velora Market** operators. An operator enters an order, a customer and a question; an LLM agent reads the order's records and returns an evidence-backed finding plus a suggested next step. The system is **read-only**: it never refunds, reships, edits records or contacts anyone. The human decides what to do.

Two roles, both served by this app:

| Role | Route | What they get |
|---|---|---|
| Operator | `/operator` | Investigation workbench, history |
| Admin | `/admin` | Analytics, workbench, invitations, profiles, history |

Accounts exist by **admin invitation only**. There is no self-service sign-up without a token and no "delete my account" button.

---

## Stack

- React + TypeScript + Vite
- Tailwind CSS v4 (`@tailwindcss/vite`), `zinc` scale only
- `react-router-dom` (routes), `@supabase/supabase-js` (sign in, session, JWT), `lucide-react` (icons)
- No state library, no data-fetching library, no test setup. Plain `useState`, `useEffect`, `useContext`.

## Getting started

Requirements: a current Node.js LTS (20.19+ or 22.12+), and the backend and a Supabase project reachable from your machine.

```bash
cd frontend
npm install
cp .env.example .env        # Windows PowerShell: copy .env.example .env
# fill in .env, then:
npm run dev                 # http://localhost:5173
```

`vite.config.ts` must include the Tailwind plugin:

```ts
import tailwindcss from '@tailwindcss/vite'
// plugins: [react(), tailwindcss()]
```

| Script | Purpose |
|---|---|
| `npm run dev` | Dev server |
| `npm run build` | Type-check and production build into `dist/` |
| `npm run preview` | Serve the production build locally |
| `npm run lint` | ESLint |

### Environment variables

All must start with `VITE_` and live in `frontend/.env` (never committed). **Restart `npm run dev` after editing `.env`**; it is only read at startup.

| Variable | Value |
|---|---|
| `VITE_SUPABASE_URL` | Your Supabase project URL, starting with `https://` (no quotes) |
| `VITE_SUPABASE_PUBLISHABLE_KEY` | The publishable (anon) key |
| `VITE_API_URL` | Backend base URL, e.g. `http://localhost:8000` |

**Never put the Supabase secret / service-role key in the frontend.** If a variable is missing or malformed the app shows a "Configuration problem" screen instead of a blank page.

### Supabase settings this app relies on

- Email confirmation is enabled.
- **Authentication → URL Configuration:** the frontend URL is in the Redirect URLs allow-list, and Site URL points to the frontend.
- A database trigger creates the `profiles` row from `user_metadata.full_name`.

---

## Project structure

```
frontend/
├── .env.example  index.html  package.json  vite.config.ts  tsconfig*.json
└── src/
    ├── main.tsx                      entry: router, auth provider, error boundary, config check
    ├── App.tsx                       route table
    ├── index.css                     Tailwind, fonts, shared classes
    ├── lib/
    │   ├── supabase.ts               Supabase client, config check, confirmation-link result
    │   ├── api.ts                    every backend call; JWT; error handling; 401 sign-out
    │   ├── types.ts                  TypeScript types for API data
    │   └── format.ts                 date, money and address formatting
    ├── auth/
    │   ├── AuthContext.tsx           session + profile (/me); signIn, signUp, resend, signOut, changePassword
    │   └── RouteGuards.tsx           RequireAuth, RequireAdmin, RedirectIfAuthed, HomeRedirect
    ├── pages/
    │   ├── AuthPage.tsx              sign in / sign up / check-your-email
    │   ├── OperatorPage.tsx
    │   └── AdminPage.tsx             Analytics | Workbench switch, invitations, profiles
    └── components/
        ├── Logo.tsx  Header.tsx  ProfileMenu.tsx  Modal.tsx  ErrorBoundary.tsx
        ├── Workbench.tsx             session tabs + form + results (shared by both consoles)
        ├── ReportView.tsx            report card + suggested-next-step card
        ├── UpfrontRecords.tsx        collapsible customer / order / shipment / events
        ├── HistoryDrawer.tsx         past investigations
        └── admin/
            ├── AnalyticsDashboard.tsx
            ├── InvitationsModal.tsx
            └── ProfilesModal.tsx
```

## How it works

### Authentication

- **Sign in:** `supabase.auth.signInWithPassword`, then `GET /me` for the profile and role. Wrong credentials show one generic message. If the password is right but the email is unconfirmed, the user is told so and can resend the confirmation email.
- **Sign up (invitation only):** full name, work email, password (min 8), confirm, access token. `POST /auth/sign-up/` creates the account and sends a confirmation email. **The user is not logged in.** They see "Check your email", confirm, then sign in manually. A **Resend** button calls `POST /auth/resend-confirmation/` (30 s cooldown in the UI).
- **Confirmation link:** the app deliberately does not log the user in from it (`detectSessionInUrl: false`). It shows "Your email is confirmed. Sign in to continue." and removes the tokens from the address bar.
- **JWT:** `api.ts` reads the current token from Supabase on every call and sends `Authorization: Bearer <token>`. Any `401` signs the user out and sends them to `/auth`.
- **Roles** come from `GET /me`, never from the JWT. Hiding the admin console is a convenience; the backend enforces access.
- **Routing:** logged out → `/auth`; logged in on `/auth` → own console; operator on `/admin` → `/operator`; `/` redirects by the same rules.

### Investigations (Workbench)

- Each investigation is its own **tab**. Starting one fires two requests in parallel: the agent run and the upfront records. Records can appear before the agent finishes.
- The form **keeps its values** after starting; edit and run again as needed. A second submit within 1.5 s is ignored to prevent accidental double runs.
- Runs have a 3-minute client timeout ("Check History in a minute"). Closing a tab only hides it; the run still finishes and is saved server-side.
- **Inconclusive is a valid result**, shown calmly in grey, not as an error.
- The suggested next step is advice text only. The UI never offers refund, reship or contact buttons.
- Confidence labels (UI-only): `>= 0.8` High, `>= 0.5` Moderate, otherwise Low, always with the percentage.

### History

The clock icon opens a drawer of the user's past investigations, newest first, reloaded each time it opens. Selecting one opens the stored result as a tab. No re-run and no extra requests.

### Admin console

- **Analytics:** KPI cards, execution trends (daily / weekly / monthly) and failures. The response shape is assumed; every field is read defensively.
- **Invitations:** create an invitation and copy its token. **The token is shown once, right after creation, and never in the list.** Deleting an invitation also permanently deletes that person's account and profile, so it needs confirmation. You cannot delete your own invitation.
- **Profiles:** promote an operator to admin after confirmation. There is no demote.
- The Workbench stays mounted while Analytics is showing, so running investigations are not lost when switching tabs.

## Backend contract

Base URL is `VITE_API_URL`. All endpoints need the Bearer JWT except the two public auth endpoints.

| Method + path | Access | Notes |
|---|---|---|
| `POST /auth/sign-up/` | public | Returns `check_email` or `created_email_failed`. 5/min |
| `POST /auth/resend-confirmation/` | public | Always returns `ok`. 3/min |
| `GET /me` | any user | Profile with `role` |
| `POST /master-pipeline/delivery-investigator-run` | any user | Agent run |
| `POST /upfront_data/get-upfront-data` | any user | Same body as the run |
| `GET /history/get_user_history` | any user | |
| `GET /admin/get_execution_analytics` | admin | |
| `GET /admin/get_all_invitation` | admin | |
| `POST /admin/insert-invitation` | admin | Returns the new `access_key` |
| `DELETE /admin/delete-invitation/` | admin | JSON body `{ access_key, email }` |
| `GET /admin/get_all_profiles` | admin | |
| `POST /admin/update-role/` | admin | Operator to admin only |

Error bodies are usually `{ status: "error", message }`; rate limits return `{ error }`. `api.ts` extracts a readable message from either.

## Conventions

- TypeScript strict, no `any`. API types live in `src/lib/types.ts`.
- All HTTP goes through `src/lib/api.ts`; components never call `fetch`.
- User-visible errors come from `ApiError.message` or a fixed friendly string, never raw JSON or stack traces.
- Styling: white, grey and black using Tailwind `zinc`. Shared classes in `src/index.css`: `.field-input`, `.btn-outline`, `.btn-primary`, `.tag`, `.card`. Inter for UI, JetBrains Mono for IDs, tokens, timestamps and numbers.
- No emoji. Icons from `lucide-react`.
- Comments: one short header per file; inline comments only where the reason is not obvious.
- Do not add dependencies without discussing it first.

## Deployment

- `npm run build` produces `dist/`. Environment variables are **baked in at build time**, so build with the production values.
- Serve `dist/` over HTTPS with a single-page-app fallback (unknown paths return `index.html`).
- Restrict backend CORS to the frontend origin (it currently allows all).
- Add the production URL to Supabase Redirect URLs and set Site URL.

## Troubleshooting

| Symptom | What to check |
|---|---|
| "Configuration problem" screen | `frontend/.env` exists with all three variables; restart `npm run dev` |
| Blank white page | Browser console (F12). Often files from different versions are mixed, or a stale Vite cache: stop the server, run `Remove-Item -Recurse -Force node_modules\.vite` (PowerShell) or `rm -rf node_modules/.vite`, restart, hard refresh (Ctrl+Shift+R) |
| Page unstyled | Tailwind plugin missing from `vite.config.ts` |
| Endless spinner on load | Backend not running, or `VITE_API_URL` wrong; check the `/me` request in the Network tab |
| Redirected to sign-in with a message | `/me` failed (403 means the account has no profile) |
| CORS error in console | Backend must allow the frontend origin |
| Confirmation email link lands on the wrong page | Redirect URL / Site URL in Supabase |

## Known limitations and open items

- The analytics response shape is assumed; confirm it against a real response.
- `GET /admin/get_all_invitation` still returns each `access_key` (needed to delete). The UI never displays it, but it is visible in the browser's Network tab.
- The backend returns a generic 500 for an unknown order, so the UI cannot say "Order not found".
- `check_invitation` should reject already-redeemed tokens, and nothing yet prevents an admin from deleting the last admin.
- No automated tests are included.
- Fonts load from Google Fonts; self-host them if the app must work without internet access.