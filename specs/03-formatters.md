# polyswarm-cli — Formatters

## Scope

How command output is rendered: the `BaseOutput` interface, the concrete formatters, how `--output-format` selects one, and the per-resource method convention. Files: `src/polyswarm/formatters/base.py`, `text.py`, `json.py`, `hashes.py`, `__init__.py`.

> **Incremental.** The interface and selection mechanism below are stable and authoritative. The exact rendering rules for each resource (field layout, labels, colour) are intentionally **not** transcribed here yet — the concrete formatters are authoritative on that. Document a resource's rendering rules here when they become non-obvious or contested.

## Invariants

- **One method per renderable resource type**, declared on `BaseOutput` and implemented by every concrete formatter. Commands call `output.<resource>(obj)`; they never `print`/`click.echo` an SDK object directly.
- **Adding a renderable resource means adding the method everywhere it's supported** — at minimum `TextOutput` and `JSONOutput`. A missing override inherits `BaseOutput`'s `NotImplementedError`, which surfaces as a bug, not silent omission.
- **Formatters render; they don't fetch or decide flow.** No SDK calls, no business logic — they turn a resource (or an iterable of them) into text/JSON on the configured stream.

## The interface — `base.py`

`BaseOutput(output, **kwargs)` holds the output stream and exposes a method per resource type, each raising `NotImplementedError`. The set includes (non-exhaustive): `artifact_instance`, `historical_result`, `hunt`, `hunt_deletion`, `local_artifact`, `ruleset`, `ioc`, `iocs`, `known_host`, `metadata`, `artifact_metadata`, `tag_link`, `family`, `tag`, `known_good`, `sandbox_list`, `sandbox_task`, `sandbox_tasks`, `bundle_task`, `sample`. Concrete formatters add further methods as command families grow (e.g. `report_task`, `webhook`, `llm_prompt_config`, `metadata_field_properties`); keep `text` and `json` in sync.

## Concrete formatters

| Formatter | Module | Output |
|---|---|---|
| `TextOutput` | `text.py` | Human-readable, labelled blocks; honours `--color/--no-color`. Dates via `polyswarm_api.core.parse_isoformat`. |
| `JSONOutput` | `json.py` | Machine-readable JSON (typically the resource's `.json` plus derived fields). |
| `SHA256Output` / `SHA1Output` / `MD5Output` | `hashes.py` | Hash-only output — prints the relevant digest per result. |

## Selecting a formatter

`formatters/__init__.py` exposes a `formatters` registry keyed by the `--output-format` / `--fmt` value (`text`, `json`, …). `polyswarm_cli` looks up the chosen key, constructs the formatter against `--output-file` (default stdout), and stores it as `ctx.obj['output']`. Hash formatters are selected for hash-only commands as applicable.

## Exit codes

Formatters don't set exit codes — that's `ExceptionHandlingGroup`'s job, by exception type (see [`01-architecture.md`](./01-architecture.md) §exit-code mapping). A formatter rendering "no results" is distinct from the no-results **exit code**, which comes from the SDK/CLI `NoResultsException` path.

## Adding a renderable resource

1. Add `def <resource>(self, result, ...)` to `BaseOutput`.
2. Implement it in `TextOutput` and `JSONOutput` (and the hash formatters if it carries hashes).
3. Match the style of the existing labelled blocks for text output.
4. Call it from the command (`output.<resource>(...)`), iterating if the SDK method returns a generator.

## Known-good artifact instances

`TextOutput.artifact_instance` special-cases a known-good binary, rendering a
**green** "Known Good" signal (a stronger benign signal than "clean") instead of
the misleading "no engines responded — rescan now" a window-closed/no-assertion
instance would otherwise get. It is gated by a single
`is_known_good = (state == 'KNOWN_GOOD') or known_good_sources` flag:

- **`state == 'KNOWN_GOOD'`** (the SDK's `ArtifactInstance.state`, the friendly
  bounty-state name) is the reliable signal — it fires even for a scan-bypassed
  instance that carries **no** feed metadata.
- **`known_good_sources`** (the sorted flagging-feed names, from
  `ArtifactInstance.known_good`) is the richer signal: when present, the
  **Detections** line names the feeds ("…known-good binary (flagged by: …); it is
  not scanned."); otherwise it reads "…is a known-good binary; it is not scanned."
  It also keeps known-good rendering working against an older SDK that has the feed
  list but not `.state`.

The **Status** line reads "Known good" whenever `is_known_good`. Both attributes are
read with `getattr(..., None)` so a CLI on an older SDK (missing either field)
renders exactly as before. `JSONOutput` needs no change — it dumps the resource's
`.json`, which already carries the raw `state` and `known_good` keys.
