# Verification note — local mock-ticket tutorial

## Revision and environment

- Baseline commit: `c1e945c71d232ea74586c41452cf6fb37b552ab9`
- Branch implementation commit: `ab19a3cf39d1bbf2486a33490279131d22bf94ce`
  (`feature/mock-jira-ticketing-tutorial`; this verification note is committed as a follow-up documentation record.)
- Host `python3 --version`: `Python 3.13.5`
- `uv --version`: `uv 0.11.6 (aarch64-unknown-linux-musl)`
- `uv run` selected CPython `3.14.4` for this project on first execution, consistent with the project's `requires-python = ">=3.14"`.

## Commands actually executed

```text
uv lock --check
uv run python -m compileall -q agents libs main.py
uv run python main.py --offline --count 6 --no-color
uv run python main.py --offline --count 1 --no-color --ticket-adapter fake-jira
uv run python main.py --offline --count 1 --no-color --ticket-adapter fake-jira --fake-ticket-failure validation
uv run python main.py --offline --count 1 --no-color --ticket-adapter fake-jira --fake-ticket-failure create
uv run python main.py --offline --count 1 --no-color --ticket-adapter fake-jira --fake-ticket-failure create-timeout
uv run python main.py --offline --count 1 --no-color --ticket-adapter fake-jira --fake-ticket-failure engineer
uv run python main.py --offline --count 1 --no-color --ticket-adapter fake-jira --fake-ticket-failure tester
uv run python main.py --offline --count 1 --no-color --ticket-adapter fake-jira --fake-ticket-failure unknown
uv run python -m unittest discover -s tests -v
```

## Observed outcomes

- `uv lock --check`, `compileall`, baseline six-scenario run, normal fake-adapter run, timeout reconciliation, engineer failure, tester failure, unknown fallback, and `unittest` all exited `0`.
- The deliberate `validation` and `create` fault paths exited `1` as designed: validation rejected the malformed report before fake ticket creation; injected create raised the local fake create error.
- Unit tests: `Ran 6 tests ... OK`. They cover malformed report rejection before creation, local create failure, timeout reconciliation without duplicate, mock fields/comments/lifecycle, engineer/tester follow-up behavior, and the unknown fallback.
- The observed normal run made `SIM-1` with `https://jira.example.invalid/browse/SIM-1`, three `[SIMULATION/MOCK]` local comments, and `SIMULATED_VALIDATED_LOCAL_ONLY`. It did not demonstrate real remediation, validation, Jira workflow behavior, or closure. See `mock-ticket-console-transcript.md` for the captured excerpt.

## Explicitly untested / not contacted

No credentials were loaded and no HTTP client or network operation was implemented for ticketing. The following live dependencies/services were deliberately untested and not contacted:

- LM Studio model mode
- TypeSafe endpoint
- Jira Cloud (all REST APIs, authentication, metadata, create/search/comment/transition behavior, and rate limits)
- production remediation and production validation

The fake adapter is local, in-memory tutorial code only; it is not evidence of a working Jira Cloud integration.
