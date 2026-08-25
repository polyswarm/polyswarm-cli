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
- There is **no lock file / compiled requirements** to keep in step: `pyproject.toml` is the only place the SDK version is expressed, and CI installs the SDK straight from the SDK repo's branch archive (see §Coordinated changes). A pin change is a one-file change *in this repo*, but it is not free of interactions — see below.
- **The floor must be satisfied by the SDK archive CI installs, and by PyPI.** CI installs the archive build and *then* runs `pip install .[tests]`; if the archive's declared version is below the floor, that second install silently pulls a newer SDK from PyPI **over** the archive build, and CI stops testing the SDK branch at all — the mechanism §Coordinated changes rests on, defeated with no error. Symmetrically, a floor above the newest **published** version breaks `pip install polyswarm-cli` for every consumer the moment it reaches `master`. So a floor bump has two preconditions: the version is on PyPI, and the SDK's `develop` declares at least that version.

  **Read the declared version off the archive's own tree, and mind pre-release suffixes.** PEP 440 orders `4.2.0.dev1 < 4.2.0`, so a `develop` head carrying a dev suffix (the SDK's `pyproject.toml` has a `[tool.bumpversion.parts.dev]`) would *not* satisfy a `>=4.2.0` floor even though it looks like 4.2.0 — and the archive build would be silently replaced from PyPI. Check the version string in the SDK branch's `pyproject.toml` / `__init__.py`, not the last release tag. For the current floor both were read from `origin/develop`: `version = "4.2.0"` and `__version__ = '4.2.0'`, no suffix.

### Current floor — `polyswarm_api>=4.3.0`

`pyproject.toml` floors at **4.3.0**, raised from 4.2.0 by `cdb7926` for the typed
known-good refusal (`KnownGoodWithheldException`, absent in 4.2.0) and the probe fixes.
That commit touched no spec, so the per-behaviour writeup below is still the **4.2.0**
one; it remains accurate about why 4.2.0 was needed, it is simply no longer the binding
constraint. Anyone raising the floor again should extend this section rather than
replace it.

Two behaviours the CLI relies on only exist from **4.2.0**; on 4.1.0 both fail *silently*, which is why the floor is a hard requirement rather than a preference:

1. **`llm_report_create` sends the client's community.** 4.2.0 passes `community=self.community` when it builds the report resource; 4.1.0 omits it. `report llm-create` (`client/report.py`) supplies no community of its own — it relies entirely on the client's — so on 4.1.0 a report requested for a sample in a private community is created without one. No error, wrong resource.
2. **A streaming download answered `204 No Content` raises `NoResultsException`.** The streaming path bypasses `parse_response`, so the 204 has to be raised by the session itself; 4.2.0 does that, 4.1.0 has no such raise anywhere in its session. The CLI's `download` commands depend on it for the no-results **exit code `1`** (§No-results signalling); against 4.1.0 an empty response reads as a successful download and exits `0`.

The known-good rendering attributes (`ArtifactInstance.state`, `.known_good`/`.known_good_sources`, read by `formatters/text.py` — see [`03-formatters.md`](./03-formatters.md) §Known-good artifact instances) ship in **4.1.0**, so they are *not* what sets the floor; they are simply covered by it.

## Worked example — the httpx SDK migration

The SDK's move to an `httpx`-based, three-layer architecture (pure-dataclass `PolyswarmRequest`, session-based execution, lazy generators) removed several 3.x affordances the CLI had reached into:

- `PolyswarmRequest(api, dict).execute().result()` → `self._single({...}, result_parser=…)`.
- `ReportTask.download_report(...).result()` → `api.report_download(id, folder)`.
- `output.ioc(api.iocs_by_hash(...))` (singular) → iterate the generator.
- requests' exception names in the error handler → match the `httpx` `HTTPError` root by **ancestry** (MRO class names), so leaf classes never need enumerating.

That migration is the canonical example of this spec's rules: consume generators by iteration, execute through `_single`/`session`, and ship the CLI change paired with the SDK release. (Tracked in the internal tracker; not named here because this repo is public.)
