"""Simulation: Wie viele Videos schaut ein Spieler Tag für Tag?

Modell (je Tag):
- Spiellust: Der Spieler will am Tag eine bestimmte Menge Ausdauer verbrauchen (fleißig ~650, wie Kari am 17.11.).
- Kostenlose Ausdauer: Regeneration (Feldküche, Lager), über Nacht nur bis zum Vorrat (Feldflasche, Lager),
  Tagesbonus +20, Truhe +20, ab Lager Stufe 2 einmal am Tag den Vorrat gratis auffüllen.
- Was fehlt, füllt er mit Münzkäufen (wenn sie gemessen an seinen Münzen billig sind) oder Videos (+20) bis zu seiner Grenze.
- Zusätzliche Videos: Offline ×2, Truhe ×2, Labor (wenn die Warteschlange lang ist), optional Sonderausstellung.
- Fortschritt: gegrabene Knochen (Ausdauer / Ausdauer pro Knochen), aber das Labor begrenzt, was fertig wird.
- Münzen: Eintritt (Formeln aus game.html) + Funde; Ausgaben in Reihenfolge des Preises: Werkstatt, Lager, Museum.
Geeicht an den Testberichten bis 17.11.: Kari 11 Skelette nach 4 Tagen, ~21 Ausdauer pro Knochen, 20–30 Videos am Tag.

Aufruf: python3 tools/sim/ads.py
"""
SPECIES = [5, 5, 7, 9, 6, 6]
NEED = [0, 0, 3, 8, 15, 22]
LABMIN = [60, 90, 130, 180, 240, 300]
TOTAL = sum(SPECIES) * 5


def shop():
    it = [("energy", round(220 * 1.58 ** i)) for i in range(10)] + [("regen", round(450 * 1.9 ** i)) for i in range(5)]
    it += [("prec", round(300 * 1.85 ** i)) for i in range(5)] + [("probe", round(180 * 1.8 ** i)) for i in range(5)]
    it += [("bench", 2500), ("bench", 12000), ("camp", 2500), ("camp", 7500), ("camp", 20000)]
    return sorted(it, key=lambda x: x[1])


MUSEUM = sorted([150, 400, 1200, 2000, 3000, 600, 1500] + [c * g for c in (150, 150, 400, 1200, 2000, 3000, 600, 1500, 400) for g in (3, 8, 20)])


def cr_rate(e, full):
    return round((4 + 2 * e + 5 * (1 + e // 2)) * (1.5 if full else 1))


def income(done):
    r, left = 0, done
    for e, n in enumerate(SPECIES):
        k = min(n, left); left -= k; r += k * cr_rate(e, k == n)
    return r + min(12, round(done * 12 / 38)) * 3


def run(P, days=60):
    dug = lab_done = 0.0
    coins, out, q, mq = 0.0, [], shop(), list(MUSEUM)
    L = dict(energy=0, regen=0, prec=0, probe=0, bench=0, camp=0)
    for d in range(1, days + 1):
        done = int(lab_done // 5)
        era = max(e for e in range(6) if done >= NEED[e])
        rate = income(done)
        camp = L["camp"]
        pool = 60 + 5 * L["energy"] + [0, 20, 40, 70][camp]
        regen_day = 1440 / ((240 - 20 * L["regen"]) / 60) * (P["regen_mult"] if camp >= 3 else 1)
        night = regen_day * P["night_h"] / 24
        free = regen_day - max(0, night - pool) + 20 + 20 + (pool if camp >= 2 else 0)
        # Spiellust sinkt, wenn alles ausgegraben ist (kein Ziel mehr)
        appetite = P["appetite"] * (1 + P["site_grow"] * era) * (1 if done < 38 else P["endgame"])   # zielorientiert: Grabungen kosten je Zeitalter mehr
        gap, ads, buys = max(0, appetite - free), 0, 0
        while gap > 0:
            price = max(P["min_price"], rate * 1.33) * (1 + .5 * buys)
            if buys < P["buy_cap"] and price <= coins * P["coin_share"]:
                coins -= price; buys += 1; gap -= 20
            elif ads < P["ad_will"]:
                ads += 1; gap -= 20
            else:
                break
        used = appetite - max(0, gap)
        e_bone = P["e_bone"] * (1 + P["e_grow"] * era)
        new = min(TOTAL - dug, used / e_bone)
        dug += new
        lab_cap = (2 + L["bench"]) * 1440 / LABMIN[era] * P["lab_use"]
        lab_done = min(dug, lab_done + lab_cap)
        # andere Videos, solange die Grenze nicht erreicht ist
        other = [1, 1] + ([1] if dug - lab_done > 5 else []) + [1] * P["show"]
        for _ in other:
            if ads < P["ad_will"]:
                ads += 1
        coins += rate * P["hours"] + rate * P["offline_h"] + rate * 1 * P["show"] + P["dig_coins"] * (1 + .5 * era) * new
        while q and q[0][1] <= coins * .6:
            k, c = q.pop(0); coins -= c; L[k] += 1
        if P["museum"]:
            while mq and mq[0] <= coins * .5:
                coins -= mq.pop(0)
        out.append(dict(day=d, done=int(lab_done // 5), ads=ads, buys=buys, free=round(free), coins=round(coins)))
    return out


BASE = dict(appetite=650, night_h=10.5, regen_mult=1 / .85, lab_use=.6, e_bone=21, e_grow=0.0, coin_share=.15, buy_cap=99,
            min_price=55, ad_will=30, hours=21.5, dig_coins=12, offline_h=8, show=0, museum=True, endgame=.4, site_grow=0.0)
DAYS = (1, 2, 3, 4, 5, 7, 10, 14, 18, 21, 25, 30, 40, 50, 60)


def show(name, P):
    r = run(P)
    print(f"\n== {name} ==")
    print(" Tag:         " + " ".join(f"{d:4}" for d in DAYS))
    print(" Skelette     " + " ".join(f"{r[d-1]['done']:4}" for d in DAYS))
    print(" Videos       " + " ".join(f"{r[d-1]['ads']:4}" for d in DAYS))
    print(" Münzkäufe    " + " ".join(f"{r[d-1]['buys']:4}" for d in DAYS))
    print(" Gratis-Ausd. " + " ".join(f"{r[d-1]['free']:4}" for d in DAYS))
    fin = next((x["day"] for x in r if x["done"] >= 38), None)
    print(f" alle 38 fertig an Tag {fin} · Videos in 30 Tagen {sum(x['ads'] for x in r[:30])}, in 60 Tagen {sum(x['ads'] for x in r)}")


if __name__ == "__main__":
    show("Vorher (bis 1.0.27)", dict(BASE))
    NEW = dict(BASE, e_grow=.1, site_grow=.1, offline_h=2, show=3)
    show("Neu: +10 % je Zeitalter, Offline-Video +2 Std., Sonderausstellung 3×", NEW)
    show("Gelegenheitsspieler vorher (Lust 300, höchstens 10 Videos)", dict(BASE, appetite=300, ad_will=10, hours=14, lab_use=.4))
    show("Gelegenheitsspieler neu", dict(NEW, appetite=300, ad_will=10, hours=14, lab_use=.4))
