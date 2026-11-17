"""Wirtschafts-Simulation für das Museum (Säle, Vergrößerungen, Deko).

Rechnet Tag für Tag: Einnahmen nach den Formeln aus game.html (crRate, seltene Funde), Fortschritt
an fertigen Skeletten, bisherige Ausgaben (Werkstatt, Expeditionslager) und die neuen Museumskosten.
Der Fortschritt ist an den Testberichten geeicht (Kari: 8 Skelette nach 3 Tagen, Finn: 5 nach 2 Tagen).

Aufruf: python3 tools/sim/museum.py            (Standardspieler und Gelegenheitsspieler)
"""
import math

SPECIES = [5, 5, 7, 9, 6, 6]          # Arten je Zeitalter
NEED = [0, 0, 3, 8, 15, 22]           # fertige Skelette zum Freischalten
LABMIN = [60, 90, 130, 180, 240, 300]
RARE_RATE = 3

# Bisherige Ausgaben, wie in game.html
WORKSHOP = (sum(round(220 * 1.58 ** i) for i in range(10)) + sum(round(450 * 1.9 ** i) for i in range(5))
            + sum(round(300 * 1.85 ** i) for i in range(5)) + sum(round(180 * 1.8 ** i) for i in range(5)) + 2500 + 12000)
CAMP = [2500, 7500, 20000]

# Museum: Baupreis je Saal; Vergrößern = Baupreis × GROW[Stufe]
# Perm-Saal und Eingangshalle stehen von Anfang an; die Schatzkammer wird mit dem ersten seltenen Fund baubar
ROOMS = {"ein": None, "e0": 150, "e1": 150, "e2": 400, "e3": 1200, "e4": 2000, "e5": 3000, "sch": 600, "hof": 1500}
GROW = [3, 8, 20]
DECO = dict(fern=300, cycad=300, bench=250, info=200, rope=150, lamp=250, case=700, globe=600, nest=900, ammo=800, desk=1500, carpet=400)


def cr_rate(e, done_era):
    ok = 5
    return round((4 + 2 * e + ok * (1 + e // 2)) * (1.5 if done_era else 1))


def income(n_done):
    """Eintritt pro Stunde, wenn n_done Skelette (in Zeitalter-Reihenfolge) fertig sind, plus seltene Funde."""
    r, left = 0, n_done
    for e, n in enumerate(SPECIES):
        k = min(n, left); left -= k
        r += k * cr_rate(e, k == n)
    rares = min(12, round(n_done * 12 / 38))
    return r + rares * RARE_RATE


def simulate(bones_per_day, hours_counted, extra_per_day, days=45, rooms=ROOMS, grow=GROW, show=False):
    """bones_per_day: neue Knochen am Tag (früh); später bremst das Labor (lange Präparierzeiten)."""
    total = sum(SPECIES) * 5
    bones, coins, spent_old = 0.0, 0.0, 0
    old_queue = sorted([*(round(220 * 1.58 ** i) for i in range(10)), *(round(450 * 1.9 ** i) for i in range(5)),
                        *(round(300 * 1.85 ** i) for i in range(5)), *(round(180 * 1.8 ** i) for i in range(5)), 2500, 12000, *CAMP])
    log = []
    for d in range(1, days + 1):
        done = int(bones // 5)
        era = max(e for e in range(6) if done >= NEED[e])
        lab_cap = 3.2 * 1440 / LABMIN[era] * 0.55          # 3 Werkbänke, Videos beschleunigen, nicht rund um die Uhr nachgelegt
        bones = min(total, bones + min(bones_per_day, lab_cap))
        done = int(bones // 5)
        inc = income(done)
        coins += inc * hours_counted + extra_per_day * (1 + .5 * era)
        # Spieler kauft zuerst die günstigsten Werkstatt-Ausbauten, solange sie nicht mehr als 40 % der Münzen kosten
        while old_queue and old_queue[0] <= coins * .4:
            coins -= old_queue[0]; spent_old += old_queue.pop(0)
        log.append(dict(day=d, done=done, era=era, inc=inc, coins=round(coins), old=spent_old, perday=round(inc * hours_counted)))
    return log


def report(name, log):
    print(f"\n== {name} ==")
    print(" Tag  fertig  Zeitalter  Eintritt/Std  Münzen/Tag  Werkstatt bezahlt")
    for r in log:
        if r["day"] in (1, 2, 3, 5, 7, 10, 14, 18, 21, 25, 30, 35, 40, 45):
            print(f"{r['day']:4} {r['done']:7} {r['era']:10} {r['inc']:13} {r['perday']:11} {r['old']:12}")
    unlock = {}
    for r in log:
        for e in range(6):
            if r["done"] >= NEED[e] and e not in unlock:
                unlock[e] = r
    print(" Zeitalter frei an Tag:", {e: unlock[e]["day"] for e in unlock})
    return unlock


def room_table(unlock, rooms=ROOMS, grow=GROW):
    print("\n Saal  Bau   (Std. Eintritt)   Stufe 2     Stufe 3     Stufe 4      Summe")
    total = 0
    for rid, c in rooms.items():
        if not c:
            continue
        e = int(rid[1]) if rid.startswith("e") else (1 if rid == "sch" else 3)
        inc = unlock.get(e, unlock[max(unlock)])["inc"] or 1
        g = [round(c * x / 50) * 50 for x in grow]
        s = c + sum(g); total += s
        print(f" {rid:4} {c:6} ({c / inc:5.1f} h)   " + "  ".join(f"{x:7} ({x / max(inc, 1):4.0f}h)" for x in g) + f"   {s:7}")
    deco = sum(DECO.values())
    print(f" Alle Säle voll ausgebaut: {total}   ·   je ein Stück jeder Deko: {deco}   ·   Werkstatt + Lager zusammen: {WORKSHOP + sum(CAMP)}")


if __name__ == "__main__":
    # Fleißig (wie Kari): ~20 Knochen am Tag früh, fast 22 Std. Eintritt gezählt (8 Std. Offline-Grenze)
    L1 = simulate(bones_per_day=20, hours_counted=21.5, extra_per_day=250)
    u1 = report("fleißiger Spieler", L1)
    room_table(u1)
    # Gelegenheitsspieler: ~8 Knochen am Tag, 2 Besuche, ~14 Std. gezählt
    L2 = simulate(bones_per_day=8, hours_counted=14, extra_per_day=120, days=60)
    u2 = report("Gelegenheitsspieler", L2)
    room_table(u2)
