# AI Agent Assembly

[![Core CI](https://github.com/ai-agent-assembly/agent-assembly/actions/workflows/ci.yml/badge.svg)](https://github.com/ai-agent-assembly/agent-assembly/actions/workflows/ci.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Core release](https://img.shields.io/github/v/release/ai-agent-assembly/agent-assembly?include_prereleases&sort=semver)](https://github.com/ai-agent-assembly/agent-assembly/releases)
[![Discussions](https://img.shields.io/badge/community-Discussions-blue?logo=github)](https://github.com/ai-agent-assembly/agent-assembly/discussions)

AI Agent Assembly is an open-source governance platform for AI agents. It enforces policy, tracks budget, and audits every action your agents take across three independent interception layers — in-process SDKs, a sidecar proxy, and eBPF kernel hooks — so you can ship multi-agent fleets without losing control of what they do.

## Developer Start Here

### Repository Status

<!-- BEGIN GENERATED: repo_table -->
| Repo | Purpose | Version | Base branch health | Activity |
| --- | --- | --- | --- | --- |
| [![agent-assembly](https://img.shields.io/badge/agent--assembly-core-000000?logo=rust)](https://github.com/ai-agent-assembly/agent-assembly) | Core Rust monorepo: gateway, policy engine, CLI, API, dashboard | [![GitHub tag](https://img.shields.io/github/v/tag/ai-agent-assembly/agent-assembly?label=GitHub&logo=github)](https://github.com/ai-agent-assembly/agent-assembly/tags) [![crates.io](https://img.shields.io/badge/crates.io-reference-000000?logo=rust)](https://crates.io/search?q=agent-assembly) | [![CI](https://github.com/ai-agent-assembly/agent-assembly/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ai-agent-assembly/agent-assembly/actions/workflows/ci.yml?query=branch%3Amain) | [![issues](https://img.shields.io/github/issues/ai-agent-assembly/agent-assembly?label=issues)](https://github.com/ai-agent-assembly/agent-assembly/issues) [![PRs](https://img.shields.io/github/issues-pr/ai-agent-assembly/agent-assembly?label=PRs)](https://github.com/ai-agent-assembly/agent-assembly/pulls) [![last commit](https://img.shields.io/github/last-commit/ai-agent-assembly/agent-assembly?label=last)](https://github.com/ai-agent-assembly/agent-assembly/commits/main) |
| [![python-sdk](https://img.shields.io/badge/python--sdk-SDK-3776AB?logo=python&logoColor=white)](https://github.com/ai-agent-assembly/python-sdk) | Python SDK (PyO3 native + pure-Python client) | [![GitHub release](https://img.shields.io/github/v/release/ai-agent-assembly/python-sdk?include_prereleases&sort=semver&label=GitHub&logo=github)](https://github.com/ai-agent-assembly/python-sdk/releases) [![PyPI](https://img.shields.io/pypi/v/agent-assembly?label=PyPI&logo=pypi&logoColor=white)](https://pypi.org/project/agent-assembly/) | [![CI](https://github.com/ai-agent-assembly/python-sdk/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/ai-agent-assembly/python-sdk/actions/workflows/ci.yaml?query=branch%3Amain) | [![issues](https://img.shields.io/github/issues/ai-agent-assembly/python-sdk?label=issues)](https://github.com/ai-agent-assembly/python-sdk/issues) [![PRs](https://img.shields.io/github/issues-pr/ai-agent-assembly/python-sdk?label=PRs)](https://github.com/ai-agent-assembly/python-sdk/pulls) [![last commit](https://img.shields.io/github/last-commit/ai-agent-assembly/python-sdk?label=last)](https://github.com/ai-agent-assembly/python-sdk/commits/main) |
| [![node-sdk](https://img.shields.io/badge/node--sdk-SDK-339933?logo=node.js&logoColor=white)](https://github.com/ai-agent-assembly/node-sdk) | TypeScript SDK (napi-rs native + JS client) | [![GitHub release](https://img.shields.io/github/v/release/ai-agent-assembly/node-sdk?include_prereleases&sort=semver&label=GitHub&logo=github)](https://github.com/ai-agent-assembly/node-sdk/releases) [![npm](https://img.shields.io/npm/v/%40agent-assembly%2Fsdk/beta?label=npm&logo=npm&logoColor=white)](https://www.npmjs.com/package/@agent-assembly/sdk) | [![Tests](https://github.com/ai-agent-assembly/node-sdk/actions/workflows/test-matrix.yml/badge.svg?branch=main)](https://github.com/ai-agent-assembly/node-sdk/actions/workflows/test-matrix.yml?query=branch%3Amain) | [![issues](https://img.shields.io/github/issues/ai-agent-assembly/node-sdk?label=issues)](https://github.com/ai-agent-assembly/node-sdk/issues) [![PRs](https://img.shields.io/github/issues-pr/ai-agent-assembly/node-sdk?label=PRs)](https://github.com/ai-agent-assembly/node-sdk/pulls) [![last commit](https://img.shields.io/github/last-commit/ai-agent-assembly/node-sdk?label=last)](https://github.com/ai-agent-assembly/node-sdk/commits/main) |
| [![go-sdk](https://img.shields.io/badge/go--sdk-SDK-00ADD8?logo=go&logoColor=white)](https://github.com/ai-agent-assembly/go-sdk) | Go SDK | [![GitHub tag](https://img.shields.io/github/v/tag/ai-agent-assembly/go-sdk?sort=semver&label=GitHub&logo=github)](https://github.com/ai-agent-assembly/go-sdk/tags) [![Go Reference](https://pkg.go.dev/badge/github.com/ai-agent-assembly/go-sdk.svg)](https://pkg.go.dev/github.com/ai-agent-assembly/go-sdk) | [![Go test](https://github.com/ai-agent-assembly/go-sdk/actions/workflows/go-test.yml/badge.svg?branch=main)](https://github.com/ai-agent-assembly/go-sdk/actions/workflows/go-test.yml?query=branch%3Amain) | [![issues](https://img.shields.io/github/issues/ai-agent-assembly/go-sdk?label=issues)](https://github.com/ai-agent-assembly/go-sdk/issues) [![PRs](https://img.shields.io/github/issues-pr/ai-agent-assembly/go-sdk?label=PRs)](https://github.com/ai-agent-assembly/go-sdk/pulls) [![last commit](https://img.shields.io/github/last-commit/ai-agent-assembly/go-sdk?label=last)](https://github.com/ai-agent-assembly/go-sdk/commits/main) |
| [![.github](https://img.shields.io/badge/.github-org--profile-181717?logo=github)](https://github.com/ai-agent-assembly/.github) | Organization profile, templates, support, and community files | — | | [![issues](https://img.shields.io/github/issues/ai-agent-assembly/.github?label=issues)](https://github.com/ai-agent-assembly/.github/issues) [![PRs](https://img.shields.io/github/issues-pr/ai-agent-assembly/.github?label=PRs)](https://github.com/ai-agent-assembly/.github/pulls) [![last commit](https://img.shields.io/github/last-commit/ai-agent-assembly/.github?label=last)](https://github.com/ai-agent-assembly/.github/commits/main) |
| [![homebrew-tap](https://img.shields.io/badge/homebrew--tap-tap-FBB040?logo=homebrew&logoColor=black)](https://github.com/ai-agent-assembly/homebrew-tap) | Homebrew tap for `aasm` | [![formula](https://img.shields.io/github/v/release/ai-agent-assembly/agent-assembly?include_prereleases&sort=semver&label=formula&logo=homebrew)](https://github.com/ai-agent-assembly/homebrew-tap/blob/main/Formula/aasm.rb) [![Homebrew](https://img.shields.io/badge/brew-ai--agent--assembly%2Ftap%2Faasm-FBB040?logo=homebrew)](https://github.com/ai-agent-assembly/homebrew-tap) | | [![issues](https://img.shields.io/github/issues/ai-agent-assembly/homebrew-tap?label=issues)](https://github.com/ai-agent-assembly/homebrew-tap/issues) [![PRs](https://img.shields.io/github/issues-pr/ai-agent-assembly/homebrew-tap?label=PRs)](https://github.com/ai-agent-assembly/homebrew-tap/pulls) [![last commit](https://img.shields.io/github/last-commit/ai-agent-assembly/homebrew-tap?label=last)](https://github.com/ai-agent-assembly/homebrew-tap/commits/main) |
| [![docs](https://img.shields.io/badge/docs-docs-4051B5?logo=materialformkdocs&logoColor=white)](https://github.com/ai-agent-assembly/docs) | Public documentation site | [![tracks](https://img.shields.io/github/v/release/ai-agent-assembly/agent-assembly?include_prereleases&sort=semver&label=tracks&logo=github)](https://github.com/ai-agent-assembly/agent-assembly/releases) | [![Deploy](https://github.com/ai-agent-assembly/docs/actions/workflows/aggregate.yml/badge.svg?branch=main)](https://github.com/ai-agent-assembly/docs/actions/workflows/aggregate.yml?query=branch%3Amain) | [![issues](https://img.shields.io/github/issues/ai-agent-assembly/docs?label=issues)](https://github.com/ai-agent-assembly/docs/issues) [![PRs](https://img.shields.io/github/issues-pr/ai-agent-assembly/docs?label=PRs)](https://github.com/ai-agent-assembly/docs/pulls) [![last commit](https://img.shields.io/github/last-commit/ai-agent-assembly/docs?label=last)](https://github.com/ai-agent-assembly/docs/commits/main) |
| [![agent-assembly-spec](https://img.shields.io/badge/agent--assembly--spec-spec-6E40C9?logo=openapiinitiative&logoColor=white)](https://github.com/ai-agent-assembly/agent-assembly-spec) | Shared specifications and protocol contracts | [![reserved](https://img.shields.io/badge/status-reserved-lightgrey)](https://github.com/ai-agent-assembly/agent-assembly-spec) | | [![issues](https://img.shields.io/github/issues/ai-agent-assembly/agent-assembly-spec?label=issues)](https://github.com/ai-agent-assembly/agent-assembly-spec/issues) [![PRs](https://img.shields.io/github/issues-pr/ai-agent-assembly/agent-assembly-spec?label=PRs)](https://github.com/ai-agent-assembly/agent-assembly-spec/pulls) [![last commit](https://img.shields.io/github/last-commit/ai-agent-assembly/agent-assembly-spec?label=last)](https://github.com/ai-agent-assembly/agent-assembly-spec/commits/main) |
| [![examples](https://img.shields.io/badge/examples-examples-22C55E?logo=github)](https://github.com/ai-agent-assembly/examples) | Runnable sample code for every SDK plus policy, approval, audit, trace, and runtime workflows | — | | [![issues](https://img.shields.io/github/issues/ai-agent-assembly/examples?label=issues)](https://github.com/ai-agent-assembly/examples/issues) [![PRs](https://img.shields.io/github/issues-pr/ai-agent-assembly/examples?label=PRs)](https://github.com/ai-agent-assembly/examples/pulls) [![last commit](https://img.shields.io/github/last-commit/ai-agent-assembly/examples?label=last)](https://github.com/ai-agent-assembly/examples/commits/main) |
| [![arena](https://img.shields.io/badge/arena-arena-DC2626?logo=github)](https://github.com/ai-agent-assembly/arena) | Public trial ground for agent-assembly governance: cross-framework adversarial trials, behavior profiles, match reports | — | [![CI](https://github.com/ai-agent-assembly/arena/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ai-agent-assembly/arena/actions/workflows/ci.yml?query=branch%3Amain) | [![issues](https://img.shields.io/github/issues/ai-agent-assembly/arena?label=issues)](https://github.com/ai-agent-assembly/arena/issues) [![PRs](https://img.shields.io/github/issues-pr/ai-agent-assembly/arena?label=PRs)](https://github.com/ai-agent-assembly/arena/pulls) [![last commit](https://img.shields.io/github/last-commit/ai-agent-assembly/arena?label=last)](https://github.com/ai-agent-assembly/arena/commits/main) |
<!-- END GENERATED: repo_table -->

> **Sample code starts here:** [**examples**](https://github.com/ai-agent-assembly/examples) is the canonical entrypoint for learning by running small, framework-specific examples for Python, Node.js/TypeScript, Go, policy enforcement, approvals, audit, trace, and runtime workflows.

> **Governance trials happen here:** [**arena**](https://github.com/ai-agent-assembly/arena) is the public trial ground for agent-assembly governance — agents enter, agent-assembly defends, and every match leaves a report. Where `examples` is small, instructional, happy-path samples, `arena` runs cross-framework adversarial trials, behavior profiles, and deterministic mock/replay agents against policy under stress. Canonical docs: <https://docs.agent-assembly.com/arena/>.

### Install channels

<!-- BEGIN GENERATED: install_channels -->
#### Homebrew (macOS, Linux)

```sh
brew install ai-agent-assembly/tap/aasm
```

#### Python — pip, uv, or poetry

```sh
# pip
pip install agent-assembly

# uv
uv add agent-assembly

# poetry
poetry add agent-assembly
```

#### Node.js — pnpm (recommended), npm, or yarn

```sh
# pnpm (recommended)
pnpm add @agent-assembly/sdk

# npm
npm install @agent-assembly/sdk

# yarn
yarn add @agent-assembly/sdk
```

#### Go — go get

```sh
go get github.com/ai-agent-assembly/go-sdk
```

#### Docker

> A published container image is coming soon. No image is available on
> `ghcr.io` yet.

#### curl one-line installer (CLI)

```sh
curl -sSf https://raw.githubusercontent.com/ai-agent-assembly/agent-assembly/HEAD/scripts/install-cli.sh | sh
```
<!-- END GENERATED: install_channels -->

## Release and Homebrew Notes

- `agent-assembly` is on a pre-stable **beta** channel — see the [Core release badge](https://github.com/ai-agent-assembly/agent-assembly/releases) above for the current version.
- The Homebrew tap's `Formula/aasm.rb` now ships real, published `sha256` checksums for the released `aasm` artifacts — the earlier zero-checksum bootstrap state is obsolete.

## Full Production Highlights

### Core differentiation

1. Lowest-intrusion integration: one-line init across major agent frameworks.
2. Three-layer interception: semantic to protocol to kernel, with selectable depth.
3. Secret Injection: real credentials never appear in LLM context windows.
4. Tool Execution Sandbox: isolated execution to reduce security risk.
5. Human-in-the-loop Gate: high-risk actions require human review.

### Enterprise governance

1. Agent Identity and Zero-trust A2A
2. Cost and Token Budget Governance
3. Org / Team / Agent hierarchy management
4. Audit Trail and Compliance Export

### Deployment flexibility

1. Local Dev Mode (zero-config, OSS)
2. SaaS Cloud (managed enterprise control plane)

> Prioritize these three above the fold: lowest-intrusion integration, Secret Injection, and Human-in-the-loop Gate.

## Documentation and Community

Start at the org profile, then follow these for every production repository:

| Resource | Link |
| --- | --- |
| 📚 Documentation site (canonical) | <https://docs.agent-assembly.com/> |
| 🤝 Contributing | [CONTRIBUTING.md](https://github.com/ai-agent-assembly/.github/blob/main/CONTRIBUTING.md) |
| 🔒 Security policy | [SECURITY.md](https://github.com/ai-agent-assembly/.github/blob/main/SECURITY.md) — report privately (see the reporting address there) |
| 💬 Support and questions | [GitHub Discussions](https://github.com/ai-agent-assembly/agent-assembly/discussions) |

> Each repository README links back to this profile and out to the canonical
> documentation site, so you can navigate from the org entrypoint to core
> runtime, SDKs, Homebrew tap, docs, and spec — and from any repo back here.
