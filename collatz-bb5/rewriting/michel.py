"""BB(5) champion's Collatz-like map (Michel): 3k -> 5k+6, 3k+1 -> 5k+9, 3k+2 -> halt,
as a ternary/quinary string rewriting system. 5k+6 = 5(k+1)+1, 5k+9 = 5(k+1)+4, so a step is
'strip last ternary digit, increment, append a quinary digit'. Symbols: 0,1,2 ternary; a..e quinary 0..4;
'+' increment marker; L/R ends; Z = halted."""
Q = "abcde"
M_RULES = [("0R", "+bR"), ("1R", "+eR"), ("2R", "Z"),                     # the three cases
           ("0+", "1"), ("1+", "2"), ("2+", "+0"), ("L+", "L1")]           # ternary increment
for a in range(3):                                                         # ternary digit . quinary digit -> quinary . ternary
    for p in range(5):
        v = 5 * a + p; M_RULES.append((str(a) + Q[p], Q[v // 3] + str(v % 3)))
M_RULES += [("La", "L0"), ("Lb", "L1"), ("Lc", "L2"), ("Ld", "L10"), ("Le", "L11")]

def enc(n):
    s = ""
    while True:
        s = str(n % 3) + s; n //= 3
        if n == 0: return "L" + s + "R"

def simulate(n, cap=10**7):
    s, seen = enc(n), [n]
    for _ in range(cap):
        for i in range(len(s)):
            hit = next(((l, r) for l, r in M_RULES if s.startswith(l, i)), None)
            if hit: s = s[:i] + hit[1] + s[i + len(hit[0]):]; break
        else: return seen, s
        if set(s[1:-1]) <= set("012") and s[0] == "L" and s[-1] == "R": seen.append(int(s[1:-1], 3))
    return seen, s

def g(x):
    k, r = divmod(x, 3)
    return None if r == 2 else 5 * k + (6 if r == 0 else 9)

if __name__ == "__main__":
    for n in range(0, 3000):
        orb, last = simulate(n); m = [n]
        while g(m[-1]) is not None: m.append(g(m[-1]))
        orb = [x for i, x in enumerate(orb) if i == 0 or x != orb[i - 1]]  # leading-zero repeats
        assert orb == m and "Z" in last, (n, orb[:10], m[:10])
    print("Michel system: %d rules, reproduces the map for n < 3000" % len(M_RULES), simulate(0)[0])
