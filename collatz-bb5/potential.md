# Attempt: a potential function V(n) = log n + g(n)

Goal (from the end of [`notes.md`](notes.md)): find a correction g so that V strictly decreases along every orbit of
`T(n) = n/2` (even) / `(3n+1)/2` (odd). That would prove Collatz. Code: [`potential.py`](potential.py), output:
[`potential_output.txt`](potential_output.txt).

**Result: the direction fails as stated.** Below is why, plus the part that does work.

## 1. Bounded corrections cannot work
**Claim.** Let g ≥ −C, and suppose V is nonincreasing along orbits. Then `g(n) ≥ log(M(n)/n) − C`, where M(n) is the
largest value in n's orbit.
*Proof:* for every j, `log n + g(n) = V(n) ≥ V(Tʲn) ≥ log Tʲn − C`. Now take j to be the step where Tʲn = M(n). ∎

For n = 2^K − 1 the orbit climbs for K steps to 3^K − 1. So `g(2^K−1) ≥ K·log(3/2) − C`, which means
`limsup g(n)/log n ≥ log₂(3/2) ≈ 0.585`. In particular, a g that depends only on n mod 2^j takes finitely many values,
so it is bounded and can't work.

Numerically (n < 10⁶), with the full orbit max: g has to reach **1.56·log n** (at n=27) and still **0.91·log n** for
n ≥ 1000 (at n=159487).

## 2. The obstruction is 2-adic, coming from the negative integers
A residue-based g exists exactly when every cycle in the transition graph on ℤ/2ʲ has negative total log-weight (a
max-mean-cycle condition). Karp's algorithm gives a maximum of **log(3/2) for every j = 1…8**. That maximum is the
2-adic fixed point −1 (T(−1) = −1). The other positive-weight cycles are the known negative-integer cycles:

| cycle (min element) | length m | odd steps k | k·ln3 − m·ln2 |
|---|---|---|---|
| −1 | 1 | 1 | **+0.406** |
| −10 (… −5, −7) | 3 | 2 | **+0.118** |
| −136 (the −17 cycle) | 11 | 7 | **+0.066** |

A cycle of positive integers would need the opposite sign: `2^m = 3^k ∏(1+1/(3nᵢ)) > 3^k`. So a g that looks only at
2-adic digits can't tell a hypothetical positive cycle apart from these negative ones. Any working g has to use the
real-number side of the problem (the sign, and the size of the +1 terms).

## 3. What a working g has to be
By §1, any g that works is at least about log(M(n)/n). Conversely, `V(n) = log M(n)` is nonincreasing (not strictly),
and it is finite exactly when the orbit is bounded. So the potential-function approach is **equivalent** to proving
there are no divergent orbits, which is half of Collatz. The approach is circular, not a shortcut.

## 4. What does work: window certificates for almost all n
For each residue class mod 2^k we check whether the parity path reaches 3^a < 2^j for some j ≤ k. If it does, that
class descends below its starting value (apart from finitely many small n). The density of classes that never get
such a certificate is:

| k | 10 | 20 | 50 | 100 | 200 |
|---|---|---|---|---|---|
| uncertified density | 6.3e-2 | 2.6e-2 | 3.3e-3 | 2.4e-4 | 3.1e-6 |

This density tends to 0, which is the classical statement that "almost all n have finite stopping time" (Terras 1976,
Everett 1977). The leftover classes are exactly the 2-adic neighbourhoods of the obstruction in §2.

**Bottom line:** a potential of the form log n + (something that depends only on residues, or is bounded) is
impossible. The only versions that would work need to know how high each orbit goes, which is equivalent to proving
orbits are bounded.
