# FEMC Calendar View and Projection Model

**Version:** 1.0.0
**Status:** Calendar Architecture
**Owner:** Calendar Office

## Views

Supported projections may include:

- month;
- week;
- day;
- agenda;
- timeline;
- family milestone;
- event-focused view.

## Model

```text
CANONICAL EVENT
      ↓
AUTHORIZED CALENDAR PROJECTION
      ↓
VIEW
```

## Rule

Editing a projection must resolve back to the canonical Event model through governed behavior.

## Principle

A view may simplify time; it must not redefine time.
