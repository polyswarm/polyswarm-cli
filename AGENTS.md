# AGENTS.md — polyswarm-cli

Orientation document for AI agents and humans new to the repo. Update it when major workflow decisions land.

This file points at the right places to read for context, lays out the gitflow / testing / commit conventions, and outlines the CLI's architecture. **Detailed contracts, invariants, and per-area design live under [`specs/`](./specs/)** — read those before changing the corresponding code.

The `specs/` tree is **incremental**: it captures what the CLI has actually defined so far and is augmented as the tool grows. Several specs are seeds today. If a spec is thin or missing for an area you're changing, fill it in **in the same PR** as the code — don't let the code outrun the docs silently.

## Reading order for a new contributor

1. This file (gitflow + conventions + architectural shape).
2. [`specs/00-overview.md`](./specs/00-overview.md) — what the CLI is and how the pieces fit.
3. The spec(s) for the area you're changing — see the [`specs/`](./specs/) index below.
4. The code in `src/polyswarm/` itself; the specs are authoritative on intent, the code on detail.

## Specs index

| Spec | Scope |
|---|---|
| [`specs/00-overview.md`](./specs/00-overview.md) | What this repo ships (the `polyswarm` CLI), where it sits in the platform, repo layout |
| [`specs/01-architecture.md`](./specs/01-architecture.md) | The click app, the `Polyswarm(PolyswarmAPI)` wrapper, `client/` command modules, `formatters/`, `utils.py`, `exceptions.py`, the `ctx.obj` pattern |
| [`specs/02-commands.md`](./specs/02-commands.md) | Command-group catalogue and the SDK methods each wraps *(incremental)* |
| [`specs/03-formatters.md`](./specs/03-formatters.md) | Output rendering: `text`/`json`/`hashes`, the `BaseOutput` interface, exit codes *(incremental)* |
| [`specs/04-testing.md`](./specs/04-testing.md) | `CliRunner` tests, SDK-boundary mocks, the VCR cassette workflow |
| [`specs/05-sdk-contract.md`](./specs/05-sdk-contract.md) | The CLI's dependency on the `polyswarm-api` SDK surface; paired-PR convention; version coupling |
| [`specs/99-open-questions.md`](./specs/99-open-questions.md) | Known follow-ups and unresolved questions |

Specs follow a convention: each opens with **Scope** and **Invariants**, lists the files/symbols it covers, and is independently readable. Update the spec in the same PR as the code change; if a PR drifts from a spec, the spec is wrong until proven otherwise.

## Gitflow — **read this before opening a PR**

This repo follows a strict `feature → develop → master` flow:

```
feature/*  ─┐
            └─► develop  ─►  master
```

**Rules:**

- **Feature PRs target `develop`**, never `master`. Branch off `develop`, push, open a PR with `develop` as the base. CI runs on the PR. Reviewers merge to `develop`.
- **`develop → master` PRs are how `master` advances.** They're opened by a maintainer when a release-worthy batch of work is on `develop`. Most contributors never open one of these.
- **Direct PRs to `master`** are wrong. If you opened one, close it, branch off `develop` instead, and re-open against `develop`.
- **PyPI release happens automatically** when `pyproject.toml`'s `version` changes on `master`. Don't bump the version inside a feature PR unless the maintainer specifically asks — version bumps belong to the `develop → master` step.

**Why this matters:** `master` is the published surface of the CLI. PyPI consumers see whatever shows up there. Skipping `develop` skips the integration soak that protects against accidentally shipping a half-baked change.

### Checking the base before pushing

Before pushing a feature branch, sanity-check what `gh pr create` will target:

```bash
gh pr create --base develop --head <your-branch> --title "<…>" --body "<…>"
```

If you ever omit `--base`, the gh CLI defaults to the repo's default branch — which on this repo is `develop`, but it's worth being explicit.

### Past incident

PR #242 was merged directly to `master` and had to be reverted (#243) and re-opened against `develop`. The version file wasn't touched, so no PyPI release fired — but the rollback was still disruptive. Don't repeat it.

## Architectural shape (the short version)

Detailed treatment is in [`specs/01-architecture.md`](./specs/01-architecture.md). The summary:

`polyswarm-cli` is a thin [`click`](https://click.palletsprojects.com/) front-end over the [`polyswarm-api`](https://github.com/polyswarm/polyswarm-api) SDK. It owns **presentation and orchestration**, not protocol — every HTTP call goes through the SDK.

- **The app** — [`src/polyswarm/client/polyswarm.py`](./src/polyswarm/client/polyswarm.py) defines `polyswarm_cli`, the top-level `click.Group` (an `ExceptionHandlingGroup` that maps exceptions to exit codes). Each command-group module is `add_command`-ed onto it. Entry point: `polyswarm = polyswarm.__main__:polyswarm_cli`.
- **The SDK wrapper** — [`src/polyswarm/polyswarm.py`](./src/polyswarm/polyswarm.py) defines `class Polyswarm(PolyswarmAPI)`. It subclasses the SDK client to add CLI-only conveniences: parallel fan-out over many hashes/ids (`search_hashes`, `download_multiple`, …), multi-step flows (`scan_file`, `submit_url`), and a `parallel` worker count. It reaches into SDK internals **only** through the documented public surface (see `specs/05-sdk-contract.md`).
- **Command modules** — [`src/polyswarm/client/`](./src/polyswarm/client/), one module per command group (`search.py`, `report.py`, `sandbox.py`, …). Each declares a `@click.group` (or commands), pulls `api = ctx.obj['api']` / `output = ctx.obj['output']`, calls SDK methods, and renders via the output formatter.
- **Formatters** — [`src/polyswarm/formatters/`](./src/polyswarm/formatters/): `text.py`, `json.py`, `hashes.py`, all implementing the `base.py` `BaseOutput` interface (one method per resource type). The `--output-format` option picks one.
- **Support** — [`src/polyswarm/utils.py`](./src/polyswarm/utils.py) (parallel executors, hash/id parsing/validation) and [`src/polyswarm/exceptions.py`](./src/polyswarm/exceptions.py) (the CLI's own exception hierarchy, distinct from the SDK's).

The `polyswarm_cli` group seeds `ctx.obj` with a constructed `Polyswarm` client (`api`) and a chosen formatter (`output`); every command reads those two from `ctx.obj`.

## When adding a new command family

Mirror the existing patterns (e.g. `field-property`, `prompt-config`, `ruleset`):

1. **SDK first.** The `polyswarm-api` repo ships the convenience methods (`api.foobar_write`, `api.foobar_get`, …). The CLI just wraps them. SDK changes that need a CLI surface ship as a pair — see `specs/05-sdk-contract.md`.
2. **Group, then subcommands.** For a multi-verb resource, declare `@<parent>.group('resource-name')` (e.g. `@search.group('field-property')`), then attach the verbs (`write`, `get`, `delete`, `list`) to that group. Keeps the command tree shallow and readable. Wire the new group into `polyswarm_cli` in `client/polyswarm.py`.
3. **Formatters.** Add a method named after the resource on both `JSONOutput` (`formatters/json.py`) and `TextOutput` (`formatters/text.py`). Text output should match the style of the existing labelled blocks (`llm_prompt_config`, `webhook`, etc.).
4. **Consume SDK generators correctly.** Paginated/search SDK methods return **generators** — iterate them (`for x in api.foo(): output.foo(x)`); never pass a generator to a singular formatter or call `len()`/index it. See `specs/05-sdk-contract.md`.
5. **Tests.** Use `click.testing.CliRunner` and `mock.patch('polyswarm_api.api.PolyswarmAPI.foobar_*')` to mock at the SDK boundary. See `specs/04-testing.md`.
6. **Update the specs** for the area you touched (at least `02-commands.md`) in the same PR.

## Testing & VCR workflow

Details in [`specs/04-testing.md`](./specs/04-testing.md). The shape:

- Tests live in `tests/` and drive command behaviour through `click.testing.CliRunner` — no live PolySwarm stack needed.
- Two styles for that: **SDK-boundary mocks** (`mock.patch('polyswarm_api.api.PolyswarmAPI.<method>')`, e.g. `tests/field_property_test.py`) and **VCR cassettes** (`tests/cli_test.py`) that replay recorded HTTP for end-to-end CLI runs. Cassettes live in `tests/vcr/` (`.vcr` for the HTTP interactions, `.click` for the expected rendered output).
- Pure rendering logic — which line a given field set produces, no command-tree behaviour — is instead unit-tested against the formatter directly (e.g. `tests/known_good_field_test.py`); see the spec's *Style 3* for when that's the right choice.
- VCR is an **efficiency cache, not a requirement** — the suite must pass against a live e2e stack with VCR off. Re-record a cassette by deleting it and re-running the test against a live stack; never hand-edit a cassette or `cp` one from a sibling test.

## Commit + PR hygiene

- Conventional commit prefixes (`feat:`, `fix:`, `refactor:`, `chore:`, `docs:`, `test:`).
- Small, scoped commits — each one should be independently reviewable.
- **Don't reference ticket IDs or internal project codes in commit messages, PR titles, or PR descriptions.** This repo is public; published artefacts shouldn't leak internal references. Track tickets in the internal tracker, not the git history.
- **Don't name private companion repos in PR descriptions or commit messages on this repo.** Refer to internal services by category, not by repo name.
- No AI-attribution trailers on commits (`Co-Authored-By: Claude …`, "Generated with Claude Code", etc.) — they're noise and they don't belong in project history.
- PRs that depend on an unreleased `polyswarm-api` surface must link the SDK PR under a `## Requires` section (see `specs/05-sdk-contract.md`).

## Companion repos (public)

- `polyswarm-api` — the SDK these commands wrap. SDK changes that need a CLI surface usually ship as a pair (`polyswarm-api` PR + `polyswarm-cli` PR with the SDK PR linked under `## Requires`).
- `artifact-index` — the server-side API the SDK talks to. New endpoints land there first; the SDK PR comes after; the CLI PR comes last.
