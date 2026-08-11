# FEMC Data Integration Contracts

**Version:** 1.0.0
**Status:** Data Architecture
**Owner:** Data Office

## Contract Contents

Material data integrations should define:

- source ownership;
- destination ownership;
- data meaning;
- schema/contract;
- transformation;
- authorization;
- frequency;
- failure handling;
- reconciliation.

## Rule

A receiving system must not silently reinterpret source data into a new canonical meaning.

## Principle

Integration transfers governed meaning, not just fields.
