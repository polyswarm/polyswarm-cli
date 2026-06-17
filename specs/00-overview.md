# polyswarm-cli — Overview

## Scope

What the `polyswarm` CLI is, what it ships, where it sits in the platform, and how the repository is laid out. Subsequent specs zoom in on a single area; this one is the map.

## Invariants

- **The CLI is a client of the SDK.** It performs no HTTP itself — every network call goes through the [`polyswarm-api`](https://github.com/polyswarm/polyswarm-api) SDK (`PolyswarmAPI`). Protocol concerns (request/response shapes, auth, retries, pagination, transport) live in the SDK, not here.
- **The product is the CLI, not a library.** The published surface is the `polyswarm` console script and its command tree. The `polyswarm` Python package is importable but isn't a supported API for third parties.
- **`master` is the release branch.** A version bump on `master` triggers a PyPI release. Feature PRs always target `develop` (see `AGENTS.md` §Gitflow).
- **Presentation + orchestration only.** The CLI's job is parsing arguments, fanning work out in parallel, calling SDK methods, and rendering results in the chosen format. Business logic and the wire contract belong to the SDK and the server.

## What this repo ships

| Artefact | Description |
|---|---|
| `polyswarm` console script | The CLI. Entry point `polyswarm.__main__:polyswarm_cli` (declared in `pyproject.toml` `[project.scripts]`). |
| `polyswarm` Python package | `src/polyswarm/` — the click app, the SDK wrapper, command modules, formatters, helpers. Importable, but the CLI is the product. |

## Where it sits

```
   ┌─────────────────────┐
   │   end user / CI     │   `polyswarm search hash …`, `polyswarm report create …`
   └──────────┬──────────┘
              │ argv
              ▼
   ┌─────────────────────┐
   │  polyswarm-cli (this)│  click commands → SDK calls → formatted output.
   │  polyswarm_cli group │  Presentation + orchestration (parallel fan-out).
   └──────────┬──────────┘
              │ PolyswarmAPI (sync)
              ▼
   ┌─────────────────────┐
   │   polyswarm-api      │  The SDK. Owns HTTP, auth, retries, pagination,
   │   PolyswarmAPI       │  request/response parsing.
   └──────────┬──────────┘
              │ httpx
              ▼
   ┌─────────────────────┐
   │   artifact-index     │  The server-side REST API.
   └─────────────────────┘
```

A change that needs a new server capability lands in `artifact-index` first, then `polyswarm-api` (SDK method + resource), then `polyswarm-cli` (the command that wraps it). See [`05-sdk-contract.md`](./05-sdk-contract.md).

## Repo layout

```
src/polyswarm/
├── __main__.py            ← console-script entry; calls polyswarm_cli(prog_name=…, obj={})
├── polyswarm.py           ← class Polyswarm(PolyswarmAPI): the SDK wrapper subclass
│                            (parallel fan-out + multi-step flows)
├── client/                ← one module per command group, plus the app definition
│   ├── polyswarm.py        ← polyswarm_cli (top-level group, ExceptionHandlingGroup),
│   │                         global options, ctx.obj seeding, add_command wiring
│   ├── search.py / report.py / sandbox.py / engine.py / live.py / historical.py /
│   │   download.py / metadata.py / tags.py / links.py / families.py / rules.py /
│   │   report_template.py / notification_webhook.py / notification.py / account.py /
│   │   event.py / bundle.py / sample.py / scan.py
│   └── utils.py            ← click-facing helpers (validate_key, validate_id, parse_hashes,
│                             any_provided decorator)
├── formatters/            ← output renderers
│   ├── base.py             ← BaseOutput (the interface; one method per resource type)
│   ├── text.py / json.py / hashes.py
│   └── __init__.py         ← `formatters` registry keyed by --output-format
├── utils.py               ← parallel executors + hash/IP/id parsing & validation
└── exceptions.py          ← CLI-side exception hierarchy (distinct from the SDK's)

specs/                     ← this directory (incremental; see AGENTS.md)
tests/                     ← CliRunner tests + VCR cassettes (tests/vcr/*.{vcr,click})
.github/workflows/         ← claude-code-review.yml (PR auto-review)
.gitlab-ci.yml             ← test (py310/311/312) + dev/release PyPI
```

## Version & release

- The CLI's own version lives in `pyproject.toml` `version` + `[tool.bumpversion]`, mirrored into `src/polyswarm/__init__.py`. It is **independent of the SDK version**.
- Don't bump it in a feature PR — version bumps belong to the `develop → master` release step (`AGENTS.md` §Gitflow). A version change on `master` fires the PyPI release.
- The dependency on the SDK is a pin in `pyproject.toml` (`polyswarm_api>=…`); see [`05-sdk-contract.md`](./05-sdk-contract.md) for the coupling rules.
