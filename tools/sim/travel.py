"""Fossiland: Simulation mit Fundstellen, Flugtickets und Expeditionslager."""
import random, statistics
LABMIN=[60,90,130,180,240,300]; NEED=[0,0,3,8,15,22]
# Fundstellen: (Zeitalter, Anzahl Arten, Kontinent)
SITES=[(0,2,'NA'),(0,2,'EU'),(0,1,'SA'),
       (1,1,'EU'),(1,1,'EU'),(1,2,'SA'),(1,1,'NA'),
       (2,2,'EU'),(2,1,'EU'),(2,2,'NA'),(2,1,'NA'),(2,1,'NA'),
       (3,3,'NA'),(3,1,'AS'),(3,1,'AF'),(3,1,'NA'),(3,1,'EU'),(3,1,'NA'),(3,1,'EU'),
       (4,3,'EU'),(4,1,'AF'),(4,1,'AS'),(4,1,'AS'),
       (5,2,'AS'),(5,1,'NA'),(5,1,'EU'),(5,1,'EU'),(5,1,'SA')]
def tickets(a,b): return 3 if SITES[a][2]==SITES[b][2] else 6
CAMP=[(5000,20,0,0),(15000,20,1,0),(40000,30,0,.15)]   # Preis, +Energie, Gratis-Füllung/Tag, schneller
def sim(sessions, ads_per_session, ad_cap=30, days=30, seed=1, buy_tickets=True):
    R=random.Random(seed)
    S=dict(coins=30,energyLv=0,regenLv=0,benchLv=0,precLv=0,probeLv=0,camp=0,tix=0)
    sp=[]  # Arten: (site, era)
    for si,(e,n,c) in enumerate(SITES):
        for k in range(n): sp.append((si,e))
    mus={i:{} for i in range(len(sp))}; lab=[]; site=0; visited={0}
    st=60; carry=0; last=0; hist={}; flights=0; tix_ad=0; tix_buy=0; stuck=0; buys=[]
    def done(i): return len(mus[i])==5
    def completed(): return sum(done(i) for i in mus)
    def era_done(e): return all(done(i) for i,(s,ee) in enumerate(sp) if ee==e)
    def unlocked(e): return completed()>=NEED[e]
    def rate(): return sum((4+2*sp[i][1]+sum(v=='ok' for v in mus[i].values())*(1+sp[i][1]//2))*(1.5 if era_done(sp[i][1]) else 1) for i in mus if done(i))
    def camp_bonus(): return sum(c[1] for c in CAMP[:S['camp']])
    def smax(): return 60+5*S['energyLv']+camp_bonus()
    def regen_min():
        f=1-(.15 if S['camp']>=3 else 0); return (240-20*S['regenLv'])/60*f
    def covered(i,p): return p in mus[i] or any(x[0]==i and x[1]==p for x in lab)
    def site_done(s): return all(all(covered(i,p) for p in range(5)) for i,(ss,e) in enumerate(sp) if ss==s)
    def price(k):
        T={'energy':(220,1.58,10),'regen':(450,1.9,5),'prec':(300,1.85,5),'probe':(180,1.8,5)}
        if k=='bench': return [2500,12000][S['benchLv']] if S['benchLv']<2 else None
        if k=='camp': return CAMP[S['camp']][0] if S['camp']<3 else None
        b,g,mx=T[k]; return round(b*g**S[k+'Lv']) if S[k+'Lv']<mx else None
    def finish(x):
        i,p,cr=x[0],x[1],x[2];was=done(i);mus[i][p]='cr' if cr else 'ok'
        if not was and done(i):S['coins']+=50*(1+.5*sp[i][1]);
    def lab_step(m):
        while m>0 and lab:
            act=lab[:2+S['benchLv']];dt=min(m,min(x[3] for x in act))
            for x in act:x[3]-=dt
            m-=dt
            for x in [x for x in act if x[3]<=1e-9]:lab.remove(x);finish(x)
    def dig(stam):
        n_b=stam/38*2.35*(1+.03*S['probeLv']);nb=int(n_b)+(R.random()<n_b%1)
        e=SITES[site][0]
        for _ in range(nb):
            c=[(i,p) for i,(s,ee) in enumerate(sp) if s==site for p in range(5) if not covered(i,p)]
            if not c: S['coins']+=3*(1+.5*e);continue
            i,p=R.choice(c);lab.append([i,p,R.random()<max(.1,.6-.12*S['precLv'])*.35,LABMIN[e]])
        S['coins']+=stam/38*2.5*9.5*(1+.5*e)
    def next_site():
        # nächste offene Fundstelle, die noch nicht fertig ist
        for s,(e,n,c) in enumerate(SITES):
            if unlocked(e) and not site_done(s) and s!=site: return s
        return None
    times=sorted((d*24+h)*60 for d in range(days) for h in sessions)
    minute=0;ads_day=0;day=-1;finish_day=None;free_fill=0
    for sm in times:
        dt=sm-minute;lab_step(dt);carry+=dt/regen_min();a=int(carry);carry-=a;st=min(smax(),st+a) if st<smax() else st;minute=sm
        if sm//1440!=day:day=sm//1440;ads_day=0;st+=20;S['tix']+=1;free_fill=1 if S['camp']>=2 else 0
        S['coins']+=rate()*min(8,(sm-last)/60);last=sm
        if free_fill and st<smax()*.3:st=smax();free_fill=0
        ads=0
        for _ in range(ads_per_session):
            if ads_day>=ad_cap:break
            ads_day+=1;ads+=1
            if lab and R.random()<.4:x=max(lab[:2+S['benchLv']],key=lambda x:x[3]);x[3]=max(0,x[3]-.2*LABMIN[sp[x[0]][1]]);lab_step(0)
            else: st+=20
        # Reisen, wenn die Fundstelle fertig ist
        while site_done(site):
            ns=next_site()
            if ns is None:break
            need=tickets(site,ns)
            while S['tix']<need and ads_day<ad_cap and ads_per_session>0: ads_day+=1;S['tix']+=1;tix_ad+=1
            while buy_tickets and S['tix']<need and S['coins']>=max(30,rate()): S['coins']-=max(30,rate());S['tix']+=1;tix_buy+=1
            if S['tix']<need: stuck+=1;break
            S['tix']-=need;flights+=1;site=ns;S['tix']+=0
        if st>0:dig(st);st=0
        while True:
            o=[(price(k),k) for k in ('bench','energy','regen','prec','probe','camp') if price(k)]
            if not o:break
            p,k=min(o)
            if S['coins']<p:break
            S['coins']-=p;S[k+('Lv' if k!='camp' else '')] = S[k+('Lv' if k!='camp' else '')]+1;buys.append((round(sm/1440,1),k,p))
        if completed()==len(sp) and finish_day is None and not lab: finish_day=round(sm/1440,1)
        hist[day+1]=dict(done=completed(),site=site,rate=round(rate()),coins=round(S['coins']),tix=S['tix'],camp=S['camp'],smax=smax())
    return dict(fertig=finish_day,flüge=flights,tix_video=tix_ad,tix_münzen=tix_buy,festgesteckt=stuck,lager=[b for b in buys if b[1]=='camp'],hist=hist)
for name,sess,ads in [("Normal: 4 Besuche, 3 Videos",[8,12.5,17,21.5],3),("Kari: 5 Besuche, 6 Videos",[8,11,14,17,20.5],6),("Ohne Werbung, 4 Besuche",[8,12.5,17,21.5],0)]:
    r=[sim(sess,ads,seed=s) for s in range(12)]
    print(f"\n{name}")
    print("  alles fertig an Tag:",statistics.median([x['fertig'] or 99 for x in r]))
    print("  Flüge:",statistics.median([x['flüge'] for x in r]),"· Tickets per Video:",statistics.median([x['tix_video'] for x in r]),"· per Münzen:",statistics.median([x['tix_münzen'] for x in r]),"· Besuche ohne genug Tickets:",statistics.median([x['festgesteckt'] for x in r]))
    print("  Lager gekauft an Tag:",[ [b[0] for b in x['lager']] for x in r[:3]])
    h=r[0]['hist'];print("  Tag 3/7/14:",{d:h[d] for d in (3,7,14) if d in h})
