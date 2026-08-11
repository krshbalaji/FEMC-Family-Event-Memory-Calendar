# FEMC Import and Migration Constitution

**Version:** 1.0.0  
**Status:** Constitutional Foundation  
**Owner:** Chief Product Architect

## Purpose

Define how external information enters FEMC and how FEMC information moves between implementations without losing family meaning.

## 1. Import Is Not Confirmation

Imported information should retain its source and status.

Importing data does not automatically make every field confirmed family truth.

## 2. Preserve Provenance

Where practical, retain:

- source;
- import time;
- original identifiers;
- transformation history;
- relevant uncertainty.

## 3. Validate Before Canonicalization

Imported information should be evaluated before becoming canonical.

## 4. Preserve Relationships

A successful migration must preserve meaningful relationships between:

- people;
- relationships;
- events;
- memories;
- media;
- albums;
- legacy information.

## 5. No Silent Data Loss

If information cannot be migrated accurately, the limitation must be identified rather than silently discarded.

## 6. Reversibility

High-risk migrations should have appropriate recovery or rollback strategies.

## 7. Vendor Independence

Migration architecture must not assume that one provider will exist forever.

## 8. AI

AI may assist mapping or classification, but AI-generated mappings must not silently alter canonical family truth.

## 9. Principle

Migration success means preserving meaning, not merely moving records.
