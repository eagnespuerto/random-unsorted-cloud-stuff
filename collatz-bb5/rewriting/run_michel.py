import sys, time, io
from multiprocessing import Pool
from srs import prove
from michel import M_RULES

def job(i):
    rules = M_RULES if i < 0 else [r for j, r in enumerate(M_RULES) if j != i]
    buf = io.StringIO(); t = time.time()
    res = prove(rules, dims=(1, 2, 3, 4) if i >= 0 else (1, 2, 3, 4, 5), bits=(2, 3),
                timeout=200 if i >= 0 else 900, log=lambda x: buf.write(x + "\n"))
    return i, res is not None, time.time() - t, buf.getvalue()

if __name__ == "__main__":
    which = [-1] if sys.argv[1:] == ["full"] else range(len(M_RULES))
    with Pool(4) as p:
        for i, ok, dt, log in p.imap_unordered(job, which):
            name = "FULL Michel system" if i < 0 else "Michel minus %s->%s" % M_RULES[i]
            print("%-28s %s  (%.0fs)" % (name, "TERMINATES (proved)" if ok else "no proof found", dt))
            print(log, end="")
            sys.stdout.flush()
