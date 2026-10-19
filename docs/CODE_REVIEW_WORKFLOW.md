# Website development and automatic model routing

| Stage | Model / effort |
| --- | --- |
| Clear, bounded, low-risk simple or repetitive work, including safe small documentation edits and mechanical code edits with obvious intent | GPT-6 Luna / medium |
| Ambiguous work, behavior changes, nontrivial debugging or cross-cutting implementation | GPT-6.1 Sol / medium |
| Reproduced difficult implementation defect | GPT-6.1 Sol / high |
| Useful bounded read-only inventory | GPT-6 Luna / medium |
| Architecture or unresolved cross-module defect | GPT-6 Astra / high |
| Independent review of credentials, publishing or durable state | GPT-6 Astra / high |

Apply this table automatically at each meaningful stage, including resumed work.
For Luna work, keep one implementation owner and escalate if the task becomes
ambiguous, changes behavior, requires nontrivial debugging or crosses subsystem
boundaries. A small diff does not reduce the risk of publishing, credential or
durable-state work; retain its applicable implementation and independent review
routes.
Do not ask the operator to repeat model selection while a supported route exists.
Verify the tool accepts the exact model ID and reasoning effort, then pass both
explicitly when dispatching: `gpt-6-luna`/`medium` for clear bounded low-risk
simple work, `gpt-6.1-sol`/`medium` for ambiguous, behavior-changing, nontrivial
or cross-cutting implementation, `gpt-6.1-sol`/`high` for a reproduced
difficult defect, and `gpt-6-astra`/`high` for architecture or required
independent safety review.

A user-confirmed parent selection persists until the user changes it; record it
as user-confirmed rather than runtime telemetry. Work directly when the parent
matches the permitted role. If it is unknown or a different model is needed,
assign that stage to one explicitly routed agent and let the parent coordinate.
Keep one owner per implementation scope and at most one necessary bounded
reviewer; no duplicate implementation or recursive delegation. Preserve explicit
user overrides and existing attempt/review limits.

The supported mechanism is model-specific agent dispatch. It does not change
an already-running parent chat's selector. Defaults configure new work/agents;
when reload is unverified, use explicit dispatch. Never edit application databases
or claim a switch from a config change. Record the requested model/effort, dispatch
acceptance, owned scope and terminal result; distinguish those from independently
observed serving-model identity. Ask for selection or fallback only when every
supported route for a required stage is unavailable. A required independent
review stays outstanding until a permitted reviewer completes it.

Routing grants no provider spend, publication, deployment, credentials, trading,
asset selection or approval authority. GitHub Actions executes deterministic
checks; it does not select the chat model or launch paid AI work.

Supported controls: [official subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents).

For website work, validate the actual site with `python scripts/validate_site_seo.py`
and review code, public behavior and reliability before direct-to-main delivery.
Shared Camela skill source and automation-review details remain in the private
sibling repository. Do not copy private source or runtime data into this public
repository. Changes to this workflow grant no new publishing authority.

## Context discipline and handoffs (2026-10-19)

Use one bounded objective and a clear stop condition per work package. Keep closely related debugging with the same owner. At a milestone or interruption, write a 150–250 word handoff with the exact checkout, branch and HEAD; pending edits; validation actually run (separate from reported or historical results); open gates; one next bounded action; and authorization limits. Recommend a fresh chat when the objective changes, but create one only if the user asks. Do not create or message chats, compact or reset them, or resume paused, blocked or usage-limited goals merely to apply this policy. A handoff is evidence, not authority to resume.

Read mandatory current instructions and safety gates once per unchanged source snapshot. Use targeted reference sections and bounded evidence instead of bulk logs or history; reread sources when they change. Use existing scripts and run handles for waits; avoid repeated AI polling when a blocker is unchanged. Do not introduce timers or replace mandated schedule checks. Scheduled work due under standing authority and actionable recovery may continue; an unchanged blocker on one item does not stop unrelated actionable work.

Keep public-repository task notes outside tracked public content; never place private chat IDs, paths, media or secrets here. Preserve existing content-bound QA, approvals and applicable publishing gates. Context savings never waive them. Keep established schedules unchanged.

## Automatic resume preflight (2026-10-19)

On startup/resume, every user goal Resume, compaction recovery, and automatic
continuation after a checkpoint, perform this preflight automatically before
substantive edits, generation, CI, publishing, deployment or trading actions.
The user does not need to remind the agent to reread instructions.

1. Freshly read the applicable current root and worktree `AGENTS.md`, this
   project's workflow/routing rules and required safety documents for the next
   bounded action. Follow current production-guidance freshness requirements
   without switching or overwriting the active checkout. Within an active work
   package, read each source once per unchanged snapshot and reread on change;
   an explicit resume always requires a fresh read.
2. Find and read the latest handoff/checkpoint for this specific goal/task and
   exact checkout, using its identity and evidence chain rather than simply the
   newest file modification time. Reconcile its branch, HEAD, dirty source,
   validation actually performed and open gates with present evidence. Keep
   historical/reported results distinct from checks actually rerun. Preserve the
   owner, attempt counters, budgets, original assets, custody, locks,
   deduplication and content-bound approvals; checkpoints never reset them.
3. If the matching handoff is missing or stale, reconstruct a compact checkpoint
   from task-local evidence. If evidence cannot be reconciled, stop only the
   dependent actions, retain unknowns and ask the user only for information or
   authority necessary to proceed. Continue independently actionable work within
   its existing scope; one blocked item does not block unrelated authorized work.
4. Update one small `resume context checked` receipt in the existing private
   checkpoint, recording checked instruction versions, reconciled source/gates
   and next bounded action. Update in place rather than appending repetitive
   history. When no checkpoint exists, retain a bounded in-memory acknowledgement;
   do not create public task notes or expose private identifiers in tracked source.

Saving, reading or installing this rule is not authority to resume any goal.
The user's actual Resume action authorizes continuing that existing goal within
its prior scope; it grants no new provider spend, deployment, publication,
trading or approval rights and does not override a later stop/cancellation.
Existing due schedules and authorized recovery continue under their own standing
authority. Do not change schedules, model configuration or hooks to implement
this behavioral requirement.

This is a mandatory agent instruction, not a claim of runtime enforcement or
live verification. Session-start resume hooks do not establish that a hook runs
for every goal Resume. Existing chats adopt saved rules when they next read
instructions; there is no implied hot reload.
