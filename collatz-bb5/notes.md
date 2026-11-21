# A small stab at Collatz: BB(5), AM–GM, lightning trees, attractors

**This does not prove Collatz.** It's four lenses on the problem, each backed by a run of
[`experiments.py`](experiments.py) (output in [`output.txt`](output.txt)). We use the shortcut map
`T(n) = n/2` (n even), `(3n+1)/2` (n odd).

## 1. BB(5) as the baseline: Collatz-like behaviour is where provability gets hard
- The BB(5) champion `1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA` halts after **47,176,870** steps with **4,098** ones (we re-ran it).
- Pascal Michel showed it's really computing a Collatz-like map: `g(3k)=5k+6`, `g(3k+1)=5k+9`, halt on `3k+2`.
  From 0 it takes **14** iterations and halts at 12284 ≡ 2 (mod 3).
- Proving BB(5) = 47,176,870 (bbchallenge, 2024) meant ruling out every 5-state machine that never halts. The hardest
  holdouts at 6 states (e.g. "Antihydra") are open Collatz-type problems. Conway (1972) showed generalised Collatz maps
  can run any program, so no single method settles them all.
- **Takeaway:** about 5–6 states is where Collatz-type questions show up. Any proof of Collatz has to use something
  specific to `3n+1`, not just the general "mod-m affine map" shape.

## 2. AM–GM in the n/2 step: why 3 sits right on the edge
Per step, `T` multiplies n by about **3/2** (odd) or **1/2** (even), and each is equally likely (see §4).
- Arithmetic mean of the multipliers: (3/2 + 1/2)/2 = **1**, so a typical step neither grows nor shrinks n on average.
- Geometric mean: √(3/4) ≈ **0.866 < 1**. AM–GM is strict here because 3/2 ≠ 1/2.
- What compounds over many steps is the geometric mean. So the typical log-drift is ½·ln(3/4) = **−0.1438**/step.
  Measured on random 200-bit numbers: **−0.1441**.
- For 5n+1: AM = 1.5, GM ≈ 1.118 > 1, so numbers drift upward. That matches the known divergent-looking orbits of 5n+1.
  So `3` is the largest odd q whose GM is below 1. Collatz depends entirely on this AM–GM gap.

**A rigorous use of AM–GM (no cycles with few odd steps).** Suppose a cycle has m steps, k of them odd, with odd
elements n_i. Multiplying around the cycle gives `2^m = 3^k ∏(1 + 1/(3n_i))`. By AM–GM and `1+x ≤ eˣ`:
`ln(2^m/3^k) ≤ k/(3·n_min)`, so `n_min ≤ k / (3·ln(2^m/3^k))`.
For every k ≤ 60, this bound is at most **1192** (the worst case is k=41, m=65, near a continued-fraction convergent
of log₂3). Every n ≤ 1192 reaches 1, so **no nontrivial cycle has ≤ 60 odd steps.** The trivial cycle 1→2→1 has
k=1, m=2, giving `n_min ≤ 1.16`, so it sits right at the bound. The published records (Eliahou; Simons–de Weger;
Hercher) push the same argument much further using continued fractions and verified ranges.

## 3. Fractal growth: the inverse tree is a lightning discharge
Grow the tree backwards from 1 (n → 2n always; n → (2n−1)/3 when that is a whole number). It branches like
dielectric-breakdown / DLA lightning, except that branching is set by n mod 3 rather than by a random field.
- Level sizes grow by **1.3331×** per level, against a heuristic of 4/3 (an extra branch about ⅓ of the time).
- Each level roughly doubles the values reached (×2 per step), so the "depth dimension" is log(4/3)/log 2 ≈ **0.415**.
  That's a sparse, lightning-like set. Krasikov–Lagarias proved that at least x^0.84 of the numbers below x reach 1.
  The gap between 0.415 and 1 is the part that comes from branches merging, and that is still unproven.
- In lightning, the main channel is the branch that wins the competition with the others. In Collatz, the claim is
  that the tree eventually fills **all** of ℕ. A fractal-dimension argument alone can't give dimension 1. You'd need
  to show that no infinite branch "screens off" a residue class.

## 4. Attractors, transformer-style
- **Tokenization (Terras):** the first k parity bits of n's orbit depend only on n mod 2^k, and every one of the 2^k
  bit strings occurs exactly once (checked for k=12). So parity "tokens" are i.i.d. fair coins. That's the
  justification for the 50/50 split used in §2.
- **The attractor:** {1, 2} is the conjectured unique global attractor. log n acts like an energy that decreases on
  average (−0.144/step), the way attention in a transformer acts like Hopfield-network energy descent (Ramsauer et
  al. 2020) and pulls the residual stream toward a few fixed points.
- **Basins:** the steps needed to drop below n follow the same geometric pattern (1: ½, 2: ¼, then 4/5, 7/8, …).
  These counts are exact consequences of the bijection above.
- **Where the analogy breaks:** in the 2-adic integers, T preserves measure and is ergodic (Lagarias), so it contracts
  nothing. The pull toward 1 exists only in the ordinary real metric, and only on average. A transformer's attractor
  comes from built-in contraction (LayerNorm, softmax). Collatz has no such contraction, which is why "average descent
  ⇒ every orbit descends" fails. Tao (2019) got as far as "almost all orbits reach almost bounded values".

## Synthesis
| Lens | What it gives | What's missing |
|---|---|---|
| BB(5) | Collatz-type maps sit at the edge of what can be decided | a 3n+1-specific invariant |
| AM–GM | the cause of the descent (GM < AM = 1); a proof of no short cycles | turning "on average" into "every orbit" |
| Lightning/DLA | the inverse tree grows at 4/3, depth dimension 0.415 | proving the branches eventually cover every n |
| Attractor/transformer | parity bits are fair coins; log n as a Lyapunov energy | a contraction that holds for every orbit |

A possible line to pursue: combine §2 and §4 into a **potential function** `V(n) = log n + c·f(n mod 2^k)`, built so
that the AM–GM gap shows up in every single window of k steps, not just on average. A V that strictly decreases
everywhere would prove the conjecture. The no-short-cycles result is the one piece of this that is actually proved.
