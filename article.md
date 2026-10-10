Two agent calls walk into a budget check. Both leave with permission to spend the same money.

You have 100 units left. Call A wants 60. Call B wants 60. Each checks the balance before either call finishes. Both pass. Your dashboard later explains that 120 is larger than 100. Excellent observability. Slightly late accounting.

The useful boundary is **reserve capacity before dispatch**, then settle it from a trusted receipt.

This tiny TypeScript build makes the race reproducible without an API key, a model, or a real bill. The units are synthetic. They are not dollars or provider token prices.

## The check is already stale

Here is the deliberately broken version from the fixture:

```ts
let naiveSpent = 0;
async function naive(cap: number) {
  if (naiveSpent + cap > 100) return false;
  await Promise.resolve();
  naiveSpent += cap;
  return true;
}
await Promise.all([naive(60), naive(60)]);
```

Both calls read zero before their continuations charge the budget. The final charge is 120.

You do not need two CPU threads to reproduce this. The asynchronous gap is enough. Keeping the check and reservation synchronous closes this particular gap inside one ledger instance. It does not coordinate separate workers.

![Two calls read the same zero balance, both pass a 60-unit check, then charge 120 against a 100-unit budget.](https://raw.githubusercontent.com/bobbyhalljr/agent-budget-reservations/main/images/race.png)

## Turn the balance into a reservation ledger

Track three quantities:

```text
available = limit - spent - active holds
```

A new call reserves its cap before any asynchronous work begins. Settling converts the hold into actual spend. Unused capacity becomes available again.

In the fixture, A reserves 60 of 100. B's request for another 60 is denied. When A's receipt reports 35, the ledger has 35 spent, no active hold, and 65 available.

The cap has to be a bound you can enforce or safely rely on. A model's guess about its eventual bill is not a bound. Count known input charges, bound output, and account for other billable work before applying this pattern to money. If the provider can charge more than the cap, this toy cannot promise a hard financial ceiling.

![A 60-unit reservation leaves 40 available; a 35-unit receipt releases the unused capacity and leaves 65 available.](https://raw.githubusercontent.com/bobbyhalljr/agent-budget-reservations/main/images/capacity.png)

The important part of `reserve` is small:

```ts
if (cap > this.snapshot().available) return false;
this.#holds.set(id, { cap, state: 'held' });
return true;
```

There is no `await` between the capacity check and the hold. The complete class also rejects invalid integers, empty keys, zero caps, and reuse of a key with a different cap.

Retrying the same active key does not reserve twice. That is accounting idempotency. It is **not permission to dispatch twice**. A separate dispatch owner and the tool's own idempotency contract still matter.

## Unknown is a state, not a refund policy

A call times out. Did the provider do the work? You do not know yet.

The ledger marks the reservation `unknown` and keeps all 60 units held. Available capacity stays at 40. It does not release the hold because a timer fired.

A trusted receipt can settle an unknown reservation. Repeating the same settlement is harmless. Changing its amount is rejected. A released or settled key cannot authorize fresh work.

![Held capacity remains reserved after an unknown outcome; only a trusted receipt settles it. Cancellation before dispatch can release capacity.](https://raw.githubusercontent.com/bobbyhalljr/agent-budget-reservations/main/images/timeout.png)

`releaseBeforeDispatch` is deliberately named. The caller must prove the dispatch never began. This ledger does not provide that proof. Do not call it from a generic timeout handler or a `finally` block after a request was sent.

If a receipt exceeds the cap, the toy rejects settlement and retains the hold. That is an escalation signal, not correct accounting for the larger bill. A production system must record the actual overrun, block or review further admissions, and reconcile the budget. Silently pretending the cap was the charge would make the dashboard look better than the bank account.

## Run the build

Public source: [bobbyhalljr/agent-budget-reservations](https://github.com/bobbyhalljr/agent-budget-reservations).

Use Node.js 22.20.0 or newer. No dependencies or API key are required.

```bash
git clone https://github.com/bobbyhalljr/agent-budget-reservations.git
cd agent-budget-reservations
npm test
```

The script runs TypeScript with Node's type stripping. [Node documents the supported syntax and its limits](https://nodejs.org/api/typescript.html); type stripping executes the file and does not type-check it.

The run prints 20 named checks, followed by these exact summary lines:

```text
20/20 checks passed
naive: admitted=2, spent=120, limit=100
reserved: admitted=1, held=60, available=40
timeout: held=60, available=40
receipt: spent=35, held=0, available=65
```

The fixture also asserts both admission outcomes and the final balances. Tests cover changed keys, repeated receipts, cancellation, terminal keys, unsafe amounts, missing reservations, unknown outcomes, and over-cap receipts. These are deterministic local checks, not evidence about a provider's billing behavior.

## Where the toy stops

This is an in-memory ledger for one process with trusted callers. Restarting loses the holds. Separate instances have separate budgets. There is no authenticated tenant boundary, receipt verifier, durable dispatch ownership, pricing engine, database transaction, or reconciliation worker.

For multiple workers, make the reservation transition durable and atomic. One database design is to lock the account row, check available capacity, insert a uniquely keyed reservation, and update held capacity in the same transaction. [PostgreSQL's row-lock documentation](https://www.postgresql.org/docs/18/explicit-locking.html) explains how conflicting row operations wait for the transaction to finish. The toy does not implement or test that database design. Do not hold a database lock during the external model call.

Unknown holds also need an operational home: an age, an owner, a receipt lookup, and an escalation path. An expiry time can trigger reconciliation. It cannot prove the provider did no work.

I am building Roster around AI employees that do real work. Real work consumes shared resources. A budget printed in the prompt is useful context. A reservation before dispatch is the application boundary.
