# FEMC Integration and Dependency Architecture

**Version:** 1.0.0
**Status:** System Architecture
**Owner:** Architecture Office

## Integration Classes

- internal domain interaction;
- platform service;
- AI provider;
- media provider;
- communication provider;
- identity provider;
- external family-facing integration;
- operational integration.

## Requirements

Material integrations should define:

- contract;
- owner;
- data exchanged;
- authorization;
- failure behavior;
- retry behavior;
- observability;
- replacement path.

## Principle

Every dependency should have a boundary, and every important boundary should have an exit story.
