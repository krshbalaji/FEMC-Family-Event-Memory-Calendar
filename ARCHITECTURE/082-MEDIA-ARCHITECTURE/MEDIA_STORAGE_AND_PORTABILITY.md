# FEMC Media Storage and Portability Architecture

**Version:** 1.0.0
**Status:** Architecture
**Owner:** Architecture Office

## Storage Separation

Separate conceptually:

- media metadata;
- canonical media reference;
- physical storage;
- derived representations;
- access delivery.

## Provider Independence

The family domain must not depend on one storage provider's proprietary representation.

## Portability

Exports should preserve media relationships and contextual metadata where practical.

## Failure

Loss of a media delivery service must not erase the family record describing the media.

## Security

Media requires appropriate encryption, authorization, access logging, and sharing controls.

## Principle

Storage is an implementation detail; family media context is part of the domain.
