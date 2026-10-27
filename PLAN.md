# PLAN.md

The team's working plan. Agents read and update this file, so a new session can pick up where
the last one stopped. Keep it short; replace old content instead of adding to it.

## Current goal
Build a Streamlit page for one option position's payoff and profit at expiration.

## Decisions so far
- 2026-10-27: Added per-share call/put expiration payoff and profit formulas, break-even, and
  maximum gain/loss formulas; tests pass against the supplied class examples.
- 2026-10-27: Assume one standard option contract represents 100 shares; the app will label this.

## Next steps
1. Review the working Streamlit page and confirm the 100-share contract multiplier.

## Open questions
- Confirm whether the class uses a 100-share contract multiplier.
