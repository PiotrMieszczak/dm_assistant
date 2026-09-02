---
title: "ADR-0004: CSS Modules over design tokens; Tailwind excluded"
status: "Accepted"
date: "2026-07-31"
authors: "Piotr Mieszczak"
tags: ["architecture", "decision", "styling", "frontend", "design-system"]
supersedes: ""
superseded_by: ""
---

# ADR-0004: CSS Modules over design tokens; Tailwind excluded

## Status

Proposed | **Accepted** | Rejected | Superseded | Deprecated

## Context

The design is high-fidelity and highly specific: exact hex values, radii ranging across
nine distinct steps (6px through 20px), bespoke shadows, asymmetric bubble radii
(`14px 14px 14px 4px`), and a floating rail that animates width and padding on a custom
easing curve.

Constraints:

- **CON-001**: The governing project instructions prohibit Tailwind CSS outright, on the
  grounds that it produces verbose markup and discourages custom design thinking.
- **CON-002**: An earlier planning document listed Tailwind in the stack, while
  simultaneously listing CSS Modules as the primary approach and marking Tailwind
  "optional" — an unresolved contradiction.
- **CON-003**: The design's values do not fall on a standard utility scale. Sizes like
  `13.5px`, `11.5px`, and `10.5px` and radii like `17px` and `11px` would each need
  bespoke config entries, at which point the utility framework provides little.
- **CON-004**: Design tokens must be the single source of visual truth so that a change
  to the accent color propagates everywhere.

## Decision

Styling is **CSS Modules layered over CSS custom properties**. Tokens are declared once
in `frontend/src/styles/tokens.css` and referenced by every component's `.module.css`.

**Tailwind is not used.** Inline styles are permitted only for genuinely dynamic values
(a computed graph node position, a progress bar width).

## Consequences

### Positive

- **POS-001**: Markup stays readable. Components carry semantic class names rather than
  long utility strings, which matters in views like character detail with deep nesting.
- **POS-002**: Tokens are enforced by convention and reviewable by grep — a raw hex value
  in a `.module.css` file is an immediate review flag.
- **POS-003**: CSS Modules scope class names automatically, so there is no naming
  methodology to maintain and no cascade collisions.
- **POS-004**: The design's unusual values are expressed directly, with no config
  indirection between the spec and the stylesheet.
- **POS-005**: No build-time CSS framework dependency, and no purge configuration to
  misconfigure.
- **POS-006**: Complies with the governing project instruction (CON-001).

### Negative

- **NEG-001**: More files. Each component with meaningful styling carries a companion
  `.module.css`.
- **NEG-002**: No utility shorthand for one-off spacing; small adjustments mean editing a
  stylesheet rather than adding a class in markup.
- **NEG-003**: Consistency depends on discipline. Nothing mechanically prevents a
  developer from writing `#E8B87A` instead of `var(--accent)` — hence IMP-002.
- **NEG-004**: Developers accustomed to Tailwind face a small adjustment.

## Alternatives Considered

### Tailwind CSS with design tokens mapped in config

- **ALT-001**: **Description**: Configure `tailwind.config.js` so utilities resolve to the
  design tokens, then style with utility classes, as one earlier planning document
  suggested.
- **ALT-002**: **Rejection Reason**: Explicitly prohibited by project instructions
  (CON-001). Independently, the design's off-scale values (CON-003) would require
  extensive custom config, and complex components would carry unwieldy class strings.

### CSS-in-JS (styled-components, Emotion)

- **ALT-003**: **Description**: Co-locate styles with components in TypeScript, with
  props-driven variants.
- **ALT-004**: **Rejection Reason**: Adds runtime cost and a dependency for no benefit
  here — the design's variants are few and expressible as modifier classes. CSS custom
  properties already provide dynamic theming without JavaScript.

### Plain global CSS with a naming methodology (BEM)

- **ALT-005**: **Description**: Conventional stylesheets with disciplined class naming.
- **ALT-006**: **Rejection Reason**: CSS Modules give the same authoring experience with
  automatic scoping, removing the need for a naming convention to prevent collisions.

## Implementation Notes

- **IMP-001**: `tokens.css` is transcribed from `docs/design/reference.md` and is the
  only file containing literal color, radius, shadow, or motion values.
- **IMP-002**: Add a lint rule or CI check rejecting raw hex values in `.module.css`
  files outside `tokens.css`. This is what makes POS-002 real rather than aspirational
  (addresses NEG-003).
- **IMP-003**: Radix UI primitives are unstyled, so they compose with CSS Modules with no
  style-override friction.
- **IMP-004**: Storybook documents each primitive with its designed states, making token
  drift visible early.
- **IMP-005**: Fonts (Crimson Pro, Inter, JetBrains Mono) are self-hosted rather than
  loaded from a CDN, consistent with local-first operation.

## References

- **REF-001**: `docs/design/reference.md` — the token set
- **REF-002**: `CLAUDE.md` (workspace root) — the prohibition in CON-001
- **REF-003**: [ADR-0001](adr-0001-react-vite-spa.md) — frontend stack this styles
