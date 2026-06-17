# polyswarm-cli — Architecture

## Scope

The components of the CLI and how a command flows from `argv` to rendered output: the click app, the `Polyswarm(PolyswarmAPI)` wrapper, the command modules, the formatters, the parallel-execution helpers, and the exception → exit-code mapping. Files: `src/polyswarm/client/polyswarm.py`, `src/polyswarm/polyswarm.py`, `src/polyswarm/client/*.py`, `src/polyswarm/formatters/*.py`, `src/polyswarm/utils.py`, `src/polyswarm/exceptions.py`.

## Invariants

- **No HTTP in the CLI.** Commands call SDK methods; the SDK owns the wire. The CLI never constructs an `httpx`/`requests` call directly.
- **Commands read `api` and `output` from `ctx.obj`.** The top-level group seeds them once; commands don't construct their own client or formatter.
- **One command-group module per resource family**, wired into `polyswarm_cli` via `add_command`. A module owns its `@click.group`, its subcommands, and nothing else.
- **Rendering goes through a formatter method**, never `print`/`click.echo` of an SDK object directly. Every renderable resource type has a method on `BaseOutput` and an implementation in each concrete formatter.
- **Exit codes are assigned centrally** by `ExceptionHandlingGroup`, by exception type — commands raise (or let SDK exceptions propagate), they don't call `sys.exit`.

## The app — `client/polyswarm.py`

`polyswarm_cli` is the top-level `click.Group`, constructed with `cls=ExceptionHandlingGroup`. It:

1. Declares the **global options** — `--api-key` (env `POLYSWARM_API_KEY`), `--api-uri` (env `POLYSWARM_API_URI`), the **endpoint shortcuts** `--stage` / `--local` / `--prod-eu` / `--stage-eu`, `--output-file`, `--output-format`/`--fmt` (`text`|`json`|…), `--color/--no-color`, `--verbose`, `--community` (env `POLYSWARM_COMMUNITY`), `--parallel`, `--verify/--no-verify`, plus `--version` / `--api-version`.

   **Endpoint resolution** (`resolve_api_uri`): the four shortcuts are convenience aliases for known public endpoints (`API_URI_SHORTCUTS`). Precedence is **explicit command-line flag → `POLYSWARM_API_URI` env var → production default** (`PROD_API_URI` = `https://api.polyswarm.network/v3`). Specifically: a shortcut and an explicit *command-line* `--api-uri` are mutually exclusive (conflict → `click.UsageError`, exit 2), as are two shortcuts; a shortcut **wins over** an ambient `POLYSWARM_API_URI` (the env var is consulted only when no shortcut is given); and a command-line `--api-uri` wins over the env var (click's own source precedence). The command-line-vs-env distinction uses `ctx.get_parameter_source('api_uri') == ParameterSource.COMMANDLINE`.
2. **Seeds `ctx.obj`** — constructs a `Polyswarm(...)` client (the SDK wrapper) as `ctx.obj['api']` and the selected formatter as `ctx.obj['output']`.
3. **Wires the command groups** — each `client/<family>.py` group/command is imported and `add_command`-ed onto `polyswarm_cli`.

The console-script entry (`__main__.py`) calls `polyswarm_cli(prog_name='polyswarm', obj={})`.

### `ExceptionHandlingGroup` — exit-code mapping

`ExceptionHandlingGroup.invoke` wraps `super().invoke(ctx)` and maps exceptions to process exit codes (commands stay clean of `sys.exit`):

| Exception (CLI `exceptions.*` and SDK `api_exceptions.*`) | Exit code |
|---|---|
| `NoResultsException`, `NotFoundException`, `FailedInstanceException` (SDK) | `1` |
| `PartialResultsException` (CLI) | `3` |
| `InternalFailureException`, `PolyswarmException`, `JSONDecodeError`, `UnicodeDecodeError` | `2` |
| Transport errors matched by ancestry class name (`httpx`'s `HTTPError` root, legacy `requests`' `RequestException`, builtin `ConnectionError`/`SSLError`) | `1` |
| Any other `Exception` | `2` |

The transport-error branch matches by **ancestry class name** — it intersects `{c.__name__ for c in type(e).__mro__}` with `{'HTTPError', 'RequestException', 'ConnectionError', 'SSLError'}` — because those classes come from the SDK's HTTP dependency (`httpx`; `requests` historically) and shouldn't be imported here directly. `httpx` roots every request/transport/status error at `HTTPError`, so ancestry matching covers all its leaf classes (`ConnectError`, `ReadTimeout`, `RemoteProtocolError`, `ProxyError`, …) without enumerating them.

## The SDK wrapper — `polyswarm.py`

`class Polyswarm(PolyswarmAPI)` subclasses the SDK's sync client to add **CLI-only** behaviour the SDK has no reason to ship:

- **A `parallel` worker count** — popped from `kwargs` in `__init__` before `super().__init__`, used as `max_workers` for fan-out.
- **Parallel fan-out** over many inputs — `search_hashes`, `search_urls`, `download_multiple`, `download_id_multiple`, `download_stream`, `sandbox_instances`, `tag_link_multiple`, `historical_results_multiple`, `historical_delete_multiple`, `scan_lookup`, etc. These drive `utils.parallel_executor*` over a per-item SDK call and yield results.
- **Multi-step flows** — `scan_file` (submit + wait), `submit_url` (inline IP-analysis submit), the `*_and_wait` helpers.

The wrapper only touches the SDK through its **documented public surface** (endpoint methods, `_single`, `session`, `resources`, `settings`); see [`05-sdk-contract.md`](./05-sdk-contract.md). Because the SDK's search/list methods are **generators**, the wrapper and its callers must iterate them — never index, `len()`, or hand a generator to a singular formatter.

## Command modules — `client/*.py`

One module per resource family. The shape of every command:

```python
@<group>.command('verb')
@click.argument(...) / @click.option(...)
@click.pass_context
def verb(ctx, ...):
    api = ctx.obj['api']
    output = ctx.obj['output']
    # single result:
    output.<resource>(api.<method>(...))
    # collection (SDK returns a generator):
    for item in api.<method>(...):
        output.<resource>(item)
```

The catalogue of groups and the SDK methods each wraps is in [`02-commands.md`](./02-commands.md).

## Formatters — `formatters/`

`BaseOutput` (`base.py`) is the interface: one method per renderable resource type (`artifact_instance`, `historical_result`, `hunt`, `local_artifact`, `ruleset`, `ioc`, `known_host`, `metadata`, `tag_link`, `family`, `tag`, `sandbox_task`, `bundle_task`, `sample`, …), each raising `NotImplementedError`. Concrete renderers — `TextOutput` (`text.py`), `JSONOutput` (`json.py`), and the hash-only `SHA256Output`/`SHA1Output`/`MD5Output` (`hashes.py`) — override them. `--output-format` selects one via the `formatters` registry (`formatters/__init__.py`). Details in [`03-formatters.md`](./03-formatters.md).

## Support — `utils.py`, `exceptions.py`

- **`utils.py`** — `parallelize`/`parallel_executor` (thread-pool fan-out with per-item exception aggregation: collects results, logs per-item no-results, raises an aggregate `NoResultsException`/`NotFoundException`/`InternalFailureException` at the end), `parallel_executor_iterable_results` (the same, for SDK methods that return generators — it materialises each generator inside the worker so per-item exception handling still fires), and input parsing/validation (`parse_hashes`, hash/IP detection).
- **`exceptions.py`** — the CLI's own hierarchy, **distinct from the SDK's**: `PolyswarmException` → `NoResultsException`, `NotFoundException`, `InternalFailureException`, `PartialResultsException`. `ExceptionHandlingGroup` catches both these and the SDK's `api_exceptions.*`.

## Lifecycle of a command (end to end)

1. `polyswarm_cli` parses global options, builds `Polyswarm(api_key, uri=…, community=…, parallel=…, verify=…)` and the formatter into `ctx.obj`.
2. The subcommand reads `api`/`output` from `ctx.obj`, parses its own args, and calls one or more SDK methods (directly or via a wrapper fan-out method).
3. Results are rendered through the formatter; collections are iterated.
4. Any exception propagates to `ExceptionHandlingGroup.invoke`, which logs it and raises `Exit(<code>)`.
