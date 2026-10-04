# Installing on Claude Code

## Installing as a plugin (recommended)

The repository root is itself a plugin, and also a marketplace. The following two lines deploy 10 skills and 16 agents.

```
/plugin marketplace add <this repository's URL or local path>
/plugin install job-change@job-change-skills
```

If you have cloned it locally, pass that path in place of the URL.

```
/plugin marketplace add C:/path/to/jobchange_Skills
/plugin install job-change@job-change-skills
```

After installation, confirm with `/plugin` that `job-change` is enabled. The list of skills can be checked with `/help` or by slash-command completion (type `/job-change-`).

Update with the following command.

```
/plugin marketplace update job-change-skills
```

## Installing by hand

Without using the plugin mechanism, place the files as follows.

| What to place | Where to place it |
|---|---|
| The 10 `skills/job-change-*` directories | `~/.claude/skills/` |
| The 16 `agents/job-change-*.md` files | `~/.claude/agents/` |

Because the 10 skills reference each other, place them all together. To scope this per project, place them under `<project>/.claude/`, which takes `~/.claude/`'s place for that project.

A symbolic link works in place of copying. Claude Code follows a symbolic link placed at `~/.claude/skills/<name>`.

```powershell
# Windows (requires administrator privileges or developer mode)
New-Item -ItemType SymbolicLink -Path "$HOME\.claude\skills\job-change-support" -Target "C:\path\to\jobchange_Skills\skills\job-change-support"
```

```bash
# macOS / Linux
ln -s /path/to/jobchange_Skills/skills/job-change-support ~/.claude/skills/job-change-support
```

## Initial configuration

Where the user's data is stored is decided solely by the configuration file. There is no default location.

After installation, saying 「転職の準備をしたい」 ("I want to prepare for a job change") or running `/job-change-support` has the hub check whether a configuration exists. If not, the hub asks where to place the data; choose from the offered options or answer with any absolute path. Because this location will store personal information including current salary, place of residence, and current employer's name, choose a local directory outside any sync or sharing scope.

To create the configuration without waiting for the dialogue, run the following.

```bash
python ~/.claude/skills/job-change-support/scripts/jc_config.py --init --data-root /absolute/path/to/job-change-data
```

When installed as a plugin, the skill's actual files live at the plugin's installation location. The path can be checked in `/plugin`'s detail view.

Check the configuration as follows.

```bash
python <installation location of the skills>/job-change-support/scripts/jc_config.py --show
```

If exit code 0 is returned along with output showing `data_root` and the absolute path for each data item, the installation is complete. The configuration specification is in [configuration.md](configuration.md).

## Verifying it works

1. Run `/job-change-support` and confirm that the hub passes the configuration gate (if unconfigured, that the dialogue starts).
2. Say 「プロファイルを作りたい」 ("I want to build a profile") and confirm that this routes to `job-change-profile`.
3. After finishing the interview, confirm that `{data_root}/career-private/profile.json` is created and that `validate_profile.py` PASSes.
4. Say 「転職の軸を決めたい」 ("I want to settle my job-change axis") and confirm that this routes to `job-change-axis`. After the interview, confirm that `{data_root}/career-private/axis.json` is created and that `validate_axis.py` PASSes.

## Common pitfalls

- **Python cannot be found.** Each skill invokes the validation scripts through the `python` command. In an environment where only `python3` works, set the configuration file's `python` to `python3`.
- **A skill does not appear in the list.** If a new skill directory was created during a running session, restarting Claude Code is required. A change to `SKILL.md` inside an existing directory takes effect without a restart.
- **An agent cannot be found.** Check whether `agents/` was left unplaced. When installed as a plugin, it is placed automatically. Even without the agents, each skill's "Role execution (by harness)" section lets the work proceed with the skill body alone.
