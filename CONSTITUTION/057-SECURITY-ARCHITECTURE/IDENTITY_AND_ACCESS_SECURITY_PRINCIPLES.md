# FEMC Identity and Access Security Principles

**Version:** 1.0.0  
**Status:** Foundation  
**Owner:** Chief Product Architect

## 1. Identity Confidence

The system should establish sufficient confidence about who is acting before granting sensitive access.

## 2. Authentication vs Authorization

Authentication answers:

> Who is this?

Authorization answers:

> What may this person or system do here?

## 3. Context

Authorization should consider relevant family context and resource sensitivity.

## 4. Privileged Access

Administrative and operational access must remain distinct from family participation.

## 5. Delegation

Delegated authority must be explicit, bounded, and revocable where applicable.

## 6. Service Identity

Machine-to-machine access should use distinct identities and permissions rather than shared unrestricted credentials.

## 7. AI Identity

AI access should be attributable to an authorized initiating context.

## 8. Failure

When identity or authorization confidence is insufficient, sensitive access should fail safely.

## 9. Principle

Convenience must never silently replace authorization.
