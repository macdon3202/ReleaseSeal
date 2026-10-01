# UI and transaction-state parity

Verified against the production Vite bundle on 2026-10-01, using contract
`0x6c91f4dcEC44607c97d35D0D5a74364b04d66232`.

| Release ID | Contract readback | UI rendering |
|---|---|---|
| #2 | `ACTIVATED / EXACT_ARTIFACT_ACTIVATED` | exact state/reason, repository, head, package, integrity, CI and regression fields displayed |
| #3 | `BLOCKED / NO_PRODUCTION_CHANGE` | exact state/reason; regression alignment `NO`; no activation action |
| #4 | `CONFLICT / PACKAGE_COMMIT_MISMATCH` | exact state/reason; package version and positive GitHub bindings remain visible |
| #6 | `RELEASABLE / SOURCE_CI_ARTIFACT_ALIGNED` | exact state/reason and exact-integrity activation action visible |
| #999 | read error | stale release card removed; `ACTION STOPPED` shown |

Transaction handling is separately covered by `frontend/transactions.test.mjs`:
the UI requires `FINALIZED`, affirmative consensus and leader execution
`SUCCESS`; finalized execution errors and consensus disagreement are failures.
The exact release ID is extracted from the finalized leader receipt rather than
inferred from the global counter. After every write, the UI reads that exact ID
and checks the expected authoritative state before reporting success.
