# FEMC Canonical and Derived Data Principles

**Version:** 1.0.0  
**Status:** Foundation  
**Owner:** Chief Product Architect

## Canonical Data

Represents authoritative family information.

Examples include confirmed:

- people;
- relationships;
- events;
- memories;
- permissions.

## Derived Data

May include:

- search indexes;
- analytics;
- recommendations;
- AI summaries;
- embeddings;
- caches.

## 1. Derived Data Can Be Rebuilt

Where practical, derived data should be reproducible from canonical sources.

## 2. Derived Data Can Be Wrong

Derived information must not silently override canonical information.

## 3. Provenance

Important derived results should be traceable to their source context.

## 4. Staleness

The architecture should recognize that derived data may become outdated.

## 5. Deletion

Deleting or correcting canonical information must have defined consequences for derived representations.

## 6. Principle

If a derived representation disagrees with canonical family information, the canonical source wins.
