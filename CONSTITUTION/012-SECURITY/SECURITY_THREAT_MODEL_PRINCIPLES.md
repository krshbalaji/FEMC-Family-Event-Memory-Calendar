# FEMC Security Threat Model Principles

**Version:** 1.0.0  
**Status:** Foundation  
**Owner:** Chief Product Architect

## Purpose

Establish the threat categories that future security architecture must consider.

## Threat Categories

### Identity Compromise

Unauthorized access through stolen or compromised identity credentials.

### Permission Abuse

A legitimate participant accessing information beyond their intended authority.

### Family Context Leakage

Private information exposed through incorrect contextual relationships or sharing.

### Integration Leakage

External systems receiving information beyond the intended purpose.

### AI Context Leakage

Unauthorized or excessive family information entering AI processing.

### Data Tampering

Unauthorized modification of family history, relationships, events, memories, or metadata.

### Data Loss

Permanent or temporary loss of family information.

### Availability Failure

Families being unable to access important information when needed.

### Insider Misuse

Authorized operational access being used improperly.

### Social Engineering

Users being manipulated into granting access or revealing information.

## Threat Modeling Rule

Security analysis should consider both:

- technical attack paths;
- product behavior that unintentionally creates exposure.

## Critical Asset Principle

The most important assets are not only files or databases.

They include:

- family identity;
- relationships;
- historical truth;
- private memories;
- access authority;
- trust.

## Security Review Trigger

A new capability should receive security review when it introduces:

- new sensitive data;
- new external integration;
- new privilege;
- new sharing behavior;
- new AI context;
- new persistence;
- new administrative power.
