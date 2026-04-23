## Context

This change creates an OpenSpec-inspired workflow for agent self-improvement: define evals for a particular agent, design how those evals will run, specify the required subsystems, and then apply the plan to add a GEPA optimization loop. OpenSpec's repo is the primary product reference for the workflow shape: repo-local artifacts, lightweight phases, agent-readable instructions, and an apply step that turns approved artifacts into implementation.

The current repo already contains a working GEPA plus Claude Managed Agents prototype. The important reference patterns are:

- GEPA uses `optimize_anything(...)` with a text-representable candidate, dataset or validation set, evaluator, objective, background, and reflection configuration.
- The evaluator compiles a candidate into Claude Managed Agents resources, runs sessions, returns a numeric score, and records structured `side_info`.
- Claude Managed Agents are built from persistent Agent resources, Environment templates, Sessions, and event streams. Agent configuration lives on the Agent, while each evaluation run starts a Session against an Environment.
- Skill authoring should stay concise and progressively disclose reference material through `references/`, templates, and scripts instead of putting every detail in `SKILL.md`.

The first implementation is intentionally narrow: it supports Claude Managed Agents only. Other runtimes can be added later once the workflow proves useful.

## Goals / Non-Goals

**Goals:**

- Create a skill-driven workflow that helps users define evals for a target Claude Managed Agent.
- Make the proposal stage capture the eval contract: input examples, expected outputs, numeric scoring, qualitative rubric, and unknowns the user wants the agent to help resolve.
- Make the design stage require discovery of how the target Managed Agent is currently created, configured, run, streamed, and evaluated.
- Make the design stage define the eval runner and optimizer system: how users invoke it, how rollouts are created, how traces are captured, how scores and ASI are produced, and how GEPA runs are configured.
- Use this repo's GEPA plus Claude Managed Agents implementation as bundled reference material for the skills.
- Produce specs and tasks that are concrete enough for an apply skill to implement an eval runner and GEPA optimization loop in a target repo.
- Keep the workflow close to OpenSpec's artifact-guided development model while adapting the content to evals and self-improvement.

**Non-Goals:**

- Build a full OpenSpec replacement, dashboard, CLI, archive system, or general schema engine in the first version.
- Support Codex, local shell agents, custom tool-loop agents, or other runtimes in the first version.
- Require users to know the final scorer or eval schema before starting; the workflow should support collaborative discovery.
- Force target repos to copy this repo's exact package layout if their existing agent architecture differs.
- Optimize arbitrary binary artifacts or non-text candidate surfaces in the first version.

## Decisions

### 1. Model the workflow after OpenSpec artifacts, but make eval definition the domain contract

The skill workflow will use the same conceptual artifact progression as OpenSpec: proposal, design, specs, tasks, and apply. The proposal is not a generic product proposal; it is the eval contract for one target agent or agent family. It must capture:

- target agent identity and runtime assumptions
- representative input cases
- expected output shape or examples
- numeric scoring intent, preferably normalized to `0.0` through `1.0`
- qualitative scoring rubric and reviewer guidance
- uncertainty, missing examples, or areas where the coding agent should help discover better eval design

Rationale: OpenSpec's value comes from making intent explicit before implementation. For this system, the most important intent is not only "what to build" but "what counts as better agent behavior."

Alternatives considered:

- Start from implementation tasks only.
  Rejected because weak eval definitions produce misleading GEPA optimization runs.
- Require a fully formal eval schema up front.
  Rejected because many users will know the desired behavior before they know the best scorer.

### 2. Keep artifacts repo-local and human-readable

The workflow should write artifacts into a predictable repo-local directory such as `gepa-evals/changes/<name>/` or another directory chosen by the installed skill. Each change should contain:

- `proposal.md`
- `design.md`
- `specs/<capability>/spec.md`
- `tasks.md`

Reference templates may also include structured snippets for eval cases or scorers, but Markdown remains the primary planning surface.

Rationale: This follows OpenSpec's strongest pattern: artifacts are inspectable, reviewable, and easy for any coding agent to consume. It also avoids making a database or hosted service a prerequisite.

Alternatives considered:

- Store the workflow only in chat history.
  Rejected because GEPA/eval implementation needs durable context.
- Start with a custom CLI and state machine.
  Deferred because the first version can be delivered as skills plus artifacts.

### 3. Split the skill pack into planning skills and an apply skill

The system should ship as a small skill pack rather than one large monolithic skill:

- a start/new skill to create an eval change and gather the eval contract
- a continue skill to create the next artifact from dependencies
- an apply skill to implement the approved eval and GEPA loop
- optional verify/archive skills after the core workflow works

Each skill should keep `SKILL.md` short and load detailed references only when needed. Shared references should include OpenSpec workflow notes, Claude Managed Agents runtime notes, GEPA evaluator patterns from this repo, eval-scorer patterns, and artifact templates.

Rationale: OpenSpec's command model maps cleanly to skills. Splitting responsibilities keeps trigger descriptions precise and reduces context loaded for simple actions.

Alternatives considered:

- One skill that does everything.
  Rejected because it would become large, harder to trigger correctly, and harder to test.
- Build only an apply skill.
  Rejected because apply quality depends on proposal/design/spec/task quality.

### 4. Require target-agent discovery during design

The design artifact must tell the coding agent to inspect the target repo before proposing an eval architecture. For Claude Managed Agents, discovery should identify:

- language and SDK surface used by the target repo
- where Agents, Environments, Sessions, tools, skills, MCP servers, resources, and event streams are configured
- whether agents are created once and referenced by ID, or created per run
- how task inputs are provided and outputs are collected
- where logs, traces, run artifacts, and errors can be captured
- which agent fields are realistic GEPA candidate fields

Rationale: eval infrastructure must fit the target agent's actual runtime. The apply skill should adapt this repo's GEPA patterns rather than paste them blindly.

Alternatives considered:

- Assume the target repo has the same Python layout as this prototype.
  Rejected because users will bring existing agents with different structure.
- Make the proposal gather all runtime details.
  Rejected because design is the right phase for technical discovery.

### 5. Use a GEPA-compatible evaluator contract as the implementation boundary

The apply workflow should implement or adapt an evaluator that accepts a candidate and an eval example, runs the target Claude Managed Agent, and returns:

- `score`: numeric scalar, preferably `0.0` through `1.0`
- `side_info`: structured diagnostics including input, expected output, actual output, qualitative judgement, runtime errors, trace excerpts, and field-specific feedback

Datasets should be split into train and validation sets when enough examples exist. The optimizer should pass objective and background text that explain the target agent, eval goal, candidate fields, and scoring rubric.

Rationale: This matches GEPA's `optimize_anything(...)` boundary and this repo's current evaluator pattern while allowing target-specific scorer implementations.

Alternatives considered:

- Optimize only prompts through a bespoke script.
  Rejected because the system should support richer agent self-improvement over time.
- Require users to write Python scorer functions manually before the workflow starts.
  Rejected because the skills should help generate those from examples and rubric.

### 5a. Define semantic runner entrypoints in design, then adapt command shape to the target repo

Every design artifact should define how the generated eval and optimization system is invoked. The exact command syntax can follow the target repo's conventions, but the apply skill must expose these semantic operations:

- `eval`: run one candidate against one split or selected eval cases without GEPA search
- `optimize`: run GEPA over the training set with the evaluator, objective, background, candidate surface, reflection settings, and budget
- `compare`: evaluate a baseline candidate and an optimized or user-provided candidate on the same examples and report score deltas
- `show-candidate` or equivalent: print the seed/current candidate so users can inspect what GEPA is mutating

A Python target repo might expose these as CLI commands, for example:

```bash
agent-self-improve eval --change gepa-evals/changes/<name> --candidate seed --split val --run-dir runs/<name>/eval
agent-self-improve optimize --change gepa-evals/changes/<name> --max-metric-calls 48 --run-dir runs/<name>/optimize
agent-self-improve compare --change gepa-evals/changes/<name> --baseline seed --candidate runs/<name>/optimize/best_candidate.json
agent-self-improve show-candidate --change gepa-evals/changes/<name>
```

For another project layout, the same operations might be package scripts, Make targets, Python module invocations, or existing app commands. The design artifact should name the chosen invocation surface, required environment variables such as `ANTHROPIC_API_KEY`, expected inputs, and output directories.

Rationale: users need an operational system, not just generated Python objects. OpenSpec-style apply should leave behind commands that can be run, debugged, and repeated.

Alternatives considered:

- Let the apply skill create hidden helper functions only.
  Rejected because users would not know how to run or compare evals.
- Mandate one global CLI name for every target repo.
  Rejected because apply should respect existing project conventions.

### 5b. Treat each rollout as candidate plus eval case plus Managed Agent session

The design should define a rollout lifecycle. A rollout is one execution of one candidate on one eval case. For Claude Managed Agents, the default lifecycle is:

1. Load the eval change artifacts, eval case, scorer config, and candidate.
2. Compile the candidate into the target agent configuration overlay.
3. Create or update candidate-specific Managed Agent resources as needed, preserving the target repo's normal setup pattern where possible.
4. Create or select the Environment required for the eval case.
5. Start a Session pinned to the candidate Agent version and Environment.
6. Attach eval inputs as user messages, files, repositories, or other Managed Agents resources.
7. Stream or poll events until idle, termination, timeout, or required user/tool action.
8. Collect final outputs, event types, tool calls, errors, usage, session IDs, resource IDs, and any generated files.
9. Run deterministic and/or qualitative scorers.
10. Build ASI with top-level feedback and candidate-field-specific feedback.
11. Persist rollout artifacts under a stable run directory.
12. Archive or clean up ephemeral Managed Agents resources when appropriate.

The default optimization path should create isolated candidate-specific resources for rollouts so candidate behavior does not leak between evaluations. A target repo may reuse long-lived Environments or existing Agent factories when that is the established local pattern, but the design must explain the reproducibility and cleanup strategy.

Rationale: GEPA's reflective evolution depends on small minibatch rollouts with useful traces, not only final scores. The rollout boundary is where runtime behavior becomes ASI.

Alternatives considered:

- Treat a rollout as only a scorer function call.
  Rejected because agent optimization requires session traces, tool behavior, output artifacts, and runtime failures.
- Reuse the production agent object for every candidate mutation.
  Rejected as the default because candidate mutations need isolated, reproducible execution.

### 5c. Build ASI as a first-class output of every rollout

The runner should produce ASI with a consistent structure that the reflection model can use directly. The baseline ASI shape should include:

- `Input`: eval input and relevant context
- `Expected`: expected output, output shape, or rubric target
- `Actual`: final answer, generated files, or observed behavior
- `Feedback`: concise qualitative judgement
- `Error`: exception, timeout, tool failure, or validation failure when present
- `Agent Trajectory`: summarized event stream, tool calls, and important state transitions
- `scores`: higher-is-better metrics such as correctness, rubric score, latency inverse, and cost inverse
- `<field>_specific_info`: targeted diagnostics for each candidate field GEPA may mutate

For Managed Agents, useful trajectory fields include session ID, agent ID and version, environment ID, event types, tool-use summaries, output file IDs, outcome explanations when available, usage, and cleanup errors. The ASI builder should include both failures and successes so reflection can identify what to preserve.

Rationale: ASI is the practical gradient for text optimization. If rollout artifacts do not explain why a candidate behaved well or badly, GEPA reflection becomes much closer to blind mutation.

Alternatives considered:

- Persist traces but keep ASI minimal.
  Rejected because GEPA consumes ASI during reflection; logs that humans can inspect later are not enough.

### 5d. Configure GEPA around reflection, not just search budget

The optimizer entrypoint should assemble:

- seed candidate
- train and validation examples
- evaluator that executes rollouts and returns `(score, side_info)`
- objective text from the artifacts
- background text describing the target agent and candidate fields
- reflection model
- component selection strategy
- per-field reflection prompt templates
- max metric calls and per-rollout runtime limits
- run directory and stdio/log capture settings

The default component selector should be chosen based on candidate-field coupling. Independent prompt/config fields can start with round-robin selection. Tightly coupled fields should be updated together. If ASI reliably identifies weak fields, a later custom selector can prioritize those fields.

Rationale: GEPA's reflective evolution works by choosing candidate components, evaluating minibatches with traces, building reflective data, and proposing targeted text changes. The workflow needs to design those reflection controls explicitly.

Alternatives considered:

- Only expose `max_metric_calls`.
  Rejected because poor reflection prompts or component selection can waste the entire budget.

### 6. Treat Claude Managed Agents as the only runtime adapter in v1

The runtime design should assume Claude Managed Agents and use its concepts directly: Agent, Environment, Session, resources, event stream, skills, tools, and optional MCP. The design should not introduce a provider-neutral runtime interface until a second runtime is actually being added.

Rationale: A premature runtime abstraction would obscure the important Managed Agents details. The first version should be excellent for one runtime before becoming generic.

Alternatives considered:

- Define a generic `AgentRuntime` interface immediately.
  Rejected because runtime differences matter most during eval design and apply.
- Support Codex and Managed Agents at the same time.
  Deferred until the Managed Agents flow is validated end to end.

### 7. Bundle reference material, not copied implementation blobs

The skill pack should include concise reference files derived from this repo and official skill guidance:

- GEPA candidate/evaluator/optimizer patterns from `src/claude_gepa/`
- Claude Managed Agents concepts needed for eval execution
- skill authoring conventions: concise frontmatter, progressive disclosure, references, validation
- OpenSpec workflow motivation and artifact examples
- scorer examples for exact match, rubric grading, structured output checks, and hybrid numeric/qualitative scoring

The apply skill should read these references and adapt patterns into the target repo. It should not require target repos to vendor this entire prototype unless that is the cleanest local implementation.

Rationale: Skills work best when they provide non-obvious procedural knowledge and reusable templates, not large context dumps.

Alternatives considered:

- Copy the prototype wholesale into every target repo.
  Rejected because it will conflict with existing agent architecture.
- Keep all reference content inside `SKILL.md`.
  Rejected because it violates progressive disclosure and bloats every skill invocation.

### 8. Validate the workflow with eval-like skill tests before broadening scope

The implementation should include sample target-agent fixtures or small test repos that exercise the skill workflow:

- proposal creation from clear eval examples
- proposal creation when scoring details are incomplete
- design creation after inspecting a Managed Agents repo
- apply creating runnable eval and GEPA entrypoints
- failure paths when the target repo is not a Claude Managed Agents project

Rationale: Anthropic's skill guidance recommends building evaluations before extensive documentation. This project is itself about eval-driven improvement, so the skill pack should be tested by realistic workflow scenarios.

Alternatives considered:

- Validate only by reading generated Markdown.
  Rejected because the hard part is whether another coding agent can use the skills to create and apply a coherent eval plan.

## Risks / Trade-offs

- [OpenSpec inspiration turns into accidental cloning] -> Keep the product reference explicit, but define requirements around eval and GEPA behavior rather than OpenSpec feature parity.
- [Proposal artifacts become too vague to drive GEPA] -> Require input/output examples, numeric scoring intent, qualitative rubric, and explicit unknowns before implementation.
- [Users may not know how to score their agent] -> Let the proposal phase include discovery questions and draft scorer options instead of blocking on a perfect rubric.
- [Apply skill may overfit to this repo's Python prototype] -> Require target-agent discovery and language/runtime detection before implementation.
- [Claude Managed Agents APIs and beta behavior may change] -> Keep API details in reference files and runtime adapters, and tell apply agents to verify against current official docs or installed SDK patterns before coding.
- [GEPA optimization may improve the scorer instead of true user value] -> Keep qualitative rubric text, validation examples, and side information visible in artifacts and run logs.
- [Skill pack context gets too large] -> Use progressive disclosure: short `SKILL.md`, one-level references, templates/assets for repeated content, and scripts only for deterministic checks.
- [Runtime costs are high] -> Start with small train/validation sets, support dry-run/direct-eval modes, and make GEPA budgets explicit in tasks.

## Migration Plan

1. Create the skill pack skeleton and shared references for OpenSpec-inspired workflow, GEPA patterns, Claude Managed Agents runtime guidance, and skill authoring rules.
2. Implement templates for proposal, design, specs, and tasks that are specific to agent eval and GEPA optimization.
3. Implement the start/new and continue skills so they create one artifact at a time and preserve dependency order.
4. Implement the apply skill so it reads completed artifacts, inspects the target Claude Managed Agents repo, and adds the eval runner, scorers, datasets, and GEPA optimization entrypoint.
5. Add validation fixtures that run the skills against small representative Managed Agents projects.
6. Refine artifact templates and references based on failed or ambiguous validation runs.

Rollback is straightforward while this is a skill pack: remove or disable the generated skills and leave target repos untouched unless the apply skill has been run. For target repos where apply has made changes, rollback follows normal source control because generated eval infrastructure should be committed as ordinary files.

## Open Questions

- What should the workflow directory be named in target repos: `gepa-evals/`, `agent-evals/`, or another project-specific path?
- Should the first implementation create a small CLI for status/instructions, or should skills manage artifact status directly from the filesystem?
- Which scorer templates should be included in v1: exact match, structured JSON match, LLM rubric grading, file-system checks, or all of these?
- Should generated GEPA candidates optimize only prompts initially, or include skills/environment/subagents when the target repo exposes those surfaces?
- Where should reusable skill references live in this repo so they can be installed cleanly into Codex and Claude Managed Agent environments?
