# FEMC Media Lifecycle Architecture

**Version:** 1.0.0
**Status:** Architecture
**Owner:** Architecture Office

## Lifecycle

```text
CAPTURE
 ↓
INGEST
 ↓
VALIDATE
 ↓
ASSOCIATE
 ↓
STORE
 ↓
DERIVE
 ↓
PRESENT / SHARE
 ↓
PRESERVE / EXPORT
 ↓
RETIRE
```

## Requirements

The lifecycle should preserve:

- source context;
- ownership;
- authorization;
- provenance;
- relationships;
- timestamps;
- transformations.

## Derived Media

Thumbnails, previews, transcodes, captions, classifications, and AI-generated derivatives are derived representations.

## Deletion

Removing a derivative must not automatically remove the canonical media asset or its family context.

## Principle

Media lifecycle management must protect both the asset and the meaning attached to it.
