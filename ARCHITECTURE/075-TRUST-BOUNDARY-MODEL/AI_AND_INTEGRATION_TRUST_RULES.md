# FEMC AI and Integration Trust Rules

**Version:** 1.0.0
**Status:** Architecture
**Owner:** Architecture Office

## AI

Before family information is provided to an AI capability, the architecture must know:

- what information is being provided;
- why it is needed;
- under whose authority;
- what action the AI may take;
- what provider receives the information;
- how output returns to FEMC.

## Integrations

External integrations require equivalent clarity.

## Output

AI or external output must not automatically become canonical family truth.

## Failure

External or AI failure must not corrupt canonical information.

## Revocation

When access is revoked, future processing must respect the new authorization boundary.

## Principle

The more powerful the external capability, the more explicit its trust boundary must be.
