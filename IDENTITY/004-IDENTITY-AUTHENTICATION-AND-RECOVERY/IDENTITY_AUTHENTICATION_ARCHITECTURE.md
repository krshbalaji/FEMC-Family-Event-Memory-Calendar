# FEMC Identity Authentication Architecture

**Version:** 1.0.0
**Status:** Identity Architecture
**Owner:** Identity Office

## Purpose

Define authentication as the mechanism that establishes confidence that a participant controls an identity representation, without confusing authentication with family membership or authorization.

## Model

```text
IDENTITY
 ↓
AUTHENTICATION
 ↓
AUTHENTICATED SESSION
 ↓
AUTHORIZATION
```

## Rules

Authentication strength should match the consequence of the action.

Recovery must not become a weaker path that silently defeats the protection of the primary authentication mechanism.

## Principle

Authentication answers “who is controlling this account?”; it does not answer “what may this person access?”
