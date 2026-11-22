# The Riemann Hypothesis, proved by a 17-million-line computer proof

*A pop-math explainer of Levent Alpöge's Lean proof (released 20 November 2026). No formulas needed.*

Code: [eagnespuerto/riemann-hypothesis-lean](https://github.com/eagnespuerto/riemann-hypothesis-lean) (a mirror of the author's release) · Author's 4-page note: <https://alpo.ge/remark.pdf> · A more technical summary for readers with some calculus: [README.md](README.md)

---

## The problem

Prime numbers (2, 3, 5, 7, 11, 13 …) look random. Some gaps between them are small and some are big, and there is no simple pattern. But zoom out and they thin out in a very regular way. The question is *how* regular.

In 1859 Bernhard Riemann found a tool to answer that. He used a function now called the **zeta function**. You can think of it as a machine that turns the primes into sound. Its **zeros** (the inputs where the machine outputs exactly zero) behave like the notes in a chord. Add all the notes together and you rebuild the exact pattern of the primes.

Riemann noticed that the zeros he could compute all sat on one straight line. He guessed that *all* of them do, infinitely many of them. That guess is the **Riemann Hypothesis**.

If it is true, the primes are as evenly spread as they could possibly be. The "noise" in the primes is as small as nature allows. Thousands of published results start with "assume the Riemann Hypothesis". It is one of the seven Clay Millennium Prize problems, with a US$1 million prize.

For 167 years nobody could prove it.

## What was released

On 20 November 2026 the number theorist Levent Alpöge released a proof. It is not a paper. It is a computer program written in **Lean**, a language for proofs.

In Lean, every step of a proof is checked by the computer all the way down to the basic rules of logic. If the program is accepted, the theorem is true. You don't have to follow the argument yourself. You only have to trust two things:

1. **the checker.** It is a small, well-tested piece of software.
2. **the statement.** Does the line that says "Riemann Hypothesis" really mean the Riemann Hypothesis?

The second point is the clever part. The author did not write his own version of the statement. He used the one already in **Mathlib**, a large shared library of mathematics written by many people long before this proof existed. So he could not quietly prove a weaker, easier version.

Since the release, the proof has been built and checked independently by others, twice. Both checks confirmed it.

The proof also covers the **Generalised Riemann Hypothesis** for a family of cousins of zeta called *Dirichlet L-functions*. These control, for example, how primes split between those ending in 1, 3, 7 and 9.

## How big is it?

It is huge.

- About **17.4 million lines** of code in 175,000 files.
- That is roughly **eight times the size of all of Mathlib**, which took a whole community years to build.
- The author says a human-readable write-up would currently run to **more than 250,000 pages**.
- It was produced in about **six weeks** (6 October to 16 November 2026), with heavy help from AI.

Most of those lines are not new mathematics. They are decades of *known* mathematics that had never been typed into Lean before. Whole folders are literally named `PublishedTheorems`. Before the new idea could be used, the computer had to be taught a big part of modern number theory.

## The idea, in three steps

### Step 1: the easy half is a mirror

The zeros all live inside a band. The Riemann Hypothesis says they sit exactly on the centre line of that band.

The zeta function has a built-in symmetry: what happens on the left of the centre line is a mirror image of what happens on the right. So if you can show there are **no zeros to the right** of the line, the mirror tells you there are none to the left either. The only place left is the line itself.

Mathematicians have known this for about 150 years. In the Lean code, this final step is short and readable. The proof literally begins: "either the zero is left of the line, or right of it". Then it rules out both.

So the whole difficulty is one claim: **no zeros to the right of the line.**

### Step 2: borrow a trick from a "toy universe"

Number theorists like to study a toy version of the primes, built from curves over finite number systems. In that toy universe, the Riemann Hypothesis was proved long ago, by André Weil in the 1940s.

Later, Sergei Stepanov found a simpler proof in the toy universe. His trick works roughly like this:

- Build a special polynomial that is zero at every point you want to count.
- Make it zero there *many times over*. Think of a graph that doesn't just cross the axis but touches it and lingers, the way (x − 3)⁵ has a root at 3 "five times". This is called **multiplicity**.
- A polynomial of limited size can't have too many of these deep roots. That limit gives a sharp count, and the sharp count is exactly what the Riemann Hypothesis needs.

The catch: to measure "zero many times over" you use derivatives, the slope-of-a-slope tools from calculus. In the toy universe you can take derivatives. With ordinary whole numbers you can't. There is no slope of the number 7. For decades, this is roughly why the toy proof never carried over to the real primes.

### Step 3: the new trick, stacking "theta lifts"

Here is the new idea. There is a classical tool called a **theta lift**. It takes a highly symmetric function (a relative of the modular forms behind the proof of Fermat's Last Theorem) and lifts it into a bigger, more symmetric setting.

Alpöge's insight is that **each theta lift acts like one derivative.** One lift gives you one extra level of "zero many times over". Stack *m* of them in a chain and you get multiplicity *m*, which is exactly what Stepanov's trick needs. Now it works for the real primes.

How long does the chain need to be? To control the primes up to some size *X*, you need a chain of about **√X** lifts. That square root is no accident. It is the same square root that appears in the Riemann Hypothesis's promise about how small the "noise" in the primes is. The author predicts this is the line that will make fellow mathematicians "fall out of their chairs".

Many famous tools from number theory help along the way, including Iwasawa towers, the Rallis seesaw, the relative trace formula and the Siegel mass formula. The author expects some of these to be unnecessary, and expects much shorter proofs to follow.

## What it means

**The theorem is settled.** The statement is the community's own. The code has been checked independently. Every result that began with "assume the Riemann Hypothesis" now stands on its own, including the strongest known estimates for how primes are spread out.

**Understanding is not settled.** This is a strange new situation. We know the proof is correct, but no human has followed all of it. The author is open about this. Mathematicians will now spend years reading, simplifying and explaining it, and maybe finding the short proof inside the long one.

**The prize is a separate question.** The Clay Institute's rules ask for publication in a refereed venue and two years of acceptance by the community. How those rules apply to a 17-million-line computer proof is up to Clay.

**The way mathematics is done may change.** A problem that resisted people for 167 years fell to a human idea, worked out at a scale only a machine could manage and checked by another machine. Whatever you think of that, it will not be the last time.

---

### Want to look for yourself?

These files in the code are short enough to open, even if you can't read Lean:

- `src/Statements.lean`: the exact claims, 16 lines
- `src/Main.lean`: the five headline theorems
- `src/Formalism/GammaFactorNonvanishing/CritLine.lean`: the mirror step
