# AGENTS.md — polyswarm-cli

Orientation document for AI agents and humans new to the repo. Update it when major workflow decisions land.

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

## Layout

- `src/polyswarm/polyswarm.py` — the top-level click app definition.
- `src/polyswarm/client/` — one module per command group (`search.py`, `report.py`, `engine.py`, …). Each registers its click commands against a `@click.group` and is wired into the top-level app in `polyswarm.py`.
- `src/polyswarm/formatters/` — output renderers: `text.py`, `json.py`, `hashes.py`, `base.py`. Each command's output goes through one of these; add a method per new resource type.
- `tests/` — `CliRunner` tests with SDK methods mocked at the boundary; no live polyswarm stack needed.

## When adding a new resource family of commands

Mirror the existing patterns (e.g. `field-property`, `prompt-config`, `ruleset`):

1. **SDK first.** The `polyswarm-api` repo ships the convenience methods (`api.foobar_write`, `api.foobar_get`, …). The CLI just wraps them.
2. **Group, then subcommands.** For a multi-verb resource, declare `@<parent>.group('resource-name')` (e.g. `@search.group('field-property')`), then attach the verbs (`write`, `get`, `delete`, `list`) to that group. Keeps the command tree shallow and readable.
3. **Formatters.** Add a method named after the resource on both `JSONOutput` (`formatters/json.py`) and `TextOutput` (`formatters/text.py`). Text output should match the style of the existing labelled blocks (`llm_prompt_config`, `webhook`, etc.).
4. **Tests.** Use `click.testing.CliRunner` and `mock.patch('polyswarm_api.api.PolyswarmAPI.foobar_*')` to mock at the SDK boundary. No live stack, no VCR.

## Companion repos

- `polyswarm-api` — the SDK these commands wrap. SDK changes that need a CLI surface usually ship as a pair (`polyswarm-api` PR + `polyswarm-cli` PR with the SDK PR linked under `## Requires`).
- `artifact-index` — the server-side API the SDK talks to. New endpoints land there first; the SDK PR comes after; the CLI PR comes last.
