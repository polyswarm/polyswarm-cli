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
| `TextOutput` | `text.py` | Human-readable, labelled blocks; honours `--color/--no-color` through `_paint`, the single place `self.color` is read. The five `_white`/`_red`/… helpers all route through it — a convention, not an enforcement point: a new helper calling `click.style` directly would re-break the flag, so add colours by adding a `_paint` caller. Dates via `polyswarm_api.core.parse_isoformat`. |
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
`is_known_good = (state == 'KNOWN_GOOD')` flag:

- **`state == 'KNOWN_GOOD'`** (the SDK's `ArtifactInstance.state`, the friendly
  bounty-state name) is **the** signal, and the only one — it is the server's single
  reliable statement that this artifact is known-good and its bytes are withheld, and
  it fires even for a scan-bypassed instance that carries **no** feed metadata. There
  is deliberately no separate "bytes withheld" field to consult.

**The wire dependency, and where it is actually pinned.** `state` is load-bearing with no
fallback, and a Style-3 test cannot see the transport boundary — it compares against a dict the
test wrote itself. So the key and the label were **read off the server's serializer**, not
inferred: `ArtifactInstanceSerializer` emits `'state': instance.state.name`, and
`BountyState.KNOWN_GOOD.name` is the exact string `'KNOWN_GOOD'`. What would catch a *future*
rename is the server's own suite (which asserts that field and the `/v3/sample` status), not a
cassette here: this repo's CI replays frozen recordings with no VCR-off e2e job, so a recorded
body would keep replaying the old shape after a rename. If a live-e2e job is ever added here, a
`cli_test.py` cassette over a known-good hash becomes the right place to pin it.
- **`known_good_sources`** (the sorted flagging-feed names, from
  `ArtifactInstance.known_good`) only **shapes the message** for an instance already
  known-good by state: when present, the **Detections** line names the feeds
  ("…known-good binary (flagged by: …); it is not scanned."); otherwise it reads
  "…is a known-good binary; it is not scanned." It must **never** decide
  known-goodness — the server emits the feed list for *any* instance whose sha256
  matches a known-good record, including a fully scanned one with real
  detections/PolyScore, so treating it as the signal would render a scanned artifact
  as "known-good … not scanned". It is therefore read as `[]` unless `is_known_good` —
  a statement of that coupling, not a guard: the list is only ever read inside the
  known-good branch, so the ternary can't change what renders today. Keep it, and keep
  reading the feeds through it if a second call site ever appears.

### A known-good instance that also carries results

Known-goodness and collected results are **not** mutually exclusive. An instance that was
scanned before its artifact was catalogued gets reconciled to `KNOWN_GOOD` with its
assertions, detections and PolyScore deliberately preserved, so that pairing is something
a client really receives — the rendering must state both facts without claiming the
artifact was never scanned. The trailing clause of the known-good **Detections** line
therefore switches on `instance.valid_assertions`:

- **no valid assertions** → "…is a known-good binary; it is not scanned." — the withheld,
  never-scanned case.
- **valid assertions, window closed** → "…is a known-good binary; N/M engines reported
  malicious." — the same count the ordinary window-closed branch renders, folded into the
  known-good sentence.
- **valid assertions, window still open** → "…is a known-good binary; its scan has not
  finished running yet." Every other **Detections** branch guards its counts on
  `window_closed`, because an open window's numbers are not final. Unreachable through the
  server's reconciliation — verified against its `RECONCILABLE_STATES`, which is `STORED`
  (a row that was never submitted, so it carries no assertions) plus `SETTLED` **and only
  when `window_closed`**; the ingest gate's own path sets `window_closed = True`. So this is
  a guard against a future state rather than a case seen in practice, stated here so the
  parity with the other branches reads as intentional. If a reconciled row ever *can* carry
  an open window alongside preserved malicious assertions, redden on `malicious_assertions`
  alone and keep only the *text* guarded on the window — the sentence would still be
  accurate, and green on a malicious detection is the mis-signal this rule exists to fix.

The flagging-feed attribution ("(flagged by: …)") is orthogonal and applies to all three. In
every branch the per-engine verdict list, the PolyScore line and "Status: Known good"
render as usual; the switch exists so "it is not scanned" is never printed directly above a
list of engine verdicts.

**Colour: any malicious verdict outranks the withheld-bytes signal.** The line is **green**
except on the *count* branch (valid assertions, window closed) when at least one of them is
malicious, where it is **red** — the same threshold and the same colour the ordinary branch
applies to that same count (1/50 reddens there too). The clause and its colour are chosen in
the **same** `if`/`elif`, not by a second condition: written separately they had to agree by
coincidence, and only the SDK's guarantee that `malicious_assertions ⊆ valid_assertions` (both
filter on `mask`) kept them in step — a fact about another repo propping up this rendering. Known-goodness is the
dominant *fact*, but it is not a stronger *warning*: rendering "40/50 engines reported
malicious" in green would be a weaker signal than the very same instance produced before it
was reconciled, which is the class of mis-signal this rendering exists to fix. "Status: Known
good" stays green in both cases — it labels the catalogue status (the counterpart of "Status:
Assertion window closed"), not the verdict. The colour decision is invisible to a test that unstyles its
output, so it is pinned against the **styled** render — `TextOutput(color=True)` read without
`click.unstyle`, which is what `_render_styled` in `known_good_field_test.py` exists for (both
halves matter: the flag makes it paint, the missing `unstyle` keeps the codes). Whether the
`--color/--no-color` **flag** reaches that rendering at all is a separate question a formatter
unit test cannot answer; `test_color_flag_reaches_the_text_formatter` (`cli_test.py`) covers it
through `CliRunner(… color=True)`.

**Scope of `--no-color`.** It governs the text formatter (via `_paint`), `PrettyJSONOutput`
(whose `_to_json` skips the pygments `ClickFormatter` when the flag is off — plain `JSONOutput`
emits unstyled JSON and has nothing to honour), and the log prefix
(`setup_logging(verbosity, color=…)` — the `NamedColorFormatter` used to style unconditionally,
so `polyswarm --no-color -v …` still emitted a green prefix on a tty). It does not attempt to
suppress colour inside third-party output.

The **Status** line reads "Known good" whenever `is_known_good`, except on a **failed**
instance — "Status: Failed" is ordered first and the known-good **Detections** branch is
gated on `not instance.failed`, so a failure is reported as a failure and never as
"…it is not scanned".

Both attributes are read with `getattr(..., None)` so a CLI on an older SDK (missing
either field) never raises `AttributeError`; an SDK without `.state` simply never takes
the known-good branch, which is the safe fallback — the pre-known-good rendering. That
degradation is belt-and-braces, not a supported configuration: `.state` is load-bearing
here with no substitute. Both attributes ship in SDK **4.1.0**, but the dependency floor is
`polyswarm_api>=4.4.0` — the pin's current value (moved there by the hunt-page change
set; 4.3.0 before it, by the #264 release bump); its *rationale* is two behaviours that landed in 4.2.0 and still hold
transitively, and [05-sdk-contract.md](./05-sdk-contract.md) §Current floor is
authoritative. Those two
fail silently on 4.1.0 (see [`05-sdk-contract.md`](./05-sdk-contract.md) §Version pin) — so
every supported install has them. `JSONOutput` needs no change — it dumps the resource's
`.json`, which already carries the raw `state` and `known_good` keys.

## Hunt-page tracking fields (rulesets + historical hunts)

Rendering rules that are deliberate, not incidental. Every one of these fields is
parsed by the pinned SDK, so the attribute always exists and `None` means the
**server** had no answer — never an older SDK (the floor forbids one; see
[`05-sdk-contract.md`](./05-sdk-contract.md) §Current floor). The formatters read
the attributes directly:

- `rule_count` / `historical_hunt_count`: `0` renders as a real zero;
  `None` (the server had no answer) omits the line — never shown as 0.
- `favorite` is truthy-only ("Favorite: yes"): False and None both print
  nothing, deliberately indistinguishable.
- `new_results_count` is the server's STORED badge (refreshed by its
  scheduled job — the window is the fixed 24 h product window, which the
  label names, since a caller cannot choose it): a number renders with its
  `new_results_counted_at` staleness marker beside it; `None` (never
  refreshed / no live hunt) omits both lines.
- `ruleset_favorite` renders the toggle response: `Favorite: yes/no`, the
  `favorited_at` timestamp when starred, and the server-owned budget as
  "Favorites used: N of M" — the client never counts.
- `source_rule_changed` is tri-state: `None` means UNKNOWN, not "unchanged",
  and prints nothing; the label names its reference point — "changed since
  this hunt froze it" — so it cannot read as "edited recently".
