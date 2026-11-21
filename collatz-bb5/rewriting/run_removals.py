import sys, time, io
from multiprocessing import Pool
from srs import T_RULES, prove

def job(i):
    rules = [r for j, r in enumerate(T_RULES) if j != i]
    buf = io.StringIO(); t = time.time()
    res = prove(rules, dims=(1, 2, 3, 4, 5), bits=(2, 3), timeout=300, log=lambda x: buf.write(x + "\n"))
    return i, res is not None, time.time() - t, buf.getvalue()

if __name__ == "__main__":
    with Pool(4) as p:
        for i, ok, dt, log in p.imap_unordered(job, range(len(T_RULES))):
            print("T minus %-12s %s  (%.0fs)" % ("%s->%s" % T_RULES[i], "TERMINATES (proved)" if ok else "no proof found", dt)); print(log, flush=True)
