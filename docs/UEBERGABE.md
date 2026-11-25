# Fossiland – Übergabe für einen neuen Chat

Stand: 18.11.2026, App-Version **1.0.27**.

## Projekt in einem Satz

Fossiland ist ein Handyspiel nach dem Prinzip von Dino Quest, aber bewusst eigenständig gestaltet. Man gräbt Fossilien aus, präpariert sie im Labor und baut ein Museum mit 38 Skeletten auf. Es gibt sechs Erdzeitalter und 28 echte Fundstellen auf einer Weltkarte. Das Spiel ist in Deutsch, Englisch, Französisch und Spanisch spielbar.

## Wo alles liegt

| Was | Wo |
| --- | --- |
| Quellcode und Grafiken | GitHub `Familienplaner-droid/fossiland` (`src/game.html`, `src/assets/`) |
| Android-App | Jeder Push auf `main` baut automatisch ein Release `v1.0.x` mit APK (GitHub Actions). Commits mit `[skip ci]` bauen nicht. |
| Spiel im Browser (Artifact) | https://claude.ai/artifact/8NMWQ2AnH5ZY3X7ii6oe4e (Seite `index.html` und Ordner `assets/`, zuletzt Version 38) |
| Auswertung der Testberichte | https://claude.ai/artifact/5M13CEfnApfwE3DR5mXPa1. Die Datenbank-Sammlung `reports` hat eine Zeile pro Tester, Dokument-ID = Tester-ID: ZMF3 Kari, 1X9K Jano, 6YM3 Finn. |
| Tester-Anleitung | Claude-Doc „Fossiland Testrunde“ (Container `33020658-ce3e-485b-9255-ac09bb7f8fac`), auch als PDF exportiert |
| Offline-Datei | `python3 tools/build_download.py Fossiland.html` bettet alle Grafiken ein (etwa 16 MB) |
| Hilfsskripte | `tools/`: Blender-Jobs, Playwright-Tests, Wirtschafts-Simulationen. Die Pfade darin stammen aus der alten Arbeitsumgebung und müssen angepasst werden. |

### Arbeitsweise

- Im Chat das Repo anhängen (`add_repo`, Zugriff „push“) und klonen.
- `src/game.html` bearbeiten.
- Mit Playwright testen: Spiel über einen lokalen Server mit `assets/` daneben laden, auf Handy- und Querformat achten.
- Pushen. Danach mit `gh run list` und `gh api repos/Familienplaner-droid/fossiland/releases` auf die neue APK warten.
- Das Artifact mit der Seite und den geänderten Dateien unter `assets/` neu veröffentlichen.

### Absprachen

- Bei größeren Änderungen **erst planen und besprechen, nicht direkt programmieren**.
- Bilder erstellt der Spielentwickler selbst aus ChatGPT. Dafür bekommt er je Bild einen eigenen Prompt, damit er ihn einzeln kopieren kann. Der Stil ist gemalt und comichaft, passend zur Paläontologin.
- Pushen ist für App-Builds der übliche Weg.

## Technik im Überblick

**Eine Datei.** `src/game.html` enthält HTML, CSS und JavaScript (rund 260 KB).
- Spielstand: Objekt `S` in `localStorage` unter dem Schlüssel `"fossilfieber"`.
- Texte: `t(key, vars)`. Neue Texte werden per `for(const [l,o] of Object.entries({...}))Object.assign(TX[l],o);` für alle vier Sprachen ergänzt.
- Grafiken: immer über `aurl("name.webp")` einbinden, nie den Text `assets/` direkt in den Code schreiben. Das Build-Skript für die Offline-Datei bricht sonst ab (Ausnahme: CSS `url(assets/…)`).

**Android.**
- Capacitor 8, App-ID `com.familienplaner.fossiland`, minSdk 24.
- Fester Testschlüssel `android/app/test-signing.p12` (Passwort und Alias `fossiland-test`), damit Updates sich installieren lassen.
- Plugins:
  - `@capacitor/local-notifications`: Labor fertig, Energie voll, Serie in Gefahr um 18 Uhr; still zwischen 21:00 und 7:30.
  - `@capacitor-community/admob`: Belohnungsvideos mit Googles **Test-IDs**, `ADS_TESTING=true`, kindgerecht markiert.
  - `@capacitor/share`: Testbericht teilen.

**Ausgraben.**
- Raster aus Zellen mit 3 Bodenschichten. Jede Schicht hat eine eigene Textur, mit zufällig harten Stellen (`soil_<zeitalter>.webp`).
- Knochen liegen in einer Tiefe und können schräg durch Schichten gehen.
- Die Sonde zeigt nur den Ort, danach muss man suchen.
- Spezialwerkzeuge: Radar und Presslufthammer, einmal per Video oder 3 Stück für Münzen.
- Beschädigte Knochen müssen erst präpariert und dann im Labor per Video restauriert werden. Das dauert so lange wie das Präparieren (`LABMIN = 60/90/130/180/240/300` Minuten je Zeitalter).
- Zeichnen mit Zwischenspeicher (`pitCache`), Pixeldichte höchstens 2. Das war nötig für schwache Handys wie Janos.

**Weitere Funde und Belohnungen.**
- Seltene Funde: 12 Stück (`RARES`, Bilder `r_*.webp`), Chance 7 % plus 1,5 % pro Fehlversuch. Sie stehen in der Museumsvitrine und bringen 3 Münzen pro Stunde.
- Tagesaufgaben, Tagestruhe, Serie, eine Anleitung mit Tipp-Hand und 5 Posen der Paläontologin (`guide_*`).

**Wirtschaft.**
- Energie: 60 Punkte, 1 Punkt alle 4 Minuten. +20 pro Video und pro Münzkauf.
- Videos: insgesamt höchstens 30 pro Tag (`AD_LIMIT`), Zurücksetzen um 0:00 Uhr.
- Zeitalter werden freigeschaltet mit 0, 0, 3, 8, 15 und 22 vollständigen Skeletten.

**Expeditionskarte.**
- `SITES` enthält 28 Fundstellen mit Position `x/y` auf der Weltkarte (1774 × 887).
- 18 davon liegen auf Detailkarten (1536 × 1024): Mitteleuropa (`r:"eu"`) und Westliche USA (`r:"us"`), jeweils mit `rx/ry`.
- Alle Kartenbilder liegen in doppelter Auflösung vor (per KI vergrößert). Höchster Zoom: 2.
- Flugtickets: 3 auf demselben Kontinent, 6 auf einen anderen. 1 Ticket pro Video, oder für Münzen zum Preis von 1 Stunde Einnahmen (mindestens 30). Geschenkt: 2 je komplett ausgegrabener Fundstelle und 1 aus der Tagestruhe.
- Reisepass mit Stempeln.
- Expeditionslager in der Werkstatt für 2.500, 7.500 und 20.000 Münzen: +20, +20 und +30 Energie, eine tägliche Gratis-Füllung und 15 % schnelleres Aufladen.
- Alte Spielstände bekamen einen Freiflug je offener Fundstelle.

**Statistik für Tester.**
- Besuche zählen erst nach 10 Minuten Abwesenheit.
- Erfasst werden auch Spielzeit, Videos und Ereignisse.
- „Testbericht senden“ in der Werkstatt hängt eine Zeile `FSL1:…` an (base64). Diese wird in die Auswertungsseite übernommen.

**Museum (seit 1.0.27).**
- Knopf „Museum betreten“ im Museum öffnet einen isometrischen Grundriss (`openHall`, Code-Abschnitt „Museum (Grundriss)“). Spielstand in `S.hall` (v:2).
- Rundgang aus 3×3 Plätzen zu je 16×16 Feldern: Eingangshalle → Perm … Eiszeit → Schatzkammer, Innenhof in der Mitte. Säle bauen, in 3 Stufen vergrößern (10 bis 16 Felder) und umbenennen.
- Exponate: gemalte Skelette `ex_<id>.webp` aus ChatGPT, Sockel-Messpunkte in `HALLMETA` (neu erzeugen mit `python3 tools/hall/meta.py src/assets`), Größe in Feldern `HALL_SZ`. Kleine Tiere stehen auf Säulen.
- Deko `dk_<art>.webp` (Tabelle `HDECO`, nur zum Anschauen), seltene Funde in Vitrinen (`dk_vitrine.webp`), Boden/Wand `hall_floor.webp`/`hall_wall.webp`, Besucher `vis_<art>_f/_b.webp`.
- Preise aus `tools/sim/museum.py`: Bau 150 bis 3.000, Vergrößern ×3/×8/×20. **Noch einmal mit dem Spielentwickler durchgehen** (Kosten und Einkommen insgesamt).
- Alle Bild-Prompts stehen im Claude-Doc „Fossiland – Prompts für die Museumshalle“ (https://claude.ai/artifact/GxfDfGheydk2qZQRQQEZgm).
- Testbericht schreibt jetzt Werbefehler mit (Code, Meldung, online) – wichtig für Janos Problem „kein Video“ (Family Link?).

## Tester

Kari, Jano und Finn. Ihre Berichte vom 14. bis 16.11. sind ausgewertet und die gefundenen Fehler behoben:
- Update ließ sich nicht installieren
- Anleitung startete nicht
- Grabung ging beim Wechsel verloren
- Besuche wurden doppelt gezählt
- Spiel lief auf Janos Handy zu langsam

## Nächste Schritte

- Testberichte zu 1.0.27 abwarten (Museum, Werbefehler bei Jano).
- Kosten und Einkommen im ganzen Spiel gemeinsam prüfen (der Spielentwickler sieht Ungereimtheiten).
- Später: mehr seltene Funde (Bilder kommen vom Spielentwickler) sowie mehr Fundstellen und Arten.
- Vorbereitung für den Play Store:
  - echte AdMob-IDs
  - Einwilligungsabfrage (UMP/DSGVO)
  - Datenschutzerklärung
  - Familienrichtlinien
  - Release-Schlüssel als GitHub-Secrets (siehe README)
  - Spielstand in der Cloud

## Erweiterung: sechs neue Zeitalter (Stand 21.11.2026)
- Zeitalter 6–11: Kambrium, Ordovizium, Silur, Devon, Karbon, Neogen (nach der Eiszeit, `need` 30–50 Skelette). 30 neue Arten, 21 Fundstellen, 12 seltene Funde, Texte in 4 Sprachen.
- Prompts: Doc „Fossiland – Prompts für neue Zeitalter“ (https://claude.ai/artifact/9C4jYZSgiWLQL8xYs1STr4).
- Fehlende Bilder zeigen eine Infotafel „Bild folgt bald“ (`iurl()`). Gelieferte Bilder der neuen Arten/Funde in `HAVE` eintragen (z. B. `"ex_parad.webp"`), für die Halle danach `tools/hall/meta.py` laufen lassen.
- `soil_6`–`soil_11` sind vorläufig eingefärbte Kopien von `soil_1`; die Landschaft wird bis zum Bild gezeichnet (`SCENES`).
- Neue Arten stehen in der Halle in den vorhandenen Sälen (eigene Säle gibt es noch nicht).

## Zeitalter in echter Reihenfolge (21.11.)
- Index jetzt chronologisch: 0 Kambrium, 1 Ordovizium, 2 Silur, 3 Devon, 4 Karbon, 5 Perm, 6 Trias, 7 Jura, 8 Kreide, 9 Paläogen, 10 Neogen, 11 Eiszeit.
- `need` = [0,0,3,6,10,14,18,23,28,35,41,46]; Wirtschaft über `eraL(e)=e*5/11` (Stufe 0–5 wie vorher), LABMIN 40…300 min.
- `scene_/floor_` gibt es nur für 5,6,7,8,9,11 (`SCENE_IMG`); `soil_0..11` umbenannt. Schnee: `S.era===11`.
- Neue Arten/Funde stehen in `NEWC`/`NEWR` (Platzhalter über `iurl`, bis Bild in `HAVE`).
- Spielstand-Migration (`S.eraV=2`): alte Nummern über N=[5,6,7,8,9,11,0,1,2,3,4,10]; früher erreichte Zeitalter bleiben über `S.eraKeep` offen.

## Museumsbilder und Fundstücke der neuen Arten (21.11.)
- 3D-Werkstatt läuft wieder: `pip install bpy`, Skripte nach /home/claude/fossil3d kopieren. Wirbeltiere: `skel3d.py <id>` (CRE-Liste), Wirbellose: `invert.py <id>` (SPEC), Fundstücke: `sprites.py all`.
- Packen wie pack.py (Maske ×40 als _m.png). Fertige Arten in `SKOWN` eintragen (dann normales Museumsbild statt ex_/Platzhalter).
- Fundstücke je Tiergruppe: `SPRX` (trilo, soft, lobo) über `sprOf(id,teil)`; andere Gruppen nutzen noch Knochen.
- Hallucigenia hat Gruppe `lobo` (Teil „Stacheln“ statt „Lappen“).
- Erledigt: Kambrium (parad, anoma, opabi, hallu, pikai).

## Testberichte 22.11.
- Bericht: „von 12 Zeitaltern“ (war fest 6), Ereignisse auf die letzten 15 gekürzt (WhatsApp schnitt die FSL1-Daten ab), ResizeObserver-Warnung wird nicht mehr als Spielfehler gezählt.
- LABMIN zurück auf die alten Werte für Perm–Eiszeit (Umsortierung hatte Perm/Trias verlangsamt), frühe Zeitalter 20–60 min.

## Bilder der neuen Zeitalter komplett (24.11.)
- Alle 6 neuen Zeitalter haben Hallen-Exponat (ex_), Comic-Lebendbild (live_), Echt-Bilder (real_/realsk_), Landschaft (scene_), Boden (soil_) und seltene Funde.
- Werkzeuge: /tmp/pairped.py (Sockel-Paare angleichen, Sockel nur untere Bildhälfte), /tmp/rescale.py (Größenvergleich maßstabsgetreu neu setzen: id:Länge_m:coin|hand|man, negative Länge = Höhe; SILX=Anteil links, ab dem die Silhouette gesucht wird).
- Offen: eigene Hallen-Säle für Kambrium–Karbon und Neogen.

## Museums-Anbau (24.11.)
- Raster jetzt 5×5 Sektoren (HN=5*HS), genutzt werden 4 Reihen × 5 Spalten. Neuer Flügel rechts: zt (Zeittunnel, 2,3), kam (2,4), ord (1,4), sil (0,4), dev (0,3), kar (1,3) mit Tür zu e0 (Perm). Neogen-Saal „neo“ auf (2,0), Eiszeit e5 eine Reihe nach vorne auf (3,0).
- Haupteingang jetzt vorne (ax "i") an der Eingangshalle. Bounds/Zoom über hExt().
- Migration S.hall.m2: Inhalte im alten Eiszeit-Sektor werden um HS verschoben; wer den Eiszeit-Saal hat, bekommt den Neogen-Saal geschenkt (sonst wäre er abgeschnitten).
- Neue Spielstände: Eingangshalle + Zeittunnel + Kambrium-Saal gebaut.
- Fix: hSpot suchte den Saal per "e"+Zeitalter-Index (seit der Umsortierung falsch), jetzt per r.e.

## Kleintier-Vitrinen (24.11.)
- SMALL (Zeitalter → [id, Länge m]) für Kambrium–Karbon; diese Arten stehen nicht einzeln, sondern in der Vitrine ihres Saals (S.hall.kv[era], kind "k", Fußabdruck 1×2).
- Bilder: vit_open.webp (Vitrine ohne Glas), vit_glass.webp (Glas-Overlay aus Differenz), vk_sheet.webp (alle freigestellten Kleintier-Fossilien in einem Bild, Lage in VKPOS; die Browser-Version darf höchstens 512 Dateien haben). DECOMETA.vitk.
- Migration S.hall.m3: einzeln aufgestellte Kleintiere wandern in die Vitrine.

## Museumsbilder für alle neuen Arten (25.11.)
- Alle 30 neuen Arten haben jetzt eigene 3D-Museumsbilder (skel3d.py für Wirbeltiere, invert.py für Trilobiten, Seeskorpione, Tausendfüßer, Libelle, Cameroceras).
- sk_<id>.webp enthält jetzt oben das Bild und unten die Teile-Maske (Graustufen ×40); die _m.png-Dateien gibt es nicht mehr (Dateilimit der Browser-Version).
- Neue Fundstück-Sätze: arthro (ar_), shell (sh_), insect (in_). Meganeura hat jetzt die Gruppe „insect“ (Kopf, Brust, Hinterleib, Flügel, Beine).

## Sonden pro Tag (Nov. 2026)
- Bodensonde gilt jetzt pro TAG statt pro Grabung: `probesMax()=1+S.probeLv`, Stufen 0–9 → 1 bis 10 Sonden/Tag.
- Vorrat `S.pr`, Tageswechsel in `prTick()` (S.prDay): Vorrat wird aufgefüllt, Ungenutztes verfällt, Zähler S.prAd/S.prBuy zurück.
- Ausbaukosten `PROBE_COST=[150,300,500,800,1200,1800,2600,3600,5000]` (Summe 15.950).
- Leer → Knopf „Sonden holen“ → `prOffer()`: Video = +2 (max. `PRAD_MAX=10` am Tag, zählt ins Werbelimit) oder Münzen = +2 für `max(100, rate())` (= 1 Std. Eintritt), jeder weitere Kauf am Tag doppelt.
- Bestandsspieler sehen einmalig `prNewsShow()`. Tagesaufgabe „Sonde benutzen“ verlangt höchstens probesMax().

## Sammeltruhe und Meisterwerkzeuge (Nov. 2026)
- `adReward` → `chKey()`: jedes Video = 1 Schlüssel (`S.chest.k`), `CH_KEYS=4` öffnen eine Truhe (`openChest`). Zähler verfällt nie.
- Inhalt: +2 Werkzeugteile (`S.chest.p`, entfällt wenn alle Meisterwerkzeuge Gold sind) und abwechselnd ein exklusives Exponat (1., 3., 5. … Truhe; Reihenfolge `XD`) oder ein Spezialwerkzeug (Radar/Presslufthammer).
- Exponate: 20 Einträge in `XD` (id, Grundfläche, Bildfaktor, flach), werden in `HDECO` mit `x:1,p:0` eingetragen (nicht kaufbar, im Deko-Lager nur wenn besessen, besessene zuerst). Bilder kommen in EIN Sammelbild `xd_sheet.webp` (Dateilimit 512!): Lage in `XDPOS[id]=[x,y,w,h]`, Größe in `XDSHEET`, Ankerpunkte in `DECOMETA[id]`. Solange `XDPOS` leer ist: Platzhalter („?“, im Saal dk_case).
- Kopfzeile: Truhen-Knopf `#chBtn` (Badge k/4, pulsiert wenn voll). Unter 440 px Breite ist der Ton-Knopf ausgeblendet; „Ton an/aus“ steht zusätzlich in der Werkstatt.
- Meisterwerkzeuge (`S.tt`, erst ab Profi-Hacke 5): Pinsel und Hacke je Bronze/Silber/Gold. Kosten `TT_PARTS=[3,6,10]` Teile + `TT_H=[2,4,8]` Stunden Eintritt (`max(100,rate())`). Pinsel: Doppelstrich `TT_BR` 15/30/50 %; Hacke: Risse `TT_CR` 7/4/2 %, Gratis-Schläge +`TT_FR` 6/12/20 %. Werkzeugknöpfe bekommen Farbfilter `tt1–3` und einen Stern.
- Bilder: alle 20 Exponate + Truhe zu/offen (`chest`, `chesto`) liegen in `xd_sheet.webp`. Neu bauen: Einzelbilder freistellen mit `tools/xd/cut.py` nach /tmp/xd/<id>.png, dann `tools/xd/build.py` (Sammelbild + Größen/Anker) und `tools/xd/inject.py` (schreibt XDPOS/XDMETA/XDSHEET und Bildfaktoren in game.html; Handkorrekturen in OV). Terrarium: Schachbrett im Glas wurde zu halbtransparentem Glas umgerechnet.
