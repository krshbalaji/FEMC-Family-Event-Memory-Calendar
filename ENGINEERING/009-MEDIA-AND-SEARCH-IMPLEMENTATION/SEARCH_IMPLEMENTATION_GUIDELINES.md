# FEMC Search Implementation Guidelines

**Version:** 1.0.0
**Status:** Engineering Design
**Owner:** Engineering Office

## Search Architecture

Search indexes are derived state.

## Rules

- authorization must constrain retrieval;
- indexes must be rebuildable;
- stale results must not expose revoked information;
- snippets must not leak inaccessible content;
- search failures must not block canonical family access.

## AI Search

AI-assisted retrieval must use authorized context and preserve source grounding.

## Principle

Search is a convenience layer over family truth, never a replacement for it.
