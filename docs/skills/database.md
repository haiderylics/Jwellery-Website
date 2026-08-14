# Skill: PostgreSQL & Database Engineering

Production database: PostgreSQL.

Money:
- DecimalField only
- never float for currency

Schema:
- normalized where appropriate
- explicit relationships
- constraints
- selective indexes
- stable unique slugs
- explicit deletion policies

Index real access paths:
- slug
- published/active state when queried
- category
- created_at for new-arrival queries
- curated ordering when materially queried

Use select_related/prefetch_related and inspect N+1.

Migrations:
- every schema change via migration
- review generated migrations
- test from clean DB
- avoid unsafe destructive migrations

Transactions:
- atomic for multi-write state changes
- do not hold transactions during network calls

Production:
- least-privilege DB user
- no public DB exposure
- externalized credentials
- backups
- tested restore procedure
