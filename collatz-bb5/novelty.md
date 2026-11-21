# Is any of this new? (Literature check, Nov 2026)

Short answer: **no.** Every result here is known, or is an elementary rephrasing of something known. What this folder
adds is putting the pieces side by side and re-checking them numerically.

| Item | Status | Source |
|---|---|---|
| BB(5) champion computes `3k→5k+6`, `3k+1→5k+9` | Known (Michel, 1993); proving that this kind of map converges in general is still open | [bbchallenge wiki: Collatz-like](https://wiki.bbchallenge.org/wiki/Collatz-like), [Michel survey](https://ar5iv.labs.arxiv.org/html/0906.3749) |
| Geometric mean √(3/4) < 1 gives log-drift ½ln(3/4); 5n+1 drifts upward | Standard heuristic (Crandall 1978, Lagarias 1985). The AM–GM wording is just Jensen's inequality | [Lagarias overview](https://arxiv.org/pdf/2111.02635), [annotated bibliography](https://arxiv.org/pdf/math/0309224) |
| AM–GM cycle bound, no cycle with ≤ 60 odd steps | Classical method (Steiner 1977, Eliahou 1993, Simons–de Weger). **Far weaker than the records:** K > 7.2·10¹⁰ odd terms, and no m-cycles with m ≤ 91 (Hercher 2023) | [Hercher, JIS 2023](https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/hercher5.html), [arXiv:2201.00406](https://arxiv.org/abs/2201.00406) |
| Inverse tree grows by 4/3 per level | Standard heuristic. The rigorous counterpart is Krasikov–Lagarias (≥ x^0.84 of numbers below x reach 1). The "depth dimension 0.415" is only a relabelling | Lagarias overview (above) |
| Parity vectors ↔ n mod 2^k is a bijection | Terras 1976 / Everett 1977 | Lagarias overview |
| Transformer / "tokenization" analogy | Already **tested experimentally**: transformers trained on Collatz learn one residue class mod 2^p at a time, which matches the Terras structure | [Charton & Narayanan 2025, arXiv:2511.10811](https://arxiv.org/abs/2511.10811) |
| No potential with a bounded or residue-only correction; max-mean-cycle framing; negative cycles as the obstruction | Folklore. The same max-mean-cycle framing appears in an unreviewed GitHub project | [tuliomarchetto/collatz](https://github.com/tuliomarchetto/collatz) |
| Uncertified density → 0 | Terras 1976 (almost all n have finite stopping time); Tao 2019 is much stronger | Lagarias overview |

Possibly a new framing, but not a new result: the bound "any working g must reach 0.91·log n" (from the excursion at
n=159487) is just the known path-record data restated as a cost for potential functions.

Note: many "proofs" of Collatz via Lyapunov or entropy arguments are circulating on Zenodo, ResearchGate and similar
sites. §3 of `potential.md` shows why that kind of argument has to fail unless it controls orbit maxima.
