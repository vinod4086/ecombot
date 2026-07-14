# eComBot Production Readiness Checklist

## Guardrails

- [x] Input guard blocks common prompt-injection attempts.
- [x] Input guard returns structured decision `{allowed, reason, action}`.
- [x] Output guard redacts common PII patterns.
- [x] Blocked states return user-visible messages.

## Tool Safety

- [x] Order ID validation enforced before order tools.
- [x] Cancellation requests require explicit confirmation.
- [x] Support flow only exposes support-safe tool operations.

## Observability

- [x] Orchestrator emits route and trace metadata for every turn.
- [x] Latency captured for voice loop stages.
- [x] LangSmith API key wiring present in config.

## Evaluation

- [x] PromptFoo config includes 10+ representative scenarios.
- [x] Safety scenarios included (injection, PII, off-topic, malformed tool args).

## Operational Hygiene

- [ ] Verify `.env` contains keys only in local env, not committed.
- [ ] Run all manual test guides Day01-Day13.
- [ ] Validate docker services and health endpoints before demo.
