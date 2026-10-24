# Canonical role execution reference (role-execution)

The canonical reference defining the per-harness execution procedure for delegating work to a dedicated role, and the judgment on how many agents to launch. Every sub-skill's "Role execution (by harness)" section refers to this file.

The content of a role itself (the role prompt) is in each sub-skill's own `references/roles/`, and which task is delegated to which role is in each sub-skill's SKILL.md. This file covers only how a role is run, and is not duplicated into the files that refer to it.

## A harness that can launch sub-agents (Claude Code)

As each Step describes, launch the agent named in SKILL.md's table with the Agent tool and hand it the instruction. The agent definitions are in the repository's `agents/`, as copies of each sub-skill's `references/roles/`.

## A harness that cannot launch sub-agents (Codex and others)

Read each Step's "launch the agent" as "read the role prompt and execute as that role yourself." The procedure is as follows.

1. Read the role prompt named in SKILL.md's table with Read.
2. Treat the items in the Step's instruction as instructions to yourself, exactly as written.
3. Follow the role prompt's "Inputs allowed" rule. When the role prompt is written for a role with no web-transmission means, do not use web search or fetch during that work.
4. The deliverable's format, its validation, and the pass/fail gate are identical regardless of the harness.

## How many agents to launch

Delegation has a cost even for a small piece of work. When one role is enough, launch only one. The same work is never doubled up across more than one role. Never launch an agent to check a deliverable you built yourself. Having the author reread it in their own context only brings that context into the judgment. The validation script handles checking the format and the rules.

No skill in this version launches an auditor. The validators check the format, and the main session reads the source URL of a value that looks doubtful.
