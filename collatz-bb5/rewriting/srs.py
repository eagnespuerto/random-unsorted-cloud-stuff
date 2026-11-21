"""Collatz as string rewriting (Yolcu-Aaronson-Heule mixed binary/ternary system) + a tiny
matrix-interpretation termination prover (natural matrices, rule removal, z3 bit-blasting).
Symbols: f,t = binary 0,1; 0,1,2 = ternary digits; L = left end (stands for the leading 1 bit); R = right end."""
import itertools, sys, time
import z3

T_RULES = [("fR", "R"), ("tR", "2R"),                                    # n/2 ; (3n+1)/2
           ("f0", "0f"), ("f1", "0t"), ("f2", "1f"),                      # move ternary digit left
           ("t0", "1t"), ("t1", "2f"), ("t2", "2t"),
           ("L0", "Lt"), ("L1", "Lff"), ("L2", "Lft")]                    # absorb into leading 1

def enc(n): return "L" + bin(n)[3:].replace("0", "f").replace("1", "t") + "R"
def dec(s):
    b = s[1:-1]
    return int("1" + b.replace("f", "0").replace("t", "1"), 2) if set(b) <= set("ft") else None

def simulate(n, rules=T_RULES, cap=10**6):
    """Leftmost-innermost rewriting; returns the sequence of pure-binary numbers visited."""
    s, seen = enc(n), [n]
    for _ in range(cap):
        for i in range(len(s)):
            for l, r in rules:
                if s.startswith(l, i): s = s[:i] + r + s[i + len(l):]; break
            else: continue
            break
        else: return seen                                                 # normal form
        v = dec(s)
        if v is not None: seen.append(v)
    return seen

# ---------- matrix interpretation prover ----------
def prove(rules, dims=(1, 2, 3, 4), bits=(2, 3), timeout=120, reverse_ok=True, log=print):
    """Repeated rule removal. Returns list of (removed rules, dim, bits, reversed) or None."""
    rules = list(rules); steps = []
    while rules:
        found = None
        for rev in ((False, True) if reverse_ok else (False,)):
            rr = [(l[::-1], r[::-1]) for l, r in rules] if rev else rules
            for d in dims:
                for b in bits:
                    res = _search(rr, d, b, timeout)
                    if res:
                        strict, mats = res
                        assert verify(rr, mats, strict), "certificate failed independent check"
                        found = ([rules[i] for i in strict], d, b, rev, mats); break
                if found: break
            if found: break
        if not found: return None
        steps.append(found); log("   removed %s  (dim %d, %d-bit entries%s)" % (found[0], found[1], found[2], ", reversed" if found[3] else ""))
        rules = [r for r in rules if r not in found[0]]
    return steps

def _search(rules, d, b, timeout):
    W = 32; syms = sorted(set("".join(l + r for l, r in rules)))
    s = z3.SolverFor("QF_BV"); s.set("timeout", timeout * 1000)
    M = {}
    for a in syms:
        mat = [[z3.BitVec(f"{a}_{i}_{j}", b) for j in range(d + 1)] for i in range(d)]
        M[a] = [[z3.ZeroExt(W - b, x) for x in row] for row in mat] + [[z3.BitVecVal(0, W)] * d + [z3.BitVecVal(1, W)]]
        s.add(M[a][0][0] >= 1)                                            # monotone in first coordinate
    def prod(A, B): return [[sum((A[i][k] * B[k][j] for k in range(d + 1)), z3.BitVecVal(0, W)) for j in range(d + 1)] for i in range(d + 1)]
    def interp(w):
        X = M[w[0]]
        for a in w[1:]: X = prod(X, M[a])
        return X
    stricts = []
    for idx, (l, r) in enumerate(rules):
        A, B = interp(l), interp(r)
        for i in range(d):
            for j in range(d + 1): s.add(z3.UGE(A[i][j], B[i][j]))
        stricts.append((idx, z3.UGT(A[0][d], B[0][d])))
    s.add(z3.Or([c for _, c in stricts]))
    if s.check() != z3.sat: return None
    m = s.model()
    mats = {a: [[m.eval(M[a][i][j]).as_long() for j in range(d + 1)] for i in range(d + 1)] for a in syms}
    return [i for i, c in stricts if z3.is_true(m.eval(c))], mats

def verify(rules, mats, strict):
    """Independent integer check of a matrix-interpretation certificate (no z3)."""
    d = len(next(iter(mats.values()))) - 1
    mul = lambda A, B: [[sum(A[i][k] * B[k][j] for k in range(d + 1)) for j in range(d + 1)] for i in range(d + 1)]
    def I(w):
        X = mats[w[0]]
        for a in w[1:]: X = mul(X, mats[a])
        return X
    if any(m[0][0] < 1 or m[d] != [0] * d + [1] for m in mats.values()): return False
    for idx, (l, r) in enumerate(rules):
        A, B = I(l), I(r)
        if any(A[i][j] < B[i][j] for i in range(d) for j in range(d + 1)): return False
        if idx in strict and not A[0][d] > B[0][d]: return False
    return bool(strict)

if __name__ == "__main__":
    def T(n): return n // 2 if n % 2 == 0 else (3 * n + 1) // 2
    for n in range(2, 2000):                                              # sanity: rewriting == Collatz
        orb, m = simulate(n), [n]
        while m[-1] != 1: m.append(T(m[-1]))
        assert orb == m, n
    print("rewriting system reproduces Collatz orbits for n < 2000")
