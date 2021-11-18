# Build Electron for Descript

## Author / Contact:
  - [Charles Van Winkle](https://github.com/cvanwinkle)
  - [Pat DeSantis](https://github.com/pdesantis) 

## Overview
- Check prerequisites
  - Electron Build Tools
  - Python
- Sync Electron Source
  - Switch Electron submodule to Descript's fork
    - From within the `electron` subfolder:
      - `git remote set-url origin git@github.com:descriptinc/electron.git`
      - `git remote set-url --fetch origin git@github.com:descriptinc/electron.git`
  - Switch to preferred branch
  - Apply patch(es)
- Build

## Patches
- `electron-remove-pre-commit-hooks.patch`
  - Author: Pat
  - Avoids certain actions for pushing
  - *NOTE*: Do not sommit this change to the branch
- `perf-patch-libuv-to-use-posix_spawn-on-macOS.patch`
  - Author: Pat
  - Fixes bug on macOS where spawning new processes in `libuv` was taking a ton of time
  - Coda: [How to Patch Electron](https://coda.io/d/macOS-HQ_dcQRZrEUtjd/How-to-Patch-Electron_suiCj#_luQty)
  - Upstream Patch: [darwin: Use posix_spawn to spawn subprocesses in macOS #3064](https://github.com/libuv/libuv/pull/3064)

