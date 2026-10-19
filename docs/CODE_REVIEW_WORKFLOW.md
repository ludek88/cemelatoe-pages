# Website development and automatic model routing

| Stage | Model / effort |
| --- | --- |
| Implementation, tests, docs, ordinary debugging | GPT-6.1 Sol / medium |
| Reproduced difficult implementation defect | GPT-6.1 Sol / high |
| Architecture or unresolved cross-module defect | GPT-6 Astra / high |
| Independent review of credentials, publishing or durable state | GPT-6 Astra / high |
| Useful bounded read-only inventory | GPT-6 Luna / medium (optional) |

Apply this table automatically at each meaningful stage, including resumed work.
Do not ask the operator to repeat model selection while a supported route exists.
Verify the tool accepts the exact model ID and reasoning effort, then pass both
explicitly when dispatching: `gpt-6.1-sol`/`medium` for routine implementation,
`gpt-6.1-sol`/`high` for a reproduced difficult defect, `gpt-6-astra`/`high` for
architecture or required independent safety review, and optional
`gpt-6-luna`/`medium` for useful bounded read-only inventory.

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
