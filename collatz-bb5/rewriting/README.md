# Collatz as string rewriting: SAT/matrix-interpretation experiments (work in progress)

- `srs.py`: the Yolcu–Aaronson–Heule 11-rule mixed binary/ternary system for Collatz, a simulator that checks
  it reproduces Collatz orbits, and a small termination prover. The prover searches for natural matrix
  interpretations with z3, removes rules one round at a time, and checks each certificate independently in
  pure Python.
- `run_removals.py` → `removals.txt`: re-derives YAH's "T minus one rule terminates" results.
  **Status:** 7/11 proved (`tR→2R`, `f1→0t`, `f2→1f`, `fR→R`, `L0→Lt`, `t0→1t`, `t1→2f`). The run was stopped
  before `f0→0f`, `t2→2t`, `L1→Lff` and `L2→Lft` finished; YAH proved all 11. Those 7 came from a version
  without the independent certificate check.
- `michel.py`: a 27-rule rewriting encoding of the BB(5) champion's Collatz-like map
  (3k→5k+6, 3k+1→5k+9, halt on 3k+2). It is checked against the map for n < 3000. Whether this map halts from
  every start is open (bbchallenge wiki). `run_michel.py` will try to prove termination; it has not been run yet.

**Observation:** all 11 single-rule-removed subsystems terminate. So, by the rule-removal theorem, proving
that any nonempty rule set S fires only finitely often in the full system, SN(S/T), is equivalent to Collatz.
Subsystem-type weakenings are therefore exhausted at "remove one rule". A strictly stronger weakening has to
change the question itself, not just drop or relativise rules.
