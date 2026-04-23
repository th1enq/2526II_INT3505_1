# Deprecation Notice for Developers

**Subject:** Deprecation of Payment/User API v1 and Migration to v2

Hello developers,

We are announcing the deprecation of API v1 endpoints:
- `/api/v1/users`
- `/api/v1/payments`

## Important dates
- **Deprecation announced:** 2026-04-23
- **Sunset date (v1 disabled):** 2026-09-30

## What is changing
1. Users schema in v2 uses `full_name` instead of `name`, plus `email`, `status`.
2. Payments v2 requires `customer_id` and returns richer lifecycle (`authorized`, action links).

## How to migrate
- Switch endpoint to `/api/v2/...`.
- Or set version via header/query in compatible routes.
- Update request/response mapping based on migration docs.

## Runtime warning signals
During transition, v1 responses include:
- `Deprecation: true`
- `Sunset: Tue, 30 Sep 2026 00:00:00 GMT`
- `Warning: 299 - "API v1 is deprecated and will be removed on 2026-09-30..."`

Please complete migration before sunset date to avoid service disruption.

Thanks,
API Platform Team
