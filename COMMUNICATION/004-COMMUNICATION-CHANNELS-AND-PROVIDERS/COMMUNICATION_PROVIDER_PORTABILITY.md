# FEMC Communication Provider Portability

**Version:** 1.0.0
**Status:** Communication Architecture
**Owner:** Communication Office

## Portability

Material communication providers should be replaceable through explicit contracts and adapters where practical.

Consider:

- message delivery;
- authentication;
- templates;
- media;
- rate limits;
- delivery receipts;
- failure semantics;
- provider data retention.

## Rule

Provider-specific identifiers and behavior must not become the canonical family communication model.

## Principle

Changing a communication provider should be an engineering migration, not a redesign of FEMC's communication meaning.
