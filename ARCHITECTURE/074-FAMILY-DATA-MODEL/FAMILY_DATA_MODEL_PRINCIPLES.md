# FEMC Family Data Model Principles

**Version:** 1.0.0
**Status:** Architecture
**Owner:** Architecture Office

## Core Concepts

```text
Person
FamilyContext
Relationship
Event
TimeContext
Memory
Media
Album
Celebration
Communication
LegacyRecord
Consent
AccessPolicy
Provenance
```

## Core Relationships

```text
FamilyContext
 ├── Person
 ├── Relationship
 ├── Event
 │    └── TimeContext
 ├── Memory
 │    ├── Media
 │    └── Album
 ├── Celebration
 ├── Communication
 └── LegacyRecord
```

## Important Distinctions

Person ≠ Account

Person ≠ Role

Relationship ≠ Permission

Event ≠ Memory

Media ≠ Memory

AI Output ≠ Canonical Fact

Analytics ≠ Canonical Fact

## Principle

The data model must preserve family meaning before optimizing storage.
