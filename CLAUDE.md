# Agent instructions

## Deterministic check (backpressure)
Before saying a task is done, or committing, run `scripts/check.sh` (compile, ruff, renderer tests)
and read the output. If it fails, fix the cause; never skip hooks (`--no-verify`) or loosen the
checks to get green. Report the actual result.

One-time per clone: `git config core.hooksPath .githooks` (runs the same check on every commit).
The scheduled refresh workflow also runs the tests before it auto-commits.
