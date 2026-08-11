# FEMC Identity External Provider Portability

**Version:** 1.0.0
**Status:** Identity Architecture
**Owner:** Identity Office

## Providers

External identity providers may support:

- authentication;
- account linking;
- verification;
- recovery.

## Rules

Provider identifiers should not become the sole canonical identity representation.

Provider replacement must preserve FEMC identity continuity and family relationships.

## Principle

A provider may authenticate a participant; FEMC must retain ownership of the identity context it creates.
