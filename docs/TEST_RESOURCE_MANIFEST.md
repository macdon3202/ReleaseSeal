# Test resource manifest

| ID | Exact authority object | Intended branch | Proven scope | Limitation |
|---|---|---|---|---|
| `ZOD-CANARY-HAPPY` | `colinhacks/zod`; base `0175a043c7dde9238c9984bce4e4c3471a65582c`; head/npm `gitHead` `dc1a40a54a063c90dbaf08d841064d7aa0120ff8`; `zod@4.5.0-canary.20260817T002538` | expected `RELEASABLE` | 26,986-byte GitHub compare changes the French locale and its regression test; 10 head-bound checks observed passing; npm exposes integrity | Does not prove bug freedom or production deployment |
| `GENLAYER-JS-NO-PROD` | `genlayerlabs/genlayer-js`; base `ae4805e09cf1626e2bfcc0b2e6e1b2639f8431cf`; head/npm `gitHead` `a76bec395aaa927720ee0ce364899a64044dd43e`; `genlayer-js@1.1.8` | expected `BLOCKED / NO_PRODUCTION_CHANGE` | npm metadata and three successful checks bind the head | Exact parent diff changes only `.github/workflows/publish.yml`; deliberately negative |
| `ZOD-INTEGRITY-ROLLBACK` | `colinhacks/zod`; base `9f0a3d81221e3ab7c09ca4911ef35b54817869a4`; head/npm `gitHead` `f300476db2942180206a08af2f093534adfbdffa`; `zod@4.5.0-canary.20260817T183748` | setup `RELEASABLE`, then wrong-integrity rollback | Exact diff changes core utility and a classic regression test; head checks pass; npm integrity is authoritative | Used only to prove exact-integrity enforcement, not production deployment |
| `SYNTHETIC-CONFLICT` | GenVM mock with wrong check head or npm `gitHead` | contract conflict tests | Deterministic mismatch handling | Synthetic; not live publisher evidence |

Observed on 2026-10-01 from GitHub API and npm registry. Live results must be recorded separately and never inferred from this manifest.
