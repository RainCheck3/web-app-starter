# Learning while building

This template carries local learning capture into new projects. One setup command per clone links it to your private notebook. No service, API key, model call, or network upload is involved.

## Enable once per project

Use Python 3.9+ and Git. From the project root:

```bash
python3 scripts/learning.py setup --notebook ../founder-notebook --project my-product
```

Choose a unique, stable project ID. The notebook must be outside this repository. Setup stores its absolute path and the Python interpreter in local Git configuration and installs a local post-commit hook. These settings and hooks are not copied by GitHub templates or clones; run setup for each new clone. If you move the notebook or interpreter, rerun setup. Build/check wrappers use `sh`; on Windows use WSL or Git Bash.

Existing hooks are preserved: setup refuses to replace a different hook or hooks manager. Use `--no-hook` to configure the notebook, then add `python3 scripts/learning.py record --kind commit` to your existing post-commit hook. Do not replace a hooks manager just for learning capture.

Normal commits and the documented build/check commands now create Markdown evidence files under `products/<project>/events/`. Before setup, wrappers simply run the original command. Logging errors warn but preserve the original command's exit status. CI has no local notebook configuration, so it does not upload private notes or create notebook artifacts. Raw compiler output, source contents, environment variables, and command arguments are not copied into the notebook.

Commit records are deduplicated by revision. Each build/check attempt gets its own record with UTC time, revision, dirty-working-tree flag, and exit code. A dirty tree means the revision alone cannot reproduce the build. These records are evidence, not inferred product or business outcomes.

## Capture a useful learning

Coding agents follow the learning instructions in `AGENTS.md`. They read recent relevant notes before work and save one concise note after a meaningful task. You can also pipe a note into the helper:

```bash
python3 scripts/learning.py note --area engineering <<'NOTE'
Hypothesis: A request timeout will make offline failures recoverable.
Evidence: Linked test, commit, observed error, or customer conversation.
Learning: What changed in our understanding, including uncertainty.
Decision / next action: One concrete change or experiment.
Confidence: Low / medium / high, with scope and caveats.
NOTE
```

Areas are `engineering`, `product`, and `revenue`. Agent instructions are guidance, not a guaranteed lifecycle hook. Deterministic commit/build capture provides the factual record even when no agent is involved. No AI runs inside a Git hook or build.

## Connect deployment evidence

This template has no deployment provider configured. A commit, CI pass, bundle export, release tag, or cloud build does not by itself prove deployment to users.

When a product gets a deployment pipeline, record only after the provider confirms the intended environment/revision succeeded:

```bash
python3 scripts/learning.py record --kind deployment --evidence 'https://provider.example/verified-release/123'
```

Wire this command into a local deploy script after its success/health verification. Cloud CI cannot write to a notebook on your laptop. For cloud deployment, let the private weekly review read provider/GitHub deployment records using existing read-only access; a future connector can make that capture immediate. The helper records supplied evidence; it does not independently verify that URL. Never put private customer/revenue notes in a public GitHub issue, PR, or Actions artifact.

## Review and improve

In the private notebook, review the week's events and notes together. Separate observed facts, hypotheses, and unknowns. Connect engineering work to customer outcomes only when there is evidence. Revenue and retention need real payment/product data or your observations; missing data stays unknown, not zero.

Choose one experiment for next week. Repeated lessons become entries in `playbook.md`, with links and the conditions where they apply. Turn product decisions into project work; propose reusable template improvements for review. Avoid automatically copying an untested lesson to every product.

Start reviews manually when you are ready. Ask your coding agent to review the private notebook since the last review (or the past seven days for the first review), cover engineering, product, and revenue evidence, and save a dated Markdown review under `weekly/` with one next experiment. No scheduled job is installed by this template. Setup automatically registers the local project path in `products/<project>/project.json` for the cross-project review. Rerun setup after moving a project. If multiple clones share a project ID, the most recently configured clone is used for review. A local notebook needs your own backup or a separate private repository; no remote is created automatically.

## Disable

Remove only the hook marked `founder-learning-hook-v1` from the path printed by `git rev-parse --git-path hooks/post-commit`, then run:

```bash
git config --local --remove-section learning
```

Existing records remain intact. If you integrated with another hooks manager, remove just the learning command you added there.
