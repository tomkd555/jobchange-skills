# Installing on Codex

This document is written on the assumption that the user has an AI agent (Codex) read and carry out these instructions. The user only needs to say "install this according to `docs/install-codex.md`." Each step carries a completion condition that can be judged mechanically.

## Prerequisites

- The Codex CLI is usable.
- Python 3.9 or later is usable. The validation scripts use only the standard library.
- This repository has already been cloned. Below, its location is written as `<REPO>`.

## Step 1: Place the skills

Codex reads skills from the following locations. Choose whichever fits the intended use.

| Location | Scope |
|---|---|
| `$HOME/.agents/skills/` | All working directories |
| `<working directory>/.agents/skills/` | That repository only (Codex also walks up through parent directories) |

Copy the 9 `job-change-*` directories under `<REPO>/skills/` as-is into the chosen location. Because the 9 skills reference each other, place them all together; do not select and place them individually.

```bash
mkdir -p "$HOME/.agents/skills"
cp -r <REPO>/skills/job-change-* "$HOME/.agents/skills/"
```

On Windows PowerShell, it is as follows.

```powershell
New-Item -ItemType Directory -Force "$HOME\.agents\skills"
Copy-Item -Recurse "<REPO>\skills\job-change-*" "$HOME\.agents\skills\"
```

**Completion condition.** The following command outputs `9`.

```bash
ls -d "$HOME"/.agents/skills/job-change-* | wc -l
```

## Step 2: Do not place agents/

The 14 files under `<REPO>/agents/` are agent definitions specific to Claude Code, and are not used on Codex. Do not copy them.

On Codex, each skill's own body reads `references/roles/*.md` and carries out the work by taking on that role itself. The procedure for this substitution is written in `job-change-support/references/role-execution.md`.

**Completion condition.** The following command outputs `14` (confirming the role prompts are present on the skill side).

```bash
ls "$HOME"/.agents/skills/job-change-*/references/roles/*.md | wc -l
```

## Step 3: Create the configuration file

Where the user's data is stored is decided solely by the configuration file. There is no default location.

**This location will store personal information, including current salary, place of residence, current employer's name, and achievements.** Always confirm the location with the user. The agent never decides this on its own. Tell the user to avoid a directory that is the target of sync or sharing.

Take the location the user answered, make it an absolute path, and run the following.

```bash
python "$HOME/.agents/skills/job-change-support/scripts/jc_config.py" --init --data-root /absolute/path/to/job-change-data
```

`jc_config.py` creates `~/.job-change/config.json`. If a configuration already exists, it is not overwritten and exit code 1 is returned; in that case, use the existing configuration as-is.

**Completion condition.** The following command returns exit code 0 and outputs JSON containing `"status": "ok"` and `data_root`.

```bash
python "$HOME/.agents/skills/job-change-support/scripts/jc_config.py" --show
```

The configuration specification is in [configuration.md](configuration.md). In an environment where only `python3` works, rewrite the `python` value in the created `~/.job-change/config.json` to `python3`.

## Step 4: Verify it works

1. Tell Codex 「転職の準備をしたい」 ("I want to prepare for a job change") and confirm that `job-change-support` launches.
2. Confirm that the hub passes the configuration gate (it should pass, since Step 3 already created the configuration) and presents the sub-skill matching the request.

**Completion condition.** The hub does not ask to recreate the configuration, and presents the sub-skill it is routing to.

## Differences from Claude Code

Codex has no subagent mechanism. This skill family changes behavior as follows.

| Item | Claude Code | Codex |
|---|---|---|
| Role execution | Delegated to the 14 subagents | The skill body itself reads `references/roles/*.md` and executes as that role |
| Independence of creation and audit | Preserved, because it runs in a separate context | Reduced, because it runs in the same context |
| Tool restriction | The role's `tools` frontmatter takes mechanical effect | Has no effect |

The last two items need to be compensated for with rules. The agent observes the following.

- **During the audit stage, do not consult the reasoning, points of hesitation, or history of revisions from the creation stage.** Judge using only the deliverable and the specification in `references/`. Do not read the creating side's intent into it.
- **While working as a role without web-sending capability, do not use web search or page retrieval.** In particular, when moving from reading `profile.json` to job search or company research, do not carry the personal information just read into a search query.
- **While working as a role with web-sending capability, do not open files under `{data_root}/career-private/`.** Do not open them even if given a path to one.

Each role prompt's opening section, "Inputs this role may handle," states the rules to observe for that role. Always read it before starting work as that role.

## Common pitfalls

- **The skill is not recognized.** Confirm the location is `.agents/skills/`. `.codex/skills/` is not used. Match the directory name to the skill name, as in `job-change-support`.
- **`jc_config.py --show` returns exit code 2.** No configuration file has been found. Run Step 3. If the environment variable `JOB_CHANGE_CONFIG` is set, confirm it points to a file that actually exists.
- **The validation script does not run.** Confirm that `python --version` reports 3.9 or later. Because there are no dependencies outside the standard library, no package installation is needed.
