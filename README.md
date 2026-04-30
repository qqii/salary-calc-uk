# Salary Calculator UK

https://qqii.github.io/salary-calc-uk/

**NOTE: This is work in progress, and has been vibe coded with AI. Based on an initial 100% human attempt [via Observable](https://observablehq.com/@qqii/pension-contribution-hacking).**

## Prerequisites

- Install [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
- Install [`direnv`](https://direnv.net/docs/installation.html) (optional — auto-runs `uv sync` and activates `.venv` on `cd`)

```shell
git config commit.template .gitmessage
lefthook install
direnv allow  # if using direnv
```

## Getting Started

With direnv, the venv is synced and activated automatically. Otherwise:

```shell
uv sync
# activate the venv at .venv

marimo edit --watch salary.nb.py 
```
