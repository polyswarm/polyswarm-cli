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
here with no substitute. Both attributes ship in SDK **4.1.0**, well under the dependency floor
(`polyswarm_api>=4.3.0`; see [`05-sdk-contract.md`](./05-sdk-contract.md) §Current floor),
so every supported install has them. `JSONOutput` needs no change — it dumps the resource's
`.json`, which already carries the raw `state` and `known_good` keys.

## Matched strings on hunt results

`TextOutput.historical_result` / `TextOutput.live_result` render `result.matched_strings`
— the yara strings behind a hit — between `Tags:` and `Download Url:`, via the shared
`TextOutput._matched_strings` helper.

The attribute is **three-state** (the SDK's `05-downstream-contract.md` is authoritative)
and the three must stay distinguishable in the output — but they do **not** each get a
line.

| `matched_strings` | Rendered |
|---|---|
| `None` | *nothing* — no line is emitted |
| `[]` | `Matched Strings: none -- the rule matched without byte evidence (a structural or negative match, or private strings)` |
| `[…]` | `Matched Strings:` followed by one indented `  $ident @ 0xOFFSET (N bytes[, truncated]): DATA` line per entry |

**The silent-`None` branch depends on list routes sending `null`, and that is measured
rather than assumed.** If a list route ever returned `[]` per row instead, every row of a
large hunt would carry the loud "matched without byte evidence" line — the permanent
false alarm this design exists to avoid, arriving through the branch deliberately kept
loud. The server pins it for **both** hunt pairs in artifact-index's
`test_list_serializers_never_touch_storage`, which asserts the key is present-and-null on
`ScanResultListSerializer` *and* `LiveResultListSerializer`, against fixture rows that do
carry evidence. This repo cannot verify it; it relies on that test.

Two constraints, both counter-intuitive enough to be worth stating:

- **`None` emits nothing, and `[]` must not follow it into silence.** The instinct is to
  explain the absence. Resist it: `None` overwhelmingly means "this is a list route",
  which *can never* carry strings, so a line there is a permanent false alarm on every
  row rather than information — and `live feed` loops over this same method, with nothing
  on the resource to tell the routes apart (`live_feed` and `live_result` both yield a
  `LiveHuntResult`). Route-awareness would mean threading a flag from the command layer
  into a new parameter on **every** `BaseOutput` implementation (`text`, `json`, all three
  `hashes` subclasses), which buys too little. `[]` is the opposite case and keeps its
  line: it only ever reaches a detail route, and "the rule matched with no byte evidence"
  is a real answer to "why did this hit". Since the analyzer always sends `strings` once
  this feature ships, `None` on a detail route means a result predating it — nothing to
  say.
- **The attribute is defended; the entry keys are not, and that is deliberate.**
  `matched_strings` / `matched_strings_dropped` are read with `getattr(..., None)` because
  the *dependency floor* admits SDKs without them — a version-skew problem. The keys
  *inside* an entry (`identifier`, `offset`, `length`, `data`, `truncated`) are
  subscripted, because a partial entry is not version skew but a producer violating its
  own contract, and rendering half a match as though it were whole is worse than failing.
  The two look inconsistent side by side and are answering different questions.
- **`data` is sanitised before rendering.** It is the only sample-derived field in a hunt
  result, so it is attacker-controlled end to end. yara escapes non-printables upstream
  and the analyzer preserves that rendering, so `_safe_data` is a no-op on valid input —
  it exists because the guarantee lives in another repo, and a raw CSI sequence reaching
  a terminal would repaint or clear an analyst's screen.
- **ASCII only, and true of this whole block.** The literals are ASCII, and both
  server-supplied fields inside the matched-strings block — `data` and `identifier` — go
  through `_safe_data`. Fields *outside* the block (`rule_name`, `tags`) are unfiltered
  and outside this claim. Stdout under a C/POSIX locale replaces non-ASCII with `?`.
- **`truncated` is not a byte count.** The stored length is capped server-side, so the
  marker means "there was more than this" and over-reports at exactly the cap. Never
  render it as an exact size.

**Read with `getattr(result, 'matched_strings', None)`, never a bare attribute access** —
the same defence, for the same reason, as the known-good attributes above. The attribute
ships in the paired SDK release, but the dependency floor admits older SDKs whose
resources lack it entirely, and a bare read would `AttributeError` on *every* text-mode
hunt command, not just the new output: `live result` / `live feed` / `live results-delete`
and the three `historical` equivalents all funnel through these two methods. A missing
attribute degrades to the silent `None` branch, which is also the honest reading — an SDK
that cannot see the field genuinely does not know.

Nothing else can catch this. The rendering tests build resources from the *installed*
SDK, so with a paired SDK on the path a bare read passes every one of them;
`test_an_sdk_without_the_attribute_does_not_raise` deletes the attribute to stand in for
an older SDK, and is the only guard.

### The dropped-count line

When `result.matched_strings_dropped` is non-zero, a final line is appended **inside** the
block, in **yellow** rather than white:

```
  ... 19 more not shown (result size limit)
```

It is the one line here reporting something the platform withheld, which is why it is not
white like the entries above it. Omitted entirely when the count is zero or `None`.

**An empty list with a non-zero count does not claim "no byte evidence".** That
combination should be unreachable — the analyzer keeps a match's first string, so
`[] ⇒ dropped == 0` — but the renderer must not *depend* on an invariant owned by another
repo while making a positive claim about the rule. It reports what is certain instead
(`none shown (N withheld, result size limit)`), because asserting a structural match and
discarding the count is the precise wrong inference this line exists to prevent.

This is not cosmetic. Without it a truncated list reads as the whole truth and a user
concludes their rule hit twice when it hit twenty-one times — the same wrong-inference
class the three-state contract above exists to prevent, one level down. Read with
`getattr(..., None)` for the same SDK-floor reason as `matched_strings` itself.

`JSONOutput` needs no change — it dumps the resource's `.json`, which already carries the
raw `matched_strings` and `matched_strings_dropped` keys.

Coverage is `tests/hunt_matched_strings_test.py` (Style 3 — the formatter driven directly
with constructed SDK resources). The `cli_test.py` cassettes predate the field, so every result they
render takes the silent `None` branch — they pin that no stray line appears, and nothing
more. They are not a substitute for those unit tests.
