"""Economy simulation for Fossilfieber. A player plays 4 sessions a day; we track coins, upgrades and progress."""
import random, sys, statistics

SPECIES = [5, 5, 7, 9, 6, 6]
NEED = [0, 0, 3, 8, 15, 22]
LABMIN = [60, 90, 130, 180, 240, 300]
SESSIONS = [8.0, 12.5, 17.0, 21.5]          # hours of day
ADS_PER_SESSION = 3
AD_LIMIT = 12
VIDEO_LAB = 0.20                             # share of total prep time per video
OFFLINE_CAP_H = 8


def make_params(**kw):
    p = dict(
        income_per_hour=True, income_scale=1.0,
        # upgrade price = base * growth**level
        energy=(150, 1.55, 12), regen=(250, 1.75, 5), bench=None, prec=(200, 1.8, 5), probe=(120, 1.7, 5),
        bench_prices=[1500, 6000],
        regen_s0=360, regen_step=30, sta0=40, sta_step=5,
        relic_base=9.5, complete_base=50, era_bonus=150,
        buy_sta_base=60,
    )
    p.update(kw)
    return p


def cr_rate(e, ok, era_done):  # coins per hour for one finished skeleton
    return (4 + 2 * e + ok * (1 + e // 2)) * (1.5 if era_done else 1)


def simulate(P, days=28, seed=1, verbose=False):
    R = random.Random(seed)
    S = dict(coins=30, energyLv=0, regenLv=0, benchLv=0, precLv=0, probeLv=0)
    museum = {(e, i): {} for e in range(6) for i in range(SPECIES[e])}
    lab = []          # [species, part, cracked, remaining_min, total_min]
    st = P['sta0']; st_carry = 0.0
    hist = {}
    ads_today = 0
    buys = []
    t_end = days * 24 * 60
    sess_minutes = sorted(int((d * 24 + h) * 60) for d in range(days) for h in SESSIONS)
    last_collect = 0
    daily_bonus_day = -1

    def done(sp): return len(museum[sp]) == 5
    def completed(): return sum(done(k) for k in museum)
    def era_done(e): return all(done((e, i)) for i in range(SPECIES[e]))
    def unlocked(e): return completed() >= NEED[e]
    def income_h(): return sum(cr_rate(k[0], sum(v == 'ok' for v in museum[k].values()), era_done(k[0])) for k in museum if done(k)) * P['income_scale']
    def sta_max(): return P['sta0'] + P['sta_step'] * S['energyLv']
    def regen_min(): return (P['regen_s0'] - P['regen_step'] * S['regenLv']) / 60
    def covered(k, i): return i in museum[k] or any(x[0] == k and x[1] == i for x in lab)
    def eramult(e): return 1 + 0.5 * e

    def price(k):
        if k == 'bench':
            return P['bench_prices'][S['benchLv']] if S['benchLv'] < 2 else None
        b, g, mx = P[k]
        return round(b * g ** S[k + 'Lv']) if S[k + 'Lv'] < mx else None

    def finish(item):
        k, i, cr = item[0], item[1], item[2]
        was = done(k)
        museum[k][i] = 'cr' if cr else 'ok'
        if not was and done(k):
            S['coins'] += P['complete_base'] * eramult(k[0])
            if era_done(k[0]):
                S['coins'] += P['era_bonus'] * (k[0] + 1)

    def lab_step(minutes):
        # advance lab by `minutes`, benches process in queue order
        while minutes > 0 and lab:
            benches = 2 + S['benchLv']
            active = lab[:benches]
            dt = min(minutes, min(x[3] for x in active))
            for x in active:
                x[3] -= dt
            minutes -= dt
            for x in [x for x in active if x[3] <= 1e-9]:
                lab.remove(x); finish(x)

    def dig(stamina):
        # returns found bones/relics for spending `stamina`
        cost_per_dig = R.uniform(32, 44) * (1 - 0.03 * S['probeLv'])
        frac = stamina / cost_per_dig
        e = max([e for e in range(6) if unlocked(e) and any(not covered((e, i), p) for i in range(SPECIES[e]) for p in range(5))] or [0])
        bones = 0; relics = 0
        n_bones = frac * 2.35
        nb = int(n_bones) + (1 if R.random() < n_bones % 1 else 0)
        for _ in range(nb):
            cands = [((e, i), p) for i in range(SPECIES[e]) for p in range(5) if not covered((e, i), p)]
            if not cands:
                S['coins'] += 3 * eramult(e); continue
            k, p = R.choice(cands)
            cr = R.random() < (max(.1, .6 - .12 * S['precLv'])) * 0.35
            lab.append([k, p, cr, LABMIN[e], LABMIN[e]])
            bones += 1
        nr = frac * 2.5
        S['coins'] += nr * P['relic_base'] * eramult(e)
        return e

    minute = 0
    finished_day = None
    for sm in sess_minutes:
        # advance time to session
        dt = sm - minute
        lab_step(dt)
        st_carry += dt / regen_min()
        add = int(st_carry); st_carry -= add
        st = min(sta_max(), st + add) if st < sta_max() else st
        minute = sm
        day = sm // 1440
        if day != daily_bonus_day:
            daily_bonus_day = day; ads_today = 0
            st += 20
        hrs = min(OFFLINE_CAP_H, (sm - last_collect) / 60)
        S['coins'] += income_h() * hrs
        last_collect = sm
        # ads
        for _ in range(ADS_PER_SESSION):
            if ads_today >= AD_LIMIT: break
            ads_today += 1
            if lab and R.random() < 0.6:
                x = max(lab[:2 + S['benchLv']], key=lambda x: x[3])
                x[3] = max(0, x[3] - VIDEO_LAB * x[4]); lab_step(0)
            else:
                st += AD_STA
        # dig everything
        if st > 0:
            dig(st); st = 0
        # buy upgrades greedily (cheapest first)
        while True:
            opts = [(price(k), k) for k in ('bench', 'energy', 'regen', 'prec', 'probe') if price(k)]
            if not opts: break
            pr, k = min(opts)
            if S['coins'] < pr: break
            S['coins'] -= pr; S[k + 'Lv'] += 1; buys.append((round(sm / 1440, 1), k, S[k + 'Lv'], pr))
        if completed() == 38 and finished_day is None and not lab:
            finished_day = round(sm / 1440, 1)
        if sm % 1440 == int(21.5 * 60):
            hist[day + 1] = dict(coins=round(S['coins']), done=completed(), inc=round(income_h()), lab=len(lab),
                                 lv=(S['energyLv'], S['regenLv'], S['benchLv'], S['precLv'], S['probeLv']))
    return hist, buys, finished_day


if __name__ == "__main__":
    P = make_params()
    hist, buys, fin = simulate(P, days=30, verbose=True)
    for d, h in hist.items():
        if d <= 30:
            print(d, h)
    print("finished day", fin)
    for b in buys:
        print(b)
