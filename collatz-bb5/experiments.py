"""Small numerical companion to notes.md. Run: python3 experiments.py [--skip-tm]"""
import math, sys, random
from fractions import Fraction

def T(n):  # shortcut Collatz map
    return n // 2 if n % 2 == 0 else (3 * n + 1) // 2

# 1. BB(5) champion: simulate the TM and its Collatz-like "Michel map"
def bb5():
    # 1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA  (Marxen-Buntrock 1989)
    rules = {('A',0):(1,1,'B'),('A',1):(1,-1,'C'),('B',0):(1,1,'C'),('B',1):(1,1,'B'),
             ('C',0):(1,1,'D'),('C',1):(0,-1,'E'),('D',0):(1,-1,'A'),('D',1):(1,-1,'D'),
             ('E',0):(1,1,'Z'),('E',1):(0,-1,'A')}
    N = 30000; tape = bytearray(N); p = N // 2; s = 'A'; steps = 0
    while s != 'Z':
        w, d, s = rules[(s, tape[p])]; tape[p] = w; p += d; steps += 1
    return steps, sum(tape)

def michel(x=0):
    orbit = [x]
    while x % 3 != 2:
        k, r = divmod(x, 3); x = 5 * k + (6 if r == 0 else 9); orbit.append(x)
    return orbit

# 2. AM-GM: arithmetic vs geometric mean of per-step multipliers for qn+1
def amgm(q):
    am = (q / 2 + 0.5) / 2; gm = math.sqrt(q / 4)
    return am, gm

def empirical_drift(samples=20000, steps=60, bits=200):
    tot = 0.0
    for _ in range(samples):
        n = random.getrandbits(bits) | 1 << (bits - 1)
        m = n
        for _ in range(steps): m = T(m)
        tot += (math.log(m) - math.log(n)) / steps
    return tot / samples

def cycle_bound(kmax=60):
    """AM-GM on 2^m = 3^k * prod(1+1/(3 n_i)) gives n_min <= k / (3*ln(2^m/3^k))."""
    best = []
    for k in range(1, kmax + 1):
        m = math.ceil(k * math.log2(3))
        gap = 2**m / 3**k - 1
        best.append((k, m, round(gap, 5), round(k / (3 * math.log1p(gap)), 1)))
    return sorted(best, key=lambda t: -t[3])[:5]

def _reaches1(n):
    while n != 1: n = T(n)
    return True

# 3. Fractal / lightning: inverse Collatz tree grown from 1
def inverse_tree(depth=40):
    level, sizes = {1}, [1]
    for _ in range(depth):
        nxt = set()
        for n in level:
            nxt.add(2 * n)
            if n % 3 == 2 and (2 * n - 1) % 3 == 0 and (2 * n - 1) // 3 > 1:  # n = T(odd)
                nxt.add((2 * n - 1) // 3)
        level = nxt; sizes.append(len(level))
    return sizes

# 4. Attractor / "tokenization": parity vectors of length k are a bijection on Z/2^k
def terras(k=12):
    seen = set()
    for r in range(2**k):
        n, v = r + 2**k * 7, []   # any lift works
        for _ in range(k): v.append(n & 1); n = T(n)
        seen.add(tuple(v))
    return len(seen) == 2**k

def basin(limit=10**6):
    hist = {}
    for n in range(2, limit):
        m, s = n, 0
        while m >= n: m = T(m); s += 1
        hist[s] = hist.get(s, 0) + 1
    return sorted(hist.items())[:8]

if __name__ == '__main__':
    random.seed(1)
    if '--skip-tm' not in sys.argv:
        print('BB(5) champion steps, ones:', bb5())
    o = michel(); print('Michel orbit (%d iterations, halts at %d = 2 mod 3):' % (len(o) - 1, o[-1]), o)
    for q in (3, 5): print('q=%d  AM=%.4f  GM=%.4f  log GM=%.4f' % ((q,) + amgm(q) + (math.log(amgm(q)[1]),)))
    print('empirical mean log-drift/step (3n+1):', round(empirical_drift(), 4), ' predicted:', round(0.5 * math.log(0.75), 4))
    print('loosest AM-GM cycle bounds (k, m, gap, n_min<=):')
    cb = cycle_bound(); [print('  ', t) for t in cb]
    ok = all(_reaches1(n) for n in range(1, int(cb[0][3]) + 1))
    print('  every n <= %d reaches 1 -> no nontrivial cycle with k<=60 odd steps: %s' % (cb[0][3], ok))
    s = inverse_tree(); r = [s[i + 1] / s[i] for i in range(30, 40)]
    print('inverse-tree level sizes:', s[::5], ' growth ->', round(sum(r) / len(r), 4), '(4/3 =1.3333)')
    print('  "depth dimension" log(4/3)/log2 =', round(math.log(4 / 3) / math.log(2), 4))
    print('Terras bijection k=12:', terras())
    print('stopping-time histogram n<1e6 (steps to drop below n):', basin())
