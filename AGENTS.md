# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project Type

This is a reusable Next.js web app starter template for side projects, product experiments, dashboards, tools, landing pages, SaaS apps, AI app frontends, and mobile companion web apps.

Keep the base template lean, stable, and broadly applicable.

## Stack

- Next.js App Router
- TypeScript
- Tailwind CSS
- ESLint
- Prettier
- pnpm
- nvm

## Package Manager

Use `pnpm`.

Do not switch to npm, Yarn, or Bun unless explicitly requested.

## Node Version

Use the Node version specified in `.nvmrc`.

Command:

```bash
nvm use
```

## Development Commands

```bash
pnpm install
pnpm dev
pnpm lint
pnpm format:check
pnpm build
pnpm check
```

Before considering work complete, run the relevant quality checks:

```bash
pnpm check
```

## Code Style

- Use TypeScript for application code.
- Prefer clear, boring code over clever abstractions.
- Prefer Server Components by default.
- Use Client Components only when interactivity, state, effects, event handlers, or browser APIs are required.
- Keep reusable UI in `components/`.
- Keep shared utilities in `lib/`.
- Keep project-level constants/configuration in `config/`.
- Keep documentation in `docs/`.

## Template Boundaries

Do not add the following to the base template unless explicitly requested:

- database
- ORM
- authentication
- payments
- email provider
- analytics
- error tracking
- AI SDKs
- background jobs
- queue systems
- deployment-specific configuration

Those should be added as project-specific modules or documented upgrade paths.

## Dependencies

Before adding a dependency, prefer using existing platform/framework features.

Only add a dependency when it meaningfully improves maintainability, user experience, or development speed.

## Environment Variables

- Do not commit secrets.
- Put example variables in `.env.example`.
- Use `.env.local` for local secrets.
- Any new environment variable should be documented in `.env.example`.

## Quality Bar

Before finalizing a change, ensure these pass:

```bash
pnpm check
```

If a command fails, explain what failed and why.

## Documentation Expectations

When making structural or architectural changes, update relevant docs:

- `README.md`
- `docs/setup.md`
- `docs/decisions.md`

Keep documentation concise and useful.

## AI Agent Behavior

- First inspect existing files and patterns before changing code.
- Make the smallest reasonable change that satisfies the request.
- Do not rewrite unrelated files.
- Do not introduce new frameworks or services without explicit approval.
- Do not remove existing functionality unless asked.
- Explain notable tradeoffs in plain language.

## Learning workflow

Read `docs/learning.md`. When `git config --local --get learning.notebook` is configured, read the notebook's direction, relevant playbook lessons, and the project's overview and recent notes before meaningful work. After a meaningful task, save one concise private note with `python3 scripts/learning.py note --area engineering` (or product/revenue), passing Markdown on stdin. Include hypothesis, observed evidence and links, what changed in understanding, decision/next action, and confidence. Mark missing product/revenue evidence unknown; never infer demand or income from a successful build. Do not create notes for every trivial edit.

The build/check wrappers and local post-commit hook capture facts automatically after one-time setup. A build is not a deployment. Only record deployment after provider/environment verification. If learning capture is unconfigured or sandbox-blocked, report that briefly; never move private notes into tracked product files. Do not change notebook visibility, publish its contents, or propagate a proposed lesson to other projects without authorization.
