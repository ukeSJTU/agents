# AGENTS.md

## Purpose

This repository is the source of truth for Uke's personal agent assets: skills,
plugins, and the metadata needed to distribute or synchronize them. It is not an
application repository and currently has no runtime service, database, CI/CD
pipeline, or test suite.

## Repository boundaries

- `skills/` contains personal, distributable skills. Each skill lives in its own
  directory and has a `SKILL.md` entry point; keep its scripts, references, and
  other bundled assets beside it.
- `plugins/` is reserved for personal plugins created in this repository. Keep
  each plugin self-contained in its own directory.
- `skills.sh.json` is the checked-in catalogue configuration for skills exposed
  through skills.sh. When adding, removing, or renaming a listed personal skill,
  update the applicable grouping in this file.
- `skills-lock.json` records externally installed development skills and their
  sources. Treat it as generated metadata: update it only through the tool that
  manages those installed skills; do not hand-edit hashes.
- `README.md` is the English, reader-facing overview. `README.zh_CN.md` is its
  Simplified Chinese counterpart; keep their user-facing information
  semantically equivalent.
- `.agents/` and `.claude/` are development-support configuration for Codex and
  Claude Code while they work on this repository. They are not locations for
  personal distributable assets. Never add a personal skill under
  `.agents/skills/` or `.claude/`; add it under `skills/` instead. Likewise,
  personal plugins belong under `plugins/`.

Do not introduce conventions for future top-level asset types without an
explicit repository decision. Ask before creating a new top-level source
directory.

## Environment and commands

- Use Node.js `>=22` and pnpm `>=10.30.3 <12` as specified in
  `package.json`.
- Install development dependencies with `pnpm install`.
- Check only formatting with `pnpm run format:check`.
- Reformat the repository with `pnpm run format`. This command writes broadly;
  do not run it when unrelated working-tree changes must be preserved.

There is no automated test command at present. Validate a changed skill or
plugin using the smallest relevant workflow described by that asset, then run
`pnpm run format:check` before handing off a change.

`pnpm check` is intended to aggregate formatting and dependency checks, but it
currently fails because `pnpm run deps:check` invokes the unavailable command
`pnpm peers check`. Do not treat this as a validation gate until the script is
repaired; report the failure if it is relevant to the task.

## Working conventions

- Read the target asset's `SKILL.md`, plugin manifest, and nearby documentation
  before modifying it. Follow its local instructions when they are more
  specific than this file.
- Keep skills focused and self-contained. Use relative links from `SKILL.md` to
  bundled references or scripts, and do not depend on files in `.agents/` or
  `.claude/` at runtime.
- When changing a user-facing asset or its distribution—for example, adding,
  removing, renaming, or materially changing a skill or plugin—check whether
  the READMEs need updating. If they do, update both `README.md` and
  `README.zh_CN.md` in the same change, including asset lists, installation
  commands, requirements, and status statements.
- Preserve the existing directory structure and avoid unrelated formatting,
  dependency, or lockfile changes.
- Do not place secrets or user-specific credentials in the repository. Use
  environment variables or a local ignored `.env` file when a tool needs them.

## Versioning and commits

Use Conventional Commits. The commit-msg hook enforces this through
Commitlint; examples include `feat(skills): add pdf reading workflow`,
`fix(plugins): correct manifest path`, and `docs: clarify installation`.

Changesets are installed but are not part of the current workflow: the
repository currently contains configuration assets rather than versioned,
published workspace packages. Do not create a changeset for skill, plugin, or
repository-configuration changes. Revisit this policy before adding a package
under `plugins/*` or `tools/*` that is independently versioned and published.
