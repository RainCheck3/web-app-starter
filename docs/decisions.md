# Decisions

## Keep the base web starter lean

The base `web-app-starter` intentionally does not include a database, authentication, payments, analytics, email, error tracking, or AI SDKs.

Reason: this template should support many product types, including landing pages, dashboards, simple tools, AI frontends, SaaS products, and mobile companion apps.

Project-specific capabilities should be added only when needed.

## Use pnpm

This template uses `pnpm` for package management.

Reason: it is fast, disk-efficient, and works well for modern TypeScript projects.

The package manager version is pinned in `package.json` so Corepack can use the expected pnpm release.

## Use nvm

This template includes `.nvmrc` so projects can pin and reuse a known Node version.

## Avoid build-time network dependencies

This template uses system font stacks rather than fetching hosted fonts during `next build`.

Reason: side projects and CI jobs should build reliably even when network access is unavailable or restricted.

## Prefer Server Components by default

In the Next.js App Router, Server Components should be the default. Client Components should be used only when browser-side interactivity is required.

## Run the local quality gate in CI

GitHub Actions runs `pnpm check` with the repository's Node and pnpm versions and a frozen lockfile install. This keeps formatting, lint, and production build checks consistent with local development.

## Keep AI coding instructions tool-agnostic

This project may be edited with Cursor, Codex, Claude Code, or other coding agents. Repository instructions should describe project conventions rather than tool-specific behavior.

## Optional private learning capture

A standard-library Python helper records commit/build/check evidence outside the repository after one-time setup. Shell wrappers preserve command output and exit status, and are inert before setup. Private reflection stays out of public repositories and CI artifacts. Agent notes and weekly reviews connect factual evidence to decisions; no model calls run inside builds or Git hooks.
