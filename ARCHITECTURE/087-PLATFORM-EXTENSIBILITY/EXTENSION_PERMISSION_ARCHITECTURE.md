# FEMC Extension Permission Architecture

**Version:** 1.0.0
**Status:** Architecture
**Owner:** Architecture Office

## Permission Model

An extension should have explicit:

- identity;
- purpose;
- resources;
- actions;
- family scope;
- duration;
- revocation behavior.

## Rules

Read permission does not imply write permission.

Write permission does not imply delete permission.

Access to one family context does not imply access to another.

AI-powered extensions follow the same rules.

## Principle

Every extension should be able to answer: what may I access, why, and what may I do with it?
