"""Attempt at the potential-function direction: V(n) = log n + g(n), required to strictly decrease along orbits.
Run: python3 potential.py"""
import math
from fractions import Fraction
L32, L12 = math.log(1.5), math.log(0.5)

def T(n): return n // 2 if n % 2 == 0 else (3 * n + 1) // 2

# A. Residue-only corrections g(n) = f(n mod 2^j): an f making every step decrease exists iff every
#    cycle of the residue transition graph has negative weight (max-mean-cycle). Check with Karp's algorithm.
def max_mean_cycle(j):
    M = 2 ** j; edges = []
    for r in range(2 * M):                      # n mod 2^(j+1) fixes both n mod 2^j and T(n) mod 2^j
        edges.append((r % M, T(r) % M if r % 2 == 0 else ((3 * r + 1) // 2) % M, L32 if r & 1 else L12))
    NEG = -1e18; D = [[NEG] * M for _ in range(M + 1)]
    for v in range(M): D[0][v] = 0.0
    for k in range(1, M + 1):
        for u, v, w in edges:
            if D[k - 1][u] > NEG and D[k - 1][u] + w > D[k][v]: D[k][v] = D[k - 1][u] + w
    return max(min((D[M][v] - D[k][v]) / (M - k) for k in range(M) if D[k][v] > NEG) for v in range(M) if D[M][v] > NEG)

# B. Which 2-adic cycles carry positive weight? The rational cycles of T on negative integers.
def neg_cycles(lim=200):
    found = {}
    for s in range(1, lim):
        n, seen = -s, []
        while n not in seen: seen.append(n); n = T(n)
        cyc = tuple(seen[seen.index(n):]); key = min(cyc)
        if key not in found:
            k = sum(x & 1 for x in cyc); m = len(cyc)
            found[key] = (m, k, round(k * math.log(3) - m * math.log(2), 4))
    return found

# C. Any V = log n + g with g >= -C nonincreasing along orbits forces g(n) >= log(max orbit / n) - C.
#    Worst ratio log(max orbit)/log n for n up to N:
def excursion(N=10**6, lo=3):
    mx = [0, 1, 2] + [0] * (N - 3); best = (0, 0)
    for n in range(3, N):
        m, top = n, n
        while m >= n: m = T(m); top = max(top, m)
        mx[n] = max(top, mx[m])                  # orbit max of the smaller number m is already known
        if n >= lo:
            r = math.log(mx[n]) / math.log(n)
            if r > best[0]: best = (r, n)
    return best

# D. Best achievable partial result: k-step affine certificates. Count residue classes mod 2^k whose
#    parity path never yet satisfies 3^a < 2^j (j <= k): these are the only classes no window-k potential handles.
def uncertified_density(K=200):
    cnt = {0: 1}; out = {}
    for j in range(1, K + 1):
        new = {}
        for a, c in cnt.items():
            for b in (0, 1):
                a2 = a + b
                if 3 ** a2 >= 2 ** j: new[a2] = new.get(a2, 0) + c   # still not below start
        cnt = new
        if j in (10, 20, 50, 100, 200): out[j] = sum(cnt.values()) / 2 ** j
    return out

if __name__ == '__main__':
    for j in range(1, 9): print('A  j=%d  max mean cycle weight = %.4f  (log 3/2 = %.4f)' % (j, max_mean_cycle(j), L32))
    print('B  negative-integer cycles (min elt: length m, odd steps k, k ln3 - m ln2):', neg_cycles())
    for lo in (3, 10**3, 10**5):
        r, n = excursion(lo=lo); print('C  n in [%d,1e6): max log(orbit max)/log n = %.3f at n=%d -> g(n) >= %.3f*log n - C' % (lo, r, n, r - 1))
    print('D  density of residue classes mod 2^k with no descent certificate:', uncertified_density())
