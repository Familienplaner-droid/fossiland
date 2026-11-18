"""Misst, wie viele Schläge eine Grabung braucht, um alle Felder freizulegen (Pinsel), je Zeitalter.
Nachbau von hardMap in game.html. Aufruf: python3 tools/sim/hard.py"""
import random,math
R,C=9,8
def gen(era,mode):
    tot=0
    for k in range(3):
        m=[1]*(R*C)
        if mode=="alt": n=2+random.randrange(3)+(1 if k==2 and random.random()<era*.12 else 0)
        else: n=2+random.randrange(3)+mode[0][era]
        for i in range(n):
            cy,cx,rad=random.random()*R,random.random()*C,.7+random.random()*1.1
            for y in range(R):
                for x in range(C):
                    if math.hypot(y+.5-cy,x+.5-cx)<rad:m[y*C+x]=2
        if mode!="alt":
            for i in range(mode[1][era] if k>0 else 0):   # sehr harte Flecken (3 Schläge) in Schicht 2 und 3
                cy,cx,rad=random.random()*R,random.random()*C,.7+random.random()*.8
                for y in range(R):
                    for x in range(C):
                        if math.hypot(y+.5-cy,x+.5-cx)<rad:m[y*C+x]=3
        tot+=sum(m)
    return tot
def avg(era,mode,N=4000):return sum(gen(era,mode) for _ in range(N))/N
base=avg(0,"alt");print("heute Perm",round(base),"Schläge (Pinsel, alles freilegen)",[round(avg(e,"alt")/base,3) for e in range(6)])

print("neu (HARD_X/VHARD):",[round(avg(e,([0,1,4,7,8,10],[0,1,1,1,3,5]),3000)/base,3) for e in range(6)])
