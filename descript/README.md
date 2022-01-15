# Build Electron for Descript

## Author / Contact:
  - [Charles Van Winkle](https://github.com/cvanwinkle)
  - [Pat DeSantis](https://github.com/pdesantis) 

## Instructions
- If starting from scratch:
  - run `bootstrap.electron.py` to setup
    - Electron `build-tools`
    - a source tree,
    - and patches
- Then
  - run `build-electron.py` from within the `electron/src/electron/descript` folder

## Bootstrap Overview
The bootstrap script automates the following basic operations. In most cases, defaults at prompts are sufficient.
- Check prerequisites
  - Electron Build Tools
  - Python
- Sync Electron Source
- Switch Electron submodule to Descript's fork
  - From within the `electron` subfolder:
    - `git remote set-url origin git@github.com:descriptinc/electron.git`
    - `git remote set-url --fetch origin git@github.com:descriptinc/electron.git`
  - Switch to preferred branch, fetch, and pull
  - Apply patch(es) (not currently automated - but may be part of the branch)

## Build Overview
The build script automates the following basic operations.
- Creates a log file for all build commands (for archiving)
- Synchronizes electron code
- Redirects the Git origin back to Descript's fork
- Builds electron for the current machine architecture (i.e. for an `arm64` build, run the script on a machine with that architecture)
- Verifies the built executable is runnable
- Creates and packages symbols for each PE file in the Electron build
- Zips up the log file
- Generates SHA 256 checksums for the build, log, and symbol archives

## Development
Known issues:
- There are warnings for pre-commit hooks when commiting to our branches within our custom fork of Electron. These are currently to be ignored.
- If you need to fetch upstream from `electron/electron`, you may need to run the following commands:
  - `git remote add upstream https://github.com/electron/electron.git`
  - `git fetch upstream`
  - `git push`

## Patches
- `electron-remove-pre-commit-hooks.patch`
  - Author: [Pat DeSantis](https://github.com/pdesantis)
  - Avoids certain actions for pushing
  - *NOTE*: Do not commit this change to the branch
- `perf-patch-libuv-to-use-posix_spawn-on-macOS.patch`
  - Author: [Pat DeSantis](https://github.com/pdesantis)
  - Fixes bug on macOS where spawning new processes in `libuv` was taking a ton of time
  - Coda: [How to Patch Electron](https://coda.io/d/macOS-HQ_dcQRZrEUtjd/How-to-Patch-Electron_suiCj#_luQty)
  - Upstream Patch: [darwin: Use posix_spawn to spawn subprocesses in macOS #3064](https://github.com/libuv/libuv/pull/3064)

