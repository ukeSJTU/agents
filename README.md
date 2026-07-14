# agents

> Personal, reusable skills and plugins for coding agents.

[简体中文](README.zh_CN.md)

This repository is the distribution source for Uke's agent assets. Install an
asset into a supported coding agent, then use it in your own projects without
copying its files by hand.

## Available assets

### Skills

| Skill                                      | What it is for                                                          | Key behavior                                                                                                 |
| ------------------------------------------ | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| [`pdf-read`](skills/pdf-read/SKILL.md)     | Reading, reviewing, searching, summarizing, and comparing existing PDFs | Produces page-level evidence from native PDF content; it never modifies PDFs or uses OCR.                    |
| [`paper-read`](skills/paper-read/SKILL.md) | Deep, evidence-traceable reading of academic paper PDFs                 | Requires an explicit reading depth and produces a three-pass reading record with a narrative paper mainline. |

### Plugins

No personal plugins are published yet. Published plugins will be listed here
with their installation instructions.

## Install a skill

The recommended installer is the [skills CLI](https://github.com/vercel-labs/skills).
It supports Codex, Claude Code, and other compatible coding agents.

Install either `pdf-read` or `paper-read` globally for Codex by replacing
`<skill-name>`:

```bash
npx skills add ukeSJTU/agents --skill <skill-name> --agent codex --global
```

Or install it globally for Claude Code:

```bash
npx skills add ukeSJTU/agents --skill <skill-name> --agent claude-code --global
```

Omit `--global` to install the skill only in the current project. To inspect
the collection before installing, run:

```bash
npx skills add ukeSJTU/agents --list
```

> [!NOTE]
> `pdf-read` requires [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
> on your `PATH` when it runs. Its bundled scripts use `uv run` to create an
> isolated environment; they do not add PDF libraries to your global Python
> installation.
>
> `paper-read` has no separate runtime dependency. Install `pdf-read` alongside
> it when page-level PDF evidence is needed.

## Use `pdf-read`

After installation, ask your agent about a PDF in ordinary language. For
example:

> Review the attached PDF, summarize its main claims, and cite the relevant
> page numbers.

The skill is intended for electronic PDFs with a usable native text layer. It
handles text, tables, images, charts, formulas, and layout-sensitive pages;
when extraction is unreliable, it reports the limitation instead of guessing.
It is deliberately read-only: it does not edit, merge, annotate, fill, sign,
encrypt, decrypt by bypass, optimize, or OCR PDFs.

## Use `paper-read`

Ask for a three-pass reading and explicitly choose `理解`, `精读`, or `审读`.
For example:

> Create a reading record for the attached paper. Reading depth: 精读.

The resulting record begins with a continuous “论文主线｜一遍读懂” narrative,
then provides the evidence-traceable three-pass analysis and source index.

## Repository layout

```text
skills/          Personal, distributable agent skills
plugins/         Personal, distributable agent plugins (none published yet)
skills.sh.json   skills.sh catalogue configuration
.agents/         Development support for this repository
.claude/         Development support for this repository
```

The `.agents/` and `.claude/` directories help maintain this repository; they
are not the source for the assets distributed above.
