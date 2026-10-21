# v0.9.1: Google Calendar without a public Pi endpoint

## Decision

Do not require a public hostname, reverse proxy, HTTPS certificate, or
inbound internet access to the Raspberry Pi. Google Calendar's
`calendar.readonly` scope is not supported by Google's limited-input device
authorization grant, so a device-code pairing flow is **not** a valid solution.

Use Google's installed/desktop application authorization-code grant with
PKCE and a browser-local loopback listener. Google redirects only to
`http://127.0.0.1:<ephemeral port>/` on the administrator's own computer,
not to the Pi.

## Connection sequence

1. Administrator signs in to the LAN dashboard and selects Connect Google.
2. Dashboard generates a **short-lived pairing ticket** tied to the admin
   session and plugin, but does not create or expose any refresh token.
3. Administrator downloads/runs a small, audited desktop pairing helper on
   their computer. The helper uses a Google **Desktop** OAuth client ID,
   chooses a random loopback port, and creates PKCE verifier, challenge and
   state locally.
4. The helper opens Google authorization in the local browser. It accepts
   the callback only on the loopback listener, verifies state, and exchanges
   the code directly with Google over HTTPS.
5. The helper uploads the resulting credentials to the authenticated
   scoreboard over the LAN, presenting the short-lived one-time pairing
   ticket. Core validates the ticket and provider/plugin binding, then saves
   the credentials to the private token vault.
6. Core reports Connected. The Calendar plugin may read selected calendars
   through a narrowly defined Core provider interface. The helper removes
   transient credentials from memory and never writes them to disk.

## Security requirements

- Pairing tickets are random, single-use, short-lived, and scoped to the
  selected plugin and admin session. They are not included in backups.
- Require an explicit user action before importing credentials; do not allow
  a third-party webpage to initiate a pairing request.
- The helper must authenticate the intended scoreboard, not blindly post
  bearer tokens to a LAN URL. Plain HTTP on a hostile LAN cannot provide
  transport confidentiality: use an authenticated encrypted pairing
  channel, or an explicit, clearly disclosed local-trust mode.
- Validate OAuth token response and scope, limit payload size, prevent
  open redirects and arbitrary provider endpoints, and scrub secrets from
  logs and HTTP responses.
- Core credential storage remains outside portable backups. Disconnect
  deletes the stored token and, where possible, revokes it at Google.
- Test cancellation, timeout, wrong ticket/session, replay, callback
  mismatch, helper interruption, and expired/denied Google authorization.

## Migration

The current HTTPS web callback code is provisional and must be removed or
disabled before the local pairing flow is exposed as production-ready.
The dashboard must no longer show 'HTTPS public origin required' once
local pairing is wired in.

## Delivery order

1. Pairing ticket lifecycle and tests.
2. Encrypted, authenticated local transfer and tests.
3. Desktop helper with loopback OAuth and tests.
4. Dashboard connection and status UX.
5. Calendar selection, refresh and disconnect, then Pi 3/Pi 5 validation.

No new Google Cloud project is required on the Pi. A Google Desktop OAuth
client ID must still be provisioned for the helper.
