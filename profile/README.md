# AI Agent Assembly

[![Core CI](https://github.com/ai-agent-assembly/agent-assembly/actions/workflows/ci.yml/badge.svg)](https://github.com/ai-agent-assembly/agent-assembly/actions/workflows/ci.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Core release](https://img.shields.io/github/v/release/ai-agent-assembly/agent-assembly?include_prereleases&sort=semver)](https://github.com/ai-agent-assembly/agent-assembly/releases)
[![Discussions](https://img.shields.io/badge/community-Discussions-blue?logo=github)](https://github.com/ai-agent-assembly/agent-assembly/discussions)

AI Agent Assembly is an open-source governance platform for AI agents. It enforces policy, tracks budget, and audits every action your agents take across three independent interception layers — in-process SDKs, a sidecar proxy, and eBPF kernel hooks — so you can ship multi-agent fleets without losing control of what they do.

## Developer Start Here

### Repository Status

| Repo | Purpose | Version | Base branch health | Activity |
| --- | --- | --- | --- | --- |
| [![agent-assembly](https://img.shields.io/badge/agent--assembly-core-000000?logo=rust)](https://github.com/ai-agent-assembly/agent-assembly) | Core Rust monorepo: gateway, policy engine, CLI, API, dashboard | [![GitHub tag](https://img.shields.io/github/v/tag/ai-agent-assembly/agent-assembly?label=GitHub&logo=github)](https://github.com/ai-agent-assembly/agent-assembly/tags) [![crates.io](https://img.shields.io/badge/crates.io-reference-000000?logo=rust)](https://crates.io/search?q=agent-assembly) | [![CI](https://github.com/ai-agent-assembly/agent-assembly/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/ai-agent-assembly/agent-assembly/actions/workflows/ci.yml?query=branch%3Amaster) | [![issues](https://img.shields.io/github/issues/ai-agent-assembly/agent-assembly?label=issues)](https://github.com/ai-agent-assembly/agent-assembly/issues) [![PRs](https://img.shields.io/github/issues-pr/ai-agent-assembly/agent-assembly?label=PRs)](https://github.com/ai-agent-assembly/agent-assembly/pulls) [![last commit](https://img.shields.io/github/last-commit/ai-agent-assembly/agent-assembly?label=last)](https://github.com/ai-agent-assembly/agent-assembly/commits/master) |
| [![python-sdk](https://img.shields.io/badge/python--sdk-SDK-3776AB?logo=python&logoColor=white)](https://github.com/ai-agent-assembly/python-sdk) | Python SDK (PyO3 native + pure-Python client) | [![GitHub tag](https://img.shields.io/github/v/tag/ai-agent-assembly/python-sdk?label=GitHub&logo=github)](https://github.com/ai-agent-assembly/python-sdk/tags) [![PyPI](https://img.shields.io/pypi/v/agent-assembly?label=PyPI&logo=pypi&logoColor=white)](https://pypi.org/project/agent-assembly/) | [![CI](https://github.com/ai-agent-assembly/python-sdk/actions/workflows/ci.yaml/badge.svg?branch=master)](https://github.com/ai-agent-assembly/python-sdk/actions/workflows/ci.yaml?query=branch%3Amaster) | [![issues](https://img.shields.io/github/issues/ai-agent-assembly/python-sdk?label=issues)](https://github.com/ai-agent-assembly/python-sdk/issues) [![PRs](https://img.shields.io/github/issues-pr/ai-agent-assembly/python-sdk?label=PRs)](https://github.com/ai-agent-assembly/python-sdk/pulls) [![last commit](https://img.shields.io/github/last-commit/ai-agent-assembly/python-sdk?label=last)](https://github.com/ai-agent-assembly/python-sdk/commits/master) |
| [![node-sdk](https://img.shields.io/badge/node--sdk-SDK-339933?logo=node.js&logoColor=white)](https://github.com/ai-agent-assembly/node-sdk) | TypeScript SDK (napi-rs native + JS client) | [![GitHub tag](https://img.shields.io/github/v/tag/ai-agent-assembly/node-sdk?label=GitHub&logo=github)](https://github.com/ai-agent-assembly/node-sdk/tags) [![npm](https://img.shields.io/npm/v/%40agent-assembly%2Fsdk/alpha?label=npm&logo=npm&logoColor=white)](https://www.npmjs.com/package/@agent-assembly/sdk) | [![Tests](https://github.com/ai-agent-assembly/node-sdk/actions/workflows/test-matrix.yml/badge.svg?branch=master)](https://github.com/ai-agent-assembly/node-sdk/actions/workflows/test-matrix.yml?query=branch%3Amaster) | [![issues](https://img.shields.io/github/issues/ai-agent-assembly/node-sdk?label=issues)](https://github.com/ai-agent-assembly/node-sdk/issues) [![PRs](https://img.shields.io/github/issues-pr/ai-agent-assembly/node-sdk?label=PRs)](https://github.com/ai-agent-assembly/node-sdk/pulls) [![last commit](https://img.shields.io/github/last-commit/ai-agent-assembly/node-sdk?label=last)](https://github.com/ai-agent-assembly/node-sdk/commits/master) |
| [![go-sdk](https://img.shields.io/badge/go--sdk-SDK-00ADD8?logo=go&logoColor=white)](https://github.com/ai-agent-assembly/go-sdk) | Go SDK | [![GitHub tag](https://img.shields.io/github/v/tag/ai-agent-assembly/go-sdk?label=GitHub&logo=github)](https://github.com/ai-agent-assembly/go-sdk/tags) [![Go Reference](https://pkg.go.dev/badge/github.com/ai-agent-assembly/go-sdk.svg)](https://pkg.go.dev/github.com/ai-agent-assembly/go-sdk) | [![Go test](https://github.com/ai-agent-assembly/go-sdk/actions/workflows/go-test.yml/badge.svg?branch=master)](https://github.com/ai-agent-assembly/go-sdk/actions/workflows/go-test.yml?query=branch%3Amaster) | [![issues](https://img.shields.io/github/issues/ai-agent-assembly/go-sdk?label=issues)](https://github.com/ai-agent-assembly/go-sdk/issues) [![PRs](https://img.shields.io/github/issues-pr/ai-agent-assembly/go-sdk?label=PRs)](https://github.com/ai-agent-assembly/go-sdk/pulls) [![last commit](https://img.shields.io/github/last-commit/ai-agent-assembly/go-sdk?label=last)](https://github.com/ai-agent-assembly/go-sdk/commits/master) |
| [![.github](https://img.shields.io/badge/.github-org--profile-181717?logo=github)](https://github.com/ai-agent-assembly/.github) | Organization profile, templates, support, and community files | [![tag](https://img.shields.io/github/v/tag/ai-agent-assembly/.github?label=tag&logo=github)](https://github.com/ai-agent-assembly/.github/tags) | [![last commit](https://img.shields.io/github/last-commit/ai-agent-assembly/.github?label=last)](https://github.com/ai-agent-assembly/.github/commits/master) | [![issues](https://img.shields.io/github/issues/ai-agent-assembly/.github?label=issues)](https://github.com/ai-agent-assembly/.github/issues) [![PRs](https://img.shields.io/github/issues-pr/ai-agent-assembly/.github?label=PRs)](https://github.com/ai-agent-assembly/.github/pulls) |
| [![homebrew-agent-assembly](https://img.shields.io/badge/homebrew--agent--assembly-tap-FBB040?logo=homebrew&logoColor=black)](https://github.com/ai-agent-assembly/homebrew-agent-assembly) | Homebrew tap for `aasm` | [![tag](https://img.shields.io/github/v/tag/ai-agent-assembly/homebrew-agent-assembly?label=tag&logo=homebrew)](https://github.com/ai-agent-assembly/homebrew-agent-assembly/tags) | [![last commit](https://img.shields.io/github/last-commit/ai-agent-assembly/homebrew-agent-assembly?label=last)](https://github.com/ai-agent-assembly/homebrew-agent-assembly/commits/master) | [![issues](https://img.shields.io/github/issues/ai-agent-assembly/homebrew-agent-assembly?label=issues)](https://github.com/ai-agent-assembly/homebrew-agent-assembly/issues) [![PRs](https://img.shields.io/github/issues-pr/ai-agent-assembly/homebrew-agent-assembly?label=PRs)](https://github.com/ai-agent-assembly/homebrew-agent-assembly/pulls) |
| [![agent-assembly-docs](https://img.shields.io/badge/agent--assembly--docs-docs-4051B5?logo=materialformkdocs&logoColor=white)](https://github.com/ai-agent-assembly/agent-assembly-docs) | Public documentation site | [![tag](https://img.shields.io/github/v/tag/ai-agent-assembly/agent-assembly-docs?label=tag&logo=github)](https://github.com/ai-agent-assembly/agent-assembly-docs/tags) | [![Deploy](https://github.com/ai-agent-assembly/agent-assembly-docs/actions/workflows/deploy.yml/badge.svg?branch=main)](https://github.com/ai-agent-assembly/agent-assembly-docs/actions/workflows/deploy.yml?query=branch%3Amain) | [![issues](https://img.shields.io/github/issues/ai-agent-assembly/agent-assembly-docs?label=issues)](https://github.com/ai-agent-assembly/agent-assembly-docs/issues) [![PRs](https://img.shields.io/github/issues-pr/ai-agent-assembly/agent-assembly-docs?label=PRs)](https://github.com/ai-agent-assembly/agent-assembly-docs/pulls) [![last commit](https://img.shields.io/github/last-commit/ai-agent-assembly/agent-assembly-docs?label=last)](https://github.com/ai-agent-assembly/agent-assembly-docs/commits/main) |
| [![agent-assembly-spec](https://img.shields.io/badge/agent--assembly--spec-spec-6E40C9?logo=openapiinitiative&logoColor=white)](https://github.com/ai-agent-assembly/agent-assembly-spec) | Shared specifications and protocol contracts | [![tag](https://img.shields.io/github/v/tag/ai-agent-assembly/agent-assembly-spec?label=tag&logo=github)](https://github.com/ai-agent-assembly/agent-assembly-spec/tags) | [![last commit](https://img.shields.io/github/last-commit/ai-agent-assembly/agent-assembly-spec?label=last)](https://github.com/ai-agent-assembly/agent-assembly-spec/commits/master) | [![issues](https://img.shields.io/github/issues/ai-agent-assembly/agent-assembly-spec?label=issues)](https://github.com/ai-agent-assembly/agent-assembly-spec/issues) [![PRs](https://img.shields.io/github/issues-pr/ai-agent-assembly/agent-assembly-spec?label=PRs)](https://github.com/ai-agent-assembly/agent-assembly-spec/pulls) |

### Install channels

#### Homebrew (macOS, Linux)

```sh
brew install agent-assembly/tap/aasm
```

#### Python — pip, uv, or poetry

```sh
# pip
pip install agent-assembly-python

# uv
uv add agent-assembly-python

# poetry
poetry add agent-assembly-python
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

#### Docker

```sh
docker pull ghcr.io/agent-assembly/python:latest
```

#### curl one-line installer

```sh
curl -fsSL https://get.agentassembly.dev | sh
```

## Release and Homebrew Notes

- `agent-assembly` is currently in a pre-stable alpha channel.
- Homebrew tap has `Formula/aasm.rb` with `version "0.0.1"`, but checksum placeholders are still all zero, so this should be treated as pre-stable/bootstrap state until real release artifacts and checksums are published.

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
