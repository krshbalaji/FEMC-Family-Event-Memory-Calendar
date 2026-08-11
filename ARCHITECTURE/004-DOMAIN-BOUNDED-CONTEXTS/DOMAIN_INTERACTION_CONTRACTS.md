# FEMC Domain Interaction Contracts

**Version:** 1.0.0
**Status:** Architecture
**Owner:** Architecture Office

## Interaction Modes

Domains may interact through:

- query;
- command;
- event;
- published read model;
- governed integration contract.

## Rules

Contracts should define:

- purpose;
- ownership;
- inputs;
- outputs;
- authorization expectations;
- failure behavior;
- compatibility expectations.

A consuming domain must not modify another domain's canonical state through an undocumented shortcut.

## Principle

Domain collaboration is explicit communication, not shared ownership disguised as convenience.
