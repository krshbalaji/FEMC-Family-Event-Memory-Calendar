# FEMC Notification Engineering

**Version:** 1.0.0
**Status:** Engineering Design
**Owner:** Engineering Office

## Requirements

Notifications should support:

- preference controls;
- priority levels;
- scheduling;
- retry behavior;
- deduplication;
- channel failure handling;
- authorization checks;
- delivery observability.

## Rules

Critical security notifications and optional celebration prompts must remain distinguishable.

Notification delivery failure must not change canonical event or memory state.

## Principle

Notification systems deliver information; they do not own the event that caused the notification.
