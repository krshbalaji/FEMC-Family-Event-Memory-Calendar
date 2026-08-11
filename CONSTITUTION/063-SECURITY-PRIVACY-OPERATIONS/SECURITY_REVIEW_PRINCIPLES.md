# FEMC Security Review Principles

**Version:** 1.0.0  
**Status:** Foundation  
**Owner:** Chief Product Architect

## Review Areas

Material changes should consider:

- identity;
- authorization;
- data exposure;
- trust boundaries;
- external dependencies;
- secrets;
- logging;
- recovery;
- abuse scenarios.

## 1. Threat Thinking

Review should consider how a capability could be misused, not only how it is intended to work.

## 2. Data-Centric Review

Identify what family information is exposed and where.

## 3. Change-Centric Review

Security review depth should reflect the materiality of the change.

## 4. AI Review

AI features require explicit review of prompt/data exposure, tool authority, output handling, and model/provider boundaries.

## 5. Evidence

Material security decisions should retain sufficient reasoning and evidence.

## 6. Principle

Security review should reduce real risk without becoming ritual paperwork.
