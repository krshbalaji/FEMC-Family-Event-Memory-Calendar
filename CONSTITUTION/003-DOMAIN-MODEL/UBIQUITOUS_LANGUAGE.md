# FEMC Ubiquitous Language

**Version:** 1.0.0  
**Status:** Foundation  
**Owner:** Chief Product Architect

This document defines canonical meanings for important FEMC terms.

## Core Vocabulary

| Term | Canonical Meaning |
|---|---|
| Family | A social context connecting people, relationships, history, and shared life |
| Person | A human represented in FEMC |
| Relationship | A meaningful connection between people |
| Family Membership | A person's participation within a family context |
| Event | A meaningful occurrence associated with time and context |
| Memory | A preserved representation of something meaningful |
| Media | Digital content associated with domain information |
| Album | A curated collection or presentation of memories/media |
| Celebration | A meaningful family activity around an occasion |
| Legacy | Long-term preservation and transmission across generations |
| Identity | Representation used to establish who a participant is |
| Permission | Rules governing authorized access and actions |
| AI Context | Information AI may use within authorized boundaries |

## Terminology Rules

The same word must not be used to represent different canonical concepts.

Product documentation, AI prompts, architecture documents, and future APIs should use these meanings consistently.

If terminology changes, the change must be documented as a deliberate domain-language evolution.

## Important Distinctions

### Person vs Identity

A person is the domain participant.

Identity is how the system establishes or represents participation.

### Memory vs Media

A memory carries meaning.

Media is evidence or content that may support a memory.

One memory may have many media items.

One media item may participate in more than one meaningful context where permitted.

### Event vs Celebration

An event is an occurrence.

A celebration is a human activity or expression associated with an occasion.

### Family vs Family Membership

A family is the social context.

Membership describes a person's participation in that context.

### Relationship vs Membership

Membership says that a person belongs to or participates in a family context.

Relationship describes how people are connected.

### AI Context vs Family Record

AI context is a controlled view of information available for a particular AI task.

It must never be assumed that AI has unrestricted access to the complete family record.

## Forbidden Ambiguity

Avoid using:

- "user" when "person", "identity", or "family member" is the actual concept;
- "photo" when the domain meaning is actually "memory";
- "calendar item" when the domain meaning is actually "event";
- "contact" when the domain meaning is actually "person" or "relationship".

The goal is precise language, not complicated language.
