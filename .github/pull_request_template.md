<!--- Summarise the change in the Title above. -->

## Description
<!--- What changed, in enough detail that a reviewer knows what to look at first. -->

## Motivation and Context
<!--- Why is this change required? What problem does it solve? -->
<!--- If it implements part of the roadmap, link the phase. -->
<!--- If it closes a design gap listed in docs/design/design-spec.md, say which. -->

## Related Issue / ADR
<!--- Link any related issue. Optional - not every change needs one. -->
<!--- If this change makes, reverses, or depends on an architectural decision, link the ADR. -->
<!--- Decisions that constrain future work belong in docs/adr/, not only in this description. -->

Closes #

## Type of Change
<!--- Put an `x` in all the boxes that apply. -->

- [ ] Documentation (docs only — no application code)
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that changes existing behaviour)
- [ ] Refactor / tooling (no user-visible behaviour change)

## Design Fidelity
<!--- Delete this section if the change touches no UI. -->
<!--- The design is the source of truth. See docs/design/design-spec.md. -->

- [ ] Values come from design tokens — no hardcoded hex, radii, or shadows
- [ ] No Tailwind (see [ADR-0004](../docs/adr/adr-0004-css-modules-over-tailwind.md))
- [ ] Verified at desktop **and** ≤900px; ≤560px too if player detail is affected
- [ ] Interaction states match the spec: hover, focus, active, disabled, loading, empty

**Screenshots** — before and after for anything visual:

## How Has This Been Tested?
<!--- Describe what you actually ran, not what could be run. -->
<!--- If you did not test something, say so. That is useful review information. -->

## Checklist

- [ ] Self-reviewed the diff
- [ ] Follows the conventions in `docs/` and the project's CLAUDE.md
- [ ] Documentation updated, **or** no documentation change is needed
- [ ] Tests added or updated for behavioural changes, **or** the change is not testable
      (say which in the section above)
- [ ] All tests pass locally
- [ ] No secrets, API keys, or personal data in the diff

## Architectural Boundaries
<!--- Delete if not applicable. These are enforced by tests; confirm you have not weakened them. -->

- [ ] No LLM call was introduced into the ingestion path
      ([ADR-0002](../docs/adr/adr-0002-deterministic-extraction.md))
- [ ] All model access still goes through the Gateway
      ([ADR-0006](../docs/adr/adr-0006-llm-gateway.md))
- [ ] Queries remain scoped by `campaign_id`

## Notes for Reviewers
<!--- Anything you want a second opinion on, known gaps, or follow-up work. -->
