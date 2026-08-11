# FEMC AI Implementation Guidelines

**Version:** 1.0.0
**Status:** Engineering Design
**Owner:** Engineering Office

## AI Boundary

AI implementation must preserve:

- authorized context;
- explicit tool permissions;
- provider independence;
- provenance;
- output validation;
- human control for consequential actions.

## Rules

- Never send more family information than required.
- Never assume model output is factual.
- Never let model instructions bypass authorization.
- Never make a model provider the canonical data owner.
- Keep AI failures isolated from core family access.

## Principle

AI implementation is controlled intelligence, not unrestricted automation.
