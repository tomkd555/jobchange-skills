# Canonical role execution reference (role-execution)

The canonical reference defining the per-harness execution procedure for delegating work to a dedicated role, and the judgment on how many agents to launch. Every sub-skill's "Role execution (by harness)" section refers to this file.

The content of a role itself (the role prompt) lives in each sub-skill's own `references/roles/`, and which task is delegated to which role lives in each sub-skill's SKILL.md. This file holds only how a role is run, and is not duplicated into the files that refer to it.

## A harness that can launch sub-agents (Claude Code)

As each Step describes, launch the agent named in SKILL.md's table with the Agent tool and hand it the instruction. The agent definitions live in the repository's `agents/`, as copies of each sub-skill's `references/roles/`.

## A harness that cannot launch sub-agents (Codex and others)

Read each Step's "launch the agent" as "read the role prompt and execute as that role yourself." The procedure is as follows.

1. Read the role prompt named in SKILL.md's table with Read.
2. Treat the items in the Step's instruction as instructions to yourself, exactly as written.
3. Follow the role prompt's "Inputs allowed" rule. When the role prompt is written for a role with no web-transmission means, do not use web search or fetch during that work.
4. The deliverable's format, its validation, and the pass/fail gate are identical regardless of the harness.

## How many agents to launch

Delegation carries a cost even for a small piece of work. When one role is enough, launch only one; the same work is never doubled up across several roles. Never launch an agent to check a deliverable you built yourself. Having the author reread it in their own context only brings that context into the judgment. The validation script handles checking the format and the rules.

The exception is the audit in the four skills covered under "Separating the writer from the auditor" below. For these four skills, always launch the auditor after confirming that the mechanical validation has passed.

## Separating the writer from the auditor

`job-change-profile`, `job-change-self-analysis`, `job-change-company-research`, and `job-change-documents` keep the role that creates a deliverable separate from the role that audits it. The auditor is never given the reasoning behind the writer's decisions; it judges from the deliverable and the specification alone. Holding no context from the writer's side is a condition of the judgment, and rereading it in the same context is no substitute. This cost is paid to catch exaggeration, fabrication, and a mismatch with the specification apart from the writer's own intent.

On a harness that cannot launch sub-agents, the same body handles both writing and auditing in the same context, which lowers this independence. In that case, during the audit stage, never refer to the reasoning behind the writer's decisions, the points of hesitation, or the history of revisions; judge from the deliverable and the canonical definition (the specification in `references/`) alone. Do not read the writer's intent into it until the judgment is complete.
