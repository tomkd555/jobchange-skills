# Configuration file

In the job-change support skill family, where the user's data is stored is decided solely by the configuration file. There is no default location. Until the configuration is settled, the hub (`job-change-support`) does not route to any sub-skill.

There are two reasons for not deciding the location implicitly. First, the user's data includes personal information such as current salary, place of residence, and current employer's name, and where it is stored should be the user's own decision. Second, if the skill body's own directory were used as a default write location, the location of personal information would shift every time the skill is updated or reinstalled.

## Search order

The following locations are searched in order, and the first one found is used.

| Order | Location | Purpose |
|---|---|---|
| 1 | The file pointed to by the environment variable `JOB_CHANGE_CONFIG` | Temporary switching, CI |
| 2 | The first `.job-change/config.json` found by walking up from the current directory | For separating configuration per project or per repository |
| 3 | `~/.job-change/config.json` | Ordinary use |

If the file pointed to by `JOB_CHANGE_CONFIG` does not exist, that setting is ignored and the search continues from 2 onward.

## Content

```json
{
  "schema_version": "1.0",
  "data_root": "/absolute/path/to/job-change-data",
  "private_dir": "career-private",
  "companies_dir": "companies",
  "job_search_dir": "job-search",
  "python": "python"
}
```

| Key | Required | Default | Content |
|---|---|---|---|
| `schema_version` | Optional | `"1.0"` | The version of the configuration file |
| `data_root` | **Required** | None | The directory that holds the user's data. Written as an absolute path. A leading `~` expands to the home directory |
| `private_dir` | Optional | `career-private` | The name of the directory holding personal information. Written as a simple name directly under `data_root` (it cannot contain a path separator) |
| `companies_dir` | Optional | `companies` | The name of the directory holding per-company deliverables |
| `job_search_dir` | Optional | `job-search` | The name of the directory holding job-search results |
| `python` | Optional | `python` | The command used to run the validation scripts. `python3` or an absolute path can also be given |

## Directory structure

```
{data_root}/
├─ career-private/          ← Personal information. Not passed to any agent with web tools
│   ├─ profile.json
│   ├─ self_analysis.json
│   ├─ company_index.json
│   ├─ commute.json
│   └─ fit/{company slug}/{fit_assessment,time_analysis}.json
├─ companies/{company slug}/  ← Per-company deliverables (non-personal information)
└─ job-search/{YYYYMMDD}-{slug}/job_search_results.json
```

`career-private/` is placed outside `companies/` in order to isolate personal information from the tree that an agent with web-sending capability works in. Renaming `private_dir` preserves this isolation.

## Creating the configuration

If no configuration exists the first time the user launches it, the hub asks where to place the data. To create it by hand, run the following.

```bash
python <installation location of the skills>/job-change-support/scripts/jc_config.py --init --data-root /absolute/path/to/job-change-data
```

If a configuration file already exists, it is not overwritten, and the exit code is 1.

## Checking the configuration

```bash
python <installation location of the skills>/job-change-support/scripts/jc_config.py --show
```

This outputs, as JSON, the configuration settled by the search order and the absolute path for each data item. The exit code is 0 on success, 1 if a configuration was found but its content is invalid, and 2 if unconfigured.

When only an individual path is needed, use `--path`. The keys are `data_root`, `private`, `companies`, `job_search`, `profile`, `company_index`, `self_analysis`, and `commute`.

```bash
python .../jc_config.py --path profile
```

None of these options create a directory. Each directory is created by the individual skill at the point it writes a deliverable.

## How paths are written in skill text

Each SKILL.md and reference document writes data paths in the form `{DATA_ROOT}/career-private/profile.json`. `{DATA_ROOT}` is read as the `data_root` returned by `jc_config.py --show`. When the directory names have been changed from their defaults, use the `paths` returned by `--show`.

There are two placeholders that refer to a skill body itself. `{SKILL_DIR}` refers to that skill's own directory, and `{HUB_SKILL_DIR}` refers to the `job-change-support` directory.
