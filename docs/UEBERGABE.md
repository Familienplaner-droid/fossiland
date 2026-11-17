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
