# FEMC Events Calendar Projection Model

**Version:** 1.0.0
**Status:** Events Architecture
**Owner:** Events Office

## Purpose

Separate canonical family-event meaning from calendar-specific presentation.

## Model

```text
CANONICAL EVENT
      ↓
CALENDAR PROJECTION
      ↓
MONTH / WEEK / DAY / AGENDA / OTHER VIEW
```

## Rules

A calendar view is a projection and must not become the canonical owner of the event.

Different calendars or interfaces may present the same event differently while preserving its meaning.

## Principle

FEMC owns the event; a calendar is one way of experiencing it.
