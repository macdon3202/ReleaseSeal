# ReleaseSeal

ReleaseSeal is a permissionless GenLayer dApp that binds an exact GitHub source revision, head-bound CI checks and npm artifact integrity before a release can be activated.

Active StudioNet deployment: [`0x6c91f4dcEC44607c97d35D0D5a74364b04d66232`](https://explorer-studio.genlayer.com/address/0x6c91f4dcEC44607c97d35D0D5a74364b04d66232).

The deployer has no runtime authority. There are no constructor arguments, wallet allowlists or admin methods. Any reviewer can register, inspect and activate a distinct valid release with their own wallet.

## Proof boundary

`RELEASABLE` means validators agree that the exact GitHub base/head relationship exists, the canonical diff changes both declared production and test paths, check-runs belong to the exact head and pass, and npm `gitHead` plus `dist.integrity` bind the artifact. It does not mean the software is bug-free, audited or deployed to production.

`ACTIVATED` is the downstream consequence: the exact registry integrity commitment can be consumed once after a positive inspection.

## Verify

```bash
python -m pytest -q
python -X utf8 -m genvm_linter.cli check contracts/release_seal.py
cd frontend
npm test
npm run build
```

See `docs/TEST_RESOURCE_MANIFEST.md`, `docs/TEST_MATRIX.md` and `docs/LIVE_EVIDENCE.md` for bounded source and execution claims.
