---
title: "ADR-0007: Local profile in v1; Supabase Auth when hosting arrives"
status: "Accepted"
date: "2026-09-02"
authors: "Piotr Mieszczak"
tags: ["architecture", "decision", "auth", "deployment", "cost"]
supersedes: ""
superseded_by: ""
---

# ADR-0007: Local profile in v1; Supabase Auth when hosting arrives

## Status

Proposed | **Accepted** | Rejected | Superseded | Deprecated

## Context

The design includes a login screen — email, password, "Continue with Google", and a
"Create a table" link. It looks like a product with accounts.

`PRIN-004` scopes v1 as local-first and single-user, and `mvp-scope.md` defers real
authentication with the revisit trigger *"multi-user or hosted deployment is on the
table."* That trigger has now fired: hosting other game masters is a wanted end state.

Constraints shaping the decision:

- **CON-001**: Hosting is wanted **eventually**, not first. The retrieval core is the
  risky, unproven part; accounts are well-understood work.
- **CON-002**: Cost must stay at or near zero. This is a personal project with no revenue.
- **CON-003**: Hosted multi-user contradicts [ADR-0003](adr-0003-sqlite-single-store.md).
  SQLite is a file on one machine; several users on a server needs Postgres.
- **CON-004**: Multi-user requires per-user data isolation. `BND-003` currently relies on
  every query remembering to filter by `campaign_id` — discipline, not enforcement.
- **CON-005**: Password reset requires sending email that reliably lands in inboxes. SPF,
  DKIM, and a sending domain are real work unrelated to this product.
- **CON-006**: The project has one developer. Anything self-hosted is also self-patched.

## Decision

**Two phases, with the second explicitly named now rather than left open.**

**v1 — local profile, no authentication.** A `profile` row in SQLite holding display name,
table name, email (as a label), and avatar. No password, no session, no token. The design's
login screen is built as specified and acts as a profile picker; "Sign in" and "Continue
with Google" both proceed to the campaign picker.

**When hosting arrives — Supabase.** Postgres for storage and Supabase Auth for accounts,
replacing both SQLite and the local profile. At that point this ADR is superseded by one
recording the migration.

Rolling authentication by hand in FastAPI is **rejected**, and self-hosted identity
providers are rejected, for the reasons below.

## Consequences

### Positive

- **POS-001**: v1 costs nothing and has no vendor. Nothing to expire, be down, or bill.
- **POS-002**: The design's login screen is built exactly as specified, so the eventual
  switch to real auth changes the wiring behind it, not the interface.
- **POS-003**: The risky part of the product — trustworthy retrieval — is proven before
  account plumbing is written. If retrieval cannot be made to work, no auth effort is
  wasted.
- **POS-004**: `PRIN-004` and [ADR-0003](adr-0003-sqlite-single-store.md) stay intact for
  v1. One file, zero setup, trivial backup.
- **POS-005**: Choosing Supabase in advance means the migration path is known while v1 is
  being built, so v1 can avoid decisions that would make it harder.
- **POS-006**: Supabase Postgres enforces per-user isolation with row-level security —
  a database rule rather than a convention. This makes `BND-003` structural, addressing
  CON-004 better than the current arrangement does.
- **POS-007**: Supabase's free tier covers 50,000 monthly active users, which is far
  beyond any realistic ceiling for this product (CON-002).

### Negative

- **NEG-001**: A migration is deferred, not avoided. Moving SQLite to Postgres and a local
  profile to real accounts is real work, and it will be done under more pressure than it
  would be today.
- **NEG-002**: v1 ships a login screen that does not authenticate. Anyone with the machine
  has full access — acceptable for a local single-user tool, and it must not be described
  as security.
- **NEG-003**: Adopting Supabase later puts user identity in a third-party system. If they
  change terms or disappear, migration is on us.
- **NEG-004**: Supabase's free tier pauses projects after roughly a week of inactivity.
  Fine for development, a real consideration for a hosted product with sporadic use.
- **NEG-005**: Supabase pulls the stack toward its ecosystem. Using its Postgres but not
  its auth, or vice versa, loses much of the benefit.

## Alternatives Considered

### Own the authentication in FastAPI (argon2 + JWT)

- **ALT-001**: **Description**: Roughly 300 lines — `passlib` with argon2 for hashing,
  `python-jose` for signed tokens, and a direct Google OAuth flow. No vendor.
- **ALT-002**: **Rejection Reason**: The code is genuinely straightforward and safe —
  the objection is not security. It is CON-005: password reset means owning email
  deliverability, which is an afternoon of DNS records and spam-folder debugging with no
  relation to the product. It also leaves CON-004 unaddressed, since per-user isolation
  would remain application discipline rather than a database rule. Worth revisiting only
  if vendor independence becomes more valuable than that work costs.

### Self-hosted identity provider (Authelia, Authentik, Keycloak)

- **ALT-003**: **Description**: Run an identity provider alongside the app. Authelia is
  the lightweight option — one container, around 25MB of memory, behind a reverse proxy.
- **ALT-004**: **Rejection Reason**: Free in licence, not in effort. With one developer
  (CON-006), a self-hosted identity provider is another service to patch, monitor, and
  recover. Sensible for someone already running several services behind a proxy; not for
  a project whose whole appeal is a single file.

### Clerk

- **ALT-005**: **Description**: Hosted auth with a generous free tier — 50,000 monthly
  *retained* users, a narrower unit than active users, so signups who never return cost
  nothing.
- **ALT-006**: **Rejection Reason**: Excellent product, but its strength is polished
  drop-in React components, and this design specifies a fully custom login screen those
  components would fight. It also solves only auth, leaving the Postgres decision (CON-003)
  still to be made separately.

### Auth0

- **ALT-007**: **Description**: The established option, free to 25,000 monthly active
  users.
- **ALT-008**: **Rejection Reason**: The smallest free tier of the three, and pricing
  beyond it is steep — roughly $0.02 per active user, so 100,000 users approaches
  $1,800/month. Its strengths are enterprise features (SSO, SCIM, fine-grained policy)
  this product will not use.

### Real authentication in v1

- **ALT-009**: **Description**: Build accounts now, whichever provider, and skip the
  local-profile phase.
- **ALT-010**: **Rejection Reason**: Contradicts CON-001. It spends effort on
  well-understood work before the unproven part is proven, and it discards the zero-setup
  property while there is only one user to serve.

## Implementation Notes

- **IMP-001**: The `profile` row is a single record with `display_name`, `table_name`,
  `email`, and `avatar_path`. It has no password column — adding one later would imply
  security that does not exist.
- **IMP-002**: **Do not describe v1's login screen as authentication** in the UI, the
  README, or commit messages. It is a profile picker wearing a login screen.
- **IMP-003**: Keep the eventual migration cheap. Every table already carries
  `campaign_id`; adding `owner_id` later is one column plus a backfill. Do not add
  structures that assume a single owner.
- **IMP-004**: Access all storage through a repository layer rather than sprinkling raw
  queries. The SQLite-to-Postgres switch should touch that layer, not every endpoint.
- **IMP-005**: Avoid SQLite-specific SQL where a portable form exists. FTS5 is the
  deliberate exception ([ADR-0005](adr-0005-fts5-before-vectors.md)) and will need
  replacing with Postgres full-text search at migration — note it as known work, not a
  surprise.
- **IMP-006**: When hosting arrives, use Postgres row-level security for per-user
  isolation rather than application filtering. That is most of why Supabase was chosen.
- **IMP-007**: Revisit trigger — a second person wanting an account, or wanting access
  from a device that is not the host machine. Neither is speculative work until it happens.

## References

- **REF-001**: [ADR-0003](adr-0003-sqlite-single-store.md) — the storage decision this
  will eventually supersede
- **REF-002**: [ADR-0005](adr-0005-fts5-before-vectors.md) — FTS5, which does not survive
  the Postgres migration unchanged
- **REF-003**: `docs/product-brief.md` PRIN-004 — local-first, single-user
- **REF-004**: `docs/mvp-scope.md` — the deferral whose trigger this ADR answers
- **REF-005**: [Supabase pricing](https://supabase.com/pricing) — verify the free tier
  before relying on the figures here; they change
