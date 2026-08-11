# FEMC Compute and Workload Boundaries

**Version:** 1.0.0
**Status:** Architecture
**Owner:** Architecture Office

## Workload Classes

### Core Transactional
Family identity, relationships, events, memories, permissions, and canonical changes.

### Derived
Search indexing, analytics, recommendations, transformations, and AI processing.

### Asynchronous
Notifications, media processing, imports, exports, migrations, and background enrichment.

### Operational
Monitoring, auditing, administration, and recovery workflows.

## Rules

1. Core transactional workloads receive the strongest consistency and availability consideration.
2. Derived workloads must not block essential family access unnecessarily.
3. Heavy asynchronous processing must be isolated from interactive family journeys.
4. Workload boundaries should be based on actual behavior and scaling characteristics.

## Principle

Separate workloads when separation improves reliability or scale—not simply because separation is fashionable.
