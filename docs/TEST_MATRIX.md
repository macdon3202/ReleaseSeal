# Test matrix

| Invariant | Coverage |
|---|---|
| Exact source + CI + package alignment reaches `RELEASABLE` | contract execution test |
| Exact integrity produces one-time `ACTIVATED` consequence | happy + replay tests |
| Missing production or regression changes cannot pass | failure matrix |
| Failed/stale CI and npm commit conflicts cannot pass | conflict matrix |
| Source outage and semantic uncertainty remain non-positive | unresolved tests |
| Wrong integrity and duplicate identity preserve full state | rollback tests |
| Any wallet can register and inspect | two-actor permissionless test |
| UI waits for finalized consensus/execution and uses returned ID | frontend transaction tests |
