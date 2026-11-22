# The Lean "proof" of the Riemann Hypothesis — a plain-language summary

**Subject:** [eagnespuerto/riemann-hypothesis-lean](https://github.com/eagnespuerto/riemann-hypothesis-lean), a fork of an unmodified mirror of the Lean code Levent Alpöge published on 2026-11-20 (announcement: <https://alpo.ge/remark.pdf>).
**Written for:** someone comfortable with algebra through Calculus 1 who has watched some 3Blue1Brown / Numberphile-type videos.
**Update (2026-11-22):** the proof has since been independently built and checked (Sutherland at MIT, plus two other groups), and the Lean and Mathlib communities certified it on 21 November. For a lighter, formula-free version, see [POP-MATH.md](POP-MATH.md). For a longer part-by-part version with sources, see [LONG-EXPLAINER.md](LONG-EXPLAINER.md). The "how much should you believe it" section below reflects the situation on release day.
**Status (2026-11-20):** a *claimed* proof. As far as I know no one has independently compiled and checked the code yet, and I did not compile it here: it is about 17 million lines and needs a very large machine. Everything below comes from reading the source files and the author's 4-page note.

---

## 1. What the Riemann Hypothesis says (a quick refresher)

The **zeta function** begins as an infinite sum

$$\zeta(s) = 1 + \frac{1}{2^s} + \frac{1}{3^s} + \frac{1}{4^s} + \cdots$$

For real $s>1$ this is a convergent p-series from Calc 2. Euler noticed that it also equals a product over the primes, $\prod_p \frac{1}{1-p^{-s}}$, so zeta "knows about" the primes.

Riemann let $s$ be a **complex number** and extended the function to the whole plane (the "analytic continuation" in the videos). It has:

- **trivial zeros** at $-2, -4, -6, \dots$, which are boring;
- infinitely many **non-trivial zeros**, all known to lie in the strip $0 < \text{Re}(s) < 1$ (the "critical strip").

**RH:** every non-trivial zero has real part exactly $\tfrac12$. In other words, they all sit on one vertical line, the "critical line".

Why it matters: the zeros act like frequencies in a Fourier series for the primes. If they all lie on the line, then the prime-counting function differs from its smooth estimate $\int_2^x \frac{dt}{\ln t}$ by about $\sqrt{x}$ at most, which is the smallest error you could hope for. Put simply, the primes are as evenly spread as they could possibly be.

**GRH (Generalized RH)** makes the same claim for a whole family of cousins of zeta, the **Dirichlet L-functions** $L(s,\chi) = \sum \chi(n)/n^s$. Here $\chi$ is a "character", a repeating pattern of weights that can pick out primes in a given residue class, for example primes ending in 7. Zeta itself is the simplest member of the family ($\chi$ = all 1's).

## 2. What Lean is and why that changes things

Lean is a programming language for writing proofs that a computer checks line by line, down to the axioms. If the code compiles, uses no `sorry` (Lean's "trust me" placeholder) and adds no axioms of its own, then the theorem is proved, *provided the statement says what you think it says*. You do not need to understand the proof to trust it. You only need to trust:

1. the small Lean "kernel" that does the checking, and
2. the **definitions** in the statement.

This is why the author published Lean code rather than a paper. He says a human-readable write-up would currently run to more than 250,000 pages.

## 3. What the code literally claims

The whole claim fits in two short files.

**`src/Main.lean`** states five theorems. The headline one is:

```lean
theorem riemannHypothesis : RiemannHypothesis := rhOfAll
```

`RiemannHypothesis` is **not defined in this repo**. It comes from Mathlib, the big community math library:

```lean
def RiemannHypothesis : Prop :=
  ∀ s, riemannZeta s = 0 → (s is not -2, -4, -6, …) → s ≠ 1 → s.re = 1/2
```

Read it as: "for every complex s, if ζ(s) = 0, s is not a trivial zero, and s ≠ 1, then the real part of s is ½." This matters because the author cannot quietly weaken the statement: it was written by other people long before.

**`src/Statements.lean`** (16 lines, imports only Mathlib) defines the GRH versions: zeros of every Dirichlet L-function in the critical strip have real part ½, and these L-functions are never zero to the right of the line.

## 4. How the proof is organized, top-down

Think of it as an upside-down pyramid. The top is a few lines a strong high-schooler could follow. The bottom is millions of lines of graduate and research-level math.

### Layer 1: the easy final steps (readable!)

The key intermediate statement is called `EveryCharacter`:

> For every character χ and every s with Re(s) > ½, L(s, χ) ≠ 0.

In words: no zeros to the right of the critical line. Everything follows from this by short arguments in `Formalism/GammaFactorNonvanishing/CritLine.lean`:

- **Zeta is a special case.** Zeta is the L-function of the trivial character mod 1, so "no zeros right of ½" holds for zeta too.
- **The mirror trick.** L-functions satisfy a **functional equation**, a symmetry that matches the value at $s$ with the value at $1-s$. Geometrically this reflects across the line Re = ½. So suppose there were a zero with Re(s) < ½. Reflecting it gives a zero at $1-s$ (for a closely related L-function), and that point has Re > ½. This contradicts `EveryCharacter`.
- **Conclusion.** No zeros on the right, and none on the left by the mirror, so every zero in the strip is on the line.

The Lean proof even opens with "either Re(s) < ½ or Re(s) > ½" (`lt_or_gt_of_ne`). The author jokes that Claude's draft write-up started the same way.

**So the entire difficulty is proving there are no zeros with Re(s) > ½.** This part of the logic is completely standard. Mathematicians have known for 150 years that RH is equivalent to it.

### Layer 2: `everyCharacter`, where the real work starts

`Development/AutomorphicArithmetic/CharacterBoxes/MainConclusion.lean` proves `EveryCharacter` by combining:

- a result about Galois representations ("local–global compatibility"), and
- a result named `vwin_of_row`, which comes from the theta-correspondence and automorphic-forms machinery.

From here down the vocabulary becomes graduate and research level.

### Layer 3: the big idea, in pop-math terms

From the author's note (he says some of it is his paraphrase of Claude's summary and might need revision):

1. **The template is a known proof over "function fields".** RH has a cousin for curves over finite fields, which André Weil proved in the 1940s. **Stepanov** later found an elementary proof. Its trick: build an auxiliary polynomial that vanishes at the points you want to count *with high multiplicity* (a root of order $m$, the way $(x-a)^m$ has one). A polynomial of bounded degree cannot have too many high-multiplicity roots, so you get an upper bound on the count. That bound is exactly RH-quality.

2. **The obstacle over the ordinary integers.** "Multiplicity" means taking derivatives, and you cannot differentiate whole numbers. That obstacle is roughly why the function-field proof never carried over to the actual primes.

3. **The new trick: theta lifts as stand-in derivatives.** "Theta lifts" are a classical way to move automorphic forms (highly symmetric functions, cousins of modular forms) from one symmetry group to a bigger one. The insight is that **each theta lift acts like one extra order of multiplicity**. Chain $m$ of them together, $U(X_0) \to U(X_1) \to \cdots \to U(X_m)$, and you get multiplicity $m$, as Stepanov needs.

4. **The famous line.** To control a prime sum up to $X$, the chain needs length about $\sqrt{X}$. The $\sqrt{X}$ is the same square-root size that shows up in the RH error term. The author calls this the line that will "make fellow mathematicians fall out of their chairs".

5. **Supporting cast** (names you might see in videos or on Wikipedia): Iwasawa towers (stacks of number fields, used as the integer stand-in for a pigeonhole argument over finite fields), the Rallis seesaw, the Bost slope inequality, the relative trace formula, Chowla–Selberg, Siegel mass formula, a weak form of Vandiver's conjecture, and even Behrend's construction of sets without 3-term arithmetic progressions. The author expects that last one is unnecessary.

The author is open that the argument is probably far longer than necessary, and he expects much shorter proofs to follow.

### Layer 4: the foundations (most of the 17 million lines)

Most of the code isn't new math. It formalizes decades of *existing* math that Mathlib does not have yet: class field theory, Chebotarev density, abelian varieties, Shimura varieties and toroidal compactifications, representation theory of real and p-adic groups, local Langlands pieces, p-adic Hodge theory, and so on. Many folders are literally named `PublishedTheorems`. The main areas:

| Folder | Files | Lines | Roughly |
|---|---:|---:|---|
| `Development/` | 141,928 | 12.2 M | the main argument plus heavy machinery (abelian varieties, automorphic forms, étale cohomology, Weil bound, …) |
| `Formalism/` | 18,254 | 3.2 M | many medium-sized named components |
| `GroundTheory/` | 8,507 | 1.1 M | local/global fields, adeles, Galois cohomology, p-adic Hodge theory |
| `ReciprocityTheory/` | 3,845 | 563 K | class field theory, Chebotarev, reductive groups |
| `CompanionTheory/` | 2,027 | 194 K | real groups, Harish-Chandra modules, spectral geometry |
| `PositivityTheory/`, `Lemmata/`, etc. | ~600 | ~65 K | positivity and small lemmas |
| **Total** | **175,187** | **≈ 17.4 M** | (Mathlib itself is about 2 M lines) |

For scale: this is about 8 times the size of all of Mathlib, which took a community of people years to build. This code was produced in roughly six weeks (the author's timeline runs from 6 Oct to 16 Nov 2026).

## 5. How much should you believe it right now?

**Points in its favour:**

- The statement is Mathlib's own definition, so it cannot be a weakened version of RH.
- The mirror's text scan of all 175k files found **no** `sorry`, `admit`, `axiom`, `native_decide`, or `unsafe` code. Those are the usual ways to cheat or slip in unproved assumptions.
- The author is a professional number theorist (Princeton PhD, worked under Bhargava), not a crank.

**Points still open:**

- **Nobody has built it yet** (as of the mirror date). A text scan cannot replace actually compiling and running `#print axioms riemannHypothesis`. The clean answer would list only `propext`, `Classical.choice`, `Quot.sound`.
- There are 22 custom tactic macros and one `addDecl` metaprogram. These are probably harmless, but they need checking. An independent kernel re-check (`lean4checker`) would settle that.
- The human-level understanding barely exists yet, and the author says so himself. Even a fully verified proof will take mathematicians a long time to digest, simplify and explain.

**Bottom line:** the logic at the top is simple and standard: no zeros right of ½, plus the mirror symmetry, gives RH. All the weight rests on a gigantic, machine-generated formalization of a genuinely new idea: Stepanov's multiplicity trick, rebuilt from about $\sqrt{X}$ chained theta lifts. If the code compiles with only standard axioms, then RH and GRH for Dirichlet L-functions are proved, whether or not any human understands every step.

---

### Files worth opening yourself

- `src/Statements.lean`: the exact claims (16 lines)
- `src/Main.lean`: the five headline theorems
- `src/Formalism/GammaFactorNonvanishing/CritLine.lean`: the "mirror trick" final step, readable with this summary
- `src/Development/AutomorphicArithmetic/CharacterBoxes/MainConclusion.lean`: where "no zeros right of ½" gets proved (by appeal to everything else)
- <https://alpo.ge/remark.pdf>: the author's 4-page note and timeline
