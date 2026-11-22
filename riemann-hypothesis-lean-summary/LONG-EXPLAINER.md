# The Lean proof of the Riemann Hypothesis, part by part

*A longer pop-math explainer of Levent Alpöge's Lean proof, released 20 November 2026. No formulas needed, though a few appear for readers who like them.*

Website version with animations: <https://eagnespuerto.github.io/riemann-2026-explainer/> ([repo](https://github.com/eagnespuerto/riemann-2026-explainer)) · Short version: [POP-MATH.md](POP-MATH.md) · Calculus-level version: [README.md](README.md) · Code: [eagnespuerto/riemann-hypothesis-lean](https://github.com/eagnespuerto/riemann-hypothesis-lean) · Author's 4-page note: <https://alpo.ge/remark.pdf>

---

## Part 1. The primes

A prime is a whole number bigger than 1 that only 1 and itself divide: 2, 3, 5, 7, 11, 13, 17, and so on forever. Every whole number breaks into primes in exactly one way, so they are the atoms of arithmetic.

Up close, primes look random. Twin primes like 11 and 13 sit side by side. Then you get a stretch like 113 to 127 with no primes at all. Nobody can predict the next prime from the last one by a simple rule.

From far away, though, they thin out smoothly. Around a million, about 1 number in 14 is prime. Around a billion, about 1 in 21. Gauss guessed the rule as a teenager: near a number *x*, the chance that a number is prime is about 1 over the natural log of *x*. This was proved in 1896 and is called the Prime Number Theorem.

So there is a smooth trend with noise on top. The Riemann Hypothesis is a statement about how big that noise can get.

## Part 2. Riemann's machine

In 1859 Bernhard Riemann wrote an 8-page paper with a new tool, the **zeta function**. It starts as a simple sum:

ζ(s) = 1 + 1/2ˢ + 1/3ˢ + 1/4ˢ + …

Euler had already seen that this same sum can be rewritten as a product with one piece for each prime. So whatever zeta does, it is secretly doing with the primes.

Riemann's move was to feed it complex numbers, points on a flat plane instead of a number line. The function then has places where its output is exactly zero. These are its **zeros**.

Some zeros are dull. They sit at −2, −4, −6 and so on, and are called trivial. The rest, infinitely many, all sit inside a vertical band of the plane, the **critical strip**. Down the middle of the band runs the **critical line**.

Riemann showed that these zeros control the primes. A good picture is sound. Each zero is like one pure note. Play all the notes together, with the right loudness, and the sound you hear is the exact pattern of the primes, gaps and all. The smooth trend from Part 1 is the bass. The zeros are the higher notes that make the noise.

Where a zero sits decides how loud its note is. A zero on the centre line gives a quiet note. A zero off to the right of the line would give a louder one, and the primes would be noisier.

## Part 3. The hypothesis

Riemann computed a few zeros by hand and found all of them on the centre line. He wrote that it was "very likely" all of them are, then set the question aside.

That guess is the **Riemann Hypothesis**: every non-trivial zero lies exactly on the critical line.

Computers have since checked more than ten trillion zeros, and all of them are on the line. That is evidence, not proof. Infinitely many zeros are left, and in number theory patterns sometimes break at sizes no computer will reach.

If the hypothesis is true, the noise in the primes is as small as it could possibly be, about the square root of the size of the numbers you look at. Up to a trillion, the error in the smooth estimate would be no bigger than about a million times a small factor. Thousands of published theorems begin with "assume the Riemann Hypothesis", so a proof turns all of them into plain theorems at once.

It has a $1 million Clay Millennium Prize attached. It was also on Hilbert's list of big problems in 1900.

### The cousins

Zeta has a family of relatives called **Dirichlet L-functions**. Each one is built like zeta but with a repeating pattern of weights on the terms. That pattern can pick out, for example, primes that end in 7. The **Generalised Riemann Hypothesis** (GRH) says the zeros of all these relatives also lie on the centre line. If it holds, primes split evenly between endings 1, 3, 7 and 9, with the smallest possible noise.

Alpöge's code claims both: RH for zeta, and GRH for every Dirichlet L-function. It does not claim GRH for the wider families (Dedekind, Hecke and general automorphic L-functions).

## Part 4. Lean, the proof checker

Alpöge did not publish a paper. He published a program in **Lean**.

Lean is a programming language where a program is a proof. Each step has to follow from earlier steps by the basic rules of logic. A small core program, the **kernel**, checks every step. If the kernel accepts the whole file, the theorem is proved.

There are only a few ways to cheat, and each one leaves a trace:

- `sorry` means "trust me, I'll fill this in later". A proof with a `sorry` in it is not finished.
- `axiom` adds a new assumption. Add the wrong one and you can prove anything.
- A few escape hatches (`native_decide`, `unsafe`, `implemented_by` and similar) let code skip parts of the kernel's checking.

Lean can list every assumption a theorem rests on. You type `#print axioms` and the name of the theorem. For a clean proof the list has three entries and no more: `propext`, `Classical.choice` and `Quot.sound`. These are standard logical rules that all of Mathlib uses.

So you don't need to read 17 million lines to trust the result. You need to trust the kernel, and you need to check that the statement at the top means what it says.

## Part 5. The statement

This is where proofs by computer can go wrong. A program can be perfectly correct and still prove the wrong thing, if someone defined "Riemann Hypothesis" in a weaker way.

Alpöge closed that door for RH. The main theorem in `src/Main.lean` reads:

```lean
theorem riemannHypothesis : RiemannHypothesis := rhOfAll
```

The word `RiemannHypothesis` is not defined anywhere in his code. It comes from **Mathlib**, the shared maths library that hundreds of people have built since 2017. Its definition says: for every complex number *s*, if zeta is zero at *s*, and *s* is not one of the trivial zeros, and *s* is not 1, then the real part of *s* is ½. That definition existed long before this proof. Alpöge could not quietly bend it.

The GRH statements are a different case. Mathlib does not have them yet, so they live in the project's own file, `src/Statements.lean`. It is 16 lines long and imports nothing but Mathlib. People have to read those 16 lines and agree they say the right thing. The checkers below did that by hand.

## Part 6. Who checked it

On release day, nobody had built the code. It takes a very large machine. Within about a day, three independent checks were done, and the Lean and Mathlib communities issued a statement.

**Andrew Sutherland (MIT)** compiled the whole project separately. Scientific American quoted him saying the proof was "independently rechecked by the Lean kernel with only the three standard axioms." His public record (updated 12:55 UTC on 21 November) reports all 175,187 modules compiling with zero errors on Lean v4.33.1. Two separate kernels written by other people, nanoda and con-leche, each accepted the full exported proof. A third, lean4lean, accepted every compiled module.

**A second check, [GRH Lean Check](https://mrubinst.github.io/grh-lean-verification/)**, is hosted at mrubinst.github.io and links to Michael Rubinstein's University of Waterloo page. It marked all its checks complete at 10:10 UTC on 21 November. It confirmed the downloaded source matched Alpöge's release byte for byte. It read the statements by hand and scanned all 175,187 files for the cheats from Part 4, finding none. It compiled everything with zero errors. `#print axioms` gave only the three standard axioms for all five headline theorems. It replayed every module through the kernel with zero rejections. The nanoda kernel checked 1,484,729 declarations with no errors.

**A third group, [Hertaspace](https://github.com/Hertaspace/alpoge-rh-lean-verification)**, says it has no ties to Alpöge. It finished its build at 22:02 UTC on 21 November and got the same three axioms. Its compiled main file has exactly the same fingerprint (SHA-256 hash) as the MIT build. Two machines, run by different people, produced the same bytes.

**The Lean and Mathlib communities** issued a joint statement on 21 November. Scientific American quotes it: "We hereby certify that both the statement and the proof of the Riemann Hypothesis are correct." Unite.ai reports that the Lean FRO and the Mathlib Initiative endorsed it. Scientific American's updated headline reads "The AI Riemann hypothesis proof is true, independent mathematicians confirm."

A few things the record still shows as open or worth knowing:

- **Kevin Buzzard** (Imperial College London) wrote that "We still await a successful comparator run." The comparator is a tool that checks the code does not secretly redefine any word in the statement. Scientific American says that run has now finished. The MIT and Hertaspace pages still listed it as running when last updated. I could not settle this from the pages I read.
- All three independent checks say they were run with **Claude Code**, Anthropic's AI agent, under human direction. The machine checking is independent of Alpöge, but the same family of AI tools sat on both sides.
- Some extra kernel runs (Lean's "paranoid" mode on the full export) were still in progress at the time of the MIT snapshot.

## Part 7. How big it is

The code is about **17.4 million lines** in **175,187 files**. All of Mathlib is about 2 million lines. So this one proof is roughly eight times the size of the library it builds on.

Alpöge says that if you wrote it out for humans, it would currently fill more than **250,000 pages**. His timeline runs from 6 October to 16 November 2026, about six weeks, with Claude writing most of the code.

Most of those lines are not new ideas. They are decades of known mathematics that nobody had typed into Lean before: class field theory, the Chebotarev density theorem, abelian varieties, Shimura varieties, p-adic Hodge theory, the representation theory of big symmetry groups. Many folders are named `PublishedTheorems`. Before the new idea could run, the computer had to learn a large slice of modern number theory.

| Folder | Lines | What's in it |
|---|---:|---|
| `Development/` | 12.2 M | the main argument and the heavy machinery under it |
| `Formalism/` | 3.2 M | medium-sized named components, including the final mirror step |
| `GroundTheory/` | 1.1 M | number fields, adeles, Galois cohomology |
| `ReciprocityTheory/` | 563 K | class field theory, Chebotarev |
| `CompanionTheory/` | 194 K | real groups, spectral geometry |
| everything else | ~65 K | small lemmas and positivity results |

## Part 8. Step one: the mirror

Now the proof itself, from the top down.

Zeta has a built-in symmetry called the **functional equation**. It ties the value at a point on the left of the centre line to the value at its mirror image on the right. So zeros come in mirror pairs. If there is a zero at some spot to the left of the line, there is one at the matching spot to the right.

That means you only have to prove one thing: **there are no zeros to the right of the line.** If none are on the right, the mirror says none are on the left. Every zero is then on the line.

Mathematicians have known this reduction for about 150 years. In the Lean code it lives in `src/Formalism/GammaFactorNonvanishing/CritLine.lean`. Line 16 starts with a step called `lt_or_gt_of_ne`, which says "a zero off the line is either left of it or right of it". The proof then rules out each side. Alpöge jokes in his note that Claude's draft write-up opened the same way.

The intermediate claim has a name in the code, `EveryCharacter`. It says that for every Dirichlet L-function, there is no zero with real part bigger than ½. Zeta is the simplest member of that family, so RH comes out as a special case.

All the difficulty is in proving `EveryCharacter`. The rest of this explainer is about that.

## Part 9. Step two: a trick from a smaller world

Number theorists keep a toy version of the primes to practise on. Instead of whole numbers, it uses curves drawn over finite number systems, like clock arithmetic where 12 + 1 = 1. These toy worlds have their own zeta functions and their own Riemann Hypothesis.

In the toy world, the hypothesis was proved. André Weil did it in the 1940s using heavy geometry. In the late 1960s Sergei Stepanov found a much more elementary proof, and his idea is the template for Alpöge's.

Stepanov's trick goes in three moves.

1. **Count points.** In the toy world, RH is equivalent to a sharp count of the points on a curve. You want to show there aren't too many.
2. **Build a polynomial that is zero at all of them, many times over.** A polynomial can touch zero at a point and linger. The polynomial (x − 3)⁵ is zero at 3 "five times": it and its first four derivatives are all zero there. This is **multiplicity**. Stepanov builds a polynomial that has a high multiplicity at every point he wants to count.
3. **Use the size limit.** A polynomial of degree *d* has at most *d* roots, counting multiplicity. If every point is a root of multiplicity *m*, there can be at most *d* / *m* points. Pick *d* and *m* well and you get exactly the count RH needs.

The catch is step 2. To measure multiplicity you take derivatives, and in the toy world you can. Over the ordinary whole numbers there is no good notion of a derivative. You can't ask for the slope of 7. That gap is roughly why Stepanov's method never crossed over to the real primes.

## Part 10. Step three: theta lifts as stand-in derivatives

Alpöge's new idea fills that gap.

There is a classical tool called a **theta lift**. It starts with an **automorphic form**, a function with an enormous amount of symmetry. Modular forms, the objects at the heart of the proof of Fermat's Last Theorem, are the simplest examples. A theta lift takes such a form living on one symmetry group and produces a new form on a bigger group.

His observation is that **one theta lift behaves like one derivative.** Each lift adds one level of "zero many times over". Chain *m* lifts together, through a sequence of bigger and bigger groups, and you get multiplicity *m*. That is exactly what Stepanov's counting argument needs, and now it works over the whole numbers.

How long a chain? To control the primes up to some size *X*, the chain needs about **√X** lifts. The square root is the same square root from Part 3, the size of the noise RH promises. Alpöge writes that this is the line that will make fellow mathematicians "fall out of their chairs".

He also says some of the description in his note is his paraphrase of Claude's summary of the code, and might need revising. The human-level account of this step is still being worked out.

## Part 11. The supporting cast

Many other famous results do jobs inside the argument. Alpöge's note names them. Below is what each one is in general. How each one fits into this proof is in his note, and in places he says even that is still provisional.

- **Iwasawa towers**: an infinite stack of number fields, each built on the last. Alpöge's note uses them as the whole-number stand-in for a pigeonhole-style counting step that works easily in the toy world.
- **The Rallis seesaw**: a classical identity that compares two different theta lifts.
- **The relative trace formula**: a tool that turns sums over automorphic forms into sums you can compute from geometry.
- **The Siegel mass formula and the Chowla–Selberg formula**: classical exact formulas, the first counting forms of a given type, the second giving special values.
- **The Bost slope inequality**: a size bound from arithmetic geometry.
- **Behrend's construction**: a large set of numbers with no three evenly spaced. Alpöge expects this one is not really needed.

He is open that the argument is probably far longer than it has to be, and he expects shorter proofs to follow.

## Part 12. What is settled and what is not

**Settled:** the code compiles, it uses only the three standard axioms, two kernels written by other people accept it, and the RH statement is Mathlib's own. The Lean and Mathlib communities have certified both statement and proof.

**Still open:**

- One comparator run was reported as still going on some pages and finished on another.
- Nobody has a human-readable proof yet. Mathematicians know *that* it is true without yet knowing in detail *why* it works.
- The Clay Institute's rules ask for publication in a refereed venue and two years of acceptance. How they apply to a 17-million-line machine proof is up to Clay.
- The broader GRH, for Dedekind, Hecke and automorphic L-functions, is not covered.

The next job is for people. Number theorists now have to read the new idea in Parts 9 and 10, write it up in a form a graduate student can follow, and look for the short proof inside the long one.

---

### Sources

- Levent Alpöge, note and timeline: <https://alpo.ge/remark.pdf>
- Scientific American, "The AI Riemann hypothesis proof is true, independent mathematicians confirm" (Clara Moskowitz, 20 Nov 2026, updated 21 Nov): <https://www.scientificamerican.com/article/the-ai-riemann-hypothesis-proof-is-almost-certainly-true-independent-mathematicians-attest/>
- Unite.ai, "Lean and Mathlib Communities Certify Claude-Assisted Riemann Proof" (21 Nov 2026): <https://www.unite.ai/lean-and-mathlib-communities-certify-claude-assisted-riemann-proof/>
- GRH Lean Check (Rubinstein-linked independent check): <https://mrubinst.github.io/grh-lean-verification/>
- Hertaspace independent build and axiom check: <https://github.com/Hertaspace/alpoge-rh-lean-verification>
- Mirror of the code: <https://github.com/CocoSgt/riemann-hypothesis-lean>
