# Agent budget reservations

A dependency-free TypeScript demonstration of budget admission, active holds, unknown outcomes and trusted-receipt settlement. Two synthetic 60-unit calls reproduce overspending against a 100-unit balance. A synchronous reservation admits only one.

Article: [Your Agent's Budget Check Has a Race Condition](https://dev.to/bobbyhalljr/your-agents-budget-check-has-a-race-condition-build-a-reservation-ledger-in-typescript-2dbe).

## Run

Node.js 22.20.0 or newer, with npm on PATH. No dependencies or API key.

```bash
git clone https://github.com/bobbyhalljr/agent-budget-reservations.git
cd agent-budget-reservations
npm test
```

`npm test` runs `node --experimental-strip-types test.ts`. Node strips types; it does not type-check. The full output is in [test-output.txt](test-output.txt).

```text
20/20 checks passed
naive: admitted=2, spent=120, limit=100
reserved: admitted=1, held=60, available=40
timeout: held=60, available=40
receipt: spent=35, held=0, available=65
```

## Files

- `budget.ts`: synchronous in-memory reservation state machine.
- `test.ts`: 20 named boundary checks plus asserted asynchronous race fixtures.
- `article.md`: illustrated tutorial.
- `images/`: cover and three diagrams, generated from `make_images.py` with Pillow.

## Limits

Synthetic units, one process and trusted callers. No model call, real billing, durability, database locks, authentication, receipt verification, or dispatch deduplication. The cap must bound actual spend for the capacity invariant to represent a hard ceiling. Over-cap receipts are rejected with the hold retained and need external reconciliation; this is not full overrun accounting. Same-key admission is accounting idempotency, not dispatch authorization. Only a caller that proves dispatch never began may release a held reservation. Unknown holds never expire automatically.

## References

- [Node TypeScript execution](https://nodejs.org/api/typescript.html)
- [PostgreSQL row locking](https://www.postgresql.org/docs/18/explicit-locking.html), relevant to a future durable implementation, not implemented here.