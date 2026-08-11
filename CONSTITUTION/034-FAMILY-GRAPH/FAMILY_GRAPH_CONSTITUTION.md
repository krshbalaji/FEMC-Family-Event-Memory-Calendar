# FEMC Family Graph Constitution

**Version:** 1.0.0  
**Status:** Constitutional Foundation  
**Owner:** Chief Product Architect

## Purpose

Define the conceptual family graph that connects people, relationships, events, memories, media, and legacy.

## 1. The Family Graph Is Conceptual

The graph describes meaningful relationships in the family domain.

It does not mandate a particular graph database or implementation technology.

## 2. Core Nodes

Conceptually, the graph may contain:

- people;
- family contexts;
- events;
- memories;
- media;
- albums;
- stories;
- places;
- legacy records.

## 3. Core Relationships

Examples include:

- person belongs to family context;
- person related to person;
- person participates in event;
- event produces memory;
- memory contains or references media;
- memory belongs to album;
- memory contributes to story;
- story contributes to legacy.

## 4. Relationships Have Meaning

A connection is not merely a technical foreign key.

It may carry family meaning and historical context.

## 5. Time-Aware Relationships

Relationships may themselves have temporal context.

## 6. Permission-Aware Graph

Graph connectivity does not equal permission.

A system may know that two objects are related while a user remains unauthorized to see one of them.

## 7. AI Boundary

AI may traverse authorized graph context to assist discovery.

It must not infer unsupported family facts simply because a graph path appears plausible.

## 8. Canonical Boundary

The graph is a representation of the family domain, not a replacement for the canonical domain model.

## 9. Principle

FEMC's power comes from meaningful connections, not from isolated records.
