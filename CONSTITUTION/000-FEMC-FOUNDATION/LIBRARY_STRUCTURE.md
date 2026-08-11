# FEMC Library Structure

**Version:** 1.0.0  
**Status:** Foundation

## Purpose

Define the organization of the FEMC constitutional repository.

## Principle

Folder structure must reflect conceptual governance, not implementation technology.

## Numbering

Numbered directories provide stable conceptual ordering.

They are not required to match software package names.

## Current Structure

```text
CONSTITUTION/
├── MASTER_INDEX.md
├── 000-FEMC-FOUNDATION/
├── 001-PRODUCT-CONSTITUTION/
├── 002-COUNCIL/
├── 003-DOMAIN-MODEL/
├── 004-PRODUCT-ARCHITECTURE/
├── 005-AI-STRATEGY/
├── 006-GOVERNANCE-TRUST/
├── 007-10-YEAR-VISION/
└── 008-COUNCIL-ARCHITECTURE/
```

## Growth Rule

New top-level areas should be created only when existing areas cannot reasonably own the concept.

Avoid folder proliferation.

## Cross-References

Documents should reference canonical documents by stable repository path rather than duplicating large sections of constitutional knowledge.

## Library Integrity

A document belongs in the library when it contains durable project knowledge that future contributors or AIs need to understand FEMC correctly.
