# polyswarm-cli — SDK contract (CLI as a consumer of polyswarm-api)

## Scope

How the CLI depends on the `polyswarm-api` SDK: which parts of the SDK's public surface it consumes, the rules for consuming them correctly, how the two repos ship coordinated changes, and how the version pin is managed. This is the mirror image of the SDK's own `specs/05-downstream-contract.md` — read that for the authoritative list of what the SDK guarantees.

## Invariants

- **The CLI consumes only the SDK's public surface.** That means `polyswarm_api.api.PolyswarmAPI` (subclassed as `Polyswarm`), `polyswarm_api.resources`, `polyswarm_api.exceptions`, `polyswarm_api.settings`, and the documented power-user helpers on the client (`_single`, `session`). It does **not** reverse-engineer private internals or transport details.
- **The SDK owns the wire; the CLI owns the UX.** If the CLI needs a new server capability, the SDK gets the method first (`AGENTS.md` §"When adding a command family", step 1).
- **SDK + CLI changes that depend on each other ship as a pair.** The SDK PR opens first; the CLI PR links it under `## Requires` and must not merge before the SDK surface it needs is released / on the SDK's `develop` (CI installs the SDK from there — see below).
- **The SDK version pin in `pyproject.toml` is the compatibility contract.** Floor it at the lowest SDK version that exposes every method/behaviour the CLI relies on.

## What the CLI imports from the SDK

| Import | Used for |
|---|---|
| `from polyswarm_api.api import PolyswarmAPI` | Base class of the `Polyswarm` wrapper (`src/polyswarm/polyswarm.py`). |
| `from polyswarm_api import settings` | Defaults: `DEFAULT_SCAN_TIMEOUT`, `DEFAULT_REPORT_TIMEOUT`, etc. |
| `from polyswarm_api import resources` | Result-parser classes for power-user calls (e.g. `resources.ArtifactInstance`); resource attributes the formatters read. |
| `from polyswarm_api import exceptions as api_exceptions` | Caught in `ExceptionHandlingGroup` and `utils.parallel_executor` (`NoResultsException`, `NotFoundException`, `FailedInstanceException`, `PolyswarmException`). |
| `from polyswarm_api.core import parse_isoformat` | Date rendering in `formatters/text.py`. |
| `import polyswarm_api` (`__version__`) | `--api-version`. |

All of the above are part of the SDK's documented public surface. If a future change needs something not on that list, that's a signal to add a method/export to the SDK rather than reach into internals.

## Consuming the SDK correctly

### Endpoint methods return generators — iterate them

The SDK's search / list / paginated methods (`search`, `search_url`, `search_scans`, `search_by_metadata`, `search_by_ioc`, `iocs_by_hash`, `check_known_hosts`, `*_list`, `historical_results`, `live_feed`, `stream`, …) are **lazy generators**. Consume them by iteration:

```python
for item in api.iocs_by_hash(type, value):
    output.ioc(item)
```

**Never** pass a generator to a singular formatter (`output.ioc(api.iocs_by_hash(...))` raises `'generator' object has no attribute …`), and never `len()` or index one. Single-resource methods (e.g. `report_get`, `sandbox_task_status`, `metadata_mapping`, `*_create`/`*_update`/`*_delete`) return one object — render those directly.

Because the generators are **lazy**, calling one does no I/O and raises nothing until iterated. Code that runs SDK calls through a thread pool must consume the generator **inside the worker** so per-item exception handling fires where it's expected — this is why `utils.parallel_executor_iterable_results` materialises each generator inside the submitted callable (see `01-architecture.md`).

### No-results signalling

A search that the server answers `204 No Content` raises `NoResultsException` from the SDK **when the generator is iterated**. The CLI's `ExceptionHandlingGroup` maps that (and the CLI's own aggregate `NoResultsException` from `parallel_executor`) to exit code `1`. Don't swallow it in command code.

### Execution helpers

For the rare CLI-owned endpoint with no dedicated SDK method (e.g. the inline IP-analysis submit in `Polyswarm.submit_url`), build the request through the client's own helper rather than hand-rolling transport:

```python
return self._single(
    {'method': 'POST', 'url': f'{self.uri}/instance/url', 'params': {...}, 'json': {...}},
    result_parser=resources.ArtifactInstance,
)
```

`_single` builds the request descriptor, executes it via `self.session`, and returns the parsed resource. Do **not** import `PolyswarmRequest` and call `.execute()`/`.result()` — those are not part of the supported surface.

## Coordinated changes (paired PRs)

When a CLI feature needs an SDK surface that doesn't exist yet:

1. Land it in the SDK first (`polyswarm-api` PR, possibly preceded by an `artifact-index` change).
2. Open the CLI PR with a `## Requires` section linking the SDK PR.
3. The CLI PR must not merge until the SDK surface it depends on is on the SDK's `develop` (or released), because **CI installs the SDK from the SDK repo's branch archive** — `.gitlab-ci.yml` does `pip install …/$CI_COMMIT_BRANCH.zip || …/develop.zip`. A CLI branch with no matching SDK branch name falls back to the SDK's `develop` archive, so a CLI change that needs an unreleased SDK surface will fail CI until that surface is on the SDK's `develop` (or you temporarily point the archive ref at the SDK feature branch).

## Version pin

- The pin lives in `pyproject.toml` `dependencies` (`polyswarm_api>=…`). Floor it at the lowest SDK version exposing everything the CLI uses; cap it below the next known-incompatible major when one is anticipated.
- The CLI is **sync-only** — it imports `polyswarm_api.api.PolyswarmAPI`, never `polyswarm_api.aio`. Don't add the `polyswarm_api[async]` extra.
- Bumping the pin is a normal code change; bumping the CLI's *own* version is a release step (`AGENTS.md` §Gitflow). They're unrelated.

## Worked example — the httpx SDK migration

The SDK's move to an `httpx`-based, three-layer architecture (pure-dataclass `PolyswarmRequest`, session-based execution, lazy generators) removed several 3.x affordances the CLI had reached into:

- `PolyswarmRequest(api, dict).execute().result()` → `self._single({...}, result_parser=…)`.
- `ReportTask.download_report(...).result()` → `api.report_download(id, folder)`.
- `output.ioc(api.iocs_by_hash(...))` (singular) → iterate the generator.
- requests' exception names in the error handler → match the `httpx` `HTTPError` root by **ancestry** (MRO class names), so leaf classes never need enumerating.

That migration is the canonical example of this spec's rules: consume generators by iteration, execute through `_single`/`session`, and ship the CLI change paired with the SDK release. (Tracked in the internal tracker; not named here because this repo is public.)
