# Open Questions

## Scope

Known follow-ups and areas the `specs/` tree hasn't fully defined yet. This is the parking lot — each item is something a future PR will flesh out. Move an item out (into the relevant spec) once it's resolved. The specs are deliberately **incremental**; this file tracks where they're still seeds.

## Command catalogue — per-subcommand detail

**Status:** seed.

[`02-commands.md`](./02-commands.md) maps each group to the SDK area it wraps, but doesn't enumerate per-subcommand arguments/options/behaviour. **Action:** as each command family is revised, document its non-obvious subcommands (flags, defaults, multi-arg fan-out semantics) in `02-commands.md`. The code is authoritative until then.

## Formatter rendering rules

**Status:** seed.

[`03-formatters.md`](./03-formatters.md) documents the interface and selection, not the field-level rendering of each resource. **Action:** when a resource's text/JSON layout becomes contested or non-obvious, capture the intended layout there (so the reviewer can catch drift).

## "VCR-off against live e2e" CI job

**Status:** not implemented.

The invariant in [`04-testing.md`](./04-testing.md) says the suite must pass against a live e2e stack with VCR off, but no CI job exercises that today (CI runs the cassette-backed suite). **Action:** decide whether to add a periodic VCR-off job and where it points.

## SDK ↔ CLI version-coupling automation

**Status:** manual.

The SDK pin and the paired-PR `## Requires` convention ([`05-sdk-contract.md`](./05-sdk-contract.md)) are enforced by humans/review today. CI installs the SDK from the SDK repo's branch archive (`$CI_COMMIT_BRANCH.zip || develop.zip`), so a CLI change that needs an unreleased SDK surface fails until that surface is on the SDK's `develop`. **Action:** decide whether to make the coupling explicit (e.g. an env-overridable SDK ref for testing a CLI change against an SDK feature branch before it merges) rather than relying on the `develop.zip` fallback.

## Wrapper vs. SDK boundary for orchestration

**Status:** open.

The `Polyswarm(PolyswarmAPI)` wrapper holds CLI-only orchestration (parallel fan-out, multi-step flows). Some of it (e.g. `submit_url`'s inline `/instance/url` endpoint) arguably belongs in the SDK so the CLI is a pure wrapper. **Action:** as the SDK grows methods that subsume wrapper logic, migrate the wrapper to call them and shrink the CLI-owned surface.
