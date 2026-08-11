# FEMC Secrets and Dependency Security

**Version:** 1.0.0
**Status:** Engineering Design
**Owner:** Engineering Office

## Secrets

Secrets must:

- remain outside source code;
- use controlled storage;
- have appropriate rotation;
- have limited access;
- be revocable.

## Dependencies

Engineering should continuously assess material dependencies for:

- vulnerabilities;
- maintenance status;
- licensing;
- transitive risk;
- provider exposure;
- replacement difficulty.

## AI Providers

Provider credentials and model configuration must remain implementation concerns behind the AI architecture boundary.

## Principle

A secret should be treated as a capability grant, not as configuration text.
