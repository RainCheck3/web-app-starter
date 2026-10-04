# Setup

## Prerequisites

- Node.js via nvm
- pnpm via Corepack
- Git

## Use the expected Node version

    nvm use

## Enable the pinned package manager

    corepack enable

## Install dependencies

    pnpm install

## Start local development

    pnpm dev

Open:

    http://localhost:3000

## Check code quality

    pnpm check

## Format code

    pnpm format

## Environment variables

Copy `.env.example` to `.env.local` when project-specific environment variables are needed.

    cp .env.example .env.local

Do not commit real secrets.

## Learning setup

For each new project, complete the one-time [learning setup](learning.md) before starting work. Keep the notebook outside the product repository.
