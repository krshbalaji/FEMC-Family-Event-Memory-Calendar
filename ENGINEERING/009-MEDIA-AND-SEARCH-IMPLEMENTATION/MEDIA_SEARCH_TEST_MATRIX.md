# FEMC Media and Search Test Matrix

**Version:** 1.0.0
**Status:** Engineering Design
**Owner:** Engineering Office

## Required Test Areas

### Media
- upload authorization;
- invalid media;
- duplicate processing;
- derivative generation;
- deletion;
- recovery;
- sharing.

### Search
- family isolation;
- revoked access;
- private memory discovery;
- stale index;
- index rebuild;
- snippets;
- AI retrieval grounding.

## Critical Negative Scenario

A user who loses access to a memory must not discover its content through:

- search results;
- snippets;
- AI answers;
- cached representations;
- derived indexes.

## Principle

Every alternate path to information must obey the same trust boundary as the primary path.
