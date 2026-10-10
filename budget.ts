export type State = 'held' | 'unknown' | 'settled' | 'released';
type Hold = { cap: number; state: State; actual?: number };
const units = (n: number) => {
  if (!Number.isSafeInteger(n) || n < 0) throw new Error('invalid units');
};
// One process, synchronous transitions, trusted caller. No await inside reserve.
export class Budget {
  #holds = new Map<string, Hold>();
  #spent = 0;
  #limit: number;
  constructor(limit: number) { units(limit); this.#limit = limit; }
  snapshot() {
    const held = [...this.#holds.values()]
      .filter(h => h.state === 'held' || h.state === 'unknown')
      .reduce((sum, h) => sum + h.cap, 0);
    return { spent: this.#spent, held, available: this.#limit - this.#spent - held };
  }
  reserve(id: string, cap: number): boolean {
    units(cap);
    if (!id.trim() || cap === 0) throw new Error('invalid reservation');
    const old = this.#holds.get(id);
    if (old) {
      if (old.cap !== cap) throw new Error('key conflict');
      // A retry cannot reuse a consumed or cancelled reservation.
      return old.state === 'held' || old.state === 'unknown';
    }
    if (cap > this.snapshot().available) return false;
    this.#holds.set(id, { cap, state: 'held' });
    return true;
  }
  unknown(id: string) {
    const h = this.#get(id);
    if (h.state === 'held') h.state = 'unknown';
    else if (h.state !== 'unknown') throw new Error('terminal reservation');
  }
  settle(id: string, actual: number) {
    units(actual);
    const h = this.#get(id);
    if (actual > h.cap) throw new Error('cap exceeded: reconcile externally');
    if (h.state === 'settled') {
      if (h.actual !== actual) throw new Error('settlement conflict');
      return;
    }
    if (h.state === 'released') throw new Error('released reservation');
    this.#spent += actual;
    h.actual = actual;
    h.state = 'settled';
  }
  releaseBeforeDispatch(id: string) {
    const h = this.#get(id);
    // Caller must prove dispatch never began. A timeout is not that proof.
    if (h.state === 'released') return;
    if (h.state !== 'held') throw new Error('cannot release');
    h.state = 'released';
  }
  #get(id: string): Hold {
    const h = this.#holds.get(id);
    if (!h) throw new Error('missing reservation');
    return h;
  }
}
