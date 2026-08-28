# polyswarm-cli — Command catalogue

## Scope

The top-level command groups, what each is for, and the primary `polyswarm-api` SDK methods each wraps. Files: `src/polyswarm/client/*.py`, wired into `polyswarm_cli` in `src/polyswarm/client/polyswarm.py`.

> **Incremental.** This is a catalogue seed: it maps each group to the SDK surface it sits on, which is what an automated reviewer needs to judge spec drift. Per-subcommand argument/option detail is intentionally **not** enumerated here yet — add a group's detail when you change it. Treat the code as authoritative on exact flags; treat this table as authoritative on "which group wraps which SDK area."

## Invariants

- **Every group is `add_command`-ed onto `polyswarm_cli`** in `client/polyswarm.py`. A new group isn't reachable until it's wired there.
- **A command wraps SDK methods; it doesn't reimplement them.** If a command needs logic the SDK doesn't expose, the logic belongs in the SDK (or, for CLI-only orchestration like parallel fan-out, in the `Polyswarm` wrapper) — not inline in the command.
- **Collection-returning SDK methods are generators** — commands iterate them (see [`05-sdk-contract.md`](./05-sdk-contract.md)).

## Catalogue

| Group / commands (module) | Purpose | Primary SDK methods wrapped |
|---|---|---|
| `search` (`search.py`) | Search by hash / URL / metadata / IOC / scans; metadata mapping; `field-property` subgroup | `search_hashes`, `search_urls`, `search_by_metadata`, `search_by_ioc`, `iocs_by_hash`, `search_scans`, `metadata_mapping`, `metadata_field_properties_{write,get,delete,list}` |
| `known` + `search known` (`search.py`) | Manage / check known-good/-bad hosts | `add_known_good_host`, `add_known_bad_host`, `update_known_good_host`, `delete_known_good_host`, `check_known_hosts` |
| `kgb` (`kgb.py`) | Known Good **Binaries** — internal-only CRUD on a sha256-keyed known-good record (`create` / `get` / `delete`, no update). Distinct from `known`, which manages known-good/-bad *hosts*. | `known_good_create`, `known_good_get`, `known_good_delete` |
| `scan`, `lookup`, `wait`, `rescan`, `rescan-id` (`scan.py`) | Submit files/dirs and await results; look up / rescan existing scans | `scan_file`, `scan_lookup`, `wait_for`, `rescan`, `rescan_id` (wrapper methods over `submit`/`lookup`/`rescan`/`rescan_id`) |
| `sandbox`, `sandbox-list` (`sandbox.py`) | Detonate artifacts/URLs in a sandbox; query sandbox tasks/providers | `sandbox_instances` (→ `sandbox`), `sandbox_file`, `sandbox_url`, `sandbox_providers`, `sandbox_task_status`, `sandbox_task_latest`, `sandbox_task_list`, `sandbox_my_tasks_list` |
| `download`, `cat`, `stream`, `download-id`, `download-sandbox-artifact` (`download.py`) | Download artifacts by hash/id, stream the feed, fetch sandbox artifacts | `download_multiple`, `download_id_multiple`, `download_stream`, `download`, `download_id`, `download_archive`, `stream` |
| `report` (`report.py`) | Create/fetch/download reports; `prompt-config` subgroup; LLM reports | `report_create`, `report_wait_for`, `report_download`, `report_get`, `llm_report_{create,get,download}`, `prompt_config_{create,get,update,list}` |
| `report-template` (`report_template.py`) | Manage report templates + logos | `report_template_{create,update,get,list}`, `report_template_logo_{download,upload}` |
| `engine` → `votes` / `assertions` (`engine.py`) | Consolidated votes/assertions bundles per engine | `votes_{create,get,delete,list}`, `assertions_{create,get,delete,list}` |
| `live` (`live.py`) | Live YARA hunts: start/stop, feed, results. `feed` takes `--since` in **MINUTES** (default 1440 — 24h, the window the ruleset badge counts; `0` means no time filter at all), plus `--livescan-id` (the drill-down for the per-ruleset new-results badge `rules list` renders — the detail view deliberately does not carry it) and `--max-results` (stop after N; unset means every page, as before). Those two need the paired SDK and are forwarded only when passed, so every pre-existing invocation is unchanged on the pin's floor — see [05-sdk-contract.md](./05-sdk-contract.md) §Current floor | `live_start`, `live_stop`, `live_feed`, `live_result`, `live_feed_delete` |
> **The two hunt `--since` options differ in unit, deliberately.** `live feed --since` is MINUTES; `historical list --since` is SECONDS. They are different endpoints and the server reads each accordingly (`timedelta(minutes=...)` for the live feed, `timedelta(seconds=...)` for historical). The live feed's unit was corrected because every surface around it — its own default of 1440, the ruleset badge's 24h window — was written for minutes; the historical endpoint was left alone because nothing there disagrees. This is recorded so the remaining `seconds` is not read as a missed rename.

| `historical` (`historical.py`) | Historical hunts: CRUD + results | `historical_{get,create,update,list}`, `historical_delete_multiple`, `historical_delete_list`, `historical_results_multiple`, `historical_result`, `historical_results_delete` |
| `tag` (`tags.py`) | Tag CRUD | `tag_{create,delete,get,list}` |
| `link` (`links.py`) | Tag/family links on artifacts | `tag_link_multiple`, `tag_link_get`, `tag_link_list` |
| `family` (`families.py`) | Malware-family CRUD | `family_{create,update,delete,get,list}` |
| `rules` (`rules.py`) | YARA ruleset CRUD plus `favorite <id> [--unfavorite]` (the star toggle: renders the new state + the server-owned "N of M used" budget, and converts the machine-readable `FAVORITE_LIMIT` refusal into a clean actionable message at exit 2, never 1 — 1 is reserved for no-results/not-found; 2 is the broad bucket `ExceptionHandlingGroup` maps the PolyswarmException hierarchies to). `list` takes the server-side filters `--name` / `--status active` / `--favorites-only` / `--has-new-results` (conjunctive; the list is keyset-paginated, so filtering locally would mean walking every page). Every pre-existing INVOCATION works unchanged on the pin's floor: an unfiltered `rules list` still calls a zero-argument `ruleset_list()`, and the hunt-page fields arrive as plain response fields the formatters getattr-guard. What needs the paired SDK is `rules favorite` and the new `rules list` filters; each degrades to a clean upgrade message on the floor (see [05-sdk-contract.md](./05-sdk-contract.md) §Current floor) | `ruleset_{create,delete,update,get,list,favorite}` |
| `metadata` (`metadata.py`) | Rerun metadata; scan lookup; IP/URL analysis | `rerun_metadata`, `scan_lookup`, `submit_url` |
| `activity` (`event.py`) | List account activity/events | `event_list` |
| `account` (`account.py`) | Account whois / features | `account_whois`, `account_features` |
| `notification` / webhooks (`notification.py`, `notification_webhook.py`) | Notification webhook CRUD | `notification_webhook_{create,get,update,delete,list}` |
| `bundle` (`bundle.py`) | Sample bundle tasks | `sample_bundle_task_create`, `sample_bundle_task_get`, `sample_bundle_download` |
| `sample` (`sample.py`) | Fetch a consolidated sample view | `sample` |

## Adding to the catalogue

When you add or materially change a group, update its row (and add per-subcommand detail here if the behaviour is non-obvious). The `AGENTS.md` §"When adding a new command family" checklist covers the wiring + formatter + test steps.
