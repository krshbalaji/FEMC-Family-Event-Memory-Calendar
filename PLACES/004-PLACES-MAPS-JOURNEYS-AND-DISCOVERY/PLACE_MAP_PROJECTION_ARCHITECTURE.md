# FEMC Place Map Projection Architecture

**Version:** 1.0.0
**Status:** Places Architecture
**Owner:** Places Office

## Purpose

Separate canonical family place meaning from map-provider presentation.

## Model

```text
CANONICAL FAMILY PLACE
        ↓
GEOGRAPHIC PROJECTION
        ↓
MAP / LIST / GLOBE / TIMELINE
```

## Rules

Map providers are presentation and geographic-service dependencies, not owners of family place identity.

A map view may simplify or transform representation for usability without changing canonical place meaning.

## Principle

FEMC owns the family relationship to a place; a map is one way to see it.
