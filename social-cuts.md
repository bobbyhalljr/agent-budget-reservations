# LinkedIn

Two agent calls check the same 100-unit budget. Each wants 60. Both pass. The bill is 120.

The bug is the gap between checking capacity and reserving it.

I built a tiny TypeScript ledger that reserves before dispatch, keeps the hold when the outcome is unknown, and settles from a trusted receipt.

20 local checks pass. The fixture admits one call, holds 60, and leaves 40 available. A 35-unit receipt restores availability to 65.

Synthetic units. One process. No model call or real billing. Same-key accounting is not dispatch deduplication, and an estimate is not an enforceable cap.

This is the kind of boundary I think about while building Roster: shared resources need application controls.

Article: DEV_URL
Code: https://github.com/bobbyhalljr/agent-budget-reservations

# X thread

1. Two agent calls check a 100-unit budget. Each wants 60. Both pass. The bill is 120.

Build a tiny TypeScript reservation ledger: reserve before dispatch, keep the hold after a timeout, settle from a receipt.

2. The fixture admits one call: 60 held, 40 available. A receipt for 35 leaves 65 available.

20 checks pass. Same-key admission avoids a second hold. It does not deduplicate dispatch. An unknown outcome is not permission to refund capacity.

3. Synthetic units, one process, no model call. Hard ceilings need enforceable caps, durable atomic reservations and reconciliation.

DEV_URL
https://github.com/bobbyhalljr/agent-budget-reservations
