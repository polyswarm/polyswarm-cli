# polyswarm-cli — Testing

## Scope

How the CLI is tested: the `CliRunner` harness, the two mocking styles (SDK-boundary mocks vs VCR cassettes), the cassette layout and record workflow, and how to run the suite. Files: `tests/`, `tests/vcr/`, `src/conftest.py`, `pyproject.toml` (`[project.optional-dependencies].tests`, `[tool.pytest.ini_options]`).

## Invariants

- **Tests drive the CLI through `click.testing.CliRunner`** — they invoke the real command tree, not internal functions. No live PolySwarm stack is required.
- **Mock at the SDK boundary, or replay HTTP with VCR — never both for the same path.** A test either patches `polyswarm_api.api.PolyswarmAPI.<method>` (unit-style) or lets VCR replay recorded HTTP (end-to-end). The CLI's own code is exercised either way.
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

```bash
rm tests/vcr/<name>.vcr            # (and regenerate <name>.click from the new run)
pytest tests/cli_test.py::<Class>::<test>   # records against whatever stack your env points at
```

Point your environment at a live e2e stack, run the test, and commit the freshly recorded `.vcr` (+ updated `.click`). The deletion is what makes VCR record.

## What to test for a new command

1. The command parses its arguments and calls the expected SDK method with the expected arguments.
2. The result is rendered through the right formatter method, for both `--output-format text` and `json` where both matter.
3. Error paths map to the right exit code (no-results → 1, partial → 3, internal/other → 2) — see [`01-architecture.md`](./01-architecture.md) §exit-code mapping.

## Incremental — to be expanded

This spec describes the harness as it stands. Not yet documented (add as the suite grows): a per-command coverage matrix, a documented "VCR-off against live e2e" CI job, and conventions for fixture/`.click` generation. See [`99-open-questions.md`](./99-open-questions.md).
