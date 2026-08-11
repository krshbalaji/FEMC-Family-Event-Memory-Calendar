# FEMC Events Negative Testing

**Version:** 1.0.0
**Status:** Events Assurance
**Owner:** Events Office

## Deliberate Tests

Test:

- incorrect time-zone conversion;
- duplicate events;
- recurrence exceptions;
- cancelled events resurfacing as active;
- historical events being edited incorrectly;
- unauthorized participants;
- impossible dates;
- ambiguous dates becoming falsely precise;
- reminders generated from invalid event state.

## Principle

Event trust depends on the system refusing to turn temporal ambiguity into false certainty.
