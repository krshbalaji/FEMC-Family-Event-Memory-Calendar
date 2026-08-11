# FEMC Provenance and Truth Model

**Version:** 1.0.0  
**Status:** Foundation  
**Owner:** Chief Product Architect

## Purpose

Define conceptual distinctions between family facts, imported information, system-derived information, and AI-generated information.

## Information States

### Confirmed

Information accepted as a family fact by an authorized person or trusted source.

### Imported

Information brought from another system.

Imported does not automatically mean confirmed.

### Derived

Information calculated or transformed from canonical information.

### Inferred

Information produced through reasoning or pattern recognition.

### AI Suggested

Information proposed by an AI system for human consideration.

### Generated

Content created by AI or another system, such as a story draft or caption.

### Unknown

Information for which FEMC does not have sufficient knowledge.

## Truth Rule

Unknown information must remain unknown.

The system must not fill gaps merely to create a complete-looking record.

## AI Rule

AI-generated output must not silently become canonical family truth.

Where AI suggests a fact, appropriate human confirmation or another governed validation process is required before it becomes confirmed.

## Provenance

Where practical, information should retain:

- source;
- creator or origin;
- creation time;
- modification history;
- confidence or status where relevant.

## Derived Data

Indexes, embeddings, classifications, summaries, recommendations, and similar derived structures must remain reconstructible or replaceable where practical.

They should not become the only representation of family truth.

## Constitutional Principle

The more important an item is to long-term family history, the stronger the requirement for provenance, integrity, and understandable status.
