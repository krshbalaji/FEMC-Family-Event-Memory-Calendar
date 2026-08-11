# FEMC Event Reminder Timing Model

**Version:** 1.0.0
**Status:** Events Architecture
**Owner:** Events Office

## Reminder Context

Reminder timing may depend on:

- event type;
- importance;
- preparation required;
- participant role;
- travel/location;
- family preference;
- prior reminder behavior.

## Rules

Reminder generation must use the current authorized event state.

Cancelled, postponed, or invalid events must not continue producing active reminders.

## Principle

A reminder is useful only while the underlying event remains meaningful and actionable.
