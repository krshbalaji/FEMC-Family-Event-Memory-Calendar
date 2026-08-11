# FEMC Domain Boundaries

**Version:** 1.0.0  
**Status:** Foundation  
**Owner:** Chief Product Architect

## Purpose

Establish conceptual boundaries so FEMC can grow without creating a tangled collection of features.

## Core Domain

The core domain is the family memory and relationship context.

It includes:

- Family
- Person
- Relationship
- Family Membership
- Event
- Time
- Memory
- Media
- Legacy

These concepts carry the product's distinctive long-term value.

## Supporting Domains

Supporting capabilities may include:

- Celebration
- Communication
- Identity
- Permission
- Notifications
- Search
- AI assistance
- Import/export
- Sharing

Supporting domains must serve the core family-memory model.

## Boundary Rule

A supporting capability must not redefine the meaning of a core domain concept merely to simplify its own implementation.

## Integration Rule

When two domains need to interact, the relationship must be explicit and documented.

Example:

A reminder capability may notify a person about an event.

It must not become the owner of the event itself.

## Future Expansion

Potential future domains may include:

- Family places
- Family traditions
- Stories
- Recipes
- Documents
- Family achievements
- Family projects
- Genealogy extensions
- Family wellbeing activities

These must be evaluated against the canonical model before becoming first-class domains.

## Avoiding Domain Explosion

Not every feature requires a new domain.

A new domain is justified only when it has:

1. Distinct business meaning.
2. Independent lifecycle or governance needs.
3. Clear relationships with existing domains.
4. Long-term value beyond one UI feature.

## Constitutional Principle

FEMC should have a small number of strong concepts rather than hundreds of weak feature-specific concepts.
