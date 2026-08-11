# FEMC Architectural Dependency Principles

**Version:** 1.0.0  
**Status:** Foundation  
**Owner:** Chief Product Architect

## 1. Dependency Direction

Dependencies should generally point from specialized capabilities toward stable domain meaning rather than allowing infrastructure to define the domain.

## 2. Minimize Cycles

Material circular dependencies should be treated as architectural warning signals.

## 3. Optional Capability Isolation

Optional AI, analytics, and integrations should not become mandatory for core family access.

## 4. External Dependency Containment

Provider-specific assumptions should remain inside appropriate boundaries.

## 5. Data Dependency Awareness

Derived representations should have identifiable sources.

## 6. Failure Awareness

Every important dependency should have understood failure consequences.

## 7. Principle

A dependency is acceptable when its purpose, owner, failure impact, and replacement implications are understood.
