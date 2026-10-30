import sys,math,bisect
L=open('eph_all.txt').read().split('$$SOE')[1].split('$$EOE')[0].strip().splitlines()
E=[tuple(map(float,l.split()[:3])) for l in L]; J=[e[0] for e in E]
def eph(jd):
    i=max(0,min(len(E)-2,bisect.bisect(J,jd)-1)); f=jd-J[i]; a,b=E[i],E[i+1]; return a[1]+(b[1]-a[1])*f,a[2]+(b[2]-a[2])*f
def sep(a,b,c,d):
    a,b,c,d=map(math.radians,(a,b,c,d)); return math.degrees(math.acos(min(1,math.sin(b)*math.sin(d)+math.cos(b)*math.cos(d)*math.cos(a-c))))
