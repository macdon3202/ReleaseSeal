# Live StudioNet evidence

- Contract: [`0x6c91f4dcEC44607c97d35D0D5a74364b04d66232`](https://explorer-studio.genlayer.com/address/0x6c91f4dcEC44607c97d35D0D5a74364b04d66232)
- Version: `RELEASE_SEAL_V1`
- Architecture: `REVISION_BOUND_MULTI_SOURCE_ACTIVATION_GATE`
- Auxiliary A: `0xFeD97e2aE1A8C1983b7cA206B3545e6A2c685E43`
- Auxiliary B: `0xc67532aeF9D2879cBA9375a02E6217A3524657B8`
- Deployer runtime authority: none

All rows below reached `FINALIZED / MAJORITY_AGREE`. Success rows also have
leader execution `SUCCESS`; rollback rows have leader execution `ERROR`.

| Path | Transactions | Authoritative result |
|---|---|---|
| Happy registration and inspection | [register](https://explorer-studio.genlayer.com/tx/0x73427dd07c3ce373d35a7a2670f4337f7aae81a0d13d341d947b64fe8cba5f0c), [inspect](https://explorer-studio.genlayer.com/tx/0x82529c4980dde106774dc3d5accb8487a9d20b8c1dbc427ceadb13c62f249c13) | release #2 `RELEASABLE / SOURCE_CI_ARTIFACT_ALIGNED`; all bindings `YES`, 5 files, 10 checks |
| Downstream activation by auxiliary B | [activate](https://explorer-studio.genlayer.com/tx/0xa25ac7e6039d8b87ff3d8585d7a0d800aada32736fed968c222fc3f99755593c) | release #2 `ACTIVATED / EXACT_ARTIFACT_ACTIVATED`; activation digest `8e1926…0527` |
| Activation replay | [rejected replay](https://explorer-studio.genlayer.com/tx/0x16e4ea6d0a6fc997b7b0fb03a089582825e8a8e07da1ca69e51e89ea532fe4fb) | `ERROR / RELEASE_NOT_RELEASABLE`; complete release #2 pre-state equals post-state |
| No production change | [register](https://explorer-studio.genlayer.com/tx/0x1961e9b068abcfb3cabd63eabf12b279a59d69c547706bf8259459a79c235c51), [inspect](https://explorer-studio.genlayer.com/tx/0xc83c79b22395d06f6c9040314d1127dbd35f9fa5ba0704e366649207f5442c87) | release #3 `BLOCKED / NO_PRODUCTION_CHANGE`; exact diff only changed a workflow file |
| Package/head conflict | [register](https://explorer-studio.genlayer.com/tx/0x2411fe669a782b2d2eb3ed0ad9a7259112b8cdd1c55f89c4c51954b4424f7676), [inspect](https://explorer-studio.genlayer.com/tx/0x3a6ca1446e7fa814c58d58dea71fe754c649021b6f6e255986b2040cef447c72) | release #4 `CONFLICT / PACKAGE_COMMIT_MISMATCH`; GitHub bindings pass but npm `gitHead` differs |
| Wrong artifact integrity | [setup register](https://explorer-studio.genlayer.com/tx/0xc57d042039e4ae6c5c72434bfd8cdae9c461427bfec5afc79083e71755269075), [setup inspect](https://explorer-studio.genlayer.com/tx/0x47b56f413b3e5f5d4a7676f2acf4196b3d798c9c9b63ad8b742f9341754dd5f0), [rejected activation](https://explorer-studio.genlayer.com/tx/0xbf2c88c79e56f1ac623b96daba536aacea51b07cb6f412abaec570017d6d31a3) | release #6 remained byte-for-byte identical in `RELEASABLE`; error `ARTIFACT_INTEGRITY_MISMATCH` |
| Malformed head commit | [rejected registration](https://explorer-studio.genlayer.com/tx/0x56c08ae8ebd0a6584a9b076cc4a9c70b3d6b990f7b59c2452862d01a04d2bff7) | `ERROR / INVALID_HEAD_COMMIT`; full config pre/post equal and `release_count` stayed 6 |

The first oversized Zod fixture was deliberately retained as release #1
`UNRESOLVED / SOURCE_NOT_VERIFIED`; it did not create an artifact commitment or
positive downstream consequence. Raw complete readbacks are stored in
`studionet-e2e.json` and `studionet-adversarial.json`.
