# FEMC AI Tool Authorization and Action Safety

**Version:** 1.0.0
**Status:** AI Safety
**Owner:** AI Office

## Tool Classes

- read;
- search;
- analyze;
- draft;
- propose;
- mutate;
- communicate;
- administrative.

Higher-impact tools require stronger authorization and validation.

## Rules

- Validate tool arguments.
- Re-check authorization at execution time.
- Make side effects explicit.
- Prevent unsafe repeated execution.
- Preserve idempotency where appropriate.
- Record material actions.

## Principle

Tool access is authority; therefore every tool must be governed as a security boundary.
