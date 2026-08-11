# FEMC Data Lifecycle and Retention Principles

**Version:** 1.0.0  
**Status:** Foundation  
**Owner:** Chief Product Architect

## Lifecycle

```text
CREATE
  ↓
VALIDATE / CLASSIFY
  ↓
STORE
  ↓
USE
  ↓
UPDATE
  ↓
ARCHIVE
  ↓
EXPORT / DELETE
```

## Create

Information may originate from users, imports, integrations, media capture, or governed AI assistance.

## Validate / Classify

Information should retain its status and provenance.

## Store

Canonical information must be stored with sufficient relationships and metadata to preserve meaning.

## Use

Access and processing must follow applicable permissions and purpose.

## Update

Changes should preserve appropriate history and integrity.

## Archive

Inactive information may be archived while remaining discoverable according to permission and preservation policy.

## Export / Delete

Families should have meaningful control over their information.

Deletion must be deliberate and must account for dependencies and legal or operational requirements where applicable.

## Retention Principle

Retention should be based on product meaning, user control, preservation needs, and applicable obligations—not merely on storage convenience.

## Derived Data

Derived structures should be replaceable or reconstructible where practical.

## AI Data

AI-generated intermediate context should not automatically become permanent family data.

## Long-Term Principle

Family information that has historical value should be preserved in a way that remains understandable beyond the lifetime of any one implementation.
