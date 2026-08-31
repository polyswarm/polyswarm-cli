# polyswarm-cli — Testing

## Scope

How the CLI is tested: the `CliRunner` harness, the two mocking styles (SDK-boundary mocks vs VCR cassettes), the formatter-unit style for pure rendering, the cassette layout and record workflow, and how to run the suite. Files: `tests/`, `tests/vcr/`, `src/conftest.py`, `pyproject.toml` (`[project.optional-dependencies].tests`, `[tool.pytest.ini_options]`).

## Invariants

- **Anything that is command behaviour is driven through `click.testing.CliRunner`** — argument parsing, the SDK call, the wiring, the exit code: exercise the real command tree, never an internal function standing in for it. No live PolySwarm stack is required. The one sanctioned exception is pure rendering logic — see [Style 3](#style-3--formatter-unit-tests).
- **Mock at the SDK boundary, or replay HTTP with VCR — never both for the same path.** A test either patches `polyswarm_api.api.PolyswarmAPI.<method>` (unit-style) or lets VCR replay recorded HTTP (end-to-end). The CLI's own code is exercised either way.

  **One sanctioned exception, where the two pin different things:** a refusal whose *rendering* is a CLI decision and whose *envelope shape* is an SDK contract. `FAVORITE_LIMIT` is covered both ways deliberately — the SDK-boundary mock pins the message and the exit code, the recorded 400 pins where in the envelope the machine-readable code actually lives. Neither substitutes for the other: the mock cannot notice either side renaming the envelope key, and the SDK's own respx suite checks that key without ever exercising this CLI's handler. The cassette is what pins the seam between them. Use this only when you can name what each half pins.
- **VCR is an efficiency cache, not a load-bearing requirement.** The suite must pass against a live e2e stack with VCR off. Don't hardcode `record_mode='none'`; if a test only works against its recorded cassette, that's a bug in the test.

- **Never `cp` a cassette from a sibling test, never hand-edit cassette bytes.** Re-record against a live stack.

## Running the suite

```bash
pip install .[tests]      # pytest, pytest-cov, PyYAML, vcrpy
pytest                    # testpaths = ["tests"]; capture to a file for analysis
```

`src/conftest.py` puts `src/` on `sys.path` so imports resolve without a `src.` prefix. The SDK (`polyswarm_api`) must be installed too — in CI it's pulled from the SDK repo's branch archive (see [`05-sdk-contract.md`](./05-sdk-contract.md)); locally, install the SDK you're testing against (an editable checkout of the SDK works).

## Style 1 — SDK-boundary mocks

For commands whose behaviour is "call this SDK method, render the result," patch the method on the SDK client and assert the call + the rendered output. Example: `tests/field_property_test.py` patches `polyswarm_api.api.PolyswarmAPI.metadata_field_properties_{write,get,delete,list}` and drives `CliRunner`. This insulates the test from SDK transport internals — it survives SDK refactors as long as the method name/signature is stable.

Use this style when the point of the test is the **command wiring + formatting**, not the wire shape.

## Style 2 — VCR cassettes

For end-to-end coverage (the CLI calling the SDK calling a recorded server), `tests/cli_test.py` uses `vcrpy`. Each test has two fixtures in `tests/vcr/`:

- `tests/vcr/<name>.vcr` — the recorded HTTP interaction(s).
- `tests/vcr/<name>.click` — the expected rendered CLI output (compared against `result.output`).

The VCR object is built with the default request matcher (`method, scheme, host, port, path, query`) — it does **not** match on headers or body, so cassettes survive User-Agent changes and request-body relocation, and the `query` matcher compares params as a set (order-independent). Default `record_mode='once'`.

Helpers in `cli_test.py`: `_run_cli(args)` invokes the command tree under a cassette; `_assert_text_result` / `_assert_json_result` compare `result.output` and the exit code against the `.click` fixture.

### Re-recording a cassette

Some cassettes need a **stack state**, not just a live stack. All three ruleset-favorite
cassettes do, because `_assert_text_result` compares the whole rendered block verbatim and
the budget counter is part of it: `test_ruleset_favorite_text` pins `Favorites used: 2 of 5`
and `test_ruleset_unfavorite_text` pins `1 of 5`, so each needs the team holding exactly
that many stars at record time. Re-record them together, in a known starting state, or the
counters disagree with each other. `test_ruleset_favorite_limit_text`
records the server refusing at the favorite cap, so it needs a ruleset that exists *and* a
team whose budget is already saturated. Against a fresh stack the recorded id is simply
absent and the run 404s; against a stack where it exists but the budget is not full, the
server accepts the star and the cassette records a success that tests nothing. Set both up
first, then record — and note that saturating the budget consumes slots the other favorite
tests use, so do it deliberately rather than as a side effect of a full-suite recording.

```bash
rm tests/vcr/<name>.vcr            # (and regenerate <name>.click from the new run)
pytest tests/cli_test.py::<Class>::<test>   # records against whatever stack your env points at
```

Point your environment at a live e2e stack, run the test, and commit the freshly recorded `.vcr` (+ updated `.click`). The deletion is what makes VCR record.

## Style 3 — formatter unit tests

For **rendering logic with no command-tree behaviour** — which labelled line a given field set produces — construct the formatter directly (`TextOutput(color=False)`) and call the resource method with an SDK resource built from a literal dict, asserting on the returned lines (`write=False`, no stream, no cassette). Example: `tests/known_good_field_test.py` renders `ArtifactInstance`s that differ only in `state` / `known_good` and asserts which Detections/Status line comes out. This is the right choice when the branch matrix is wide and every branch is a function of the resource's fields — a cassette per branch would mean recording a server state that only the formatter cares about.

Use it **only** for that. Argument parsing, SDK calls, generator consumption, `ctx.obj` wiring and exit codes are command behaviour: a formatter unit test can't observe them, so those need Style 1 or Style 2. A command whose rendering is covered by Style 3 still needs at least one `CliRunner` test proving the command reaches the formatter at all.

## What to test for a new command

1. The command parses its arguments and calls the expected SDK method with the expected arguments.
2. The result is rendered through the right formatter method, for both `--output-format text` and `json` where both matter.
3. Error paths map to the right exit code (no-results → 1, partial → 3, internal/other → 2) — see [`01-architecture.md`](./01-architecture.md) §exit-code mapping.

## Incremental — to be expanded

This spec describes the harness as it stands. Not yet documented (add as the suite grows): a per-command coverage matrix, a documented "VCR-off against live e2e" CI job, and conventions for fixture/`.click` generation. See [`99-open-questions.md`](./99-open-questions.md).

## The SDK floor is a version pin, not a runtime probe

**A test never asks the installed SDK whether it has a feature. The pin guarantees
it.** (For the one pre-existing render guard this does not cover, see
[`03-formatters.md`](./03-formatters.md) §Known-good artifact instances.) When this repo needs a surface the SDK does not yet publish, the SDK bumps its
version and `pyproject.toml` raises `polyswarm_api>=` to it. `pip` then refuses the
combination that would fail, at install time, before a single test runs — so a test
can simply use the surface.

**Do not reintroduce per-test skip guards** — `hasattr` on a method, a built resource's
attribute, a parameter in the installed signature. They are the shape this rule exists to
exclude, and the reasons are worth keeping written down:

- **The fact lived twice.** The pin said one thing; each guard re-derived the same
  thing at runtime. Nothing kept them in sync, so every guard was one edit away from
  disagreeing with the tests it gated.
- **Both ways of disagreeing are defects.** A guard that checks *less* than its test
  uses lets the test run and **fail** where it should have skipped. One that checks
  *more* **skips** a test that would have passed — silently dropping coverage while CI
  stays green. The second is the dangerous one, because nothing reports it.
- **It never verified the thing it claimed to protect.** A green run against the paired
  SDK said nothing about the floor install the guards existed for.

The version contract has none of that: the claim is checked once, by a tool, against
the artifact that will actually be installed.

**When you need a new SDK surface**, in order: add it in `polyswarm-api` → bump that
repo's version (minor, for an additive surface) **in the same PR**, because this repo's
floor cannot name a version the SDK has not declared → raise the floor here → use the
surface in code and tests with no guard. CI installs the SDK from git by branch name,
so an unreleased version is not an obstacle; see
[`05-sdk-contract.md`](./05-sdk-contract.md) §Current floor for the ordering that
forces at release time.

**The failure mode to expect**, and it is a good one: if the paired SDK branch is
missing, CI falls back to the SDK's `develop`, whose version does not satisfy the new
floor, and `pip install .[tests]` fails loudly. Before, that fallback silently tested
against the wrong SDK.
